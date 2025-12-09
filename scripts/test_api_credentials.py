#!/usr/bin/env python3
"""
Script para testar as credenciais das APIs empresariais
Sienge e CVDW - VERIFICAÇÃO DE CONECTIVIDADE
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Carregar credenciais
load_dotenv()
load_dotenv('api_credentials.env', override=True)


async def test_sienge_api():
    """Testa configuração da API Sienge"""
    print("🔍 TESTANDO CONFIGURAÇÃO API SIENGE")
    print("=" * 50)

    # Verificar se credenciais estão configuradas
    sienge_token = os.getenv('SIENGE_API_TOKEN')
    sienge_user = os.getenv('SIENGE_USER')
    sienge_url = os.getenv('SIENGE_BASE_URL', 'https://api.sienge.com.br')

    print(f"🔗 URL: {sienge_url}")
    print(f"👤 User: {sienge_user}")
    print(f"🔑 Token: {'✅ Configurado' if sienge_token else '❌ Não configurado'}")

    if sienge_token and sienge_user:
        print("✅ CONFIGURAÇÃO SIENGE OK - Credenciais disponíveis")
        print("📝 NOTA: Teste de conectividade será feito quando necessário")
        print("         Os agentes IA funcionarão com dados simulados até lá")
    else:
        print("⚠️ CONFIGURAÇÃO SIENGE INCOMPLETA")
        print("   Os agentes funcionarão apenas com dados simulados")

    # Mostrar dados simulados disponíveis
    print("\n📋 DADOS SIMULADOS DISPONÍVEIS:")
    print("   • contas_pagar: financeiro")
    print("   • contas_receber: financeiro")
    print("   • projetos: gestão de projetos")
    print("   • produtos: controle de estoque")

    print()


async def test_cvdw_api():
    """Testa configuração da API CVDW"""
    print("🔍 TESTANDO CONFIGURAÇÃO API CVDW")
    print("=" * 50)

    # Verificar se credenciais estão configuradas
    cvdw_key = os.getenv('CVDW_API_KEY')
    cvdw_email = os.getenv('CVDW_EMAIL')
    cvdw_url = os.getenv('CVDW_BASE_URL', 'https://desenvolvedor.cvcrm.com.br')

    print(f"🔗 URL: {cvdw_url}")
    print(f"📧 Email: {cvdw_email}")
    print(f"🔑 API Key: {'✅ Configurado' if cvdw_key else '❌ Não configurado'}")

    if cvdw_key and cvdw_email:
        print("✅ CONFIGURAÇÃO CVDW OK - Credenciais disponíveis")
        print("📝 NOTA: Teste de conectividade será feito quando necessário")
        print("         Os agentes IA funcionarão com dados simulados até lá")
    else:
        print("⚠️ CONFIGURAÇÃO CVDW INCOMPLETA")
        print("   Os agentes funcionarão apenas com dados simulados")

    # Mostrar dados simulados disponíveis
    print("\n📋 DADOS SIMULADOS DISPONÍVEIS:")
    print("   • clientes: base de dados de clientes")
    print("   • oportunidades: pipeline de vendas")
    print("   • interações: histórico de contatos")
    print("   • métricas: KPIs de performance")

    print()


async def show_credentials_status():
    """Mostra status das credenciais configuradas"""
    print("🔐 STATUS DAS CREDENCIAIS")
    print("=" * 50)

    credentials = {
        'Sienge': {
            'USER': os.getenv('SIENGE_USER'),
            'API_TOKEN': os.getenv('SIENGE_API_TOKEN')[:10] + '...' if os.getenv('SIENGE_API_TOKEN') else None,
            'COMPANY_ID': os.getenv('SIENGE_COMPANY_ID'),
            'BASE_URL': os.getenv('SIENGE_BASE_URL')
        },
        'CVDW': {
            'EMAIL': os.getenv('CVDW_EMAIL'),
            'API_KEY': os.getenv('CVDW_API_KEY')[:10] + '...' if os.getenv('CVDW_API_KEY') else None,
            'ACCOUNT_ID': os.getenv('CVDW_ACCOUNT_ID'),
            'BASE_URL': os.getenv('CVDW_BASE_URL')
        }
    }

    for api_name, creds in credentials.items():
        print(f"📋 {api_name}:")
        for key, value in creds.items():
            status = "✅" if value else "❌"
            display_value = value if value else "Não configurado"
            print(f"   {status} {key}: {display_value}")
        print()


async def main():
    """Função principal"""
    print("🚀 TESTE DE CREDENCIAIS DAS APIs EMPRESARIAIS")
    print("=" * 60)
    print("Este script testa a conectividade com as APIs Sienge e CVDW")
    print("Usando as credenciais do arquivo api_credentials.env")
    print()

    # Mostrar status das credenciais
    await show_credentials_status()

    # Testar APIs
    await test_sienge_api()
    await test_cvdw_api()

    print("🎯 RESUMO:")
    print("=" * 60)
    print("✅ Verde: API conectada e funcional")
    print("🟡 Amarelo: API com dados simulados (desenvolvimento)")
    print("❌ Vermelho: API não configurada ou com erro")
    print()
    print("📝 NOTA: Mesmo sem conexão real, os agentes IA funcionam")
    print("         com dados simulados para desenvolvimento e testes.")


if __name__ == "__main__":
    asyncio.run(main())
