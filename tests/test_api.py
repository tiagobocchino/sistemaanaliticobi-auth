"""
Script para testar a API de autenticação
Execute: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Helper para imprimir respostas formatadas"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_auth_flow():
    """Testa o fluxo completo de autenticação"""

    # Dados de teste
    test_user = {
        "email": "teste@exemplo.com",
        "password": "senha123456",
        "full_name": "Usuário Teste"
    }

    print("🚀 Iniciando testes da API de Autenticação...")

    # 1. Health Check
    print("\n1️⃣ Testando Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("HEALTH CHECK", response)

    # 2. Registro de usuário
    print("\n2️⃣ Registrando novo usuário...")
    response = requests.post(
        f"{BASE_URL}/auth/signup",
        json=test_user
    )
    print_response("SIGN UP", response)

    if response.status_code == 201:
        data = response.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        print(f"\n✅ Usuário registrado com sucesso!")
        print(f"Access Token: {access_token[:50]}...")
    else:
        print("\n❌ Erro no registro. Tentando fazer login...")

        # 3. Login (caso o usuário já exista)
        print("\n3️⃣ Fazendo login...")
        response = requests.post(
            f"{BASE_URL}/auth/signin",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        print_response("SIGN IN", response)

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            print(f"\n✅ Login realizado com sucesso!")
        else:
            print("\n❌ Erro no login. Encerrando testes.")
            return

    # 4. Obter dados do usuário
    print("\n4️⃣ Obtendo dados do usuário autenticado...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print_response("GET USER", response)

    # 5. Acessar rota protegida
    print("\n5️⃣ Acessando rota protegida...")
    response = requests.get(f"{BASE_URL}/protected", headers=headers)
    print_response("PROTECTED ROUTE", response)

    # 6. Renovar token
    print("\n6️⃣ Renovando token...")
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    print_response("REFRESH TOKEN", response)

    if response.status_code == 200:
        new_access_token = response.json().get("access_token")
        print(f"\n✅ Token renovado com sucesso!")
        access_token = new_access_token

    # 7. Logout
    print("\n7️⃣ Fazendo logout...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(f"{BASE_URL}/auth/signout", headers=headers)
    print_response("SIGN OUT", response)

    # 8. Tentar acessar rota protegida após logout
    print("\n8️⃣ Tentando acessar rota protegida após logout...")
    response = requests.get(f"{BASE_URL}/protected", headers=headers)
    print_response("PROTECTED ROUTE (após logout)", response)

    print("\n" + "="*60)
    print("✅ Testes concluídos!")
    print("="*60)


if __name__ == "__main__":
    try:
        test_auth_flow()
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro: Não foi possível conectar à API.")
        print("Certifique-se de que o servidor está rodando:")
        print("  python main.py")
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {str(e)}")
