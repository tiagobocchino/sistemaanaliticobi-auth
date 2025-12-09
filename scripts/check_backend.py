"""
Script para verificar se o backend está rodando e acessível
"""
import requests
import sys
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

def check_backend():
    """Verifica se o backend está rodando"""
    print("=" * 60)
    print("VERIFICAÇÃO DO BACKEND")
    print("=" * 60)
    print(f"URL da API: {API_URL}")
    print()
    
    # Teste 1: Health check
    print("1. Testando endpoint /health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ BACKEND ESTÁ RODANDO!")
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.json()}")
        else:
            print(f"   ⚠️  Backend respondeu com status: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except requests.exceptions.ConnectionError:
        print("   ❌ ERRO: Não foi possível conectar ao backend!")
        print("   → O backend provavelmente não está rodando")
        print("   → Execute: python main.py")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ ERRO: Timeout ao conectar ao backend")
        return False
    except Exception as e:
        print(f"   ❌ ERRO: {str(e)}")
        return False

    print()
    
    # Teste 2: Root endpoint
    print("2. Testando endpoint /...")
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Root endpoint funcionando!")
            print(f"   Resposta: {response.json()}")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERRO: {str(e)}")
    
    print()
    
    # Teste 3: Verificar variáveis de ambiente
    print("3. Verificando configuração do backend...")
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"   ✅ Arquivo .env encontrado")
        with open(env_file, 'r') as f:
            lines = f.readlines()
            has_url = any('SUPABASE_URL' in line for line in lines)
            has_key = any('SUPABASE_KEY' in line or 'SUPABASE_ANON_KEY' in line for line in lines)
            if has_url and has_key:
                print("   ✅ Variáveis do Supabase configuradas")
            else:
                print("   ⚠️  Variáveis do Supabase podem estar faltando")
    else:
        print("   ❌ Arquivo .env não encontrado!")
        print("   → Crie um arquivo .env na raiz do projeto")
    
    print()
    print("=" * 60)
    print("INSTRUÇÕES:")
    print("=" * 60)
    print("1. Se o backend não estiver rodando:")
    print("   → Abra um terminal na raiz do projeto")
    print("   → Execute: python main.py")
    print()
    print("2. Verifique se a porta 8000 está livre:")
    print("   → Windows: netstat -ano | findstr :8000")
    print("   → Linux/Mac: lsof -i :8000")
    print()
    print("3. Se houver erro de dependências:")
    print("   → pip install -r requirements.txt")
    print()
    print("4. Verifique o arquivo .env:")
    print("   → Deve conter: SUPABASE_URL e SUPABASE_ANON_KEY")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = check_backend()
    sys.exit(0 if success else 1)
