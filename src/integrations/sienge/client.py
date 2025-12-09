"""
Cliente para integração com API Sienge ERP
Documentação: https://api.sienge.com.br/docs/
"""
import os
from typing import Dict, Any, Optional, List
from ..base_client import BaseAPIClient


class SiengeClient(BaseAPIClient):
    """
    Cliente para API Sienge ERP
    Funcionalidades: Financeiro, Vendas, Projetos, Estoque
    """

    def __init__(self):
        # Base URL da API Sienge
        base_url = os.getenv("SIENGE_BASE_URL", "https://api.sienge.com.br")

        # Configurações específicas do Sienge
        self.company_id = os.getenv("SIENGE_COMPANY_ID")
        self.user = os.getenv("SIENGE_USER")
        self.api_token = self._get_api_key()

        super().__init__(base_url, self.api_token, timeout=30)

    def _get_api_key(self) -> Optional[str]:
        """Retorna o token da API Sienge"""
        return os.getenv("SIENGE_API_TOKEN")

    def _get_default_headers(self) -> Dict[str, str]:
        """Headers específicos do Sienge"""
        headers = super()._get_default_headers()

        if self.api_token:
            headers.update({
                'Authorization': f'Bearer {self.api_token}',
                'X-Company-ID': self.company_id or '',
                'X-API-Version': 'v1'
            })

        return headers

    # ========== MÉTODOS DE FINANCEIRO ==========

    async def get_contas_pagar(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Busca contas a pagar
        """
        params = filters or {}
        return await self.get("/financeiro/contas-pagar", params=params)

    async def get_contas_receber(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Busca contas a receber
        """
        params = filters or {}
        return await self.get("/financeiro/contas-receber", params=params)

    async def get_fluxo_caixa(self, data_inicio: str, data_fim: str) -> Dict[str, Any]:
        """
        Busca fluxo de caixa por período
        """
        params = {
            "data_inicio": data_inicio,
            "data_fim": data_fim
        }
        return await self.get("/financeiro/fluxo-caixa", params=params)

    # ========== MÉTODOS DE VENDAS ==========

    async def get_pedidos_venda(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Busca pedidos de venda
        """
        params = filters or {}
        return await self.get("/vendas/pedidos", params=params)

    async def get_clientes(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Busca cadastro de clientes
        """
        params = filters or {}
        return await self.get("/vendas/clientes", params=params)

    async def get_faturamento(self, periodo: str) -> Dict[str, Any]:
        """
        Busca faturamento por período
        """
        params = {"periodo": periodo}
        return await self.get("/vendas/faturamento", params=params)

    # ========== MÉTODOS DE PROJETOS ==========

    async def get_projetos(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Busca projetos
        """
        params = {}
        if status:
            params["status"] = status
        return await self.get("/projetos", params=params)

    async def get_projeto_detalhes(self, projeto_id: str) -> Dict[str, Any]:
        """
        Busca detalhes de um projeto específico
        """
        return await self.get(f"/projetos/{projeto_id}")

    # ========== MÉTODOS DE ESTOQUE ==========

    async def get_produtos(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Busca produtos em estoque
        """
        params = filters or {}
        return await self.get("/estoque/produtos", params=params)

    async def get_movimentacoes_estoque(self, data_inicio: str, data_fim: str) -> Dict[str, Any]:
        """
        Busca movimentações de estoque por período
        """
        params = {
            "data_inicio": data_inicio,
            "data_fim": data_fim
        }
        return await self.get("/estoque/movimentacoes", params=params)

    # ========== MÉTODOS DE RELATÓRIOS ==========

    async def get_relatorio_financeiro(self, tipo: str, periodo: str) -> Dict[str, Any]:
        """
        Gera relatório financeiro
        Tipos: 'contas_pagar', 'contas_receber', 'fluxo_caixa', 'resultado'
        """
        data = {
            "tipo": tipo,
            "periodo": periodo
        }
        return await self.post("/relatorios/financeiro", data=data)

    async def get_relatorio_vendas(self, tipo: str, periodo: str) -> Dict[str, Any]:
        """
        Gera relatório de vendas
        Tipos: 'faturamento', 'pedidos', 'clientes', 'produtos'
        """
        data = {
            "tipo": tipo,
            "periodo": periodo
        }
        return await self.post("/relatorios/vendas", data=data)

    # ========== MÉTODO PARA TESTE ==========

    async def test_connection(self) -> Dict[str, Any]:
        """
        Testa conexão com a API Sienge
        Retorna dados simulados se não conseguir conectar
        """
        try:
            # Tentar fazer uma requisição simples
            result = await self.get("/health")
            return {
                "status": "connected",
                "api": "sienge",
                "data": result
            }
        except Exception as e:
            # Retornar dados simulados para desenvolvimento
            return {
                "status": "simulated",
                "api": "sienge",
                "message": "API Sienge não configurada. Usando dados simulados.",
                "error": str(e),
                "sample_data": {
                    "contas_pagar": {"total": 125000.00, "quantidade": 45},
                    "contas_receber": {"total": 98000.00, "quantidade": 32},
                    "projetos_ativos": 12,
                    "produtos_estoque": 156
                }
            }
