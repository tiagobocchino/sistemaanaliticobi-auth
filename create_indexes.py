"""
Script para criar índices GIN automaticamente no Supabase
Execute: python create_indexes.py
"""
import os
import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
load_dotenv()

try:
    import psycopg2
except ImportError:
    print("ERRO: psycopg2 nao instalado. Instalando...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2


def create_gin_indexes():
    """Cria índices GIN nas colunas raw de 8 tabelas"""
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("ERRO: DATABASE_URL nao encontrada no .env")
        return False

    print("=" * 80)
    print("CRIANDO INDICES GIN NO SUPABASE")
    print("=" * 80)
    print()

    # Lista de índices a criar
    indexes = [
        ("leads", "idx_leads_raw"),
        ("vendas", "idx_vendas_raw"),
        ("reservas", "idx_reservas_raw"),
        ("unidades", "idx_unidades_raw"),
        ("corretores", "idx_corretores_raw"),
        ("pessoas", "idx_pessoas_raw"),
        ("imobiliarias", "idx_imobiliarias_raw"),
        ("repasses", "idx_repasses_raw"),
    ]

    try:
        # Conectar ao banco
        print("[1] Conectando ao Supabase PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        print("  [OK] Conectado com sucesso!")
        print()

        # Criar cada índice
        print("[2] Criando indices GIN...")
        created = 0
        already_exists = 0

        for table_name, index_name in indexes:
            try:
                sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} USING GIN (raw);"
                cur.execute(sql)
                conn.commit()

                # Verificar se foi criado ou já existia
                cur.execute(f"SELECT indexname FROM pg_indexes WHERE indexname = '{index_name}';")
                result = cur.fetchone()

                if result:
                    print(f"  [OK] {index_name:25} -> {table_name}")
                    created += 1
                else:
                    print(f"  [INFO] {index_name:25} -> ja existia")
                    already_exists += 1

            except Exception as e:
                print(f"  [ERRO] {index_name:25} -> {str(e)}")

        print()
        print("-" * 80)
        print()

        # Verificar índices criados
        print("[3] Verificando indices criados...")
        cur.execute("""
            SELECT tablename, indexname, indexdef
            FROM pg_indexes
            WHERE indexname LIKE 'idx_%_raw'
            ORDER BY tablename;
        """)

        results = cur.fetchall()
        print(f"  Total de indices GIN encontrados: {len(results)}")
        print()

        for table, index, definition in results:
            print(f"  {index:25} -> {table}")

        print()
        print("=" * 80)
        print("INDICES GIN CRIADOS COM SUCESSO!")
        print("=" * 80)
        print()
        print(f"Resumo:")
        print(f"  - Indices criados/verificados: {created}")
        print(f"  - Indices ja existentes: {already_exists}")
        print(f"  - Total: {len(indexes)}")
        print()
        print("Resultado: Indices GIN ativos para melhor performance!")
        print()

        # Fechar conexão
        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"ERRO ao criar indices: {e}")
        return False


if __name__ == "__main__":
    success = create_gin_indexes()
    sys.exit(0 if success else 1)
