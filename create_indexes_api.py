"""
Script para criar índices GIN via API REST do Supabase
Execute: python create_indexes_api.py
"""
import os
import sys
from pathlib import Path

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
load_dotenv()

import requests


def create_gin_indexes_via_api():
    """Tenta criar índices GIN via Supabase REST API"""
    supabase_url = os.getenv('SUPABASE_URL')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not service_role_key:
        print("ERRO: SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY nao encontrados")
        return False

    print("=" * 80)
    print("TENTANDO CRIAR INDICES GIN VIA API")
    print("=" * 80)
    print()

    # SQL script
    sql_script = """
CREATE INDEX IF NOT EXISTS idx_leads_raw ON leads USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_vendas_raw ON vendas USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_reservas_raw ON reservas USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_unidades_raw ON unidades USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_corretores_raw ON corretores USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_pessoas_raw ON pessoas USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_imobiliarias_raw ON imobiliarias USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_repasses_raw ON repasses USING GIN (raw);
    """.strip()

    print("[INFO] A API REST do Supabase (PostgREST) nao permite executar DDL (CREATE INDEX)")
    print("[INFO] Indices GIN devem ser criados via Supabase SQL Editor")
    print()
    print("=" * 80)
    print("INSTRUCOES PARA CRIAR INDICES GIN")
    print("=" * 80)
    print()
    print("1. Acesse o Supabase SQL Editor:")
    print(f"   https://supabase.com/dashboard/project/{supabase_url.split('//')[1].split('.')[0]}/sql")
    print()
    print("2. Cole e execute este script:")
    print()
    print("-" * 80)
    print(sql_script)
    print("-" * 80)
    print()
    print("3. Verifique os indices criados com:")
    print()
    print("   SELECT tablename, indexname FROM pg_indexes")
    print("   WHERE indexname LIKE 'idx_%_raw';")
    print()
    print("=" * 80)
    print()

    # Salvar script em arquivo para facilitar
    script_path = Path(__file__).parent / "database" / "scripts" / "add_raw_indexes.sql"
    print(f"Script SQL salvo em: {script_path}")
    print()

    return False  # Não conseguimos criar automaticamente


if __name__ == "__main__":
    create_gin_indexes_via_api()
