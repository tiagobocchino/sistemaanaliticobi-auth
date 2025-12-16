"""Script para consultar dados RAW das tabelas do Supabase"""
import os
import sys
import json
import argparse
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from supabase import create_client

# Carregar variáveis de ambiente
load_dotenv()

def query_raw(table: str, limit: int = 5, id_column: str = None):
    """
    Consulta dados RAW de uma tabela específica

    Args:
        table: Nome da tabela (ex: corretores, leads, vendas)
        limit: Número máximo de registros a retornar
        id_column: Nome da coluna de ID (ex: idcorretor, idlead)
    """
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        print("ERRO: SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY devem estar no .env")
        return

    supabase = create_client(url, key)

    print(f"\n{'='*80}")
    print(f"CONSULTANDO TABELA: {table}")
    print(f"{'='*80}\n")

    try:
        # Buscar dados com a coluna raw
        if id_column:
            result = supabase.table(table).select(f"{id_column},raw").limit(limit).execute()
        else:
            result = supabase.table(table).select("*").limit(limit).execute()

        if not result.data:
            print(f"Nenhum registro encontrado na tabela {table}")
            return

        print(f"Total de registros retornados: {len(result.data)}\n")

        for i, row in enumerate(result.data, 1):
            print(f"\n{'='*80}")
            print(f"REGISTRO #{i}")
            print(f"{'='*80}")

            # Mostrar ID se disponível
            if id_column and id_column in row:
                print(f"ID ({id_column}): {row[id_column]}")

            # Mostrar dados RAW
            if 'raw' in row and row['raw']:
                print("\nDADOS RAW:")
                try:
                    if isinstance(row['raw'], str):
                        raw_data = json.loads(row['raw'])
                    else:
                        raw_data = row['raw']

                    print(json.dumps(raw_data, indent=2, ensure_ascii=False)[:1500])
                    if len(json.dumps(raw_data)) > 1500:
                        print("\n... (dados truncados)")
                except json.JSONDecodeError:
                    print(row['raw'][:500])
            else:
                print("\nNenhum dado RAW encontrado neste registro")
                # Mostrar outras colunas disponíveis
                print("\nColunas disponiveis:")
                for col in row.keys():
                    if col != 'raw':
                        val = str(row[col])[:100]
                        print(f"  - {col}: {val}")

    except Exception as e:
        print(f"ERRO ao consultar tabela {table}: {e}")
        return

    print(f"\n{'='*80}\n")

def main():
    parser = argparse.ArgumentParser(description='Consulta dados RAW das tabelas do Supabase')
    parser.add_argument('--table', '-t', required=True,
                       choices=['corretores', 'imobiliarias', 'leads', 'pessoas',
                               'repasses', 'reservas', 'unidades', 'vendas'],
                       help='Nome da tabela a consultar')
    parser.add_argument('--limit', '-l', type=int, default=5,
                       help='Número de registros a retornar (padrão: 5)')
    parser.add_argument('--id-column', '-i', type=str,
                       help='Nome da coluna de ID (ex: idcorretor, idlead)')

    args = parser.parse_args()
    query_raw(args.table, args.limit, args.id_column)

if __name__ == "__main__":
    main()
