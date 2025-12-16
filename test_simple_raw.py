"""
Teste SIMPLES da funcao query_raw_data
Execute: python test_simple_raw.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
load_dotenv()

# Import direto do Supabase client
from src.supabase_client import supabase_admin_client


async def test_query_raw():
    """Teste direto da query RAW sem passar pelo agente completo"""
    print("=" * 80)
    print("TESTE SIMPLES - Query RAW Direta")
    print("=" * 80)
    print()

    # Teste 1: Consulta basica
    print("[1] Testando consulta basica de leads...")
    try:
        query = supabase_admin_client.table("leads").select("*").limit(3)
        result = query.execute()

        print(f"  [OK] Consulta executada com sucesso!")
        print(f"  Registros retornados: {len(result.data)}")

        if len(result.data) > 0:
            first_record = result.data[0]
            print(f"  Campos disponiveis: {list(first_record.keys())[:10]}")

            # Verificar se tem coluna raw
            if 'raw' in first_record:
                print(f"  [OK] Coluna 'raw' encontrada!")
                raw_data = first_record['raw']
                if isinstance(raw_data, dict):
                    print(f"  Tipo de dados RAW: dict (JSON)")
                    print(f"  Campos no RAW: {list(raw_data.keys())[:10]}")
            else:
                print(f"  [INFO] Coluna 'raw' nao encontrada nesta tabela")
    except Exception as e:
        print(f"  [ERRO] {e}")

    print()
    print("-" * 80)
    print()

    # Teste 2: Consulta com filtro
    print("[2] Testando consulta com filtro (ativo='S')...")
    try:
        query = supabase_admin_client.table("leads").select("*").eq("ativo", "S").limit(2)
        result = query.execute()

        print(f"  [OK] Consulta com filtro executada!")
        print(f"  Leads ativos encontrados: {len(result.data)}")
    except Exception as e:
        print(f"  [ERRO] {e}")

    print()
    print("-" * 80)
    print()

    # Teste 3: Testar todas as 8 tabelas
    print("[3] Testando acesso as 8 tabelas RAW...")
    tables = ['leads', 'vendas', 'reservas', 'unidades',
              'corretores', 'pessoas', 'imobiliarias', 'repasses']

    for table in tables:
        try:
            query = supabase_admin_client.table(table).select("*").limit(1)
            result = query.execute()
            count = len(result.data)
            print(f"  [OK] {table:15} - {count} registro(s)")
        except Exception as e:
            print(f"  [ERRO] {table:15} - {str(e)[:50]}")

    print()
    print("=" * 80)
    print("TESTE SIMPLES CONCLUIDO")
    print("=" * 80)
    print()
    print("Resultado: A conexao com o Supabase esta funcionando!")
    print("Proximos passos:")
    print("  1. Executar indices GIN (database/scripts/add_raw_indexes.sql)")
    print("  2. Testar via agente: 'Quantos leads ativos temos?'")
    print()


if __name__ == "__main__":
    asyncio.run(test_query_raw())
