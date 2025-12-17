"""
Responde: Quantos leads ativos temos?
"""
import sys
from pathlib import Path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from src.supabase_client import supabase_admin_client

print("="*80)
print("RESPONDENDO: Quantos leads ativos temos?")
print("="*80)

# Buscar leads ativos
print("\nConsultando tabela 'leads' com filtro ativo='S'...")
result = supabase_admin_client.table("leads")\
    .select("referencia, nome, situacao, data_cad")\
    .eq("ativo", "S")\
    .execute()

total = len(result.data)
print(f"\n{'='*80}")
print(f"RESPOSTA: Voce tem {total} leads ativos")
print(f"{'='*80}")

# Distribuicao por situacao
print("\nDistribuicao por situacao:")
situacoes = {}
for lead in result.data:
    sit = lead.get('situacao', 'Sem situacao')
    situacoes[sit] = situacoes.get(sit, 0) + 1

for sit, count in sorted(situacoes.items(), key=lambda x: x[1], reverse=True):
    percentual = (count / total * 100) if total > 0 else 0
    print(f"  - {sit}: {count} leads ({percentual:.1f}%)")

# Ultimos 5 leads cadastrados
print("\nUltimos 5 leads cadastrados:")
ultimos = sorted(result.data, key=lambda x: x.get('data_cad', ''), reverse=True)[:5]
for lead in ultimos:
    ref = lead.get('referencia', 'N/A')
    nome = lead.get('nome', 'Sem nome')
    sit = lead.get('situacao', 'N/A')
    data = lead.get('data_cad', 'N/A')
    print(f"  - [{ref}] {nome} - {sit} (cadastrado em {data})")

print("\n" + "="*80)
print("Fonte: Tabela 'leads' do Supabase (campo 'raw' com dados completos)")
print("Filtro aplicado: ativo = 'S'")
print("="*80)
