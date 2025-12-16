"""Script para listar todas as tabelas disponíveis no Supabase"""
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from supabase import create_client

# Carregar variáveis de ambiente
load_dotenv()

def list_tables():
    """Lista todas as tabelas acessíveis via Supabase API"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        print("❌ SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY devem estar no .env")
        return

    supabase = create_client(url, key)

    # Lista de tabelas comuns para testar
    test_tables = [
        'users', 'dashboards', 'dashboard_permissions', 'audit_logs',
        'cvdw_empreendimentos', 'cvdw_propostas', 'cvdw_clientes',
        'cvdw_negocios', 'cvdw_imoveis', 'raw_data', 'raw',
        'empresas', 'propostas', 'clientes', 'negocios', 'imoveis'
    ]

    print("Verificando tabelas disponiveis...\n")
    available_tables = []

    for table in test_tables:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            columns = result.data[0].keys() if result.data else []
            available_tables.append((table, columns, len(result.data) > 0))
            status = "OK (com dados)" if result.data else "OK (vazia)"
            print(f"{status} {table}")
            if columns:
                print(f"   Colunas: {', '.join(list(columns)[:10])}")
                # Verificar se tem coluna 'raw'
                if 'raw' in columns:
                    print(f"   >>> ENCONTROU COLUNA 'raw'!")
        except Exception as e:
            if "PGRST205" not in str(e):  # Ignora erro de tabela não encontrada
                print(f"ERRO {table}: {e}")

    print(f"\nTotal de tabelas encontradas: {len(available_tables)}")

    # Mostrar tabelas com coluna 'raw'
    tables_with_raw = [(t, c) for t, c, _ in available_tables if 'raw' in c]
    if tables_with_raw:
        print("\nTabelas com coluna 'raw':")
        for table, columns in tables_with_raw:
            print(f"   - {table}")

    return available_tables

if __name__ == "__main__":
    list_tables()
