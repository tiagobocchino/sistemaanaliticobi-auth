#!/usr/bin/env python3
"""
Teste rápido do chat com agentes IA
"""
import requests
import json

def test_chat():
    # Login
    login_data = {
        'email': 'tiago.bocchino@4pcapital.com.br',
        'password': 'Admin123!@#'
    }

    print('🤖 TESTANDO CHAT COM AGENTES IA')
    print('=' * 50)

    login_response = requests.post('http://localhost:8000/auth/signin', json=login_data)

    if login_response.status_code != 200:
        print(f'❌ Login falhou: {login_response.status_code}')
        return

    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print('✅ Login realizado!')

    # Teste 1: Pergunta sobre dashboards
    print('\n1️⃣ Teste: "Quais dashboards eu posso acessar?"')
    chat_data = {'message': 'Quais dashboards eu posso acessar?'}
    response = requests.post('http://localhost:8000/agents/chat', json=chat_data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print('✅ Resposta do agente:')
        print(f'   💬 "{result["message"][:150]}..."')
        print(f'   📊 Confiança: {result["confidence"]}')
        print(f'   🎯 Fonte: {result["data_source"]}')
    else:
        print(f'❌ Erro no chat: {response.status_code}')
        print(f'   Resposta: {response.text}')

    # Teste 2: Pergunta sobre vendas
    print('\n2️⃣ Teste: "Como estão as vendas este mês?"')
    chat_data2 = {'message': 'Como estão as vendas este mês?'}
    response2 = requests.post('http://localhost:8000/agents/chat', json=chat_data2, headers=headers)

    if response2.status_code == 200:
        result2 = response2.json()
        print('✅ Resposta do agente:')
        print(f'   💬 "{result2["message"][:150]}..."')
        print(f'   📊 Confiança: {result2["confidence"]}')
        print(f'   🎯 Fonte: {result2["data_source"]}')
    else:
        print(f'❌ Erro no chat: {response2.status_code}')

    print('\n🎯 Teste concluído!')

if __name__ == "__main__":
    test_chat()
