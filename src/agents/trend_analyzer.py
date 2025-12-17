"""
Analisador de Tendências para dados do CRM e ERP
"""
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime, timedelta
import json


class TrendAnalyzer:
    """Analisa tendências em dados temporais do CRM e ERP"""

    def analyze_sales_trend(
        self,
        data: List[Dict],
        date_column: str = 'data_venda',
        value_column: str = 'valor_venda',
        period: str = 'monthly'
    ) -> Dict[str, Any]:
        """
        Analisa tendências de vendas ao longo do tempo

        Args:
            data: Lista de dicionários com dados de vendas
            date_column: Nome da coluna de data
            value_column: Nome da coluna de valor
            period: Período de agregação ('daily', 'weekly', 'monthly')

        Returns:
            Dict com análise de tendência
        """
        if not data:
            return {
                "erro": "Dados vazios",
                "tendencia": "indefinido",
                "crescimento_percentual": 0.0
            }

        try:
            df = pd.DataFrame(data)
            df[date_column] = pd.to_datetime(df[date_column])

            # Agrupar por período
            if period == 'monthly':
                df['periodo'] = df[date_column].dt.to_period('M')
            elif period == 'weekly':
                df['periodo'] = df[date_column].dt.to_period('W')
            elif period == 'daily':
                df['periodo'] = df[date_column].dt.to_period('D')
            else:
                df['periodo'] = df[date_column].dt.to_period('M')

            # Calcular métricas
            grouped = df.groupby('periodo')[value_column].agg(['sum', 'count', 'mean'])

            # Identificar tendência
            trend = self._calculate_trend(grouped['sum'].values)

            # Calcular variações
            variations = self._calculate_variations(grouped['sum'].values)

            return {
                'periodo_analisado': period,
                'tendencia': trend['direction'],
                'crescimento_percentual': round(trend['growth_rate'], 2),
                'periodos_analisados': len(grouped),
                'vendas_totais': float(grouped['sum'].sum()),
                'media_por_periodo': float(grouped['sum'].mean()),
                'variacao_periodo_anterior': round(variations['last_period_change'], 2),
                'insights': self._generate_insights(grouped, trend)
            }
        except Exception as e:
            return {
                "erro": f"Erro ao analisar tendência: {str(e)}",
                "tendencia": "indefinido",
                "crescimento_percentual": 0.0
            }

    def _calculate_trend(self, values: Any) -> Dict[str, Any]:
        """Calcula direção da tendência e taxa de crescimento"""
        if len(values) < 2:
            return {'direction': 'estavel', 'growth_rate': 0.0}

        # Regressão linear simples
        x = list(range(len(values)))
        y = values

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)

        # Coeficiente angular (slope)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

        # Taxa de crescimento percentual
        avg_value = sum_y / n
        if avg_value != 0:
            growth_rate = (slope / avg_value) * 100
        else:
            growth_rate = 0.0

        # Determinar direção
        if growth_rate > 5:
            direction = 'crescimento'
        elif growth_rate < -5:
            direction = 'queda'
        else:
            direction = 'estavel'

        return {
            'direction': direction,
            'growth_rate': growth_rate,
            'slope': slope
        }

    def _calculate_variations(self, values: Any) -> Dict[str, float]:
        """Calcula variações entre períodos"""
        if len(values) < 2:
            return {'last_period_change': 0.0}

        last = values[-1]
        previous = values[-2]

        if previous != 0:
            change = ((last - previous) / previous) * 100
        else:
            change = 0.0

        return {'last_period_change': change}

    def _generate_insights(self, grouped: Any, trend: Dict) -> List[str]:
        """Gera insights baseados na análise"""
        insights = []

        direction = trend['direction']
        growth_rate = trend['growth_rate']

        if direction == 'crescimento':
            insights.append(f"Tendência positiva detectada com crescimento de {abs(growth_rate):.1f}% ao longo do período")
            insights.append("Recomendação: Manter estratégias atuais e considerar expansão")
        elif direction == 'queda':
            insights.append(f"Tendência negativa detectada com queda de {abs(growth_rate):.1f}% ao longo do período")
            insights.append("Alerta: Revisar estratégias de vendas e marketing")
        else:
            insights.append("Vendas estáveis no período analisado")
            insights.append("Sugestão: Implementar ações para impulsionar crescimento")

        # Adicionar insight sobre volatilidade
        if len(grouped) >= 3:
            std = grouped['sum'].std()
            mean = grouped['sum'].mean()
            cv = (std / mean) * 100 if mean != 0 else 0

            if cv > 30:
                insights.append(f"Alta volatilidade detectada (CV: {cv:.1f}%) - vendas oscilando significativamente")
            elif cv < 10:
                insights.append(f"Vendas consistentes (CV: {cv:.1f}%) - padrão estável")

        return insights


