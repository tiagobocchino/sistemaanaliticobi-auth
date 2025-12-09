"""
Script de diagnóstico para verificar dashboards Power BI
"""
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from src.analyses.service import AnalysisService
from src.analyses.powerbi_dashboards import PowerBIDashboards

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


async def test_dashboards():
    """Test Power BI dashboards configuration and access"""

    print("=" * 80)
    print("DIAGNÓSTICO: DASHBOARDS POWER BI")
    print("=" * 80)

    # 1. Verificar configuração dos dashboards
    print("\n1. CONFIGURAÇÃO DOS DASHBOARDS:")
    print("-" * 80)
    all_dashboards = PowerBIDashboards.get_all_dashboards()
    for key, dashboard in all_dashboards.items():
        print(f"\n  Dashboard: {key}")
        print(f"    Nome: {dashboard['nome']}")
        print(f"    Descrição: {dashboard['descricao']}")
        print(f"    URL: {dashboard['embed_url'][:80]}...")
        print(f"    Divisões permitidas: {dashboard['divisoes_permitidas']}")
        print(f"    Nível mínimo: {dashboard['nivel_acesso_minimo']}")

    # 2. Verificar usuários no banco
    print("\n\n2. USUÁRIOS NO BANCO DE DADOS:")
    print("-" * 80)

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Buscar todos os usuários
    result = supabase.table('usuarios').select(
        'id, email, nome, cargo_id, divisao_id, cargos(nome, nivel_acesso), divisoes(nome, codigo)'
    ).execute()

    if result.data:
        for user in result.data:
            email = user.get('email', '')
            masked_email = f"{email[:3]}...@{email.split('@')[1]}" if '@' in email else f"{email[:3]}..."
            print(f"\n  Usuário: {masked_email}")
            print(f"    ID: {user.get('id')}")
            print(f"    Nome: {user.get('nome')}")
            print(f"    Cargo ID: {user.get('cargo_id')}")

            cargo = user.get('cargos')
            if cargo:
                print(f"    Cargo: {cargo.get('nome')} (nível {cargo.get('nivel_acesso')})")
            else:
                print(f"    Cargo: ⚠️ NÃO ATRIBUÍDO")

            print(f"    Divisão ID: {user.get('divisao_id')}")

            divisao = user.get('divisoes')
            if divisao:
                print(f"    Divisão: {divisao.get('nome')} ({divisao.get('codigo')})")
            else:
                print(f"    Divisão: ⚠️ NÃO ATRIBUÍDA")
    else:
        print("  ⚠️ Nenhum usuário encontrado no banco!")

    # 3. Testar permissões para cada usuário
    print("\n\n3. DASHBOARDS ACESSÍVEIS POR USUÁRIO:")
    print("-" * 80)

    service = AnalysisService()

    if result.data:
        for user in result.data:
            user_id = user.get('id')
            email = user.get('email')

            print(f"\n  Usuário: {email}")

            # Obter permissões
            try:
                permissions = await service.get_user_permissions(user_id)
                print(f"    Permissões: {permissions}")

                # Obter dashboards acessíveis
                dashboards = await service.get_powerbi_dashboards_for_user(user_id)

                if dashboards:
                    print(f"    ✅ Dashboards acessíveis ({len(dashboards)}):")
                    for key, dashboard in dashboards.items():
                        print(f"      - {key}: {dashboard['nome']}")
                else:
                    print(f"    ⚠️ NENHUM dashboard acessível!")
                    print(f"    Motivo: Verifique cargo e divisão do usuário")

            except Exception as e:
                print(f"    ❌ Erro ao obter permissões: {e}")

    # 4. Verificar dados na tabela analyses
    print("\n\n4. DADOS NA TABELA 'analyses':")
    print("-" * 80)

    analyses_result = supabase.table('analyses').select('*').execute()

    if analyses_result.data:
        print(f"  Total de análises no banco: {len(analyses_result.data)}")
        for analysis in analyses_result.data:
            print(f"\n  Análise: {analysis.get('nome')}")
            print(f"    ID: {analysis.get('id')}")
            print(f"    Tipo: {analysis.get('tipo')}")
            print(f"    Público: {analysis.get('publico')}")
            print(f"    Divisão restrita: {analysis.get('divisao_restrita_id')}")
    else:
        print("  ℹ️ Nenhuma análise encontrada na tabela 'analyses'")
        print("  (Isso é normal - dashboards Power BI vêm do código, não do banco)")

    # 5. Sugestões
    print("\n\n5. SUGESTÕES:")
    print("-" * 80)

    if result.data:
        for user in result.data:
            cargo = user.get('cargos')
            divisao = user.get('divisoes')

            if not cargo:
                email = user.get('email', '')
                masked_email = f"{email[:3]}...@{email.split('@')[1]}" if '@' in email else f"{email[:3]}..."
                print(f"  ⚠️ {masked_email}: Atribua um cargo ao usuário")
                print(f"     SQL: UPDATE usuarios SET cargo_id = 5 WHERE email = '{email}'; -- Admin")

            if not divisao:
                print(f"  ⚠️ {masked_email}: Atribua uma divisão ao usuário")
                print(f"     SQL: UPDATE usuarios SET divisao_id = 3 WHERE email = '{email}'; -- FIN")
                print(f"     SQL: UPDATE usuarios SET divisao_id = 4 WHERE email = '{email}'; -- COM")

    print("\n" + "=" * 80)
    print("DIAGNÓSTICO COMPLETO!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_dashboards())
