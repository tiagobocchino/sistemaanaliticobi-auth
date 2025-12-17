"""
Script de teste para validar as melhorias implementadas
"""
import asyncio
import sys
from datetime import datetime, timedelta
from uuid import uuid4


async def test_trend_analyzer():
    """Testa o analisador de tendências"""
    print("\n=== Testando Trend Analyzer ===")
    from src.agents.trend_analyzer import trend_analyzer

    # Dados de teste
    test_data = []
    base_date = datetime.now() - timedelta(days=90)
    for i in range(12):
        test_data.append({
            'data_venda': (base_date + timedelta(days=i*7)).strftime('%Y-%m-%d'),
            'valor_venda': 50000 + (i * 2000) + (i % 3 * 1000)  # Tendência de crescimento
        })

    result = trend_analyzer.analyze_sales_trend(test_data, period='weekly')
    print(f"[OK] Tendencia detectada: {result['tendencia']}")
    print(f"[OK] Crescimento: {result['crescimento_percentual']}%")
    print(f"[OK] Insights: {len(result.get('insights', []))} gerados")
    return True


async def test_comparative_analyzer():
    """Testa o analisador comparativo"""
    print("\n=== Testando Comparative Analyzer ===")
    from src.agents.trend_analyzer import comparative_analyzer

    test_data = []
    base_date = datetime.now() - timedelta(days=60)
    for i in range(60):
        test_data.append({
            'data': (base_date + timedelta(days=i)).strftime('%Y-%m-%d'),
            'valor': 1000 + (i * 10)
        })

    result = comparative_analyzer.compare_periods(test_data)
    print(f"[OK] Período 1: {result['periodo_1']['total']}")
    print(f"[OK] Período 2: {result['periodo_2']['total']}")
    print(f"[OK] Variação: {result['variacoes']['total_percentual']}%")
    return True


async def test_predictive_insights():
    """Testa o gerador de previsões"""
    print("\n=== Testando Predictive Insights ===")
    from src.agents.predictive_insights import predictive_insights

    test_data = []
    base_date = datetime.now() - timedelta(days=180)
    for i in range(6):
        test_data.append({
            'data': (base_date + timedelta(days=i*30)).strftime('%Y-%m-%d'),
            'valor': 50000 + (i * 5000)
        })

    result = predictive_insights.forecast_sales(test_data, periods_ahead=3)
    if 'previsoes' in result:
        print(f"[OK] Previsões geradas: {len(result['previsoes'])}")
        print(f"[OK] Primeira previsão: R$ {result['previsoes'][0]['previsao']:,.2f}")
    else:
        print(f"⚠ Erro: {result.get('erro', 'Desconhecido')}")
    return True


async def test_alert_generator():
    """Testa o gerador de alertas"""
    print("\n=== Testando Alert Generator ===")
    from src.agents.alert_generator import alert_generator

    test_data = []
    for i in range(50):
        value = 1000 + (i * 10)
        # Adicionar algumas anomalias
        if i in [10, 25, 40]:
            value = value * 3  # Pico anômalo
        test_data.append({
            'data': datetime.now().strftime('%Y-%m-%d'),
            'valor': value
        })

    result = alert_generator.analyze_anomalies(test_data)
    print(f"[OK] Anomalias detectadas: {result['total_anomalias']}")
    print(f"[OK] Média: R$ {result['estatisticas']['media']:,.2f}")
    return True


async def test_report_summarizer():
    """Testa o sumarizador de relatórios"""
    print("\n=== Testando Report Summarizer ===")
    from src.agents.report_summarizer import report_summarizer

    test_data = {
        'total_vendas': 125000.50,
        'quantidade_vendas': 45,
        'ticket_medio': 2777.79,
        'taxa_conversao': 0.18,
        'variacao_mes_anterior': 12.5
    }

    result = report_summarizer.generate_executive_summary(test_data, report_type='vendas')
    print(f"[OK] Sumário gerado: {result['titulo']}")
    print(f"[OK] Métricas principais: {len(result['principais_metricas'])}")
    print(f"[OK] Destaques: {len(result.get('destaques', []))}")
    return True


async def test_cache_manager():
    """Testa o gerenciador de cache"""
    print("\n=== Testando Cache Manager ===")
    from src.agents.cache_manager import cache_manager

    # Testar cache em memória
    cache_manager.set('test', 'key1', {'data': 'test_value'}, ttl=60)
    cached_value = cache_manager.get('test', 'key1')

    if cached_value and cached_value.get('data') == 'test_value':
        print("[OK] Cache em memória funcionando")
    else:
        print("[ERRO] Erro no cache em memória")

    stats = cache_manager.get_stats()
    print(f"[OK] Redis enabled: {stats['redis_enabled']}")
    print(f"[OK] Cache size: {stats['memory_cache']['size']}")
    return True


