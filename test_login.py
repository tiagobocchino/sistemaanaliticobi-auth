"""
Teste rapido de login
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # Usar anon key para login

def test_login():
    print("=" * 80)
    print("TESTE DE LOGIN")
    print("=" * 80)

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    email = os.getenv("TEST_USER_EMAIL", "tiago.bocchino@4pcapital.com.br")
    password = os.getenv("TEST_USER_PASSWORD", "Admin123!@#")

    print(f"\nTentando login com:")
    print(f"  Email: {email}")
    print(f"  Senha: {password}")

    try:
        # Fazer login
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if response.user:
            print("\n" + "=" * 80)
            print("LOGIN BEM-SUCEDIDO!")
            print("=" * 80)
            print(f"\nUsuario:")
            print(f"  ID: {response.user.id}")
            print(f"  Email: {response.user.email}")
            print(f"\nToken de acesso:")
            print(f"  {response.session.access_token[:50]}...")
            print(f"\nToken expira em: {response.session.expires_in} segundos")
            print("\n" + "=" * 80)
            print("PODE USAR ESTAS CREDENCIAIS NO SISTEMA!")
            print("=" * 80)
        else:
            print("\nERRO: Login falhou (sem usuario retornado)")

    except Exception as e:
        print(f"\nERRO ao fazer login: {e}")
        print("\nPossiveis causas:")
        print("  1. Senha incorreta")
        print("  2. Email nao confirmado")
        print("  3. Usuario nao existe")
        print("\nTente resetar a senha novamente com:")
        print("  python reset_password.py")


if __name__ == "__main__":
    test_login()
