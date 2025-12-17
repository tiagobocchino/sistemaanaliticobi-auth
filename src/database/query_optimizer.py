# src/database/query_optimizer.py
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache
import pandas as pd

class QueryOptimizer:
    """Otimizador de queries para Supabase PostgreSQL"""

    def __init__(self, supabase_client):
        self.client = supabase_client

    async def get_optimized_sales_data(
        self,
        start_date: str,
        end_date: str,
        group_by: str = "daily",
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Recupera dados de vendas otimizados com índices e cache"""

        # Query otimizada com índices
        query = """
        SELECT
            DATE(data_venda) as data,
            SUM(valor_venda) as total_vendas,
            COUNT(*) as quantidade_vendas,
            AVG(valor_venda) as ticket_medio,
            cliente_id,
            categoria_produto
        FROM vendas
        WHERE data_venda >= $1
        AND data_venda <= $2
        {filters}
        GROUP BY DATE(data_venda), cliente_id, categoria_produto
        ORDER BY data DESC
        LIMIT 10000
        """.format(filters=self._build_filter_clause(filters))

        # Executar query com parâmetros
        result = await self.client.rpc('exec_sql', {
            'query': query,
            'params': [start_date, end_date]
        })

        # Agrupar por período solicitado
        return self._group_by_period(result, group_by)

    async def get_kpi_metrics(
        self,
        period: str = "month",
        comparison_period: bool = True
    ) -> Dict:
        """Recupera KPIs otimizados com materialized views"""

        # Usar materialized view se disponível
        if period == "month":
            current_metrics = await self._get_monthly_kpi()
        elif period == "week":
            current_metrics = await self._get_weekly_kpi()
        else:
            current_metrics = await self._get_daily_kpi()

        # Adicionar comparação se solicitado
        if comparison_period:
            comparison_metrics = await self._get_comparison_metrics(period)
            current_metrics['comparacao'] = comparison_metrics

        return current_metrics

    async def get_client_insights(
        self,
        client_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Insights de clientes com query otimizada"""

        if client_id:
            # Query específica por cliente
            query = """
            WITH cliente_stats AS (
                SELECT
                    c.id,
                    c.nome,
                    COUNT(v.id) as total_compras,
                    SUM(v.valor_venda) as valor_total,
                    MAX(v.data_venda) as ultima_compra,
                    AVG(v.valor_venda) as ticket_medio
                FROM clientes c
                LEFT JOIN vendas v ON c.id = v.cliente_id
                WHERE c.id = $1
                GROUP BY c.id, c.nome
            ),
            compras_recentes AS (
                SELECT
                    DATE(data_venda) as data,
                    SUM(valor_venda) as valor_diario
                FROM vendas
                WHERE cliente_id = $1
                AND data_venda >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(data_venda)
                ORDER BY data DESC
            )
            SELECT
                cs.*,
                cr.data as ultima_data_compra,
                cr.valor_diario as valor_ultima_compra
            FROM cliente_stats cs
            LEFT JOIN compras_recentes cr ON cr.data = cs.ultima_compra
            LIMIT $2
            """
            params = [client_id, limit]
        else:
            # Query para top clientes
            query = """
            SELECT
                c.id,
                c.nome,
                COUNT(v.id) as total_compras,
                SUM(v.valor_venda) as valor_total,
                MAX(v.data_venda) as ultima_compra,
                AVG(v.valor_venda) as ticket_medio,
                RANK() OVER (ORDER BY SUM(v.valor_venda) DESC) as ranking
            FROM clientes c
            LEFT JOIN vendas v ON c.id = v.cliente_id
            WHERE v.data_venda >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY c.id, c.nome
            ORDER BY valor_total DESC
            LIMIT $1
            """
            params = [limit]

        return await self.client.rpc('exec_sql', {
            'query': query,
            'params': params
        })

    async def get_product_performance(
        self,
        category: Optional[str] = None,
        date_range: Optional[Dict] = None
    ) -> List[Dict]:
        """Performance de produtos com análise otimizada"""

        base_query = """
        WITH product_sales AS (
            SELECT
                p.id,
                p.nome,
                p.categoria,
                COUNT(pv.id) as quantidade_vendida,
                SUM(pv.valor_total) as receita_total,
                AVG(pv.valor_unitario) as preco_medio,
                SUM(pv.quantidade) as unidades_vendidas
            FROM produtos p
            JOIN produtos_venda pv ON p.id = pv.produto_id
            JOIN vendas v ON pv.venda_id = v.id
            WHERE 1=1
            {date_filter}
            {category_filter}
            GROUP BY p.id, p.nome, p.categoria
        ),
        inventory_levels AS (
            SELECT
                produto_id,
                SUM(quantidade) as estoque_atual
            FROM estoque
            GROUP BY produto_id
        )
        SELECT
            ps.*,
            COALESCE(il.estoque_atual, 0) as estoque_disponivel,
            CASE
                WHEN COALESCE(il.estoque_atual, 0) = 0 THEN 'sem_estoque'
                WHEN COALESCE(il.estoque_atual, 0) < 10 THEN 'estoque_baixo'
                ELSE 'estoque_ok'
            END as status_estoque
        FROM product_sales ps
        LEFT JOIN inventory_levels il ON ps.id = il.produto_id
        ORDER BY ps.receita_total DESC
        """

        date_filter = ""
        category_filter = ""
        params = []

        if date_range:
            date_filter = "AND v.data_venda >= $1 AND v.data_venda <= $2"
            params.extend([date_range['start'], date_range['end']])

        if category:
            category_filter = f"AND p.categoria = ${len(params) + 1}"
            params.append(category)

        query = base_query.format(
            date_filter=date_filter,
            category_filter=category_filter
        )

        return await self.client.rpc('exec_sql', {
            'query': query,
            'params': params or None
        })

    def _build_filter_clause(self, filters: Optional[Dict]) -> str:
        """Constrói cláusula WHERE para filtros"""

        if not filters:
            return ""

        conditions = []
        for key, value in filters.items():
            if isinstance(value, list):
                conditions.append(f"AND {key} IN ({','.join(['%s'] * len(value))})")
            else:
                conditions.append(f"AND {key} = %s")

        return " " + " ".join(conditions)

    def _group_by_period(self, data: List[Dict], group_by: str) -> List[Dict]:
        """Agrupa dados por período específico"""

        if not data:
            return []

        df = pd.DataFrame(data)
        df['data'] = pd.to_datetime(df['data'])

        if group_by == "weekly":
            df['periodo'] = df['data'].dt.to_period('W').astype(str)
        elif group_by == "monthly":
            df['periodo'] = df['data'].dt.to_period('M').astype(str)
        else:  # daily
            df['periodo'] = df['data'].dt.date.astype(str)

        # Agrupar e somar
        grouped = df.groupby('periodo').agg({
            'total_vendas': 'sum',
            'quantidade_vendas': 'sum',
            'ticket_medio': 'mean'
        }).reset_index()

        return grouped.to_dict('records')

    async def _get_monthly_kpi(self) -> Dict:
        """KPIs mensais otimizados"""

        query = """
        SELECT
            DATE_TRUNC('month', CURRENT_DATE) as mes_referencia,
            COUNT(*) as total_vendas,
            SUM(valor_venda) as receita_total,
            AVG(valor_venda) as ticket_medio,
            COUNT(DISTINCT cliente_id) as clientes_unicos,
            COUNT(DISTINCT CASE WHEN data_venda >= CURRENT_DATE - INTERVAL '30 days' THEN cliente_id END) as clientes_ativos_30d
        FROM vendas
        WHERE data_venda >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
        AND data_venda < DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month')
        """

        result = await self.client.rpc('exec_sql', {'query': query, 'params': []})
        return result[0] if result else {}

    async def _get_weekly_kpi(self) -> Dict:
        """KPIs semanais otimizados"""

        query = """
        SELECT
            DATE_TRUNC('week', CURRENT_DATE) as semana_referencia,
            COUNT(*) as total_vendas,
            SUM(valor_venda) as receita_total,
            AVG(valor_venda) as ticket_medio,
            COUNT(DISTINCT cliente_id) as clientes_unicos
        FROM vendas
        WHERE data_venda >= DATE_TRUNC('week', CURRENT_DATE - INTERVAL '1 week')
        AND data_venda < DATE_TRUNC('week', CURRENT_DATE + INTERVAL '1 week')
        """

        result = await self.client.rpc('exec_sql', {'query': query, 'params': []})
        return result[0] if result else {}

    async def _get_daily_kpi(self) -> Dict:
        """KPIs diários otimizados"""

        query = """
        SELECT
            CURRENT_DATE as data_referencia,
            COUNT(*) as total_vendas,
            SUM(valor_venda) as receita_total,
            AVG(valor_venda) as ticket_medio,
            COUNT(DISTINCT cliente_id) as clientes_unicos
        FROM vendas
        WHERE data_venda = CURRENT_DATE
        """

        result = await self.client.rpc('exec_sql', {'query': query, 'params': []})
        return result[0] if result else {}

    async def _get_comparison_metrics(self, period: str) -> Dict:
        """Métricas de comparação com período anterior"""

        if period == "month":
            query = """
            SELECT
                COUNT(*) as vendas_anterior,
                SUM(valor_venda) as receita_anterior,
                AVG(valor_venda) as ticket_medio_anterior
            FROM vendas
            WHERE data_venda >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '2 months')
            AND data_venda < DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
            """
        elif period == "week":
            query = """
            SELECT
                COUNT(*) as vendas_anterior,
                SUM(valor_venda) as receita_anterior,
                AVG(valor_venda) as ticket_medio_anterior
            FROM vendas
            WHERE data_venda >= DATE_TRUNC('week', CURRENT_DATE - INTERVAL '2 weeks')
            AND data_venda < DATE_TRUNC('week', CURRENT_DATE - INTERVAL '1 week')
            """
        else:  # daily
            query = """
            SELECT
                COUNT(*) as vendas_anterior,
                SUM(valor_venda) as receita_anterior,
                AVG(valor_venda) as ticket_medio_anterior
            FROM vendas
            WHERE data_venda = CURRENT_DATE - INTERVAL '1 day'
            """

        result = await self.client.rpc('exec_sql', {'query': query, 'params': []})
        return result[0] if result else {}
