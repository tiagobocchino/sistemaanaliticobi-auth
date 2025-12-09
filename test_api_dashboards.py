"""
Teste rapido da API de dashboards
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 80)
    print("TESTE DA API - DASHBOARDS POWER BI")
    print("=" * 80)

    # 1. Login
    print("\n1. FAZENDO LOGIN...")
    print("-" * 80)

    login_data = {
        "email": "tiago.bocchino@4pcapital.com.br",
        "password": "Master123#"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/signin", json=login_data)

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print("Login OK!")
            print(f"Token obtido: {access_token[:50]}...")
        else:
            print(f"ERRO no login: {response.status_code}")
            print(response.text)
            return

    except Exception as e:
        print(f"ERRO ao fazer login: {e}")
        return

    # 2. Buscar dashboards Power BI
    print("\n\n2. BUSCANDO DASHBOARDS POWER BI...")
    print("-" * 80)

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(f"{BASE_URL}/analyses/powerbi-dashboards", headers=headers)

        if response.status_code == 200:
            dashboards = response.json()
            print(f"Dashboards retornados: {len(dashboards)}")

            if dashboards:
                for key, dashboard in dashboards.items():
                    print(f"\nDashboard: {key}")
                    print(f"  Nome: {dashboard.get('nome')}")
                    print(f"  Descricao: {dashboard.get('descricao')}")
                    print(f"  URL: {dashboard.get('embed_url')[:80]}...")
            else:
                print("NENHUM dashboard retornado!")
                print("Verifique as permissoes do usuario")
        else:
            print(f"ERRO ao buscar dashboards: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"ERRO ao buscar dashboards: {e}")

    # 3. Buscar analyses
    print("\n\n3. BUSCANDO ANALYSES...")
    print("-" * 80)

    try:
        response = requests.get(f"{BASE_URL}/analyses", headers=headers)

        if response.status_code == 200:
            analyses = response.json()
            print(f"Analyses retornadas: {len(analyses)}")

            if analyses:
                for analysis in analyses:
                    print(f"\nAnalysis: {analysis.get('nome')}")
                    print(f"  ID: {analysis.get('id')}")
                    print(f"  Tipo: {analysis.get('tipo')}")
            else:
                print("Nenhuma analysis retornada")
        else:
            print(f"ERRO ao buscar analyses: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"ERRO ao buscar analyses: {e}")

    # 4. Debug do usuario
    print("\n\n4. DEBUG DO USUARIO...")
    print("-" * 80)

    try:
        response = requests.get(f"{BASE_URL}/analyses/debug-user", headers=headers)

        if response.status_code == 200:
            debug_data = response.json()
            print(json.dumps(debug_data, indent=2))
        else:
            print(f"ERRO no debug: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"ERRO no debug: {e}")

    print("\n" + "=" * 80)
    print("TESTE COMPLETO!")
    print("=" * 80)


if __name__ == "__main__":
    test_api()
