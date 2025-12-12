"""
Cliente para integração com API CVDW CRM
Documentação: https://desenvolvedor.cvcrm.com.br/reference/
"""
import os
from typing import Dict, Any, Optional, List
from ..base_client import BaseAPIClient
from src.config import get_settings


class CVDWClient(BaseAPIClient):
    """
    Cliente para API CVDW CRM
    Funcionalidades: Clientes, Oportunidades, Métricas, Segmentação
    """

    def __init__(self):
        # Base URL da API CVDW
        # Default para API real (ajustável via CVDW_BASE_URL)
        settings = get_settings()
        base_url = settings.cvdw_base_url or os.getenv("CVDW_BASE_URL", "https://bpincorporadora.cvcrm.com.br/api/v1/cvdw")

        # Configurações específicas do CVDW (preferir settings)
        self.api_key = settings.cvdw_api_key or self._get_api_key()
        self.email = settings.cvdw_email or os.getenv("CVDW_EMAIL")
        self.account_id = settings.cvdw_account_id or os.getenv("CVDW_ACCOUNT_ID")

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
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            })
        if self.email:
            headers['email'] = self.email
        if self.api_key:
            headers['token'] = self.api_key

        return headers

    # ========== MÉTODOS DE CLIENTES ==========

    def _is_error_response(self, result: Dict[str, Any]) -> bool:
        """Verifica se a resposta indica erro HTTP ou payload de erro"""
        if not isinstance(result, dict):
            return False
        if "error" in result:
            return True
        status = result.get("status_code")
        try:
            if status is not None and int(status) >= 400:
                return True
        except Exception:
            pass
        return False

    def _fallback_oportunidades(self) -> Dict[str, Any]:
        """Dados simulados para oportunidades"""
        return {
            "oportunidades_abertas": 67,
            "valor_pipeline": 1_250_000.00,
            "taxa_conversao": 0.23,
            "fonte": "dados_simulados_cvcrm"
        }

    def _fallback_clientes(self) -> Dict[str, Any]:
        """Dados simulados para clientes"""
        return {
            "total_clientes": 1250,
            "novos_clientes_mes": 45,
            "clientes_ativos": 890,
            "fonte": "dados_simulados_cvcrm"
        }

    def _with_auth(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Anexa email/token às chamadas, pois a API exige esses campos.
        """
        merged = params.copy() if params else {}
        if self.email:
            merged.setdefault("email", self.email)
        if self.api_key:
            merged.setdefault("token", self.api_key)
        return merged

    async def get_clientes(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Busca base de clientes, com fallback seguro em caso de erro da API
        """
        params = self._with_auth(filters)
        result = await self.get("/clientes", params=params)
        if self._is_error_response(result):
            return self._fallback_clientes()
        return result

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
        Busca oportunidades de venda, com fallback seguro em caso de erro da API
        """
        params = self._with_auth(filters)
        # endpoints documentados: /vendas ou /oportunidades; tentar ambos
        result = await self.get("/vendas", params=params)
        if self._is_error_response(result):
            result = await self.get("/oportunidades", params=params)
        if self._is_error_response(result):
            return self._fallback_oportunidades()
        return result

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
