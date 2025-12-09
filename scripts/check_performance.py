"""
Teste de performance do backend
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_performance():
    print("=" * 80)
    print("TESTE DE PERFORMANCE DO BACKEND")
    print("=" * 80)

    # 1. Health check
    print("\n1. HEALTH CHECK (deve ser instantaneo):")
    print("-" * 80)

    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        elapsed = time.time() - start

        if response.status_code == 200:
            print(f"OK - {elapsed:.3f} segundos")
            if elapsed > 1:
                print("  AVISO: Health check lento (deveria ser < 0.1s)")
        else:
            print(f"ERRO: Status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("ERRO: Backend NAO esta rodando!")
        print("Execute: python main.py")
        return
    except Exception as e:
        print(f"ERRO: {e}")
        return

    # 2. Login
    print("\n2. LOGIN (deve ser rapido, < 2s):")
    print("-" * 80)

    login_data = {
        "email": "tiago.bocchino@4pcapital.com.br",
        "password": "Admin123!@#"
    }

    start = time.time()
    try:
        response = requests.post(f"{BASE_URL}/auth/signin", json=login_data, timeout=10)
        elapsed = time.time() - start

        if response.status_code == 200:
            print(f"OK - {elapsed:.3f} segundos")
            if elapsed > 2:
                print("  AVISO: Login lento (deveria ser < 2s)")

            data = response.json()
            access_token = data.get("access_token")
        else:
            print(f"ERRO: Status {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"ERRO: {e}")
        return

    # 3. Buscar dashboards Power BI
    print("\n3. BUSCAR DASHBOARDS POWER BI (pode demorar 1-3s):")
    print("-" * 80)

    headers = {"Authorization": f"Bearer {access_token}"}

    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/analyses/powerbi-dashboards", headers=headers, timeout=10)
        elapsed = time.time() - start

        if response.status_code == 200:
            dashboards = response.json()
            print(f"OK - {elapsed:.3f} segundos")
            print(f"  Dashboards retornados: {len(dashboards)}")

            if elapsed > 3:
                print("  AVISO: Busca de dashboards lenta (deveria ser < 3s)")
                print("  Isso pode ser normal se o banco estiver distante")
        else:
            print(f"ERRO: Status {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"ERRO: {e}")
        return

    # 4. Buscar analyses do banco
    print("\n4. BUSCAR ANALYSES DO BANCO (deve ser rapido, < 1s):")
    print("-" * 80)

    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/analyses", headers=headers, timeout=10)
        elapsed = time.time() - start

        if response.status_code == 200:
            analyses = response.json()
            print(f"OK - {elapsed:.3f} segundos")
            print(f"  Analyses retornadas: {len(analyses)}")

            if elapsed > 1:
                print("  AVISO: Busca de analyses lenta (deveria ser < 1s)")
        else:
            print(f"ERRO: Status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"ERRO: {e}")

    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO:")
    print("=" * 80)
    print("Se todos os testes foram OK em menos de 5s total:")
    print("  -> O BACKEND esta RAPIDO!")
    print("\nSe a demora esta no NAVEGADOR:")
    print("  -> Pode ser o iframe do Power BI carregando (normal)")
    print("  -> Dashboards Power BI podem demorar 5-15s para carregar")
    print("=" * 80)


if __name__ == "__main__":
    test_performance()
