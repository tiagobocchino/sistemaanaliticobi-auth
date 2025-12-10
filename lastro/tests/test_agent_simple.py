#!/usr/bin/env python3
"""
Teste simples do Agente de IA Analytics
"""
import asyncio
import sys
from uuid import UUID

# Adicionar path do projeto
sys.path.insert(0, '.')

from src.agents.agno_agent import analytics_agent


async def test_agent():
    """
    Teste básico do agente
    """
    print("=" * 60)
    print("🤖 TESTANDO AGENTE DE IA ANALYTICS")
    print("=" * 60)

    # 1. Inicializar agente
    print("\n📚 1. Inicializando agente...")
    await analytics_agent.initialize()

    # 2. Configurar permissões de teste
    permissions = {
        "user_id": "test-user",
        "nivel_acesso": 5,  # Admin
        "divisao": "ALL",
        "can_access_sienge": True,
        "can_access_cvdw": True,
        "can_access_powerbi": True
    }

    print(f"\n✅ Agente inicializado!")
    print(f"   - Modelo: {analytics_agent.agent.model.id if analytics_agent.agent.model else 'Fallback (sem IA)'}")
    print(f"   - Endpoints Sienge: {len(analytics_agent.doc_reader.sienge_endpoints)}")
    print(f"   - Endpoints CVCRM: {len(analytics_agent.doc_reader.cvcrm_endpoints)}")

    # 3. Testes de perguntas
    perguntas = [
        "Quanto temos em contas a pagar este mês?",
        "Como está o pipeline de vendas?",
        "Me mostre estatísticas de clientes"
    ]

    for i, pergunta in enumerate(perguntas, 1):
        print("\n" + "=" * 60)
        print(f"📊 TESTE {i}: {pergunta}")
        print("=" * 60)

        try:
            user_id = UUID("00000000-0000-0000-0000-000000000000")
            result = await analytics_agent.process_query(
                user_id,
                pergunta,
                permissions
            )

            if result.get("success"):
                print(f"\n✅ Consulta processada com sucesso!")
                print(f"\n📝 Resposta:")
                print("-" * 60)
                print(result.get("response", ""))
                print("-" * 60)

                if result.get("tools_used"):
                    print(f"\n🔧 Tools usadas: {', '.join(result['tools_used'])}")

                if result.get("explanation"):
                    exp = result["explanation"]
                    print(f"\n📋 Explicação:")
                    print(f"   - Fontes: {len(exp.fontes)}")
                    print(f"   - Tabelas: {len(exp.tabelas)}")
                    print(f"   - Filtros: {len(exp.filtros)}")
                    print(f"   - Relacionamentos: {len(exp.relacionamentos)}")
                    print(f"   - Cálculos: {len(exp.calculos)}")

                if result.get("charts"):
                    print(f"\n📊 Gráficos gerados: {len(result['charts'])}")
                    for j, chart in enumerate(result['charts'], 1):
                        print(f"   {j}. {chart.title} ({chart.chart_type})")

            else:
                print(f"\n❌ Erro: {result.get('error', 'Desconhecido')}")

        except Exception as e:
            print(f"\n❌ Erro ao processar: {str(e)}")
            import traceback
            traceback.print_exc()

    # 4. Teste de explicação detalhada
    print("\n" + "=" * 60)
    print("📋 TESTE DETALHADO: Explicação Completa")
    print("=" * 60)

    try:
        user_id = UUID("00000000-0000-0000-0000-000000000000")
        result = await analytics_agent.process_query(
            user_id,
            "Me mostre um relatório financeiro completo",
            permissions
        )

        if result.get("success") and result.get("explanation"):
            exp = result["explanation"]

            print("\n📊 FONTES DE DADOS:")
            for fonte in exp.fontes:
                print(f"   - {fonte.name} ({fonte.tipo})")
                if fonte.endpoint:
                    print(f"     Endpoint: {fonte.endpoint}")

            print("\n📋 TABELAS USADAS:")
            for tabela in exp.tabelas:
                print(f"   - {tabela.nome} ({tabela.fonte})")
                print(f"     {tabela.descricao}")
                if tabela.colunas_usadas:
                    print(f"     Colunas: {', '.join(tabela.colunas_usadas[:5])}...")

            if exp.relacionamentos:
                print("\n🔗 RELACIONAMENTOS:")
                for rel in exp.relacionamentos:
                    print(f"   - {rel.tabela_origem}.{rel.coluna_origem} → "
                          f"{rel.tabela_destino}.{rel.coluna_destino} ({rel.tipo})")

            if exp.calculos:
                print("\n🧮 CÁLCULOS:")
                for calc in exp.calculos:
                    print(f"   - {calc.nome}: {calc.formula}")
                    if calc.resultado:
                        unit = f" {calc.unidade}" if calc.unidade else ""
                        print(f"     Resultado: {calc.resultado}{unit}")

    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")

    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_agent())
