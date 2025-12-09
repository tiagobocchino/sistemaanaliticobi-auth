#!/usr/bin/env python3
"""
Reset user password via Supabase Admin API
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def reset_user_password(email: str, new_password: str):
    """Reset password for a user via Supabase Admin API"""

    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("❌ SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não configurados")
        return False

    # First, get user by email
    get_user_url = f"{SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }

    # Get user ID by email
    response = requests.get(get_user_url, headers=headers, params={"email": email})
    if response.status_code != 200:
        print(f"❌ Erro ao buscar usuário {email}: {response.status_code}")
        return False

    users = response.json()
    if not users.get('users') or len(users['users']) == 0:
        print(f"❌ Usuário {email} não encontrado")
        return False

    user_id = users['users'][0]['id']
    print(f"✅ Usuário encontrado: {email} (ID: {user_id})")

    # Reset password
    update_url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
    update_data = {
        "password": new_password
    }

    response = requests.put(update_url, headers=headers, json=update_data)
    if response.status_code == 200:
        print(f"✅ Senha resetada com sucesso para {email}")
        return True
    else:
        print(f"❌ Erro ao resetar senha para {email}: {response.status_code} - {response.text}")
        return False

def main():
    """Main function"""
    print("🔑 RESETANDO SENHAS DOS USUÁRIOS")
    print("=" * 50)

    new_password = os.getenv("ADMIN_PASSWORD", "Admin123!@#")

    users = [
        "tiago.bocchino@4pcapital.com.br",
        "tiago.bocchino@gmail.com"
    ]

    success_count = 0
    for email in users:
        if reset_user_password(email, new_password):
            success_count += 1

    print("=" * 50)
    if success_count == len(users):
        print(f"🎉 SUCESSO: {success_count}/{len(users)} senhas resetadas!")
        print(f"📧 NOVA SENHA: {'*' * len(new_password)} (oculta por segurança)")
        print("\nPara fazer login:")
        print("1. Acesse: http://localhost:5173/login")
        print(f"2. Use a senha: {'*' * len(new_password)} (oculta por segurança)")
        print("3. Teste os dashboards: http://localhost:5173/analyses")
    else:
        print(f"❌ FALHA: Apenas {success_count}/{len(users)} senhas resetadas")

if __name__ == "__main__":
    main()
