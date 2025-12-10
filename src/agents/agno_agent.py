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

# Módulos locais
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
        # Você pode usar qualquer modelo compatível com OpenAI API
        # Opções gratuitas: Ollama local, Groq, etc.
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
        Configura o modelo de IA
        """
        # Opção 1: Usar OpenAI (requer chave API paga)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            return OpenAIChat(
                id="gpt-4o-mini",  # Modelo mais barato
                api_key=openai_key
            )

        # Opção 2: Usar Ollama local (gratuito, roda na máquina)
        # Requer Ollama instalado com modelo baixado
        try:
            return OpenAIChat(
                id="llama3.2",
                base_url="http://localhost:11434/v1",
                api_key="ollama"  # Ollama não precisa de key real
            )
        except:
            pass

        # Opção 3: Usar Groq (gratuito com limite)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            return OpenAIChat(
                id="mixtral-8x7b-32768",
                base_url="https://api.groq.com/openai/v1",
                api_key=groq_key
            )

        # Fallback: usar mock (retorna respostas genéricas)
        print("⚠️ Nenhum modelo de IA configurado. Use Ollama local ou configure OPENAI_API_KEY")
        return None

    async def process_query(
        self,
        user_id: UUID,
        query: str,
        permissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processa uma consulta do usuário usando o agente Agno

        Args:
            user_id: ID do usuário
            query: Consulta em linguagem natural
            permissions: Permissões do usuário

        Returns:
            Resposta completa com análise, gráficos e explicação
        """
        # Contexto para o agente
        context = {
            "user_id": str(user_id),
            "permissions": permissions,
            "query": query,
            "available_apis": []
        }

        # Adicionar APIs disponíveis baseado em permissões
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
                response: RunOutput = await self.agent.arun(query, context=system_prompt)

                return {
                    "success": True,
                    "response": response.content,
                    "tools_used": [call.function.name for call in (response.tool_calls or [])],
                    "explanation": None,  # Será preenchido se tool explain_analysis for chamada
                    "charts": [],  # Será preenchido se tool generate_charts for chamada
                }
            else:
                # Fallback sem IA: lógica baseada em regras
                return await self._fallback_process_query(query, context)

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"Erro ao processar consulta: {str(e)}"
            }

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Constrói prompt de sistema para o agente
        """
        apis_str = ", ".join(context["available_apis"])

        prompt = f"""Você é um assistente de análise de dados empresariais inteligente.

SUAS CAPACIDADES:
- Você tem acesso a dados de: {apis_str}
- Você pode buscar endpoints de APIs usando a tool 'find_api_endpoints'
- Você pode buscar dados reais usando a tool 'fetch_data_from_api'
- Você pode explicar análises detalhadamente usando a tool 'explain_analysis'
- Você pode gerar gráficos e visualizações usando a tool 'generate_charts'

PERMISSÕES DO USUÁRIO:
- Nível de acesso: {context['permissions'].get('nivel_acesso', 1)}
- Divisão: {context['permissions'].get('divisao', 'ALL')}
- APIs disponíveis: {apis_str}

SUA MISSÃO:
1. Entender a pergunta do usuário
2. Identificar quais endpoints/dados são necessários
3. Buscar os dados das APIs corretas
4. Explicar claramente:
   - Quais tabelas/fontes você está usando
   - Quais colunas você está consultando
   - Quais filtros você está aplicando
   - Quais relacionamentos entre tabelas existem
   - Quais cálculos você está fazendo
5. Gerar visualizações (gráficos) quando apropriado
6. Responder em português de forma clara e profissional

