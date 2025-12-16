"""
Teste rápido da integração agente + dados RAW
Execute: python test_quick_raw.py
"""
import asyncio
import json
from src.agents.agno_agent import analytics_agent


async def test_quick():
    """Teste rápido de integração"""
    print("=" * 80)
    print("TESTE RÁPIDO - Integração Agente IA + Dados RAW")
    print("=" * 80)
    print()

    # Teste 1: Verificar se a tool foi registrada
    print("[1] Verificando tools registradas...")
    await analytics_agent.initialize()
    tool_names = [tool.__name__ for tool in analytics_agent.agent.tools]

    if 'query_raw_data' in tool_names:
        print(f"  [OK] Tool 'query_raw_data' registrada com sucesso!")
        print(f"  Total de tools: {len(tool_names)}")
        print(f"  Tools: {', '.join(tool_names)}")
    else:
        print(f"  [ERRO] Tool 'query_raw_data' NAO encontrada!")
        print(f"  Tools disponiveis: {', '.join(tool_names)}")
        return

    print()
    print("-" * 80)
    print()

    # Teste 2: Consulta básica de leads
    print("[2] Testando consulta basica de leads...")
    try:
        result = await analytics_agent.query_raw_data(
            table_name="leads",
            limit=3
        )
        data = json.loads(result)

        if "error" in data:
            print(f"  [ERRO] Erro na consulta: {data['error']}")
        else:
            print(f"  [OK] Consulta bem-sucedida!")
            print(f"  Tabela: {data['table']}")
            print(f"  Registros retornados: {data['count']}")
            print(f"  Filtros aplicados: {data['filters_applied']}")

            if data['count'] > 0:
                print(f"  Exemplo de registro (primeiros campos):")
                first_record = data['data'][0]
                for key in list(first_record.keys())[:5]:
                    value = str(first_record[key])[:50]
                    print(f"     - {key}: {value}")
    except Exception as e:
        print(f"  [ERRO] Erro ao executar consulta: {e}")

    print()
    print("-" * 80)
    print()

    # Teste 3: Consulta com filtros
    print("[3] Testando consulta com filtros (leads ativos)...")
    try:
        result = await analytics_agent.query_raw_data(
            table_name="leads",
            filters={"ativo": "S"},
            limit=2
        )
        data = json.loads(result)

        if "error" in data:
            print(f"  [ERRO] Erro na consulta: {data['error']}")
        else:
            print(f"  [OK] Consulta com filtros bem-sucedida!")
            print(f"  Leads ativos encontrados: {data['count']}")
    except Exception as e:
        print(f"  [ERRO] Erro ao executar consulta: {e}")

    print()
    print("-" * 80)
    print()

    # Teste 4: Validação de segurança (tabela inválida)
    print("[4] Testando validacao de seguranca (tabela invalida)...")
    try:
        result = await analytics_agent.query_raw_data(
            table_name="tabela_maliciosa",
            limit=1
        )
        data = json.loads(result)

        if "error" in data and "invalida" in data['error'].lower():
            print(f"  [OK] Validacao funcionando corretamente!")
            print(f"  Mensagem de erro: {data['error']}")
        else:
            print(f"  [ERRO] Validacao NAO bloqueou tabela invalida!")
    except Exception as e:
        print(f"  [ERRO] Erro inesperado: {e}")

    print()
    print("-" * 80)
    print()

    # Teste 5: Validação de dados sensíveis
    print("[5] Testando mascaramento de dados sensiveis...")
    try:
        result = await analytics_agent.query_raw_data(
            table_name="pessoas",
            limit=2
        )
        data = json.loads(result)

        if "error" not in data and data['count'] > 0:
            has_masked = False
            first_record = data['data'][0]

            sensitive_fields = ['cpf', 'documento', 'email', 'telefone', 'celular']
            for field in sensitive_fields:
                if field in first_record and "***" in str(first_record[field]):
                    has_masked = True
                    print(f"  [OK] Campo '{field}' mascarado: {first_record[field]}")

            if has_masked:
                print(f"  [OK] Dados sensiveis sendo mascarados corretamente!")
            else:
                print(f"  [INFO] Nenhum campo sensivel encontrado nos registros de teste")
        else:
            print(f"  [INFO] Tabela 'pessoas' vazia ou erro: {data.get('error', 'vazia')}")
    except Exception as e:
        print(f"  [ERRO] Erro ao testar mascaramento: {e}")

    print()
    print("=" * 80)
    print("TESTE RÁPIDO CONCLUÍDO")
    print("=" * 80)
    print()
    print("📋 Próximos passos:")
    print("  1. Executar índices GIN no Supabase (database/scripts/add_raw_indexes.sql)")
    print("  2. Rodar testes completos: pytest tests/test_raw_data_agent.py -v")
    print("  3. Testar via chat: 'Quantos leads ativos temos?'")
    print()


if __name__ == "__main__":
    asyncio.run(test_quick())
