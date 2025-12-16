"""
Testes E2E para integração do agente IA com dados RAW do Supabase
"""
import pytest
import asyncio
from uuid import UUID

from src.agents.agno_agent import analytics_agent


# Queries de teste
TEST_QUERIES = [
    "Quantos leads ativos temos?",
    "Mostre as últimas 10 vendas",
    "Quais corretores venderam mais este mês?",
    "Liste as unidades disponíveis",
    "Quantas reservas temos em Brasília?",
    "Qual o total de repasses do mês?",
]


@pytest.fixture
def test_user_id():
    """ID de usuário para testes"""
    return UUID("00000000-0000-0000-0000-000000000000")


@pytest.fixture
def test_permissions():
    """Permissões de teste com acesso total"""
    return {
        "nivel_acesso": 5,
        "divisao": "ALL",
        "can_access_sienge": True,
        "can_access_cvdw": True,
        "can_access_powerbi": True,
    }


class TestRawDataIntegration:
    """Testes de integração do agente com dados RAW"""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Testa se o agente foi inicializado corretamente"""
        await analytics_agent.initialize()
        assert analytics_agent.agent is not None
        assert analytics_agent.agent.tools is not None

        # Verificar se a nova tool foi registrada
        tool_names = [tool.__name__ for tool in analytics_agent.agent.tools]
        assert 'query_raw_data' in tool_names

    @pytest.mark.asyncio
    async def test_query_raw_data_basic(self):
        """Testa consulta básica de dados RAW"""
        result = await analytics_agent.query_raw_data(
            table_name="leads",
            limit=5
        )

        import json
        data = json.loads(result)

        assert "error" not in data
        assert "table" in data
        assert data["table"] == "leads"
        assert "count" in data
        assert "data" in data
        assert isinstance(data["data"], list)

    @pytest.mark.asyncio
    async def test_query_raw_data_with_filters(self):
        """Testa consulta com filtros"""
        result = await analytics_agent.query_raw_data(
            table_name="leads",
            filters={"ativo": "S"},
            limit=10
        )

        import json
        data = json.loads(result)

        assert "error" not in data
        assert data["filters_applied"] == {"ativo": "S"}

    @pytest.mark.asyncio
    async def test_query_invalid_table(self):
        """Testa tentativa de consultar tabela inválida"""
        result = await analytics_agent.query_raw_data(
            table_name="tabela_falsa",
            limit=5
        )

        import json
        data = json.loads(result)

        assert "error" in data
        assert "invalida" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_query_invalid_column_filter(self):
        """Testa filtro em coluna não permitida"""
        result = await analytics_agent.query_raw_data(
            table_name="leads",
            filters={"coluna_invalida": "valor"},
            limit=5
        )

        import json
        data = json.loads(result)

        assert "error" in data
        assert "nao permitida" in data["error"].lower()

    @pytest.mark.asyncio
    async def test_sensitive_data_masking(self):
        """Testa se dados sensíveis são mascarados"""
        result = await analytics_agent.query_raw_data(
            table_name="pessoas",
            limit=5
        )

        import json
        data = json.loads(result)

        if data.get("count", 0) > 0:
            first_record = data["data"][0]

            # Verificar se campos sensíveis foram mascarados
            sensitive_fields = ['cpf', 'documento', 'email', 'telefone', 'celular']
            for field in sensitive_fields:
                if field in first_record:
                    value = first_record[field]
                    if value and value != "***":
                        assert "***" in str(value), f"Campo {field} não foi mascarado: {value}"

    @pytest.mark.asyncio
    async def test_limit_enforcement(self):
        """Testa se o limite máximo de 500 é respeitado"""
        result = await analytics_agent.query_raw_data(
            table_name="leads",
            limit=1000  # Tentar limite acima do máximo
        )

        import json
        data = json.loads(result)

        # Deve retornar no máximo 500 registros
        assert data.get("count", 0) <= 500

    @pytest.mark.asyncio
    @pytest.mark.parametrize("query", TEST_QUERIES)
    async def test_agent_processes_query(self, query, test_user_id, test_permissions):
        """Testa se o agente processa queries sobre dados RAW"""
        result = await analytics_agent.process_query(
            user_id=test_user_id,
            query=query,
            permissions=test_permissions
        )

        assert result["success"] is True
        assert "response" in result
        # Verificar se alguma tool foi usada
        assert len(result.get("tools_used", [])) > 0


class TestAllRawTables:
    """Testa acesso a todas as 8 tabelas RAW"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("table_name", [
        "leads",
        "vendas",
        "reservas",
        "unidades",
        "corretores",
        "pessoas",
        "imobiliarias",
        "repasses",
    ])
    async def test_access_all_tables(self, table_name):
        """Testa se todas as tabelas RAW são acessíveis"""
        result = await analytics_agent.query_raw_data(
            table_name=table_name,
            limit=2
        )

        import json
        data = json.loads(result)

        # Não deve retornar erro de tabela inválida
        if "error" in data:
            assert "invalida" not in data["error"].lower()
        else:
            assert data["table"] == table_name


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])