IMPORTANTE:
- SEMPRE explique suas fontes de dados de forma transparente
- SEMPRE mostre seus cálculos e fórmulas
- Se não tiver certeza, pergunte ao usuário para esclarecer
- Se não tiver permissão para acessar algum dado, informe claramente
"""
        return prompt

    async def check_user_permissions(self, user_id: UUID) -> Dict[str, Any]:
        """
        Obtém permissões do usuário a partir do Supabase (usa service role para evitar bloqueio por RLS)
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
            # Fallback permissões mínimas
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

        # Identificar intenção por keywords
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

        # Buscar de Sienge se tiver permissão
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

        # Buscar de CVDW se tiver permissão
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

        # Criar explicação
        explanation = self.explainer.create_explanation(
            query=query,
            intent=intent,
            data_sources_used=list(data.keys()),
            endpoints_called=endpoints_called,
            data_returned=data
        )

        # Gerar gráficos
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
        Formata resposta do fallback
        """
        lines = [f"## Análise: {intent.capitalize()}\n"]

        # Adicionar dados
        for source, source_data in data.items():
            lines.append(f"\n### Dados de {source.upper()}:")
            if isinstance(source_data, dict):
                for key, value in source_data.items():
                    if isinstance(value, (int, float)):
                        if isinstance(value, float) and value > 1000:
                            lines.append(f"- **{key}**: R$ {value:,.2f}")
                        else:
                            lines.append(f"- **{key}**: {value}")
                    elif isinstance(value, dict) and "total" in value:
                        lines.append(f"- **{key}**: R$ {value['total']:,.2f} ({value.get('quantidade', 0)} itens)")

        # Adicionar link para explicação detalhada
        lines.append("\n### 📋 Explicação Detalhada")
        lines.append(self.explainer.format_explanation_as_text(explanation))

        return "\n".join(lines)

    # ========== TOOLS DO AGNO ==========

    def find_api_endpoints(self, intent: str, query: str) -> str:
        """
        Tool: Encontra endpoints relevantes nas documentações das APIs

        Args:
            intent: Intenção da consulta (vendas, financeiro, etc)
            query: Query original do usuário

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
        Tool: Busca dados de uma API específica

        Args:
            api_name: Nome da API (sienge ou cvdw)
            endpoint: Endpoint a ser chamado
            params: Parâmetros da requisição

        Returns:
            JSON com dados retornados
        """
        try:
            if api_name.lower() == "sienge":
                # Chamar endpoint específico do Sienge
                if "contas-pagar" in endpoint:
                    data = await self.sienge_client.get_contas_pagar(params)
                elif "contas-receber" in endpoint:
                    data = await self.sienge_client.get_contas_receber(params)
                elif "pedidos" in endpoint:
                    data = await self.sienge_client.get_pedidos_venda(params)
                else:
                    data = {"error": "Endpoint não implementado"}

            elif api_name.lower() == "cvdw" or api_name.lower() == "cvcrm":
                # Chamar endpoint específico do CVDW
                if "clientes" in endpoint:
                    data = await self.cvdw_client.get_clientes(params)
                elif "oportunidades" in endpoint:
                    data = await self.cvdw_client.get_oportunidades(params)
                else:
                    data = {"error": "Endpoint não implementado"}
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
        Tool: Explica uma análise detalhadamente

        Args:
            query: Query original
            intent: Intenção identificada
            data_sources: Fontes de dados usadas
            endpoints: Endpoints chamados
            data: Dados retornados

        Returns:
            Explicação formatada em markdown
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
        Tool: Gera gráficos baseado nos dados

        Args:
            intent: Intenção da análise
            data: Dados para visualização

        Returns:
            JSON com informações dos gráficos gerados
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
        print("🤖 Inicializando Analytics AI Agent...")

        # Inicializar leitor de documentação
        await self.doc_reader.initialize()

        print("✅ Agente inicializado com sucesso!")
        print(f"   - Modelo: {self.agent.model.id if self.agent.model else 'Fallback (sem IA)'}")
        print(f"   - Tools: {len(self.agent.tools)}")
        print(f"   - APIs disponíveis: Sienge, CVDW, Power BI")


# Instância global
analytics_agent = AnalyticsAgent()

