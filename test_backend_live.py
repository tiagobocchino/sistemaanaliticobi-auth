"""
Teste ao vivo do backend - verifica se esta rodando e se retorna dashboards
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_backend():
    print("=" * 80)
    print("TESTE AO VIVO DO BACKEND")
    print("=" * 80)

    # 1. Verificar se backend esta rodando
    print("\n1. VERIFICANDO SE BACKEND ESTA RODANDO...")
    print("-" * 80)

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        if response.status_code == 200:
            print("Backend RODANDO!")
            print(f"Resposta: {response.json()}")
        else:
            print(f"Backend respondeu com status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("ERRO: Backend NAO esta rodando!")
        print("\nPor favor, inicie o backend com:")
        print("  python main.py")
        return
    except Exception as e:
        print(f"ERRO ao conectar: {e}")
        return

    # 2. Fazer login
    print("\n2. FAZENDO LOGIN...")
    print("-" * 80)

    login_data = {
        "email": "tiago.bocchino@4pcapital.com.br",
        "password": "Admin123!@#"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/signin", json=login_data)

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print("Login OK!")
        else:
            print(f"ERRO no login: {response.status_code}")
            print(response.text)
            return

    except Exception as e:
        print(f"ERRO ao fazer login: {e}")
        return

    # 3. Buscar dashboards Power BI
    print("\n3. BUSCANDO DASHBOARDS POWER BI...")
    print("-" * 80)

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(f"{BASE_URL}/analyses/powerbi-dashboards", headers=headers)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            dashboards = response.json()
            print(f"\nDASHBOARDS RETORNADOS: {len(dashboards)}")

            if dashboards:
                print("\n" + "=" * 80)
                print("SUCESSO! DASHBOARDS ENCONTRADOS:")
                print("=" * 80)

                for key, dashboard in dashboards.items():
                    print(f"\nDashboard: {key}")
                    print(f"  Nome: {dashboard.get('nome')}")
                    print(f"  Descricao: {dashboard.get('descricao')}")
                    print(f"  URL: {dashboard.get('embed_url')[:60]}...")

                print("\n" + "=" * 80)
                print("DASHBOARD DEVEM APARECER NO FRONTEND!")
                print("=" * 80)
            else:
                print("\n" + "=" * 80)
                print("PROBLEMA: NENHUM DASHBOARD RETORNADO!")
                print("=" * 80)
                print("\nPossiveis causas:")
                print("  1. Backend nao foi reiniciado apos a correcao")
                print("  2. Usuario nao tem permissoes")
                print("\nSolucao:")
                print("  1. REINICIE o backend (Ctrl+C e python main.py)")
                print("  2. Aguarde 5 segundos")
                print("  3. Execute este script novamente")

        else:
            print(f"ERRO: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"ERRO ao buscar dashboards: {e}")

    # 4. Buscar analyses do banco
    print("\n\n4. BUSCANDO ANALYSES DO BANCO...")
    print("-" * 80)

    try:
        response = requests.get(f"{BASE_URL}/analyses", headers=headers)

        if response.status_code == 200:
            analyses = response.json()
            print(f"Analyses retornadas do banco: {len(analyses)}")

            if analyses:
                for analysis in analyses:
                    print(f"  - {analysis.get('nome')} ({analysis.get('tipo')})")
            else:
                print("  (Nenhuma analysis no banco - isto e NORMAL)")
                print("  (Dashboards Power BI vem do codigo, nao do banco)")
        else:
            print(f"ERRO: {response.status_code}")

    except Exception as e:
        print(f"ERRO: {e}")

    print("\n" + "=" * 80)
    print("TESTE COMPLETO!")
    print("=" * 80)


if __name__ == "__main__":
    test_backend()