class ComparativeAnalyzer:
    """Realiza análises comparativas entre períodos e categorias"""

    def compare_periods(
        self,
        data: List[Dict],
        date_column: str = 'data',
        value_column: str = 'valor',
        period1_start: Optional[str] = None,
        period1_end: Optional[str] = None,
        period2_start: Optional[str] = None,
        period2_end: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compara métricas entre dois períodos

        Args:
            data: Lista de dados
            date_column: Nome da coluna de data
            value_column: Nome da coluna de valor
            period1_start/end: Datas do primeiro período
            period2_start/end: Datas do segundo período

        Returns:
            Análise comparativa
        """
        if not data:
            return {"erro": "Dados vazios"}

        try:
            df = pd.DataFrame(data)
            df[date_column] = pd.to_datetime(df[date_column])

            # Se períodos não fornecidos, usar últimos 2 meses
            if not period1_start:
                max_date = df[date_column].max()
                period2_end = max_date
                period2_start = max_date - timedelta(days=30)
                period1_end = period2_start - timedelta(days=1)
                period1_start = period1_end - timedelta(days=30)
            else:
                period1_start = pd.to_datetime(period1_start)
                period1_end = pd.to_datetime(period1_end)
                period2_start = pd.to_datetime(period2_start)
                period2_end = pd.to_datetime(period2_end)

            # Filtrar dados por período
            period1_data = df[(df[date_column] >= period1_start) & (df[date_column] <= period1_end)]
            period2_data = df[(df[date_column] >= period2_start) & (df[date_column] <= period2_end)]

            # Calcular métricas
            p1_total = float(period1_data[value_column].sum())
            p2_total = float(period2_data[value_column].sum())
            p1_count = len(period1_data)
            p2_count = len(period2_data)
            p1_avg = float(period1_data[value_column].mean()) if p1_count > 0 else 0
            p2_avg = float(period2_data[value_column].mean()) if p2_count > 0 else 0

            # Calcular variações
            total_change = ((p2_total - p1_total) / p1_total * 100) if p1_total != 0 else 0
            count_change = ((p2_count - p1_count) / p1_count * 100) if p1_count != 0 else 0
            avg_change = ((p2_avg - p1_avg) / p1_avg * 100) if p1_avg != 0 else 0

            return {
                'periodo_1': {
                    'inicio': str(period1_start.date()),
                    'fim': str(period1_end.date()),
                    'total': p1_total,
                    'quantidade': p1_count,
                    'media': p1_avg
                },
                'periodo_2': {
                    'inicio': str(period2_start.date()),
                    'fim': str(period2_end.date()),
                    'total': p2_total,
                    'quantidade': p2_count,
                    'media': p2_avg
                },
                'variacoes': {
                    'total_percentual': round(total_change, 2),
                    'quantidade_percentual': round(count_change, 2),
                    'media_percentual': round(avg_change, 2)
                },
                'insights': self._generate_comparison_insights(total_change, count_change, avg_change)
            }
        except Exception as e:
            return {"erro": f"Erro na comparação: {str(e)}"}

    def _generate_comparison_insights(
        self,
        total_change: float,
        count_change: float,
        avg_change: float
    ) -> List[str]:
        """Gera insights da comparação"""
        insights = []

        if total_change > 10:
            insights.append(f"Crescimento significativo de {total_change:.1f}% no valor total")
        elif total_change < -10:
            insights.append(f"Queda significativa de {abs(total_change):.1f}% no valor total")

        if count_change > 10:
            insights.append(f"Aumento de {count_change:.1f}% na quantidade de transações")
        elif count_change < -10:
            insights.append(f"Redução de {abs(count_change):.1f}% na quantidade de transações")

        if avg_change > 10:
            insights.append(f"Ticket médio aumentou {avg_change:.1f}%")
        elif avg_change < -10:
            insights.append(f"Ticket médio diminuiu {abs(avg_change):.1f}%")

        if not insights:
            insights.append("Métricas estáveis entre os períodos comparados")

        return insights


# Instâncias globais
trend_analyzer = TrendAnalyzer()
comparative_analyzer = ComparativeAnalyzer()
