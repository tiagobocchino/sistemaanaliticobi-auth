"""
Script simplificado de diagnostico para dashboards Power BI
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def test():
    print("="* 80)
    print("DIAGNOSTICO: DASHBOARDS POWER BI")
    print("=" * 80)

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 1. Verificar usuarios
    print("\n1. USUARIOS NO BANCO:")
    print("-" * 80)

    # Teste 1: Query simples
    result = supabase.table('usuarios').select('id, email, nome, cargo_id, divisao_id').execute()

    if result.data:
        for user in result.data:
            email = user.get('email', '')
            masked_email = f"{email[:3]}...@{email.split('@')[1]}" if '@' in email else f"{email[:3]}..."
            print(f"\nUsuario: {masked_email}")
            print(f"  ID: {user.get('id')}")
            print(f"  Cargo ID: {user.get('cargo_id')}")
            print(f"  Divisao ID: {user.get('divisao_id')}")
    else:
        print("Nenhum usuario encontrado!")

    # 2. Verificar cargos
    print("\n\n2. CARGOS DISPONIVEIS:")
    print("-" * 80)

    cargos_result = supabase.table('cargos').select('*').execute()

    if cargos_result.data:
        for cargo in cargos_result.data:
            print(f"\nCargo: {cargo.get('nome')}")
            print(f"  ID: {cargo.get('id')}")
            print(f"  Nivel: {cargo.get('nivel_acesso')}")
    else:
        print("Nenhum cargo encontrado!")

    # 3. Verificar divisoes
    print("\n\n3. DIVISOES DISPONIVEIS:")
    print("-" * 80)

    divisoes_result = supabase.table('divisoes').select('*').execute()

    if divisoes_result.data:
        for divisao in divisoes_result.data:
            print(f"\nDivisao: {divisao.get('nome')}")
            print(f"  ID: {divisao.get('id')}")
            print(f"  Codigo: {divisao.get('codigo')}")
    else:
        print("Nenhuma divisao encontrada!")

    # 4. Teste de LEFT JOIN
    print("\n\n4. TESTE DE LEFT JOIN:")
    print("-" * 80)

    try:
        # Sintaxe correta para PostgREST
        join_result = supabase.table('usuarios').select('''
            id, email, nome, cargo_id, divisao_id,
            cargos(id, nome, nivel_acesso),
            divisoes(id, nome, codigo)
        ''').execute()

        if join_result.data:
            for user in join_result.data:
                email = user.get('email', '')
                masked_email = f"{email[:3]}...@{email.split('@')[1]}" if '@' in email else f"{email[:3]}..."
                print(f"\nUsuario: {masked_email}")

                cargo = user.get('cargos')
                if cargo:
                    print(f"  Cargo: {cargo.get('nome')} (nivel {cargo.get('nivel_acesso')})")
                else:
                    print("  Cargo: NAO ATRIBUIDO")

                divisao = user.get('divisoes')
                if divisao:
                    print(f"  Divisao: {divisao.get('nome')} ({divisao.get('codigo')})")
                else:
                    print("  Divisao: NAO ATRIBUIDA")
        else:
            print("ERRO: Nenhum dado retornado no LEFT JOIN!")

    except Exception as e:
        print(f"ERRO no LEFT JOIN: {e}")

    # 5. Teste com usuario especifico
    print("\n\n5. TESTE COM USUARIO ESPECIFICO:")
    print("-" * 80)

    if result.data and len(result.data) > 0:
        user_id = result.data[0].get('id')
        print(f"Testando com usuario ID: {user_id}")

        try:
            single_result = supabase.table('usuarios').select('''
                id, email, nome, cargo_id, divisao_id,
                cargos(id, nome, nivel_acesso),
                divisoes(id, nome, codigo)
            ''').eq('id', user_id).single().execute()

            if single_result.data:
                user_data = single_result.data
                print(f"\nDados retornados:")
                print(f"  Email: {user_data.get('email')}")

                cargo = user_data.get('cargos')
                print(f"  Cargo: {cargo}")

                divisao = user_data.get('divisoes')
                print(f"  Divisao: {divisao}")

                # Calcular permissoes
                nivel_acesso = cargo.get('nivel_acesso', 0) if cargo else 0
                codigo_divisao = divisao.get('codigo') if divisao else None

                print(f"\nPermissoes calculadas:")
                print(f"  Nivel de acesso: {nivel_acesso}")
                print(f"  Codigo da divisao: {codigo_divisao}")
                print(f"  Pode acessar tudo: {nivel_acesso >= 4}")

                # Verificar quais dashboards pode acessar
                print(f"\nDashboards acessiveis:")

                # Dashboard Compras (FIN, nivel 4+)
                if nivel_acesso >= 4 and codigo_divisao == 'FIN':
                    print("  - Compras: SIM (divisao FIN)")
                elif nivel_acesso >= 4:
                    print("  - Compras: SIM (nivel alto)")
                else:
                    print("  - Compras: NAO")

                # Dashboard SDRs (COM, nivel 4+)
                if nivel_acesso >= 4 and codigo_divisao == 'COM':
                    print("  - SDRs: SIM (divisao COM)")
                elif nivel_acesso >= 4:
                    print("  - SDRs: SIM (nivel alto)")
                else:
                    print("  - SDRs: NAO")

                # Dashboard Pastas (COM, nivel 4+)
                if nivel_acesso >= 4 and codigo_divisao == 'COM':
                    print("  - Pastas: SIM (divisao COM)")
                elif nivel_acesso >= 4:
                    print("  - Pastas: SIM (nivel alto)")
                else:
                    print("  - Pastas: NAO")

        except Exception as e:
            print(f"ERRO ao buscar usuario: {e}")

    print("\n" + "=" * 80)
    print("DIAGNOSTICO COMPLETO!")
    print("=" * 80)


if __name__ == "__main__":
    test()
