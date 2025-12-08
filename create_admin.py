import os
from dotenv import load_dotenv
from supabase import create_client, Client

def create_admin_user():
    """
    Cria um usuário administrador no Supabase.
    """
    load_dotenv() # Carrega as variáveis do arquivo .env

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("Erro: SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")
        return

    supabase: Client = create_client(url, key)

    admin_email = os.environ.get("ADMIN_EMAIL", "tiago.bocchino@4pcapital.com.br")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Master123#")
    admin_full_name = os.environ.get("ADMIN_NAME", "Usuário Master")

    print(f"Tentando criar o usuário: {admin_email}...")

    try:
        # 1. Cria o usuário no sistema de autenticação do Supabase
        res = supabase.auth.sign_up({
            "email": admin_email,
            "password": admin_password,
            "options": { "data": { "full_name": admin_full_name } }
        })
        user_id = res.user.id
        print(f"Usuário criado com sucesso! ID: {user_id}")

        # 2. O trigger já criou a linha em public.users. Agora, atualizamos a role.
        print("Atualizando a role para 'admin'...")
        supabase.table("users").update({"role": "admin"}).eq("id", user_id).execute()
        print("Role atualizada para 'admin' com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    create_admin_user()