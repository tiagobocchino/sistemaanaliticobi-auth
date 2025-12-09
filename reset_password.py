"""
Script para resetar senha do usuario no Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def reset_password():
    print("=" * 80)
    print("RESET DE SENHA - SUPABASE AUTH")
    print("=" * 80)

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    email = os.getenv("ADMIN_EMAIL", "tiago.bocchino@4pcapital.com.br")
    new_password = os.getenv("ADMIN_PASSWORD", "Admin123!@#")

    print(f"\nEmail: {email}")
    print(f"Nova senha: {'*' * len(new_password)} (oculta por segurança)")

    # 1. Verificar se usuario existe em auth.users
    print("\n1. Verificando usuario em auth.users...")
    print("-" * 80)

    try:
        # Buscar usuario na tabela usuarios (public)
        user_result = supabase.table('usuarios').select('id, email, nome').eq('email', email).execute()

        if user_result.data and len(user_result.data) > 0:
            user = user_result.data[0]
            print(f"Usuario encontrado na tabela usuarios:")
            print(f"  ID: {user.get('id')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Nome: {user.get('nome')}")

            user_id = user.get('id')

            # 2. Resetar senha usando admin API
            print("\n2. Resetando senha...")
            print("-" * 80)

            try:
                # Update user password using admin API
                response = supabase.auth.admin.update_user_by_id(
                    user_id,
                    {"password": new_password}
                )

                print("Senha resetada com sucesso!")
                print(f"\nNOVAS CREDENCIAIS:")
                print(f"  Email: {email}")
                print(f"  Senha: {'*' * len(new_password)} (oculta por segurança)")

            except Exception as e:
                print(f"ERRO ao resetar senha: {e}")
                print("\nTentando metodo alternativo...")

                # Metodo alternativo: enviar email de reset
                try:
                    supabase.auth.reset_password_for_email(email)
                    print(f"Email de reset enviado para {email}")
                    print("Verifique seu email e clique no link para resetar a senha")
                except Exception as e2:
                    print(f"ERRO no metodo alternativo: {e2}")

        else:
            print(f"Usuario nao encontrado com email: {email}")
            print("\nUsuarios disponiveis:")

            all_users = supabase.table('usuarios').select('email, nome').execute()
            for u in all_users.data:
                print(f"  - {u.get('email')}")

    except Exception as e:
        print(f"ERRO: {e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    reset_password()
