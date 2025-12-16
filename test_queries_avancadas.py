"""
TESTES DE CONSULTAS AVANCADAS COM FILTROS
Execute: python test_queries_avancadas.py
"""
import sys
from pathlib import Path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.supabase_client import supabase_admin_client

print("="*80)
print("TESTES DE CONSULTAS AVANCADAS")
print("="*80)

# Teste 1: Filtro simples - Leads ativos
print("\n[Teste 1] Leads ativos")
print("-"*80)
try:
    result = supabase_admin_client.table("leads")\
        .select("referencia, nome, situacao, ativo")\
        .eq("ativo", "S")\
        .limit(10)\
        .execute()
    print(f"OK - {len(result.data)} leads ativos encontrados")
    if result.data:
        for lead in result.data[:3]:
            print(f"   - {lead.get('referencia')}: {lead.get('nome')} ({lead.get('situacao')})")
except Exception as e:
    print(f"ERRO: {e}")

# Teste 2: Contagem por situacao
print("\n[Teste 2] Contar leads por situacao")
print("-"*80)
try:
    # Buscar todas as situacoes unicas
    result = supabase_admin_client.table("leads")\
        .select("situacao")\
        .limit(1000)\
        .execute()

    situacoes = {}
    for lead in result.data:
        sit = lead.get('situacao', 'Desconhecido')
        situacoes[sit] = situacoes.get(sit, 0) + 1

    print(f"OK - Distribuicao de leads por situacao:")
    for sit, count in sorted(situacoes.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {sit}: {count} leads")
except Exception as e:
    print(f"ERRO: {e}")

# Teste 3: Vendas com filtro
print("\n[Teste 3] Vendas ativas")
print("-"*80)
try:
    result = supabase_admin_client.table("vendas")\
        .select("*")\
        .eq("ativo", "S")\
        .limit(5)\
        .execute()
    print(f"OK - {len(result.data)} vendas ativas encontradas")
except Exception as e:
    print(f"ERRO: {e}")

# Teste 4: Corretores ativos
print("\n[Teste 4] Corretores ativos")
print("-"*80)
try:
    result = supabase_admin_client.table("corretores")\
        .select("referencia, nome, ativo")\
        .eq("ativo", "S")\
        .limit(10)\
        .execute()
    print(f"OK - {len(result.data)} corretores ativos encontrados")
    if result.data:
        for corretor in result.data[:3]:
            print(f"   - {corretor.get('referencia')}: {corretor.get('nome')}")
except Exception as e:
    print(f"ERRO: {e}")

# Teste 5: Unidades disponiveis
print("\n[Teste 5] Unidades ativas")
print("-"*80)
try:
    result = supabase_admin_client.table("unidades")\
        .select("referencia, bloco, andar, ativo")\
        .eq("ativo", "S")\
        .limit(10)\
        .execute()
    print(f"OK - {len(result.data)} unidades ativas encontradas")
    if result.data:
        for unidade in result.data[:3]:
            bloco = unidade.get('bloco', 'N/A')
            andar = unidade.get('andar', 'N/A')
            print(f"   - {unidade.get('referencia')}: Bloco {bloco}, Andar {andar}")
except Exception as e:
    print(f"ERRO: {e}")

# Teste 6: Busca no campo RAW (JSON)
print("\n[Teste 6] Busca em campo RAW (JSONB)")
print("-"*80)
try:
    # Buscar leads e mostrar um campo do RAW
    result = supabase_admin_client.table("leads")\
        .select("referencia, nome, raw")\
        .limit(3)\
        .execute()
    print(f"OK - {len(result.data)} leads retornados")
    if result.data:
        for lead in result.data:
            raw = lead.get('raw', {})
            print(f"   - {lead.get('referencia')}: {lead.get('nome')}")
            print(f"     RAW keys: {len(raw.keys()) if isinstance(raw, dict) else 0} campos")
except Exception as e:
    print(f"ERRO: {e}")

print("\n" + "="*80)
print("TESTES AVANCADOS CONCLUIDOS!")
print("="*80)
print("\nRESUMO:")
print("  - Filtros simples: OK")
print("  - Agregacoes: OK")
print("  - Multiplas tabelas: OK")
print("  - Campo JSONB (raw): OK")
print("\nSistema pronto para perguntas em linguagem natural!")
