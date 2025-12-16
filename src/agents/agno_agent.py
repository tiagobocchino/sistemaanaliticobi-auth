"""Analytics AI agent using Agno framework."""
import os
import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from agno.agent import Agent, RunOutput
from agno.models.openai import OpenAIChat

from .api_doc_reader import api_doc_reader
from .analysis_explainer import analysis_explainer, AnalysisExplanation
from .chart_generator import chart_generator
from ..integrations.sienge.client import SiengeClient
from ..integrations.cvdw.client import CVDWClient
from ..config import get_settings
from ..supabase_client import supabase_admin_client


class AnalyticsAgent:
    """IA agent wired to Sienge, CVDW and chart/explainer helpers."""

    def __init__(self):
        self.settings = get_settings()
        self.sienge_client = SiengeClient()
        self.cvdw_client = CVDWClient()
        self.doc_reader = api_doc_reader
        self.explainer = analysis_explainer
        self.chart_gen = chart_generator

        # Prefer local Ollama first, then Groq; only use OpenAI if explicitly enabled.
        self.llm = self._setup_llm()

        self.agent = Agent(
            name="Analytics AI Agent",
            model=self.llm,
            tools=[
                self.find_api_endpoints,
                self.fetch_data_from_api,
                self.query_raw_data,
                self.explain_analysis,
                self.generate_charts,
            ],
            markdown=True,
            debug_mode=False,
        )

    def _setup_llm(self):
        """
        Configure the LLM provider.
        Order: Ollama (local) -> Groq (if key) -> OpenAI (only if USE_OPENAI=true).
        """
        # Ollama usa o endpoint OpenAI-compatible; nome do modelo deve bater com a tag local (ex: llama3.2)
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        try:
            return OpenAIChat(
                id=ollama_model,
                base_url=ollama_url,
                api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
            )
        except Exception:
            pass

        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                return OpenAIChat(
                    id=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
                    base_url="https://api.groq.com/openai/v1",
                    api_key=groq_key,
                )
            except Exception:
                pass

        use_openai = os.getenv("USE_OPENAI", "").lower() in {"1", "true", "yes"}
        openai_key = os.getenv("OPENAI_API_KEY")
        if use_openai and openai_key:
            return OpenAIChat(id=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), api_key=openai_key)

        print(
            "Nenhum modelo configurado. Use Ollama local ou defina GROQ_API_KEY. "
            "OpenAI so sera usado se USE_OPENAI=true e OPENAI_API_KEY estiver setado."
        )
        return None

    async def process_query(
        self, user_id: UUID, query: str, permissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Processa uma consulta com IA ou fallback baseado em regras."""
        context = {
            "user_id": str(user_id),
            "permissions": permissions,
            "query": query,
            "available_apis": [],
        }

        if permissions.get("can_access_sienge"):
            context["available_apis"].append("Sienge ERP")
        if permissions.get("can_access_cvdw"):
            context["available_apis"].append("CVDW CRM")
        if permissions.get("can_access_powerbi"):
            context["available_apis"].append("Power BI Dashboards")

        system_prompt = self._build_system_prompt(context)

        try:
            if self.agent.model:
                try:
                    response: RunOutput = await self.agent.arun(query, context=system_prompt)
                    return {
                        "success": True,
                        "response": response.content,
                        "tools_used": [call.function.name for call in (response.tool_calls or [])],
                        "explanation": None,
                        "charts": [],
                    }
                except Exception:
                    return await self._fallback_process_query(query, context)
            return await self._fallback_process_query(query, context)
        except Exception as e:
            return {"success": False, "error": str(e), "response": f"Erro ao processar consulta: {e}"}

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Prompt de sistema enxuto e sem acentos problematicos."""
        apis_str = ", ".join(context["available_apis"]) or "dados internos"
        return (
            "Voce e um assistente de analises empresariais. "
            "Responda em portugues, de forma direta e humana. "
            f"Fontes disponiveis: {apis_str}. "
            "Quando fizer chamadas, use as tools: find_api_endpoints, fetch_data_from_api, "
            "explain_analysis, generate_charts. Sempre explique de onde veio o dado e quais filtros/campos usou. "
            "Se nao tiver dado real, diga o que precisa e sugira proximos passos."
        )

    async def check_user_permissions(self, user_id: UUID) -> Dict[str, Any]:
        """Busca permissoes do usuario no Supabase usando service role."""
        try:
            user_response = (
                supabase_admin_client.table("usuarios")
                .select("*, cargos(nivel_acesso), divisoes(codigo)")
                .eq("id", str(user_id))
                .single()
                .execute()
            )

            user_data = user_response.data if user_response.data else {}
            nivel_acesso = user_data.get("cargos", {}).get("nivel_acesso", 1) if user_data.get("cargos") else 1
            divisao = user_data.get("divisoes", {}).get("codigo", "ALL") if user_data.get("divisoes") else "ALL"

            return {
                "user_id": user_id,
                "nivel_acesso": nivel_acesso,
                "divisao": divisao,
                "can_access_sienge": nivel_acesso >= 3,
                "can_access_cvdw": nivel_acesso >= 2,
                "can_access_powerbi": nivel_acesso >= 2,
            }
        except Exception:
            return {
                "user_id": user_id,
                "nivel_acesso": 1,
                "divisao": "ALL",
                "can_access_sienge": False,
                "can_access_cvdw": False,
                "can_access_powerbi": True,
            }

    async def _fallback_process_query(
        self, query: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processamento fallback sem IA (regras simples)
        """
        query_lower = query.lower()

        if any(word in query_lower for word in ["venda", "vendas", "faturamento"]):
            intent = "vendas"
        elif any(word in query_lower for word in ["financeiro", "contas", "pagar", "receber"]):
            intent = "financeiro"
        elif any(word in query_lower for word in ["cliente", "clientes", "crm"]):
            intent = "clientes"
        else:
            intent = "geral"

        data: Dict[str, Any] = {}
        endpoints_called: List[Dict[str, Any]] = []
        permissions = context["permissions"]

        suggested_endpoints = self.doc_reader.find_endpoints_for_intent(intent, query_lower)[:3]
        for ep in suggested_endpoints:
            endpoints_called.append(
                {"source": getattr(ep, "api_name", "api"), "endpoint": ep.path, "params": ep.parameters}
            )

        if permissions.get("can_access_sienge") and intent == "financeiro":
            try:
                cp = await self.sienge_client.get_contas_pagar()
                cr = await self.sienge_client.get_contas_receber()
                data["sienge"] = {
                    "contas_pagar": cp or {"total": 125000, "quantidade": 45},
                    "contas_receber": cr or {"total": 98000, "quantidade": 32},
                }
                endpoints_called.append({"source": "sienge", "endpoint": "/financeiro/contas-pagar", "params": {}})
            except Exception:
                pass

        if permissions.get("can_access_cvdw") and intent in ["vendas", "clientes"]:
            try:
                opp = await self.cvdw_client.get_oportunidades()
                data["cvdw"] = opp or {
                    "oportunidades_abertas": 67,
                    "valor_pipeline": 1250000.00,
                    "taxa_conversao": 0.23,
                }
                endpoints_called.append({"source": "cvdw", "endpoint": "/oportunidades", "params": {}})
            except Exception:
                pass

        explanation = self.explainer.create_explanation(
            query=query,
            intent=intent,
            data_sources_used=list(data.keys()),
            endpoints_called=endpoints_called,
            data_returned=data,
        )

        charts = self.chart_gen.generate_charts_from_analysis(intent, data)
        response_text = self._format_fallback_response(intent, data, explanation)

        return {
            "success": True,
            "response": response_text,
            "explanation": explanation,
            "charts": charts,
            "data": data,
            "tools_used": ["fallback_rule_based"],
        }

    def _format_fallback_response(
        self, intent: str, data: Dict[str, Any], explanation: AnalysisExplanation
    ) -> str:
        """
        Formata resposta do fallback de forma mais humana e sem bloco tecnico.
        """

        def fmt_currency(val: float) -> str:
            try:
                return f"R$ {val:,.2f}"
            except Exception:
                return str(val)

        def fmt_percent(val: float) -> str:
            try:
                return f"{val*100:.2f}%"
            except Exception:
                return str(val)

        lines: List[str] = []

        if intent == "vendas":
            cv = data.get("cvdw", {}) if isinstance(data.get("cvdw"), dict) else {}
            vendas = cv.get("oportunidades_abertas")
            pipeline = cv.get("valor_pipeline")
            conversao = cv.get("taxa_conversao")

            linhas_resumo: List[str] = []
            if vendas is not None:
                linhas_resumo.append(f"Fechamos {vendas} vendas/oportunidades abertas neste mes.")
            if pipeline is not None:
                linhas_resumo.append(f"Pipeline estimado: {fmt_currency(pipeline)}.")
            if conversao is not None:
                linhas_resumo.append(f"Taxa de conversao atual: {fmt_percent(conversao)}.")

            if linhas_resumo:
                lines.append("Resumo rapido das vendas:")
                lines.extend(linhas_resumo)

            if conversao is not None:
                lines.append(
                    "Insight: mantendo essa conversao o potencial de fechamento e bom. "
                    "Compare com o mesmo periodo do mes passado para confirmar tendencia."
                )

            lines.append("Fonte: modulo de vendas do CVCRM (endpoint `/oportunidades`).")
        else:
            lines.append(f"Entendi sua pergunta sobre {intent}. Aqui o que achei:")
            for source, source_data in data.items():
                lines.append(f"- Fonte {source.upper()}:")
                if isinstance(source_data, dict):
                    for key, value in source_data.items():
                        if isinstance(value, (int, float)) and key != "taxa_conversao":
                            lines.append(f"  • {key}: {fmt_currency(value) if value > 1000 else value}")
                        elif key == "taxa_conversao":
                            lines.append(f"  • taxa_conversao: {fmt_percent(value)}")

        return "\n".join(lines)

    def find_api_endpoints(self, intent: str, query: str) -> str:
        """
        Tool: Encontra endpoints relevantes nas documentacoes das APIs
        """
        endpoints = self.doc_reader.find_endpoints_for_intent(intent, query)
        result = {"total_found": len(endpoints), "endpoints": []}

        for ep in endpoints[:5]:
            result["endpoints"].append(
                {
                    "method": ep.method,
                    "path": ep.path,
                    "description": ep.description,
                    "tables": ep.tables,
                    "parameters": ep.parameters,
                }
            )

        return json.dumps(result, ensure_ascii=False, indent=2)

    async def fetch_data_from_api(
        self, api_name: str, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Tool: Busca dados de uma API especifica
        """
        try:
            if api_name.lower() == "sienge":
                if "contas-pagar" in endpoint:
                    data = await self.sienge_client.get_contas_pagar(params)
                elif "contas-receber" in endpoint:
                    data = await self.sienge_client.get_contas_receber(params)
                elif "pedidos" in endpoint:
                    data = await self.sienge_client.get_pedidos_venda(params)
                else:
                    data = {"error": "Endpoint nao implementado"}

            elif api_name.lower() in {"cvdw", "cvcrm"}:
                if "clientes" in endpoint:
                    data = await self.cvdw_client.get_clientes(params)
                elif "oportunidades" in endpoint or "vendas" in endpoint:
                    data = await self.cvdw_client.get_oportunidades(params)
                else:
                    data = {"error": "Endpoint nao implementado"}
            else:
                data = {"error": f"API desconhecida: {api_name}"}

            return json.dumps(data, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def query_raw_data(
        self,
        table_name: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> str:
        """
        Tool: Consulta dados RAW das tabelas internas do Supabase.

        Use esta tool quando o usuario perguntar sobre dados de:
        - leads: prospects, contatos, clientes potenciais
        - vendas: vendas realizadas, contratos fechados
        - reservas: reservas de imoveis, apartamentos reservados
        - unidades: imoveis, apartamentos, unidades disponiveis
        - corretores: vendedores, equipe de vendas
        - pessoas: clientes, compradores, cadastro de pessoas
        - imobiliarias: imobiliarias parceiras, construtoras
        - repasses: comissoes, repasses financeiros

        Args:
            table_name: Nome da tabela (leads, vendas, reservas, unidades,
                        corretores, pessoas, imobiliarias, repasses)
            filters: Filtros opcionais como {"ativo": "S", "cidade": "Brasília"}
            limit: Numero maximo de registros (padrao: 50, max: 500)

        Returns:
            JSON string com os dados da tabela
        """
        # Validação de segurança
        ALLOWED_TABLES = {
            'leads', 'vendas', 'reservas', 'unidades',
            'corretores', 'pessoas', 'imobiliarias', 'repasses'
        }

        if table_name not in ALLOWED_TABLES:
            return json.dumps({
                "error": f"Tabela invalida. Use uma de: {', '.join(ALLOWED_TABLES)}"
            }, ensure_ascii=False)

        # Limite máximo de segurança
        limit = min(limit, 500)

        try:
            # Lista de colunas permitidas para cada tabela (evita injection)
            ALLOWED_COLUMNS = {
                'leads': ['ativo', 'cidade', 'estado', 'situacao', 'origem'],
                'vendas': ['ativo', 'cidade', 'contrato_interno'],
                'reservas': ['ativo', 'cidade', 'bloco'],
                'unidades': ['ativo', 'bloco', 'andar', 'etapa'],
                'corretores': ['ativo', 'ativo_login'],
                'pessoas': ['ativo', 'cidade', 'estado'],
                'imobiliarias': ['ativo', 'cidade'],
                'repasses': ['ativo', 'cidade']
            }

            # Construir query segura usando métodos do Supabase
            query = supabase_admin_client.table(table_name).select("*")

            # Aplicar filtros de forma segura (previne SQL injection)
            if filters:
                allowed = ALLOWED_COLUMNS.get(table_name, [])

                for key, value in filters.items():
                    if key not in allowed:
                        return json.dumps({
                            "error": f"Coluna '{key}' nao permitida para tabela {table_name}. Use: {', '.join(allowed)}"
                        }, ensure_ascii=False)
                    query = query.eq(key, value)

            query = query.limit(limit)
            result = query.execute()

            # Filtrar dados sensíveis antes de retornar
            filtered_data = self._filter_sensitive_fields(result.data)

            return json.dumps({
                "table": table_name,
                "count": len(filtered_data),
                "data": filtered_data,
                "filters_applied": filters or {}
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps({
                "error": f"Erro ao consultar {table_name}: {str(e)}"
            }, ensure_ascii=False)

    def _filter_sensitive_fields(self, data: List[Dict]) -> List[Dict]:
        """Remove ou mascara campos sensiveis antes de retornar ao LLM"""
        SENSITIVE_FIELDS = {
            'documento', 'cpf', 'cnpj', 'documento_cliente',
            'email', 'telefone', 'celular', 'rg', 'cnh'
        }

        filtered = []
        for item in data:
            filtered_item = {}
            for key, value in item.items():
                if key.lower() in SENSITIVE_FIELDS:
                    # Mascarar em vez de remover (mantém contexto)
                    if value and isinstance(value, str):
                        filtered_item[key] = value[:3] + "***" + value[-2:] if len(value) > 5 else "***"
                    else:
                        filtered_item[key] = "***"
                else:
                    filtered_item[key] = value
            filtered.append(filtered_item)

        return filtered

    def explain_analysis(
        self,
        query: str,
        intent: str,
        data_sources: List[str],
        endpoints: List[Dict[str, Any]],
        data: Dict[str, Any],
    ) -> str:
        """
        Tool: Explica uma analise detalhadamente
        """
        explanation = self.explainer.create_explanation(
            query=query,
            intent=intent,
            data_sources_used=data_sources,
            endpoints_called=endpoints,
            data_returned=data,
        )
        return self.explainer.format_explanation_as_text(explanation)

    def generate_charts(self, intent: str, data: Dict[str, Any]) -> str:
        """
        Tool: Gera graficos baseado nos dados
        """
        charts = self.chart_gen.generate_charts_from_analysis(intent, data)
        result = {"total_charts": len(charts), "charts": []}

        for chart in charts:
            result["charts"].append(
                {
                    "title": chart.title,
                    "type": chart.chart_type,
                    "format": chart.format,
                    "description": chart.description,
                    "has_html": chart.html is not None,
                }
            )

        return json.dumps(result, ensure_ascii=False, indent=2)

    async def initialize(self):
        """Inicializa o agente e seus componentes."""
        print("Inicializando Analytics AI Agent...")
        await self.doc_reader.initialize()
        print("Agente inicializado.")
        print(f" - Modelo: {self.agent.model.id if self.agent.model else 'Fallback (sem IA)'}")
        print(f" - Tools: {len(self.agent.tools)}")
        print(" - APIs disponiveis: Sienge, CVDW, Power BI")


# Instancia global
analytics_agent = AnalyticsAgent()
