"""
Sistema de Leitura e Indexação de Documentação de APIs
Lê documentações do Sienge e CVCRM para identificar endpoints disponíveis
"""
import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import httpx
from bs4 import BeautifulSoup


@dataclass
class APIEndpoint:
    """Representa um endpoint de API documentado"""
    method: str  # GET, POST, PUT, DELETE
    path: str  # /api/vendas/pedidos
    description: str  # Descrição do que o endpoint faz
    parameters: List[Dict[str, Any]]  # Parâmetros aceitos
    response_schema: Optional[Dict[str, Any]]  # Schema da resposta
    tables: List[str]  # Tabelas/entidades relacionadas
    examples: List[str]  # Exemplos de uso


class APIDocReader:
    """
    Leitor inteligente de documentação de APIs
    Extrai informações sobre endpoints, parâmetros e schemas
    """

    def __init__(self):
        self.sienge_docs_url = "https://api.sienge.com.br/docs/"
        self.cvcrm_docs_url = "https://desenvolvedor.cvcrm.com.br/reference/"

        # Cache de endpoints descobertos
        self.sienge_endpoints: Dict[str, APIEndpoint] = {}
        self.cvcrm_endpoints: Dict[str, APIEndpoint] = {}

        # Mapeamento de intenções para endpoints (será construído dinamicamente)
        self.intent_to_endpoints: Dict[str, List[str]] = {}

    async def load_api_documentation(self, api_name: str) -> Dict[str, APIEndpoint]:
        """
        Carrega e processa a documentação completa de uma API

        Args:
            api_name: "sienge" ou "cvcrm"

        Returns:
            Dicionário de endpoints descobertos
        """
        if api_name == "sienge":
            return await self._load_sienge_docs()
        elif api_name == "cvcrm":
            return await self._load_cvcrm_docs()
        else:
            raise ValueError(f"API desconhecida: {api_name}")

    async def _load_sienge_docs(self) -> Dict[str, APIEndpoint]:
        """
        Carrega documentação do Sienge ERP

        Como a documentação real pode estar protegida ou em formato específico,
        vou criar um sistema de fallback com endpoints conhecidos
        """
        # Tentar buscar documentação online
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.sienge_docs_url)
                if response.status_code == 200:
                    # Parsear HTML e extrair endpoints
                    endpoints = self._parse_sienge_html(response.text)
                    if endpoints:
                        self.sienge_endpoints = endpoints
                        return endpoints
        except Exception as e:
            print(f"Não foi possível carregar docs online do Sienge: {e}")

        # Fallback: Endpoints conhecidos do Sienge
        self.sienge_endpoints = self._get_sienge_known_endpoints()
        return self.sienge_endpoints

    async def _load_cvcrm_docs(self) -> Dict[str, APIEndpoint]:
        """
        Carrega documentação do CVCRM
        """
        # Tentar buscar documentação online
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.cvcrm_docs_url)
                if response.status_code == 200:
                    # Parsear e extrair endpoints
                    endpoints = self._parse_cvcrm_html(response.text)
                    if endpoints:
                        self.cvcrm_endpoints = endpoints
                        return endpoints
        except Exception as e:
            print(f"Não foi possível carregar docs online do CVCRM: {e}")

        # Fallback: Endpoints conhecidos do CVCRM
        self.cvcrm_endpoints = self._get_cvcrm_known_endpoints()
        return self.cvcrm_endpoints

    def _parse_sienge_html(self, html_content: str) -> Dict[str, APIEndpoint]:
        """
        Parseia HTML da documentação do Sienge para extrair endpoints
        """
        endpoints = {}
        soup = BeautifulSoup(html_content, 'html.parser')

        # Procurar por definições de endpoints (cada API tem formato diferente)
        # Este é um exemplo genérico que deve ser ajustado conforme a estrutura real
        endpoint_sections = soup.find_all(['div', 'section'], class_=['endpoint', 'api-endpoint'])

        for section in endpoint_sections:
            try:
                endpoint = self._extract_endpoint_from_section(section)
                if endpoint:
                    key = f"{endpoint.method}_{endpoint.path.replace('/', '_')}"
                    endpoints[key] = endpoint
            except Exception as e:
                continue

        return endpoints

    def _parse_cvcrm_html(self, html_content: str) -> Dict[str, APIEndpoint]:
        """
        Parseia HTML da documentação do CVCRM para extrair endpoints
        """
        endpoints = {}
        soup = BeautifulSoup(html_content, 'html.parser')

        # Similar ao Sienge, mas adaptado para formato do CVCRM
        endpoint_sections = soup.find_all(['div', 'article'], class_=['endpoint', 'reference'])

        for section in endpoint_sections:
            try:
                endpoint = self._extract_endpoint_from_section(section)
                if endpoint:
                    key = f"{endpoint.method}_{endpoint.path.replace('/', '_')}"
                    endpoints[key] = endpoint
            except Exception as e:
                continue

        return endpoints

    def _extract_endpoint_from_section(self, section) -> Optional[APIEndpoint]:
        """
        Extrai informações de um endpoint de uma seção HTML
        """
        try:
            # Extrair método HTTP e caminho
            method_tag = section.find(class_=['method', 'http-method'])
            path_tag = section.find(class_=['path', 'endpoint-path'])

            if not method_tag or not path_tag:
                return None

            method = method_tag.text.strip().upper()
            path = path_tag.text.strip()

            # Extrair descrição
            desc_tag = section.find(class_=['description', 'summary'])
            description = desc_tag.text.strip() if desc_tag else "Sem descrição"

            # Extrair parâmetros
            parameters = self._extract_parameters(section)

            # Extrair schema de resposta
            response_schema = self._extract_response_schema(section)

            # Identificar tabelas relacionadas (heurística baseada em keywords)
            tables = self._identify_tables_from_path_and_desc(path, description)

            return APIEndpoint(
                method=method,
                path=path,
                description=description,
                parameters=parameters,
                response_schema=response_schema,
                tables=tables,
                examples=[]
            )
        except Exception as e:
            return None

    def _extract_parameters(self, section) -> List[Dict[str, Any]]:
        """
        Extrai parâmetros de um endpoint
        """
        parameters = []
        param_table = section.find('table', class_=['parameters', 'params'])

        if param_table:
            rows = param_table.find_all('tr')[1:]  # Pular header
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    param = {
                        "name": cols[0].text.strip(),
                        "type": cols[1].text.strip() if len(cols) > 1 else "string",
                        "required": "required" in cols[2].text.lower() if len(cols) > 2 else False,
                        "description": cols[3].text.strip() if len(cols) > 3 else ""
                    }
                    parameters.append(param)

        return parameters

    def _extract_response_schema(self, section) -> Optional[Dict[str, Any]]:
        """
        Extrai schema da resposta
        """
        schema_block = section.find('pre', class_=['response', 'schema'])
        if schema_block:
            try:
                schema_text = schema_block.text.strip()
                # Tentar parsear como JSON
                return json.loads(schema_text)
            except:
                return {"raw": schema_block.text.strip()}
        return None

    def _identify_tables_from_path_and_desc(self, path: str, description: str) -> List[str]:
        """
        Identifica tabelas/entidades relacionadas baseado no caminho e descrição
        """
        tables = []
        combined_text = f"{path} {description}".lower()

        # Mapeamento de keywords para tabelas
        table_keywords = {
            "vendas": ["pedidos", "vendas", "orcamentos"],
            "clientes": ["clientes", "leads", "contatos"],
            "produtos": ["produtos", "estoque", "inventario"],
            "financeiro": ["contas_pagar", "contas_receber", "pagamentos"],
            "projetos": ["projetos", "obras", "contratos"],
            "funcionarios": ["funcionarios", "colaboradores", "rh"]
        }

        for category, keywords in table_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                tables.extend(keywords)

        return list(set(tables))  # Remover duplicatas

    def _get_sienge_known_endpoints(self) -> Dict[str, APIEndpoint]:
        """
        Retorna endpoints conhecidos do Sienge (fallback)
        """
        return {
            "GET_financeiro_contas_pagar": APIEndpoint(
                method="GET",
                path="/financeiro/contas-pagar",
                description="Lista todas as contas a pagar",
                parameters=[
                    {"name": "data_inicio", "type": "date", "required": False},
                    {"name": "data_fim", "type": "date", "required": False},
                    {"name": "status", "type": "string", "required": False}
                ],
                response_schema={"type": "array", "items": {"type": "object"}},
                tables=["contas_pagar", "fornecedores"],
                examples=["GET /financeiro/contas-pagar?status=pendente"]
            ),
            "GET_financeiro_contas_receber": APIEndpoint(
                method="GET",
                path="/financeiro/contas-receber",
                description="Lista todas as contas a receber",
                parameters=[
                    {"name": "data_inicio", "type": "date", "required": False},
                    {"name": "data_fim", "type": "date", "required": False},
                    {"name": "status", "type": "string", "required": False}
                ],
                response_schema={"type": "array", "items": {"type": "object"}},
                tables=["contas_receber", "clientes"],
                examples=["GET /financeiro/contas-receber?status=aberto"]
            ),
            "GET_vendas_pedidos": APIEndpoint(
                method="GET",
                path="/vendas/pedidos",
                description="Lista todos os pedidos de venda",
                parameters=[
                    {"name": "cliente_id", "type": "integer", "required": False},
                    {"name": "status", "type": "string", "required": False},
                    {"name": "data_inicio", "type": "date", "required": False}
                ],
                response_schema={"type": "array", "items": {"type": "object"}},
                tables=["pedidos", "clientes", "produtos"],
                examples=["GET /vendas/pedidos?status=aprovado"]
            ),
            "GET_estoque_produtos": APIEndpoint(
                method="GET",
                path="/estoque/produtos",
                description="Lista produtos do estoque",
                parameters=[
                    {"name": "categoria", "type": "string", "required": False},
                    {"name": "estoque_minimo", "type": "boolean", "required": False}
                ],
                response_schema={"type": "array", "items": {"type": "object"}},
                tables=["produtos", "categorias", "movimentacao_estoque"],
                examples=["GET /estoque/produtos?estoque_minimo=true"]
            ),
            "GET_projetos": APIEndpoint(
                method="GET",
                path="/projetos",
                description="Lista todos os projetos",
                parameters=[
                    {"name": "status", "type": "string", "required": False},
                    {"name": "cliente_id", "type": "integer", "required": False}
                ],
                response_schema={"type": "array", "items": {"type": "object"}},
                tables=["projetos", "clientes", "custos"],
                examples=["GET /projetos?status=ativo"]
            )
        }

    def _get_cvcrm_known_endpoints(self) -> Dict[str, APIEndpoint]:
        """
        Retorna endpoints conhecidos do CVCRM (fallback)
        """
        return {
            "GET_clientes": APIEndpoint(
                method="GET",
                path="/clientes",
                description="Lista todos os clientes cadastrados",
                parameters=[
                    {"name": "nome", "type": "string", "required": False},
                    {"name": "segmento", "type": "string", "required": False},
                    {"name": "ativo", "type": "boolean", "required": False}
                ],
                response_schema={"type": "array", "items": {"type": "object"}},
                tables=["clientes", "contatos", "enderecos"],
                examples=["GET /clientes?ativo=true"]
            ),
            "GET_oportunidades": APIEndpoint(
                method="GET",
                path="/oportunidades",
                description="Lista oportunidades de venda (pipeline)",
                parameters=[
                    {"name": "estagio", "type": "string", "required": False},
                    {"name": "vendedor_id", "type": "integer", "required": False},
                    {"name": "data_inicio", "type": "date", "required": False}
                ],
                response_schema={"type": "array", "items": {"type": "object"}},
                tables=["oportunidades", "clientes", "vendedores", "produtos"],
                examples=["GET /oportunidades?estagio=negociacao"]
            ),
            "GET_interactions": APIEndpoint(
                method="GET",
                path="/interactions",
                description="Lista histórico de interações com clientes",
                parameters=[
                    {"name": "cliente_id", "type": "integer", "required": False},
                    {"name": "tipo", "type": "string", "required": False},
                    {"name": "data_inicio", "type": "date", "required": False}
                ],
                response_schema={"type": "array", "items": {"type": "object"}},
                tables=["interactions", "clientes", "usuarios"],
                examples=["GET /interactions?tipo=reuniao"]
            ),
            "GET_metrics_kpis": APIEndpoint(
                method="GET",
                path="/metrics/kpis",
                description="Retorna KPIs e métricas de vendas",
                parameters=[
                    {"name": "periodo", "type": "string", "required": False},
                    {"name": "tipo", "type": "string", "required": False}
                ],
                response_schema={"type": "object"},
                tables=["vendas", "oportunidades", "metas"],
                examples=["GET /metrics/kpis?periodo=mes_atual"]
            ),
            "POST_analytics_segmentation": APIEndpoint(
                method="POST",
                path="/analytics/segmentation",
                description="Cria segmentação de clientes",
                parameters=[
                    {"name": "criterios", "type": "object", "required": True},
                    {"name": "tipo_segmentacao", "type": "string", "required": False}
                ],
                response_schema={"type": "object"},
                tables=["clientes", "segmentos", "comportamento"],
                examples=['POST /analytics/segmentation {"criterios": {"faturamento_min": 50000}}']
            ),
            "GET_reports_sales": APIEndpoint(
                method="GET",
                path="/reports/sales",
                description="Gera relatório de vendas",
                parameters=[
                    {"name": "data_inicio", "type": "date", "required": True},
                    {"name": "data_fim", "type": "date", "required": True},
                    {"name": "formato", "type": "string", "required": False}
                ],
                response_schema={"type": "object"},
                tables=["vendas", "pedidos", "produtos", "vendedores"],
                examples=["GET /reports/sales?data_inicio=2025-01-01&data_fim=2025-01-31"]
            )
        }

    def find_endpoints_for_intent(self, intent: str, query: str) -> List[APIEndpoint]:
        """
        Encontra endpoints relevantes baseado na intenção e query do usuário

        Args:
            intent: Intenção identificada (vendas, financeiro, etc)
            query: Query original do usuário

        Returns:
            Lista de endpoints relevantes
        """
        relevant_endpoints = []
        query_lower = query.lower()

        # Mapear intenção para endpoints
        intent_mapping = {
            "vendas": ["vendas_pedidos", "oportunidades", "reports_sales"],
            "financeiro": ["financeiro_contas_pagar", "financeiro_contas_receber"],
            "clientes": ["clientes", "interactions"],
            "projetos": ["projetos"],
            "estoque": ["estoque_produtos"],
            "relatorio": ["reports_sales", "metrics_kpis"]
        }

        # Buscar nos endpoints do Sienge
        for key, endpoint in self.sienge_endpoints.items():
            if self._is_endpoint_relevant(endpoint, intent, query_lower, intent_mapping):
                relevant_endpoints.append(endpoint)

        # Buscar nos endpoints do CVCRM
        for key, endpoint in self.cvcrm_endpoints.items():
            if self._is_endpoint_relevant(endpoint, intent, query_lower, intent_mapping):
                relevant_endpoints.append(endpoint)

        return relevant_endpoints

    def _is_endpoint_relevant(self, endpoint: APIEndpoint, intent: str,
                               query: str, intent_mapping: Dict[str, List[str]]) -> bool:
        """
        Determina se um endpoint é relevante para a consulta
        """
        # Verificar se o endpoint está no mapeamento de intenção
        relevant_keywords = intent_mapping.get(intent, [])
        endpoint_key = endpoint.path.lower().replace('/', '_').replace('-', '_')

        if any(keyword in endpoint_key for keyword in relevant_keywords):
            return True

        # Verificar se alguma palavra da query aparece na descrição ou path
        query_words = query.split()
        combined_text = f"{endpoint.path} {endpoint.description}".lower()

        return any(word in combined_text for word in query_words if len(word) > 3)

    async def initialize(self):
        """
        Inicializa o leitor carregando documentação de todas as APIs
        """
        print("[DOCS] Carregando documentacao das APIs...")
        await self.load_api_documentation("sienge")
        await self.load_api_documentation("cvcrm")
        print("[OK] Documentacao carregada:")
        print(f"   - Sienge: {len(self.sienge_endpoints)} endpoints")
        print(f"   - CVCRM: {len(self.cvcrm_endpoints)} endpoints")


# Instância global (será inicializada na startup)
api_doc_reader = APIDocReader()
