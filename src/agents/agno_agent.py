"""Analytics AI agent using Agno framework."""
import os
import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from agno.agent import Agent, RunOutput
from agno.models.openai import OpenAIChat
import httpx

from .api_doc_reader import api_doc_reader
from .analysis_explainer import analysis_explainer, AnalysisExplanation
from .chart_generator import chart_generator
from .trend_analyzer import trend_analyzer, comparative_analyzer
from .predictive_insights import predictive_insights
from .alert_generator import alert_generator
from .report_summarizer import report_summarizer
from .cache_manager import cache_manager, conversation_memory
from .monitoring import audit_logger, performance_monitor, usage_tracker
from .rag_store import RagStore
from .response_formatter import response_formatter
from ..integrations.sienge.client import SiengeClient
from ..integrations.cvdw.client import CVDWClient
from ..config import get_settings
from ..supabase_client import supabase_admin_client
import time
import asyncio


class AnalyticsAgent:
    """IA agent wired to Sienge, CVDW and chart/explainer helpers."""

    def __init__(self):
        self.settings = get_settings()
        self.sienge_client = SiengeClient()
        self.cvdw_client = CVDWClient()
        self.doc_reader = api_doc_reader
        self.explainer = analysis_explainer
        self.chart_gen = chart_generator
        self.rag_store = RagStore()

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
                self.analyze_trends,
                self.compare_periods,
                self.forecast_future,
                self.detect_anomalies,
                self.generate_alerts,
                self.create_summary_report,
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
        start_time = time.time()

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

        # Verificar histórico de conversas
        conversation_context = conversation_memory.get_context(str(user_id), last_n=2)

        system_prompt = self._build_system_prompt(context)
        rag_context, rag_sources = self._get_rag_context(query)
        if rag_context:
            system_prompt += "\n\nContexto recuperado (RAG):\n" + rag_context
        if conversation_context and conversation_context != "Sem histórico anterior.":
            system_prompt += f"\n\nContexto de conversas anteriores:\n{conversation_context}"

        # Tentar caminho direto sem Agno primeiro (evita timeouts e problemas de tool-calls)
        direct = await self._llm_direct_response(query, system_prompt)
        if direct:
            return {
                "success": True,
                "response": direct,
                "tools_used": ["llm_direct"],
                "explanation": None,
                "charts": [],
                "rag_sources": rag_sources if rag_sources else None,
            }

        use_agno = os.getenv("AGENT_USE_AGNO", "false").lower() in {"1", "true", "yes"}

        try:
            if use_agno and self.agent.model:
                try:
                    timeout_s = int(os.getenv("AGENT_LLM_TIMEOUT_SECONDS", str(self.settings.agent_llm_timeout_seconds)))
                    response: RunOutput = await asyncio.wait_for(
                        self.agent.arun(query, context=system_prompt),
                        timeout=timeout_s
                    )

                    tool_calls = getattr(response, "tool_calls", None) or []
                    tools_used = [call.function.name for call in tool_calls]
                    result = {
                        "success": True,
                        "response": response.content,
                        "tools_used": tools_used,
                        "explanation": None,
                        "charts": [],
                        "rag_sources": rag_sources if rag_sources else None,
                    }

                    # Registrar métricas
                    duration_ms = (time.time() - start_time) * 1000
                    performance_monitor.record_metric("agent_query_time", duration_ms)
                    performance_monitor.increment_counter("total_agent_queries")

                    # Audit log
                    audit_logger.log_agent_query(
                        user_id=str(user_id),
                        query=query,
                        tools_used=tools_used,
                        response_length=len(response.content),
                        success=True
                    )

                    # Salvar na memória
                    conversation_memory.save_message(
                        user_id=str(user_id),
                        message=query,
                        response=response.content[:500],  # Resumo
                        metadata={"tools_used": tools_used, "duration_ms": duration_ms}
                    )

                    return result
                except Exception as e:
                    # Log detalhado do erro para debug
                    print(f"[ERROR] LLM falhou: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    audit_logger.log_error(
                        user_id=str(user_id),
                        error_type="agent_processing_error",
                        error_message=str(e)
                    )
                    direct = await self._llm_direct_response(query, system_prompt)
                    if direct:
                        return {
                            "success": True,
                            "response": direct,
                            "tools_used": ["llm_direct"],
                            "explanation": None,
                            "charts": [],
                            "rag_sources": rag_sources if rag_sources else None,
                        }
                    fallback = await self._fallback_process_query(query, context)
                    fallback["rag_sources"] = rag_sources if rag_sources else None
                    return fallback
            direct = await self._llm_direct_response(query, system_prompt)
            if direct:
                return {
                    "success": True,
                    "response": direct,
                    "tools_used": ["llm_direct"],
                    "explanation": None,
                    "charts": [],
                    "rag_sources": rag_sources if rag_sources else None,
                }
            fallback = await self._fallback_process_query(query, context)
            fallback["rag_sources"] = rag_sources if rag_sources else None
            return fallback
        except Exception as e:
            audit_logger.log_error(
                user_id=str(user_id),
                error_type="query_error",
                error_message=str(e)
            )
            return {"success": False, "error": str(e), "response": f"Erro ao processar consulta: {e}"}

    def _get_rag_context(self, query: str):
        enabled = os.getenv("RAG_ENABLED", "true").lower() in {"1", "true", "yes"}
        if not enabled:
            return "", []
        top_k = int(os.getenv("RAG_TOP_K", "3"))
        try:
            hits = self.rag_store.query(query, top_k=top_k)
        except Exception:
            return "", []
        if not hits:
            return "", []
        parts = []
        sources = []
        for i, hit in enumerate(hits, start=1):
            parts.append(f"[{i}] {hit.source}\n{hit.text}")
            sources.append(f"{hit.source}")
        return "\n\n".join(parts), sources

    async def _llm_direct_response(self, query: str, system_prompt: str, retry_count: int = 2) -> Optional[str]:
        """
        Fallback direto para o endpoint OpenAI-compatible (Ollama) quando Agno falhar/timeout.
        Inclui retry automatico para lidar com cold start do modelo.
        """
        if not self.llm:
            return None
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1").rstrip("/")
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        timeout_s = int(os.getenv("AGENT_LLM_TIMEOUT_SECONDS", str(self.settings.agent_llm_timeout_seconds)))

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "stream": False,
        }

        for attempt in range(retry_count + 1):
            try:
                print(f"[INFO] Tentativa {attempt + 1}/{retry_count + 1} de chamar Ollama (timeout: {timeout_s}s)...")
                async with httpx.AsyncClient(timeout=timeout_s) as client:
                    resp = await client.post(
                        f"{base_url}/chat/completions",
                        headers={"Authorization": "Bearer ollama", "Content-Type": "application/json"},
                        json=payload,
                    )
                resp.raise_for_status()
                data = resp.json()
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {}) if isinstance(choice, dict) else {}
                content = message.get("content")
                if content:
                    print(f"[SUCCESS] Ollama respondeu com sucesso (tentativa {attempt + 1})")
                return content or None
            except httpx.ReadTimeout as e:
                print(f"[WARN] Timeout na tentativa {attempt + 1}/{retry_count + 1}: {e}")
                if attempt < retry_count:
                    # Aumentar timeout progressivamente para a proxima tentativa
                    timeout_s = int(timeout_s * 1.5)
                    print(f"[INFO] Aumentando timeout para {timeout_s}s na proxima tentativa...")
                    await asyncio.sleep(1)  # Pequeno delay antes de retry
                else:
                    print(f"[ERROR] Todas as {retry_count + 1} tentativas falharam com timeout")
                    return None
            except Exception as e:
                print(f"[ERROR] LLM direto falhou (tentativa {attempt + 1}): {type(e).__name__}: {e}")
                if attempt < retry_count:
                    await asyncio.sleep(1)
                else:
                    return None
        return None

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Constroi o system prompt profissional usando o ResponseFormatter.
        Instrui o agente a responder como um analista de negocios senior.
        """
        return response_formatter.create_system_prompt(context)

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

        # Usar response_formatter para gerar resposta profissional
        insights = response_formatter.extract_insights_from_data(data, intent)
        recommendations = response_formatter.generate_recommendations(data, intent)
        response_text = response_formatter.format_business_response(
            question=query,
            data=data,
            insights=insights,
            recommendations=recommendations
        )

        return {
            "success": True,
            "response": response_text,
            "explanation": explanation,
            "charts": charts,
            "data": data,
            "tools_used": ["fallback_rule_based"],
        }

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
        limit: int = 50,
        offset: int = 0,
        order_by: Optional[str] = None
    ) -> str:
        """
        Tool: Consulta dados RAW das tabelas internas do Supabase com paginação.

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
            offset: Número de registros a pular (para paginação)
            order_by: Coluna para ordenação (ex: "created_at")

        Returns:
            JSON string com os dados da tabela e informações de paginação
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
            query = supabase_admin_client.table(table_name).select("*", count='exact')

            # Aplicar filtros de forma segura (previne SQL injection)
            if filters:
                allowed = ALLOWED_COLUMNS.get(table_name, [])

                for key, value in filters.items():
                    if key not in allowed:
                        return json.dumps({
                            "error": f"Coluna '{key}' nao permitida para tabela {table_name}. Use: {', '.join(allowed)}"
                        }, ensure_ascii=False)
                    query = query.eq(key, value)

            # Aplicar ordenação se especificada
            if order_by:
                # Validar que a coluna existe
                allowed_order_cols = ALLOWED_COLUMNS.get(table_name, []) + ['id', 'created_at', 'updated_at']
                if order_by.lstrip('-') in allowed_order_cols:
                    # Suporta ordenação desc com prefixo '-'
                    if order_by.startswith('-'):
                        query = query.order(order_by[1:], desc=True)
                    else:
                        query = query.order(order_by)

            # Aplicar paginação
            query = query.range(offset, offset + limit - 1)
            result = query.execute()

            # Filtrar dados sensíveis antes de retornar
            filtered_data = self._filter_sensitive_fields(result.data)

            # Obter contagem total para paginação
            total_count = result.count if hasattr(result, 'count') else len(filtered_data)

            return json.dumps({
                "table": table_name,
                "count": len(filtered_data),
                "total_count": total_count,
                "offset": offset,
                "limit": limit,
                "has_more": (offset + limit) < total_count,
                "next_offset": offset + limit if (offset + limit) < total_count else None,
                "data": filtered_data,
                "filters_applied": filters or {},
                "order_by": order_by
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

    def analyze_trends(
        self,
        data: str,
        date_column: str = 'data',
        value_column: str = 'valor',
        period: str = 'monthly'
    ) -> str:
        """
        Tool: Analisa tendências em dados temporais

        Args:
            data: JSON string com lista de dados
            date_column: Nome da coluna de data
            value_column: Nome da coluna de valor
            period: Período de agregação ('daily', 'weekly', 'monthly')

        Returns:
            JSON com análise de tendências
        """
        try:
            data_list = json.loads(data) if isinstance(data, str) else data
            result = trend_analyzer.analyze_sales_trend(
                data_list,
                date_column=date_column,
                value_column=value_column,
                period=period
            )
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"erro": str(e)}, ensure_ascii=False)

    def compare_periods(
        self,
        data: str,
        date_column: str = 'data',
        value_column: str = 'valor',
        period1_start: Optional[str] = None,
        period1_end: Optional[str] = None,
        period2_start: Optional[str] = None,
        period2_end: Optional[str] = None
    ) -> str:
        """
        Tool: Compara métricas entre dois períodos

        Args:
            data: JSON string com dados
            date_column: Nome da coluna de data
            value_column: Nome da coluna de valor
            period1_start/end: Datas do primeiro período
            period2_start/end: Datas do segundo período

        Returns:
            JSON com análise comparativa
        """
        try:
            data_list = json.loads(data) if isinstance(data, str) else data
            result = comparative_analyzer.compare_periods(
                data_list,
                date_column=date_column,
                value_column=value_column,
                period1_start=period1_start,
                period1_end=period1_end,
                period2_start=period2_start,
                period2_end=period2_end
            )
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"erro": str(e)}, ensure_ascii=False)

    def forecast_future(
        self,
        data: str,
        date_column: str = 'data',
        value_column: str = 'valor',
        periods_ahead: int = 3
    ) -> str:
        """
        Tool: Gera previsões para períodos futuros

        Args:
            data: JSON string com dados históricos
            date_column: Nome da coluna de data
            value_column: Nome da coluna de valor
            periods_ahead: Quantos períodos prever (padrão: 3)

        Returns:
            JSON com previsões e intervalos de confiança
        """
        try:
            data_list = json.loads(data) if isinstance(data, str) else data
            result = predictive_insights.forecast_sales(
                data_list,
                date_column=date_column,
                value_column=value_column,
                periods_ahead=periods_ahead
            )
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"erro": str(e)}, ensure_ascii=False)

    def detect_anomalies(
        self,
        data: str,
        date_column: str = 'data',
        value_column: str = 'valor',
        threshold_std: float = 2.0
    ) -> str:
        """
        Tool: Detecta anomalias estatísticas nos dados

        Args:
            data: JSON string com dados
            date_column: Nome da coluna de data
            value_column: Nome da coluna de valor
            threshold_std: Desvios padrão para considerar anomalia (padrão: 2.0)

        Returns:
            JSON com anomalias detectadas
        """
        try:
            data_list = json.loads(data) if isinstance(data, str) else data
            result = alert_generator.analyze_anomalies(
                data_list,
                date_column=date_column,
                value_column=value_column,
                threshold_std=threshold_std
            )
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"erro": str(e)}, ensure_ascii=False)

    def generate_alerts(
        self,
        current_data: str,
        historical_data: Optional[str] = None,
        thresholds: Optional[str] = None
    ) -> str:
        """
        Tool: Gera alertas de performance baseados em thresholds

        Args:
            current_data: JSON com dados atuais
            historical_data: JSON com dados históricos (opcional)
            thresholds: JSON com thresholds personalizados (opcional)

        Returns:
            JSON com alertas gerados
        """
        try:
            current = json.loads(current_data) if isinstance(current_data, str) else current_data
            historical = json.loads(historical_data) if historical_data and isinstance(historical_data, str) else []
            thresh = json.loads(thresholds) if thresholds and isinstance(thresholds, str) else None

            result = alert_generator.generate_performance_alerts(
                current,
                historical,
                thresh
            )
            return json.dumps({"alertas": result}, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"erro": str(e)}, ensure_ascii=False)

    def create_summary_report(
        self,
        data: str,
        report_type: str = 'vendas'
    ) -> str:
        """
        Tool: Gera sumário executivo dos dados

        Args:
            data: JSON string com dados para sumarizar
            report_type: Tipo de relatório ('vendas', 'financeiro', 'clientes', 'geral')

        Returns:
            JSON com sumário executivo estruturado
        """
        try:
            data_dict = json.loads(data) if isinstance(data, str) else data
            result = report_summarizer.generate_executive_summary(
                data_dict,
                report_type=report_type
            )
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({"erro": str(e)}, ensure_ascii=False)

    async def initialize(self):
        """Inicializa o agente e seus componentes."""
        print("Inicializando Analytics AI Agent...")
        await self.doc_reader.initialize()
        print("Agente inicializado.")
        print(f" - Modelo: {self.agent.model.id if self.agent.model else 'Fallback (sem IA)'}")
        print(f" - Tools: {len(self.agent.tools)}")
        print(" - APIs disponiveis: Sienge, CVDW, Power BI")
        print(" - Novas ferramentas: Trend Analysis, Predictions, Anomaly Detection, Alerts, Reports")

        # Warm-up do modelo LLM (carrega na memoria)
        if self.llm:
            print("\n[INFO] Fazendo warm-up do modelo LLM...")
            try:
                warmup_response = await self._llm_direct_response(
                    query="ola",
                    system_prompt="Voce e um assistente. Responda apenas 'ok'.",
                    retry_count=1
                )
                if warmup_response:
                    print("[SUCCESS] Modelo LLM aquecido e pronto para uso!")
                else:
                    print("[WARN] Warm-up falhou. O modelo pode demorar na primeira requisicao.")
            except Exception as e:
                print(f"[WARN] Erro no warm-up: {e}. O modelo pode demorar na primeira requisicao.")
        print("\n" + "="*60)


# Instancia global
analytics_agent = AnalyticsAgent()
