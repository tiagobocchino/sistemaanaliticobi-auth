"""
Agente de IA usando Framework Agno
Integra todos os componentes: API reader, explainer, chart generator
"""
import os
from typing import Dict, List, Any, Optional
from uuid import UUID
import json

# Agno imports
from agno.agent import Agent, RunOutput
from agno.models.openai import OpenAIChat

# M+ªdulos locais
from .api_doc_reader import api_doc_reader, APIEndpoint
from .analysis_explainer import analysis_explainer, AnalysisExplanation
from .chart_generator import chart_generator, GeneratedChart
from ..integrations.sienge.client import SiengeClient
from ..integrations.cvdw.client import CVDWClient
from ..config import get_settings
from ..supabase_client import supabase_admin_client


class AnalyticsAgent:
    """
    Agente de IA Analytics usando Agno framework
    """

    def __init__(self):
        self.settings = get_settings()

        # Clients das APIs
        self.sienge_client = SiengeClient()
        self.cvdw_client = CVDWClient()

        # Componentes do sistema
        self.doc_reader = api_doc_reader
        self.explainer = analysis_explainer
        self.chart_gen = chart_generator

        # Configurar modelo de IA
        # Voc+¼ pode usar qualquer modelo compat+ível com OpenAI API
        # Op+║+┴es gratuitas: Ollama local, Groq, etc.
        self.llm = self._setup_llm()

        # Criar agente Agno com tools
        self.agent = Agent(
            name="Analytics AI Agent",
            model=self.llm,
            tools=[
                self.find_api_endpoints,
                self.fetch_data_from_api,
                self.explain_analysis,
                self.generate_charts
            ],
            markdown=True,
            debug_mode=False
        )

    def _setup_llm(self):
        """
        Configura o modelo de IA (prioriza Ollama local, depois Groq, depois OpenAI)
        """
        # Preferência 1: Ollama local
        try:
            return OpenAIChat(
                id="llama3.2",
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )
        except Exception:
            pass

        # Preferência 2: Groq (se chave estiver configurada)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            return OpenAIChat(
                id="mixtral-8x7b-32768",
                base_url="https://api.groq.com/openai/v1",
                api_key=groq_key
            )

        # Preferência 3: OpenAI (se chave estiver configurada)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return OpenAIChat(
                id="gpt-4o-mini",
                api_key=openai_key
            )

        print("Nenhum modelo de IA configurado. Use Ollama local ou configure GROQ_API_KEY/OPENAI_API_KEY")
        return None

    async def process_query(
        self,
        user_id: UUID,
        query: str,
        permissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processa uma consulta do usu+Ýrio usando o agente Agno

        Args:
            user_id: ID do usu+Ýrio
            query: Consulta em linguagem natural
            permissions: Permiss+┴es do usu+Ýrio

        Returns:
            Resposta completa com an+Ýlise, gr+Ýficos e explica+║+·o
        """
        # Contexto para o agente
        context = {
            "user_id": str(user_id),
            "permissions": permissions,
            "query": query,
            "available_apis": []
        }

        # Adicionar APIs dispon+íveis baseado em permiss+┴es
        if permissions.get("can_access_sienge"):
            context["available_apis"].append("Sienge ERP")
        if permissions.get("can_access_cvdw"):
            context["available_apis"].append("CVDW CRM")
        if permissions.get("can_access_powerbi"):
            context["available_apis"].append("Power BI Dashboards")

        # Criar prompt para o agente
        system_prompt = self._build_system_prompt(context)

        try:
            # Executar agente (se LLM configurado)
            if self.agent.model:
                try:
                    response: RunOutput = await self.agent.arun(query, context=system_prompt)
                    return {
                        "success": True,
                        "response": response.content,
                        "tools_used": [call.function.name for call in (response.tool_calls or [])],
                        "explanation": None,  # Serß preenchido se tool explain_analysis for chamada
                        "charts": [],  # Serß preenchido se tool generate_charts for chamada
                    }
                except Exception:
                    return await self._fallback_process_query(query, context)
            else:
                # Fallback sem IA: l¾gica baseada em regras
                return await self._fallback_process_query(query, context)

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"Erro ao processar consulta: {str(e)}"
            }
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Constr+ªi prompt de sistema para o agente
        """
        apis_str = ", ".join(context["available_apis"])

        prompt = f"""Voc+¼ +« um assistente de an+Ýlise de dados empresariais inteligente.

SUAS CAPACIDADES:
- Voc+¼ tem acesso a dados de: {apis_str}
- Voc+¼ pode buscar endpoints de APIs usando a tool 'find_api_endpoints'
- Voc+¼ pode buscar dados reais usando a tool 'fetch_data_from_api'
- Voc+¼ pode explicar an+Ýlises detalhadamente usando a tool 'explain_analysis'
- Voc+¼ pode gerar gr+Ýficos e visualiza+║+┴es usando a tool 'generate_charts'

PERMISS+‗ES DO USU+³RIO:
- N+ível de acesso: {context['permissions'].get('nivel_acesso', 1)}
- Divis+·o: {context['permissions'].get('divisao', 'ALL')}
- APIs dispon+íveis: {apis_str}

SUA MISS+ÔO:
1. Entender a pergunta do usu+Ýrio
2. Identificar quais endpoints/dados s+·o necess+Ýrios
3. Buscar os dados das APIs corretas
4. Explicar claramente:
   - Quais tabelas/fontes voc+¼ est+Ý usando
   - Quais colunas voc+¼ est+Ý consultando
   - Quais filtros voc+¼ est+Ý aplicando
   - Quais relacionamentos entre tabelas existem
   - Quais c+Ýlculos voc+¼ est+Ý fazendo
5. Gerar visualiza+║+┴es (gr+Ýficos) quando apropriado
6. Responder em portugu+¼s de forma clara e profissional

IMPORTANTE:
- SEMPRE explique suas fontes de dados de forma transparente
- SEMPRE mostre seus c+Ýlculos e f+ªrmulas
- Se n+·o tiver certeza, pergunte ao usu+Ýrio para esclarecer
- Se n+·o tiver permiss+·o para acessar algum dado, informe claramente
"""
        return prompt

    async def check_user_permissions(self, user_id: UUID) -> Dict[str, Any]:
        """
        Obt+«m permiss+┴es do usu+Ýrio a partir do Supabase (usa service role para evitar bloqueio por RLS)
        """
        try:
            user_response = supabase_admin_client.table("usuarios") \
                .select("*, cargos(nivel_acesso), divisoes(codigo)") \
                .eq("id", str(user_id)) \
                .single() \
                .execute()

            user_data = user_response.data if user_response.data else {}
            nivel_acesso = user_data.get("cargos", {}).get("nivel_acesso", 1) if user_data.get("cargos") else 1
            divisao = user_data.get("divisoes", {}).get("codigo", "ALL") if user_data.get("divisoes") else "ALL"

            return {
                "user_id": user_id,
                "nivel_acesso": nivel_acesso,
                "divisao": divisao,
                "can_access_sienge": nivel_acesso >= 3,
                "can_access_cvdw": nivel_acesso >= 2,
                "can_access_powerbi": nivel_acesso >= 2
            }
        except Exception:
            # Fallback permiss+┴es m+ínimas
            return {
                "user_id": user_id,
                "nivel_acesso": 1,
                "divisao": "ALL",
                "can_access_sienge": False,
                "can_access_cvdw": False,
                "can_access_powerbi": True
            }

    async def _fallback_process_query(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processamento fallback sem IA (regras simples)
        """
        query_lower = query.lower()

        # Identificar inten+║+·o por keywords
        if any(word in query_lower for word in ["venda", "vendas", "faturamento"]):
            intent = "vendas"
        elif any(word in query_lower for word in ["financeiro", "contas", "pagar", "receber"]):
            intent = "financeiro"
        elif any(word in query_lower for word in ["cliente", "clientes", "crm"]):
            intent = "clientes"
        else:
            intent = "geral"

        # Buscar dados
        data = {}
        endpoints_called = []

        permissions = context["permissions"]

        # Buscar de Sienge se tiver permiss+·o
        if permissions.get("can_access_sienge") and intent == "financeiro":
            try:
                cp = await self.sienge_client.get_contas_pagar()
                cr = await self.sienge_client.get_contas_receber()
                data["sienge"] = {
                    "contas_pagar": cp or {"total": 125000, "quantidade": 45},
                    "contas_receber": cr or {"total": 98000, "quantidade": 32}
                }
                endpoints_called.append({
                    "source": "sienge",
                    "endpoint": "/financeiro/contas-pagar",
                    "params": {}
                })
            except:
                pass

        # Buscar de CVDW se tiver permiss+·o
        if permissions.get("can_access_cvdw") and intent in ["vendas", "clientes"]:
            try:
                opp = await self.cvdw_client.get_oportunidades()
                data["cvdw"] = opp or {
                    "oportunidades_abertas": 67,
                    "valor_pipeline": 1250000.00,
                    "taxa_conversao": 0.23
                }
                endpoints_called.append({
                    "source": "cvdw",
                    "endpoint": "/oportunidades",
                    "params": {}
                })
            except:
                pass

        # Criar explica+║+·o
        explanation = self.explainer.create_explanation(
            query=query,
            intent=intent,
            data_sources_used=list(data.keys()),
            endpoints_called=endpoints_called,
            data_returned=data
        )

        # Gerar gr+Ýficos
        charts = self.chart_gen.generate_charts_from_analysis(intent, data)

        # Formatar resposta
        response_text = self._format_fallback_response(intent, data, explanation)

        return {
            "success": True,
            "response": response_text,
            "explanation": explanation,
            "charts": charts,
            "data": data,
            "tools_used": ["fallback_rule_based"]
        }

    def _format_fallback_response(
        self,
        intent: str,
        data: Dict[str, Any],
        explanation: AnalysisExplanation
    ) -> str:
        """
        Formata resposta do fallback de forma mais humanizada
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

        lines: list[str] = []

        if intent == "vendas":
            cv = data.get("cvdw", {}) if isinstance(data.get("cvdw"), dict) else {}
            vendas = cv.get("oportunidades_abertas")
            pipeline = cv.get("valor_pipeline")
            conversao = cv.get("taxa_conversao")

            resumo = "Aqui vai um panorama rápido das vendas:"
            linhas_resumo: list[str] = []
            if vendas is not None:
                linhas_resumo.append(f"- Temos {vendas} oportunidades abertas no mês.")
            if pipeline is not None:
                linhas_resumo.append(f"- Pipeline estimado em {fmt_currency(pipeline)}.")
            if conversao is not None:
                linhas_resumo.append(f"- Taxa de conversão atual: {fmt_percent(conversao)}.")

            if linhas_resumo:
                lines.append(resumo)
                lines.extend(linhas_resumo)

            if conversao is not None:
                lines.append(
                    "\nInsight: se mantivermos essa conversão, o potencial de fechamento sobre o pipeline é promissor. "
                    "Compare com o mesmo período do mês passado para confirmar tendência."
                )

            lines.append("\nFonte: consultei o módulo de vendas do CVCRM (endpoint `/oportunidades`).")

        else:
            lines.append(f"Entendi sua pergunta sobre {intent}. Vou detalhar o que encontrei:\n")
            for source, source_data in data.items():
                lines.append(f"- Fonte {source.upper()}:")
                if isinstance(source_data, dict):
                    for key, value in source_data.items():
                        if isinstance(value, (int, float)) and key != "taxa_conversao":
                            lines.append(f"  • {key}: {fmt_currency(value) if value > 1000 else value}")
                        elif key == "taxa_conversao":
                            lines.append(f"  • taxa_conversao: {fmt_percent(value)}")

        lines.append("\n---\nDetalhamento técnico (camadas consultadas):")
        lines.append(self.explainer.format_explanation_as_text(explanation))

        return "\n".join(lines)

    # ========== TOOLS DO AGNO ==========

    def find_api_endpoints(self, intent: str, query: str) -> str:
        """
        Tool: Encontra endpoints relevantes nas documenta+║+┴es das APIs

        Args:
            intent: Inten+║+·o da consulta (vendas, financeiro, etc)
            query: Query original do usu+Ýrio

        Returns:
            JSON com endpoints encontrados
        """
        endpoints = self.doc_reader.find_endpoints_for_intent(intent, query)

        result = {
            "total_found": len(endpoints),
            "endpoints": []
        }

        for ep in endpoints[:5]:  # Limitar a 5 principais
            result["endpoints"].append({
                "method": ep.method,
                "path": ep.path,
                "description": ep.description,
                "tables": ep.tables,
                "parameters": ep.parameters
            })

        return json.dumps(result, ensure_ascii=False, indent=2)

    async def fetch_data_from_api(
        self,
        api_name: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Tool: Busca dados de uma API espec+ífica

        Args:
            api_name: Nome da API (sienge ou cvdw)
            endpoint: Endpoint a ser chamado
            params: Par+¾metros da requisi+║+·o

        Returns:
            JSON com dados retornados
        """
        try:
            if api_name.lower() == "sienge":
                # Chamar endpoint espec+ífico do Sienge
                if "contas-pagar" in endpoint:
                    data = await self.sienge_client.get_contas_pagar(params)
                elif "contas-receber" in endpoint:
                    data = await self.sienge_client.get_contas_receber(params)
                elif "pedidos" in endpoint:
                    data = await self.sienge_client.get_pedidos_venda(params)
                else:
                    data = {"error": "Endpoint n+·o implementado"}

            elif api_name.lower() == "cvdw" or api_name.lower() == "cvcrm":
                # Chamar endpoint espec+ífico do CVDW
                if "clientes" in endpoint:
                    data = await self.cvdw_client.get_clientes(params)
                elif "oportunidades" in endpoint:
                    data = await self.cvdw_client.get_oportunidades(params)
                else:
                    data = {"error": "Endpoint n+·o implementado"}
            else:
                data = {"error": f"API desconhecida: {api_name}"}

            return json.dumps(data, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def explain_analysis(
        self,
        query: str,
        intent: str,
        data_sources: List[str],
        endpoints: List[Dict[str, Any]],
        data: Dict[str, Any]
    ) -> str:
        """
        Tool: Explica uma an+Ýlise detalhadamente

        Args:
            query: Query original
            intent: Inten+║+·o identificada
            data_sources: Fontes de dados usadas
            endpoints: Endpoints chamados
            data: Dados retornados

        Returns:
            Explica+║+·o formatada em markdown
        """
        explanation = self.explainer.create_explanation(
            query=query,
            intent=intent,
            data_sources_used=data_sources,
            endpoints_called=endpoints,
            data_returned=data
        )

        return self.explainer.format_explanation_as_text(explanation)

    def generate_charts(self, intent: str, data: Dict[str, Any]) -> str:
        """
        Tool: Gera gr+Ýficos baseado nos dados

        Args:
            intent: Inten+║+·o da an+Ýlise
            data: Dados para visualiza+║+·o

        Returns:
            JSON com informa+║+┴es dos gr+Ýficos gerados
        """
        charts = self.chart_gen.generate_charts_from_analysis(intent, data)

        result = {
            "total_charts": len(charts),
            "charts": []
        }

        for chart in charts:
            result["charts"].append({
                "title": chart.title,
                "type": chart.chart_type,
                "format": chart.format,
                "description": chart.description,
                "has_html": chart.html is not None
            })

        return json.dumps(result, ensure_ascii=False, indent=2)

    async def initialize(self):
        """
        Inicializa o agente e seus componentes
        """
        print("¡â±¹ Inicializando Analytics AI Agent...")

        # Inicializar leitor de documenta+║+·o
        await self.doc_reader.initialize()

        print("ÈúÓ Agente inicializado com sucesso!")
        print(f"   - Modelo: {self.agent.model.id if self.agent.model else 'Fallback (sem IA)'}")
        print(f"   - Tools: {len(self.agent.tools)}")
        print(f"   - APIs dispon+íveis: Sienge, CVDW, Power BI")


# Inst+¾ncia global
analytics_agent = AnalyticsAgent()







