"""
Teste do fluxo completo de permissoes dos dashboards
"""
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client
from src.analyses.service import AnalysisService
from src.analyses.powerbi_dashboards import PowerBIDashboards

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

async def test_flow():
    print("=" * 80)
    print("TESTE COMPLETO DO FLUXO DE DASHBOARDS")
    print("=" * 80)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 1. Pegar usuario
    user_result = supabase.table('usuarios').select('id, email').limit(1).execute()

    if not user_result.data:
        print("Nenhum usuario encontrado!")
        return

    user_id = user_result.data[0]['id']
    user_email = user_result.data[0]['email']

    print(f"\nTestando com usuario: {user_email}")
    print(f"ID: {user_id}")

    # 2. Verificar dashboards configurados
    print("\n" + "=" * 80)
    print("1. DASHBOARDS CONFIGURADOS NO CODIGO:")
    print("=" * 80)

    all_dashboards = PowerBIDashboards.get_all_dashboards()
    print(f"\nTotal configurados: {len(all_dashboards)}")

    for key, dashboard in all_dashboards.items():
        print(f"\n  [{key}]")
        print(f"    Nome: {dashboard['nome']}")
        print(f"    Divisoes: {dashboard['divisoes_permitidas']}")
        print(f"    Nivel minimo: {dashboard['nivel_acesso_minimo']}")

    # 3. Obter permissoes do usuario
    print("\n" + "=" * 80)
    print("2. PERMISSOES DO USUARIO:")
    print("=" * 80)

    service = AnalysisService()

    try:
        permissions = await service.get_user_permissions(user_id)
        print(f"\nPermissoes retornadas:")
        print(f"  can_access_all: {permissions.get('can_access_all')}")
        print(f"  user_division_code: {permissions.get('user_division_code')}")
        print(f"  user_role_level: {permissions.get('user_role_level')}")
        print(f"  user_division_id: {permissions.get('user_division_id')}")

    except Exception as e:
        print(f"\nERRO ao obter permissoes: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Testar acesso a cada dashboard
    print("\n" + "=" * 80)
    print("3. TESTE DE ACESSO POR DASHBOARD:")
    print("=" * 80)

    for key in all_dashboards.keys():
        can_access = PowerBIDashboards.user_can_access_dashboard(permissions, key)
        status = "SIM" if can_access else "NAO"
        print(f"\n  [{key}]: {status}")

        if not can_access:
            dashboard = all_dashboards[key]
            print(f"    Motivo:")

            # Debug detalhado
            if permissions.get('can_access_all'):
                print(f"      - Usuario tem acesso total (nivel {permissions.get('user_role_level')})")
            else:
                print(f"      - Usuario NAO tem acesso total (nivel {permissions.get('user_role_level')} < 4)")

            user_level = permissions.get('user_role_level', 0)
            min_level = dashboard.get('nivel_acesso_minimo', 5)
            print(f"      - Nivel usuario: {user_level}, Nivel minimo: {min_level}")

            if user_level < min_level:
                print(f"      - BLOQUEADO: Nivel insuficiente")

            user_div = permissions.get('user_division_code')
            allowed_divs = dashboard.get('divisoes_permitidas', [])
            print(f"      - Divisao usuario: {user_div}, Divisoes permitidas: {allowed_divs}")

            if user_div not in allowed_divs:
                print(f"      - BLOQUEADO: Divisao nao permitida")

    # 5. Dashboards acessiveis finais
    print("\n" + "=" * 80)
    print("4. DASHBOARDS ACESSIVEIS (RESULTADO FINAL):")
    print("=" * 80)

    try:
        accessible = await service.get_powerbi_dashboards_for_user(user_id)
        print(f"\nTotal acessiveis: {len(accessible)}")

        if accessible:
            for key, dashboard in accessible.items():
                print(f"\n  [{key}]")
                print(f"    Nome: {dashboard['nome']}")
                print(f"    URL: {dashboard['embed_url'][:60]}...")
        else:
            print("\nNENHUM dashboard acessivel!")
            print("\nDEBUG:")
            print(f"  Permissoes passadas para funcao:")
            print(f"    {permissions}")

    except Exception as e:
        print(f"\nERRO ao obter dashboards acessiveis: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_flow())
