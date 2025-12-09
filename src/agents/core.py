"""
Núcleo do Agente IA - Integração com APIs Empresariais
"""
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import UUID

from ..config import get_settings
from ..supabase_client import supabase_client
from .models import ChatMessage, AgentResponse, AgentQuery, APIResponse
from ..integrations.sienge.client import SiengeClient
from ..integrations.cvdw.client import CVDWClient
from ..analyses.powerbi_dashboards import PowerBIDashboards


class AIAgent:
    """
    Agente IA principal que integra dados de múltiplas fontes empresariais
    """

    def __init__(self):
        self.settings = get_settings()
        self.sienge_client = SiengeClient()
        self.cvdw_client = CVDWClient()
        self.powerbi_data = PowerBIDashboards.DASHBOARDS

        # Mapeamento de intenções para fontes de dados
        self.intent_mapping = {
            "vendas": ["cvdw", "powerbi"],
            "financeiro": ["sienge", "powerbi"],
            "clientes": ["cvdw"],
            "projetos": ["sienge"],
            "estoque": ["sienge"],
            "dashboard": ["powerbi"],
            "relatorio": ["powerbi", "sienge", "cvdw"],
            "comparacao": ["powerbi", "sienge", "cvdw"]
        }

    async def process_query(self, user_id: UUID, message: str) -> AgentResponse:
        """
        Processa uma consulta do usuário e retorna resposta inteligente
        """
        try:
            # 1. Analisar intenção da mensagem
            query = await self._analyze_intent(message)

            # 2. Verificar permissões do usuário
            permissions = await self._check_user_permissions(user_id)

            # 3. Coletar dados das APIs relevantes
            data = await self._gather_data(query, permissions)

            # 4. Gerar resposta inteligente
            response = await self._generate_response(message, data, query)

            return response

        except Exception as e:
            return AgentResponse(
                message=f"Desculpe, ocorreu um erro ao processar sua consulta: {str(e)}",
                confidence=0.0,
                data_source=None
            )

    async def _analyze_intent(self, message: str) -> AgentQuery:
        """
        Analisa a intenção da mensagem usando regras simples
        (Será substituído por IA mais avançada futuramente)
        """
        message_lower = message.lower()

        # Palavras-chave para identificar intenção
        keywords = {
            "vendas": ["venda", "vendas", "faturamento", "receita", "pedido", "orçamento"],
            "financeiro": ["financeiro", "contas", "pagar", "receber", "custo", "despesa", "saldo"],
            "clientes": ["cliente", "lead", "oportunidade", "crm", "contato"],
            "projetos": ["projeto", "obra", "contrato", "andamento"],
            "estoque": ["estoque", "produto", "inventário", "material"],
            "dashboard": ["dashboard", "relatório", "painel", "visualizar"],
            "relatorio": ["relatório", "análise", "métricas", "kpi"],
            "comparacao": ["comparar", "comparação", "versus", "vs", "diferença"]
        }

        # Identificar intenção principal
        intent = "geral"
        max_matches = 0

        for intent_type, words in keywords.items():
            matches = sum(1 for word in words if word in message_lower)
            if matches > max_matches:
                max_matches = matches
                intent = intent_type

        # Identificar fontes de dados necessárias
        data_sources = self.intent_mapping.get(intent, ["powerbi"])

        return AgentQuery(
            intent=intent,
            data_sources=data_sources,
            entities={"message": message}
        )

    async def _check_user_permissions(self, user_id: UUID) -> Dict[str, Any]:
        """
        Verifica permissões do usuário para acessar diferentes sistemas
        """
        try:
            # Buscar dados do usuário no Supabase
            response = supabase_client.table("usuarios").select("*").eq("id", user_id).single().execute()

            if response.data:
                user = response.data
                nivel_acesso = user.get("cargo", {}).get("nivel_acesso", 1) if user.get("cargo") else 1

                return {
                    "user_id": user_id,
                    "nivel_acesso": nivel_acesso,
                    "divisao": user.get("divisao", {}).get("codigo", "ALL") if user.get("divisao") else "ALL",
                    "can_access_sienge": nivel_acesso >= 3,
                    "can_access_cvdw": nivel_acesso >= 2,
                    "can_access_powerbi": nivel_acesso >= 2
                }

        except Exception as e:
            print(f"Erro ao verificar permissões: {e}")

        # Fallback: permissões mínimas
        return {
            "user_id": user_id,
            "nivel_acesso": 1,
            "divisao": "ALL",
            "can_access_sienge": False,
            "can_access_cvdw": False,
            "can_access_powerbi": True  # Power BI sempre acessível
        }

    async def _gather_data(self, query: AgentQuery, permissions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coleta dados das APIs relevantes baseado na query e permissões
        """
        data = {}

        # Power BI - sempre disponível
        if permissions.get("can_access_powerbi", True):
            data["powerbi"] = await self._get_powerbi_data(query)

        # Sienge API
        if "sienge" in query.data_sources and permissions.get("can_access_sienge", False):
            try:
                data["sienge"] = await self._get_sienge_data(query)
            except Exception as e:
                data["sienge"] = {"error": f"Erro na API Sienge: {str(e)}"}

        # CVDW API
        if "cvdw" in query.data_sources and permissions.get("can_access_cvdw", False):
            try:
                data["cvdw"] = await self._get_cvdw_data(query)
            except Exception as e:
                data["cvdw"] = {"error": f"Erro na API CVDW: {str(e)}"}

        return data

    async def _get_powerbi_data(self, query: AgentQuery) -> Dict[str, Any]:
        """
        Busca dados dos dashboards Power BI disponíveis
        """
        # Por enquanto retorna metadados dos dashboards
        # Futuramente pode fazer queries mais específicas
        available_dashboards = []

        for key, dashboard in self.powerbi_data.items():
            # Verificar se o usuário tem acesso baseado na divisão
            divisao = dashboard.get("divisao", [])
            if query.intent == "vendas" and "COM" in divisao:
                available_dashboards.append({
                    "key": key,
                    "nome": dashboard["nome"],
                    "tipo": "vendas"
                })
            elif query.intent == "financeiro" and "FIN" in divisao:
                available_dashboards.append({
                    "key": key,
                    "nome": dashboard["nome"],
                    "tipo": "financeiro"
                })

        return {
            "dashboards": available_dashboards,
            "total": len(available_dashboards)
        }

    async def _get_sienge_data(self, query: AgentQuery) -> Dict[str, Any]:
        """
        Busca dados da API Sienge baseado na intenção
        """
        try:
            # Tentar conexão com API real
            test_result = await self.sienge_client.test_connection()

            if test_result.get("status") == "connected":
                # API conectada - buscar dados reais
                if query.intent == "financeiro":
                    contas_pagar = await self.sienge_client.get_contas_pagar()
                    contas_receber = await self.sienge_client.get_contas_receber()
                    return {
                        "contas_pagar": contas_pagar,
                        "contas_receber": contas_receber,
                        "fonte": "sienge_api_real"
                    }
                elif query.intent == "projetos":
                    projetos = await self.sienge_client.get_projetos()
                    return {
                        "projetos": projetos,
                        "fonte": "sienge_api_real"
                    }
                elif query.intent == "vendas":
                    pedidos = await self.sienge_client.get_pedidos_venda()
                    return {
                        "pedidos_venda": pedidos,
                        "fonte": "sienge_api_real"
                    }
        except Exception as e:
            # API não conectada ou erro - usar dados simulados
            pass

        # Fallback: dados simulados para desenvolvimento
        if query.intent == "financeiro":
            return {
                "contas_pagar": {"total": 125000.00, "quantidade": 45},
                "contas_receber": {"total": 98000.00, "quantidade": 32},
                "saldo_atual": -27000.00,
                "fonte": "dados_simulados",
                "nota": "API Sienge não conectada - usando dados de exemplo"
            }
        elif query.intent == "projetos":
            return {
                "projetos_ativos": 12,
                "projetos_concluidos": 8,
                "valor_total": 2500000.00,
                "fonte": "dados_simulados",
                "nota": "API Sienge não conectada - usando dados de exemplo"
            }

        return {"message": "Dados Sienge não disponíveis para esta consulta", "fonte": "indisponivel"}

    async def _get_cvdw_data(self, query: AgentQuery) -> Dict[str, Any]:
        """
        Busca dados da API CVDW baseado na intenção
        """
        try:
            # Tentar conexão com API real
            test_result = await self.cvdw_client.test_connection()

            if test_result.get("status") == "connected":
                # API conectada - buscar dados reais
                if query.intent == "clientes":
                    clientes = await self.cvdw_client.get_clientes()
                    return {
                        "clientes": clientes,
                        "fonte": "cvdw_api_real"
                    }
                elif query.intent == "vendas":
                    oportunidades = await self.cvdw_client.get_oportunidades()
                    pipeline = await self.cvdw_client.get_pipeline_vendas()
                    return {
                        "oportunidades": oportunidades,
                        "pipeline": pipeline,
                        "fonte": "cvdw_api_real"
                    }
        except Exception as e:
            # API não conectada ou erro - usar dados simulados
            pass

        # Fallback: dados simulados para desenvolvimento
        if query.intent == "clientes":
            return {
                "total_clientes": 1250,
                "novos_clientes_mes": 45,
                "clientes_ativos": 890,
                "fonte": "dados_simulados",
                "nota": "API CVDW não conectada - usando dados de exemplo"
            }
        elif query.intent == "vendas":
            return {
                "oportunidades_abertas": 67,
                "valor_pipeline": 1250000.00,
                "taxa_conversao": 0.23,
                "fonte": "dados_simulados",
                "nota": "API CVDW não conectada - usando dados de exemplo"
            }

        return {"message": "Dados CVDW não disponíveis para esta consulta", "fonte": "indisponivel"}

    async def _generate_response(self, original_message: str, data: Dict[str, Any], query: AgentQuery) -> AgentResponse:
        """
        Gera resposta inteligente baseada nos dados coletados
        """
        # Por enquanto gera resposta baseada em regras simples
        # Futuramente será substituído por IA real

        if query.intent == "dashboard":
            powerbi_data = data.get("powerbi", {})
            dashboards = powerbi_data.get("dashboards", [])

            if dashboards:
                response_text = f"Encontrei {len(dashboards)} dashboard(s) relacionado(s) à sua consulta:\n\n"
                for dashboard in dashboards:
                    response_text += f"• {dashboard['nome']}\n"
                response_text += f"\nAcesse: http://localhost:5173/analyses"

                return AgentResponse(
                    message=response_text,
                    data_source="powerbi",
                    confidence=0.9,
                    suggestions=["Visualizar dashboards", "Exportar dados", "Compartilhar insights"]
                )
            else:
                return AgentResponse(
                    message="Não encontrei dashboards específicos para sua consulta. Você pode acessar todos os dashboards disponíveis em: http://localhost:5173/analyses",
                    data_source="powerbi",
                    confidence=0.7
                )

        elif query.intent == "vendas":
            response_parts = []

            # Dados CVDW
            cvdw_data = data.get("cvdw", {})
            if "oportunidades_abertas" in cvdw_data:
                opp = cvdw_data["oportunidades_abertas"]
                valor = cvdw_data.get("valor_pipeline", 0)
                response_parts.append(f"📊 Pipeline de Vendas: {opp} oportunidades abertas, valor total de R$ {valor:,.2f}")

            # Dados Power BI
            powerbi_data = data.get("powerbi", {})
            sales_dashboards = [d for d in powerbi_data.get("dashboards", []) if d.get("tipo") == "vendas"]
            if sales_dashboards:
                response_parts.append(f"📈 Dashboards de Vendas disponíveis: {len(sales_dashboards)}")

            if response_parts:
                return AgentResponse(
                    message="\n".join(response_parts),
                    data_source="cvdw,powerbi",
                    confidence=0.85,
                    suggestions=["Ver detalhes das oportunidades", "Analisar tendências", "Comparar com mês anterior"]
                )

        # Resposta genérica
        return AgentResponse(
            message=f"Entendi sua consulta sobre '{original_message}'. Baseado nos dados disponíveis, posso ajudar com informações sobre vendas, financeiro, clientes e dashboards. Que tipo de informação você precisa?",
            data_source="geral",
            confidence=0.6,
            suggestions=["Informações sobre vendas", "Dados financeiros", "Relatórios de clientes"]
        )