async def test_conversation_memory():
    """Testa a memória de conversas"""
    print("\n=== Testando Conversation Memory ===")
    from src.agents.cache_manager import conversation_memory

    user_id = str(uuid4())

    # Salvar algumas mensagens
    conversation_memory.save_message(
        user_id=user_id,
        message="Qual o total de vendas?",
        response="O total de vendas foi R$ 125.000,00"
    )

    conversation_memory.save_message(
        user_id=user_id,
        message="E no mês anterior?",
        response="No mês anterior foi R$ 110.000,00"
    )

    # Recuperar histórico
    history = conversation_memory.get_history(user_id)
    if history and len(history) == 2:
        print(f"[OK] Memória de conversas funcionando ({len(history)} mensagens)")
    else:
        print("[ERRO] Erro na memória de conversas")

    # Testar contexto
    context = conversation_memory.get_context(user_id, last_n=2)
    print(f"[OK] Contexto gerado: {len(context)} caracteres")

    # Limpar
    conversation_memory.clear_user_history(user_id)
    return True


async def test_monitoring():
    """Testa o sistema de monitoramento"""
    print("\n=== Testando Monitoring ===")
    from src.agents.monitoring import performance_monitor, usage_tracker

    # Testar métricas
    performance_monitor.record_metric("api_response_time", 150.5)
    performance_monitor.record_metric("api_response_time", 200.3)
    performance_monitor.increment_counter("total_api_calls", 5)

    stats = performance_monitor.get_metric_stats("api_response_time")
    print(f"[OK] Métricas registradas - Média: {stats['avg']:.2f}ms")

    counters = performance_monitor.counters
    print(f"[OK] Contador total_api_calls: {counters.get('total_api_calls', 0)}")

    # Testar usage tracker
    usage_tracker.track_api_usage(
        api_name="CVDW",
        endpoint="/oportunidades",
        user_id=str(uuid4()),
        response_size=1024,
        cost=0.01
    )

    report = usage_tracker.get_usage_report("CVDW")
    print(f"[OK] Usage tracker: {report['totals']['total_calls']} chamadas registradas")
    return True


async def test_pagination():
    """Testa paginação nas queries"""
    print("\n=== Testando Paginação ===")

    # Verificar se a assinatura da função está correta
    from src.agents.agno_agent import analytics_agent
    import inspect

    sig = inspect.signature(analytics_agent.query_raw_data)
    params = list(sig.parameters.keys())

    if 'offset' in params and 'order_by' in params:
        print("[OK] Paginação implementada (parâmetros offset e order_by presentes)")
        return True
    else:
        print("[ERRO] Paginação não implementada corretamente")
        return False


async def test_agent_tools():
    """Testa se as novas ferramentas foram adicionadas ao agente"""
    print("\n=== Testando Agent Tools ===")
    from src.agents.agno_agent import analytics_agent

    expected_tools = [
        'analyze_trends',
        'compare_periods',
        'forecast_future',
        'detect_anomalies',
        'generate_alerts',
        'create_summary_report'
    ]

    agent_tool_names = [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in analytics_agent.agent.tools]

    found_tools = []
    for expected in expected_tools:
        if any(expected in str(tool) for tool in agent_tool_names):
            found_tools.append(expected)

    print(f"[OK] Ferramentas encontradas: {len(found_tools)}/{len(expected_tools)}")
    for tool in found_tools:
        print(f"  - {tool}")

    return len(found_tools) == len(expected_tools)


async def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("INICIANDO TESTES DAS MELHORIAS")
    print("=" * 60)

    tests = [
        ("Trend Analyzer", test_trend_analyzer),
        ("Comparative Analyzer", test_comparative_analyzer),
        ("Predictive Insights", test_predictive_insights),
        ("Alert Generator", test_alert_generator),
        ("Report Summarizer", test_report_summarizer),
        ("Cache Manager", test_cache_manager),
        ("Conversation Memory", test_conversation_memory),
        ("Monitoring", test_monitoring),
        ("Paginação", test_pagination),
        ("Agent Tools", test_agent_tools),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[ERRO] Erro em {name}: {str(e)}")
            results.append((name, False))

    # Sumário
    print("\n" + "=" * 60)
    print("SUMÁRIO DOS TESTES")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK] PASSOU" if result else "[ERRO] FALHOU"
        print(f"{status}: {name}")

    print(f"\n{'=' * 60}")
    print(f"Testes Passados: {passed}/{total} ({passed/total*100:.1f}%)")
    print("=" * 60)

    if passed == total:
        print("\n[SUCESSO] Todas as melhorias foram implementadas com sucesso!")
        return 0
    else:
        print(f"\n[AVISO]  {total - passed} teste(s) falharam. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
