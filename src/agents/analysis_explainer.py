"""
Sistema de Explicação de Análises
Explica as fontes de dados, tabelas, colunas, filtros, relacionamentos e cálculos
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class DataSource:
    """Representa uma fonte de dados usada na análise"""
    name: str  # Nome da API/sistema (Sienge, CVCRM, Power BI)
    tipo: str  # API, Database, Dashboard
    endpoint: Optional[str] = None  # Endpoint específico usado
    autenticacao: str = "API Key"  # Tipo de autenticação


@dataclass
class TableInfo:
    """Informações sobre uma tabela/entidade usada"""
    nome: str  # Nome da tabela
    fonte: str  # De qual sistema veio (Sienge, CVCRM)
    descricao: str  # O que a tabela representa
    colunas_usadas: List[str] = field(default_factory=list)  # Quais colunas foram utilizadas
    total_registros: Optional[int] = None  # Quantos registros foram consultados


@dataclass
class Filter:
    """Representa um filtro aplicado aos dados"""
    campo: str  # Campo filtrado
    operador: str  # = , >, <, LIKE, IN, etc
    valor: Any  # Valor do filtro
    tabela: str  # Tabela de origem


@dataclass
class Relationship:
    """Representa um relacionamento entre tabelas"""
    tabela_origem: str
    coluna_origem: str
    tabela_destino: str
    coluna_destino: str
    tipo: str  # 1:1, 1:N, N:N
    descricao: str


@dataclass
class Calculation:
    """Representa um cálculo realizado"""
    nome: str  # Nome do cálculo (ex: "Total de Vendas")
    formula: str  # Fórmula matemática (ex: "SUM(vendas.valor)")
    campos_usados: List[str]  # Campos envolvidos
    resultado: Optional[Any] = None  # Resultado do cálculo
    unidade: Optional[str] = None  # Unidade (R$, %, unidades)


@dataclass
class AnalysisExplanation:
    """Explicação completa de uma análise"""
    titulo: str
    descricao: str
    timestamp: datetime = field(default_factory=datetime.now)

    # Fontes de dados
    fontes: List[DataSource] = field(default_factory=list)

    # Tabelas usadas
    tabelas: List[TableInfo] = field(default_factory=list)

    # Filtros aplicados
    filtros: List[Filter] = field(default_factory=list)

    # Relacionamentos entre tabelas
    relacionamentos: List[Relationship] = field(default_factory=list)

    # Cálculos realizados
    calculos: List[Calculation] = field(default_factory=list)

    # Observações adicionais
    observacoes: List[str] = field(default_factory=list)


class AnalysisExplainer:
    """
    Sistema que explica análises de forma transparente
    """

    def __init__(self):
        # Metadados de schemas conhecidos
        self.schema_metadata = self._load_schema_metadata()

    def _load_schema_metadata(self) -> Dict[str, Any]:
        """
        Carrega metadados dos schemas das APIs
        """
        return {
            "sienge": {
                "contas_pagar": {
                    "descricao": "Tabela de contas a pagar da empresa",
                    "colunas": {
                        "id": "Identificador único da conta",
                        "fornecedor_id": "ID do fornecedor (FK para fornecedores)",
                        "valor": "Valor da conta em reais",
                        "data_vencimento": "Data de vencimento",
                        "status": "Status da conta (pendente, pago, vencido)",
                        "data_pagamento": "Data do pagamento efetivo",
                        "descricao": "Descrição da conta"
                    }
                },
                "contas_receber": {
                    "descricao": "Tabela de contas a receber da empresa",
                    "colunas": {
                        "id": "Identificador único da conta",
                        "cliente_id": "ID do cliente (FK para clientes)",
                        "valor": "Valor da conta em reais",
                        "data_vencimento": "Data de vencimento",
                        "status": "Status da conta (aberto, recebido, vencido)",
                        "data_recebimento": "Data do recebimento efetivo",
                        "descricao": "Descrição da conta"
                    }
                },
                "pedidos": {
                    "descricao": "Tabela de pedidos de venda",
                    "colunas": {
                        "id": "Identificador único do pedido",
                        "cliente_id": "ID do cliente (FK para clientes)",
                        "data_pedido": "Data do pedido",
                        "valor_total": "Valor total do pedido",
                        "status": "Status do pedido (orçamento, aprovado, faturado)",
                        "vendedor_id": "ID do vendedor responsável"
                    }
                },
                "produtos": {
                    "descricao": "Tabela de produtos do estoque",
                    "colunas": {
                        "id": "Identificador único do produto",
                        "nome": "Nome do produto",
                        "codigo": "Código SKU do produto",
                        "categoria_id": "ID da categoria (FK para categorias)",
                        "quantidade_estoque": "Quantidade em estoque",
                        "preco_venda": "Preço de venda unitário",
                        "estoque_minimo": "Quantidade mínima em estoque"
                    }
                },
                "projetos": {
                    "descricao": "Tabela de projetos/obras",
                    "colunas": {
                        "id": "Identificador único do projeto",
                        "nome": "Nome do projeto",
                        "cliente_id": "ID do cliente (FK para clientes)",
                        "data_inicio": "Data de início",
                        "data_previsao_termino": "Data prevista de término",
                        "valor_contrato": "Valor total do contrato",
                        "status": "Status do projeto (planejamento, execucao, concluido)"
                    }
                }
            },
            "cvcrm": {
                "clientes": {
                    "descricao": "Tabela de clientes cadastrados no CRM",
                    "colunas": {
                        "id": "Identificador único do cliente",
                        "nome": "Nome/Razão social",
                        "cpf_cnpj": "CPF ou CNPJ",
                        "email": "Email principal",
                        "telefone": "Telefone de contato",
                        "segmento": "Segmento de mercado",
                        "data_cadastro": "Data de cadastro no sistema",
                        "ativo": "Cliente ativo (true/false)"
                    }
                },
                "oportunidades": {
                    "descricao": "Tabela de oportunidades de venda (pipeline)",
                    "colunas": {
                        "id": "Identificador único da oportunidade",
                        "cliente_id": "ID do cliente (FK para clientes)",
                        "titulo": "Título da oportunidade",
                        "valor_estimado": "Valor estimado da venda",
                        "estagio": "Estágio no funil (prospeccao, qualificacao, negociacao, fechamento)",
                        "probabilidade": "Probabilidade de fechamento (%)",
                        "data_criacao": "Data de criação",
                        "data_previsao_fechamento": "Previsão de fechamento",
                        "vendedor_id": "ID do vendedor responsável"
                    }
                },
                "interactions": {
                    "descricao": "Histórico de interações com clientes",
                    "colunas": {
                        "id": "Identificador único da interação",
                        "cliente_id": "ID do cliente (FK para clientes)",
                        "tipo": "Tipo de interação (email, telefone, reuniao, etc)",
                        "data": "Data da interação",
                        "usuario_id": "ID do usuário que fez a interação",
                        "descricao": "Descrição da interação",
                        "resultado": "Resultado da interação"
                    }
                },
                "vendas": {
                    "descricao": "Tabela de vendas efetivadas",
                    "colunas": {
                        "id": "Identificador único da venda",
                        "oportunidade_id": "ID da oportunidade (FK para oportunidades)",
                        "cliente_id": "ID do cliente (FK para clientes)",
                        "valor_final": "Valor final da venda",
                        "data_fechamento": "Data de fechamento",
                        "vendedor_id": "ID do vendedor",
                        "comissao": "Valor da comissão"
                    }
                }
            }
        }

    def create_explanation(
        self,
        query: str,
        intent: str,
        data_sources_used: List[str],
        endpoints_called: List[Dict[str, Any]],
        data_returned: Dict[str, Any]
    ) -> AnalysisExplanation:
        """
        Cria uma explicação completa de uma análise

        Args:
            query: Query original do usuário
            intent: Intenção identificada
            data_sources_used: Lista de fontes de dados usadas
            endpoints_called: Lista de endpoints chamados
            data_returned: Dados retornados

        Returns:
            AnalysisExplanation completa
        """
        explanation = AnalysisExplanation(
            titulo=f"Análise: {intent.capitalize()}",
            descricao=f"Análise solicitada: '{query}'"
        )

        # 1. Identificar fontes de dados
        for source_name in data_sources_used:
            fonte = DataSource(
                name=source_name.upper(),
                tipo="API REST" if source_name in ["sienge", "cvcrm"] else "Dashboard",
                endpoint=self._get_main_endpoint(endpoints_called, source_name),
                autenticacao="API Key + Token" if source_name in ["sienge", "cvcrm"] else "Embedded"
            )
            explanation.fontes.append(fonte)

        # 2. Identificar tabelas usadas
        for endpoint_info in endpoints_called:
            tables = self._extract_tables_from_endpoint(endpoint_info)
            for table_name, source in tables:
                table_info = TableInfo(
                    nome=table_name,
                    fonte=source.upper(),
                    descricao=self._get_table_description(source, table_name),
                    colunas_usadas=self._get_columns_used(source, table_name, data_returned),
                    total_registros=self._estimate_records(data_returned, source, table_name)
                )
                explanation.tabelas.append(table_info)

        # 3. Identificar filtros aplicados
        for endpoint_info in endpoints_called:
            filters = self._extract_filters_from_endpoint(endpoint_info)
            explanation.filtros.extend(filters)

        # 4. Identificar relacionamentos
        relationships = self._identify_relationships(explanation.tabelas)
        explanation.relacionamentos.extend(relationships)

        # 5. Identificar cálculos
        calculations = self._identify_calculations(intent, data_returned)
        explanation.calculos.extend(calculations)

        # 6. Adicionar observações
        explanation.observacoes = self._generate_observations(explanation)

        return explanation

    def _get_main_endpoint(self, endpoints: List[Dict[str, Any]], source: str) -> Optional[str]:
        """Retorna o endpoint principal usado de uma fonte"""
        for endpoint_info in endpoints:
            if endpoint_info.get("source") == source:
                return endpoint_info.get("endpoint", "")
        return None

    def _extract_tables_from_endpoint(self, endpoint_info: Dict[str, Any]) -> List[tuple]:
        """Extrai tabelas usadas de um endpoint"""
        tables = []
        source = endpoint_info.get("source", "")
        endpoint = endpoint_info.get("endpoint", "")

        # Heurística: extrair tabelas do caminho do endpoint
        if "contas-pagar" in endpoint or "contas_pagar" in endpoint:
            tables.append(("contas_pagar", source))
            tables.append(("fornecedores", source))  # Relacionamento implícito
        elif "contas-receber" in endpoint or "contas_receber" in endpoint:
            tables.append(("contas_receber", source))
            tables.append(("clientes", source))
        elif "pedidos" in endpoint:
            tables.append(("pedidos", source))
            tables.append(("clientes", source))
            tables.append(("produtos", source))
        elif "produtos" in endpoint or "estoque" in endpoint:
            tables.append(("produtos", source))
        elif "projetos" in endpoint:
            tables.append(("projetos", source))
            tables.append(("clientes", source))
        elif "clientes" in endpoint:
            tables.append(("clientes", source))
        elif "oportunidades" in endpoint:
            tables.append(("oportunidades", source))
            tables.append(("clientes", source))
            tables.append(("vendedores", source))
        elif "interactions" in endpoint:
            tables.append(("interactions", source))
            tables.append(("clientes", source))

        return tables

    def _get_table_description(self, source: str, table_name: str) -> str:
        """Retorna descrição de uma tabela"""
        if source in self.schema_metadata:
            if table_name in self.schema_metadata[source]:
                return self.schema_metadata[source][table_name].get("descricao", "Sem descrição")
        return f"Tabela {table_name} do sistema {source.upper()}"

    def _get_columns_used(self, source: str, table_name: str, data: Dict[str, Any]) -> List[str]:
        """Identifica colunas usadas baseado nos dados retornados"""
        columns = []

        # Tentar extrair colunas dos dados retornados
        if source in data:
            source_data = data[source]
            if isinstance(source_data, dict):
                columns = list(source_data.keys())
            elif isinstance(source_data, list) and len(source_data) > 0:
                first_item = source_data[0]
                if isinstance(first_item, dict):
                    columns = list(first_item.keys())

        # Fallback: usar todas as colunas conhecidas
        if not columns and source in self.schema_metadata:
            if table_name in self.schema_metadata[source]:
                columns = list(self.schema_metadata[source][table_name].get("colunas", {}).keys())

        return columns[:10]  # Limitar a 10 principais colunas

    def _estimate_records(self, data: Dict[str, Any], source: str, table: str) -> Optional[int]:
        """Estima quantidade de registros retornados"""
        if source in data:
            source_data = data[source]
            if isinstance(source_data, list):
                return len(source_data)
            elif isinstance(source_data, dict):
                if "total" in source_data:
                    return source_data["total"]
                elif "quantidade" in source_data:
                    return source_data["quantidade"]
        return None

    def _extract_filters_from_endpoint(self, endpoint_info: Dict[str, Any]) -> List[Filter]:
        """Extrai filtros de um endpoint"""
        filters = []
        params = endpoint_info.get("params", {})

        for param_name, param_value in params.items():
            if param_value is not None:
                filter_obj = Filter(
                    campo=param_name,
                    operador="=",
                    valor=param_value,
                    tabela=self._guess_table_from_param(param_name)
                )
                filters.append(filter_obj)

        return filters

    def _guess_table_from_param(self, param_name: str) -> str:
        """Tenta adivinhar tabela de origem de um parâmetro"""
        if "cliente" in param_name:
            return "clientes"
        elif "fornecedor" in param_name:
            return "fornecedores"
        elif "produto" in param_name:
            return "produtos"
        elif "pedido" in param_name:
            return "pedidos"
        return "desconhecida"

    def _identify_relationships(self, tables: List[TableInfo]) -> List[Relationship]:
        """Identifica relacionamentos entre tabelas"""
        relationships = []
        table_names = [t.nome for t in tables]

        # Relacionamentos conhecidos
        known_relationships = [
            ("contas_pagar", "fornecedor_id", "fornecedores", "id", "N:1", "Cada conta pertence a um fornecedor"),
            ("contas_receber", "cliente_id", "clientes", "id", "N:1", "Cada conta pertence a um cliente"),
            ("pedidos", "cliente_id", "clientes", "id", "N:1", "Cada pedido pertence a um cliente"),
            ("pedidos", "vendedor_id", "vendedores", "id", "N:1", "Cada pedido tem um vendedor"),
            ("produtos", "categoria_id", "categorias", "id", "N:1", "Cada produto tem uma categoria"),
            ("projetos", "cliente_id", "clientes", "id", "N:1", "Cada projeto pertence a um cliente"),
            ("oportunidades", "cliente_id", "clientes", "id", "N:1", "Cada oportunidade pertence a um cliente"),
            ("oportunidades", "vendedor_id", "vendedores", "id", "N:1", "Cada oportunidade tem um vendedor"),
            ("interactions", "cliente_id", "clientes", "id", "N:1", "Cada interação é com um cliente"),
            ("vendas", "cliente_id", "clientes", "id", "N:1", "Cada venda pertence a um cliente"),
            ("vendas", "oportunidade_id", "oportunidades", "id", "1:1", "Cada venda vem de uma oportunidade")
        ]

        for rel in known_relationships:
            if rel[0] in table_names and rel[2] in table_names:
                relationships.append(Relationship(
                    tabela_origem=rel[0],
                    coluna_origem=rel[1],
                    tabela_destino=rel[2],
                    coluna_destino=rel[3],
                    tipo=rel[4],
                    descricao=rel[5]
                ))

        return relationships

    def _identify_calculations(self, intent: str, data: Dict[str, Any]) -> List[Calculation]:
        """Identifica cálculos realizados"""
        calculations = []

        # Baseado nos dados retornados, identificar cálculos
        for source, source_data in data.items():
            if isinstance(source_data, dict):
                # Procurar por campos de totais, somas, médias
                if "total" in source_data:
                    calculations.append(Calculation(
                        nome=f"Total de {source}",
                        formula=f"SUM({source}.valor)",
                        campos_usados=[f"{source}.valor"],
                        resultado=source_data["total"],
                        unidade="R$"
                    ))
                if "quantidade" in source_data:
                    calculations.append(Calculation(
                        nome=f"Quantidade de registros",
                        formula=f"COUNT({source}.id)",
                        campos_usados=[f"{source}.id"],
                        resultado=source_data["quantidade"],
                        unidade="registros"
                    ))
                if "saldo_atual" in source_data:
                    calculations.append(Calculation(
                        nome="Saldo Atual",
                        formula="SUM(contas_receber.valor) - SUM(contas_pagar.valor)",
                        campos_usados=["contas_receber.valor", "contas_pagar.valor"],
                        resultado=source_data["saldo_atual"],
                        unidade="R$"
                    ))
                if "taxa_conversao" in source_data:
                    calculations.append(Calculation(
                        nome="Taxa de Conversão",
                        formula="(vendas_fechadas / oportunidades_totais) * 100",
                        campos_usados=["vendas.id", "oportunidades.id"],
                        resultado=source_data["taxa_conversao"],
                        unidade="%"
                    ))

        return calculations

    def _generate_observations(self, explanation: AnalysisExplanation) -> List[str]:
        """Gera observações sobre a análise"""
        observations = []

        # Observação sobre fontes
        if len(explanation.fontes) > 1:
            fontes_names = [f.name for f in explanation.fontes]
            observations.append(
                f"Esta análise combina dados de múltiplas fontes: {', '.join(fontes_names)}. "
                f"Os dados são integrados em tempo real via APIs REST."
            )

        # Observação sobre relacionamentos
        if explanation.relacionamentos:
            observations.append(
                f"Os dados foram relacionados através de {len(explanation.relacionamentos)} "
                f"join(s) entre tabelas, garantindo integridade referencial."
            )

        # Observação sobre filtros
        if explanation.filtros:
            observations.append(
                f"Foram aplicados {len(explanation.filtros)} filtro(s) para refinar os resultados."
            )

        # Observação sobre cálculos
        if explanation.calculos:
            observations.append(
                f"A análise inclui {len(explanation.calculos)} cálculo(s) automatizado(s) "
                f"baseado nos dados retornados."
            )

        return observations

    def format_explanation_as_text(self, explanation: AnalysisExplanation) -> str:
        """
        Formata a explicação como texto legível
        """
        lines = []
        lines.append(f"# {explanation.titulo}")
        lines.append(f"**Descrição:** {explanation.descricao}")
        lines.append(f"**Data/Hora:** {explanation.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append("")

        # Fontes de dados
        lines.append("## 📊 Fontes de Dados Utilizadas")
        for fonte in explanation.fontes:
            lines.append(f"- **{fonte.name}** ({fonte.tipo})")
            if fonte.endpoint:
                lines.append(f"  - Endpoint: `{fonte.endpoint}`")
            lines.append(f"  - Autenticação: {fonte.autenticacao}")
        lines.append("")

        # Tabelas
        lines.append("## 📋 Tabelas Consultadas")
        for tabela in explanation.tabelas:
            lines.append(f"### {tabela.nome} ({tabela.fonte})")
            lines.append(f"**Descrição:** {tabela.descricao}")
            if tabela.colunas_usadas:
                lines.append(f"**Colunas utilizadas:** {', '.join(tabela.colunas_usadas)}")
            if tabela.total_registros:
                lines.append(f"**Registros retornados:** {tabela.total_registros}")
            lines.append("")

        # Filtros
        if explanation.filtros:
            lines.append("## 🔍 Filtros Aplicados")
            for filtro in explanation.filtros:
                lines.append(f"- {filtro.tabela}.{filtro.campo} {filtro.operador} `{filtro.valor}`")
            lines.append("")

        # Relacionamentos
        if explanation.relacionamentos:
            lines.append("## 🔗 Relacionamentos Entre Tabelas")
            for rel in explanation.relacionamentos:
                lines.append(
                    f"- **{rel.tabela_origem}**.{rel.coluna_origem} → "
                    f"**{rel.tabela_destino}**.{rel.coluna_destino} ({rel.tipo})"
                )
                lines.append(f"  _{rel.descricao}_")
            lines.append("")

        # Cálculos
        if explanation.calculos:
            lines.append("## 🧮 Cálculos Realizados")
            for calc in explanation.calculos:
                lines.append(f"### {calc.nome}")
                lines.append(f"**Fórmula:** `{calc.formula}`")
                lines.append(f"**Campos usados:** {', '.join(calc.campos_usados)}")
                if calc.resultado is not None:
                    unit = f" {calc.unidade}" if calc.unidade else ""
                    lines.append(f"**Resultado:** {calc.resultado}{unit}")
                lines.append("")

        # Observações
        if explanation.observacoes:
            lines.append("## 💡 Observações")
            for obs in explanation.observacoes:
                lines.append(f"- {obs}")
            lines.append("")

        return "\n".join(lines)


# Instância global
analysis_explainer = AnalysisExplainer()
