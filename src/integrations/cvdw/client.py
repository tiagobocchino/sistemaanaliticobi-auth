"""
Cliente para integração com API CVDW CRM
Documentação: https://desenvolvedor.cvcrm.com.br/reference/
"""
import os
from typing import Dict, Any, Optional, List
from ..base_client import BaseAPIClient


class CVDWClient(BaseAPIClient):
    """
    Cliente para API CVDW CRM
    Funcionalidades: Clientes, Oportunidades, Métricas, Segmentação
    """

    def __init__(self):
        # Base URL da API CVDW
        base_url = os.getenv("CVDW_BASE_URL", "https://desenvolvedor.cvcrm.com.br")

        # Configurações específicas do CVDW
        self.api_key = self._get_api_key()
        self.email = os.getenv("CVDW_EMAIL")
        self.account_id = os.getenv("CVDW_ACCOUNT_ID")

        super().__init__(base_url, self.api_key, timeout=30)

    def _get_api_key(self) -> Optional[str]:
        """Retorna a chave da API CVDW"""
        return os.getenv("CVDW_API_KEY")

    def _get_default_headers(self) -> Dict[str, str]:
        """Headers específicos do CVDW"""
        headers = super()._get_default_headers()

        if self.api_key:
            headers.update({
                'X-API-Key': self.api_key,
                'X-Account-ID': self.account_id or '',
                'Accept': 'application/json'
            })

        return headers

    # ========== MÉTODOS DE CLIENTES ==========

    async def get_clientes(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Busca base de clientes
        """
        params = filters or {}
        return await self.get("/clientes", params=params)

    async def get_cliente_detalhes(self, cliente_id: str) -> Dict[str, Any]:
        """
        Busca detalhes de um cliente específico
        """
        return await self.get(f"/clientes/{cliente_id}")

    async def get_clientes_segmento(self, segmento: str) -> Dict[str, Any]:
        """
        Busca clientes por segmento
        """
        params = {"segmento": segmento}
        return await self.get("/clientes/segmento", params=params)

    # ========== MÉTODOS DE OPORTUNIDADES ==========

    async def get_oportunidades(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Busca oportunidades de venda
        """
        params = filters or {}
        return await self.get("/oportunidades", params=params)

    async def get_oportunidade_detalhes(self, oportunidade_id: str) -> Dict[str, Any]:
        """
        Busca detalhes de uma oportunidade específica
        """
        return await self.get(f"/oportunidades/{oportunidade_id}")

    async def get_pipeline_vendas(self, periodo: Optional[str] = None) -> Dict[str, Any]:
        """
        Busca pipeline de vendas
        """
        params = {}
        if periodo:
            params["periodo"] = periodo
        return await self.get("/oportunidades/pipeline", params=params)

    # ========== MÉTODOS DE INTERAÇÕES ==========

    async def get_interactions(self, cliente_id: Optional[str] = None,
                              periodo: Optional[str] = None) -> Dict[str, Any]:
        """
        Busca histórico de interações
        """
        params = {}
        if cliente_id:
            params["cliente_id"] = cliente_id
        if periodo:
            params["periodo"] = periodo
        return await self.get("/interactions", params=params)

    async def get_interaction_detalhes(self, interaction_id: str) -> Dict[str, Any]:
        """
        Busca detalhes de uma interação específica
        """
        return await self.get(f"/interactions/{interaction_id}")

    # ========== MÉTODOS DE MÉTRICAS ==========

    async def get_kpis(self, periodo: str, tipo: Optional[str] = None) -> Dict[str, Any]:
        """
        Busca KPIs e métricas
        """
        params = {"periodo": periodo}
        if tipo:
            params["tipo"] = tipo
        return await self.get("/metrics/kpis", params=params)

    async def get_metricas_vendas(self, periodo: str) -> Dict[str, Any]:
        """
        Busca métricas específicas de vendas
        """
        params = {"periodo": periodo}
        return await self.get("/metrics/vendas", params=params)

    async def get_metricas_clientes(self, periodo: str) -> Dict[str, Any]:
        """
        Busca métricas específicas de clientes
        """
        params = {"periodo": periodo}
        return await self.get("/metrics/clientes", params=params)

    # ========== MÉTODOS DE SEGMENTAÇÃO ==========

    async def segmentar_clientes(self, criterios: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza segmentação de clientes baseada em critérios
        """
        return await self.post("/analytics/segmentation", data=criterios)

    async def get_segmentos_existentes(self) -> Dict[str, Any]:
        """
        Lista segmentos de clientes já criados
        """
        return await self.get("/analytics/segmentos")

    # ========== MÉTODOS DE RELATÓRIOS ==========

    async def get_relatorio_vendas(self, periodo: str, formato: str = "json") -> Dict[str, Any]:
        """
        Gera relatório de vendas
        """
        params = {
            "periodo": periodo,
            "formato": formato
        }
        return await self.get("/reports/sales", params=params)

    async def get_relatorio_clientes(self, periodo: str, formato: str = "json") -> Dict[str, Any]:
        """
        Gera relatório de clientes
        """
        params = {
            "periodo": periodo,
            "formato": formato
        }
        return await self.get("/reports/clientes", params=params)

    async def get_relatorio_performance(self, periodo: str) -> Dict[str, Any]:
        """
        Gera relatório de performance geral
        """
        params = {"periodo": periodo}
        return await self.get("/reports/performance", params=params)

    # ========== MÉTODO PARA TESTE ==========

    async def test_connection(self) -> Dict[str, Any]:
        """
        Testa conexão com a API CVDW
        Retorna dados simulados se não conseguir conectar
        """
        try:
            # Tentar fazer uma requisição simples
            result = await self.get("/health")
            return {
                "status": "connected",
                "api": "cvdw",
                "data": result
            }
        except Exception as e:
            # Retornar dados simulados para desenvolvimento
            return {
                "status": "simulated",
                "api": "cvdw",
                "message": "API CVDW não configurada. Usando dados simulados.",
                "error": str(e),
                "sample_data": {
                    "total_clientes": 1250,
                    "oportunidades_abertas": 67,
                    "interactions_mes": 450,
                    "taxa_conversao": 0.23
                }
            }
