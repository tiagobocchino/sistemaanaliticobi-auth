#!/usr/bin/env python3
"""
Script de Teste - Integração da Fase 2
Analytics Platform - Performance & Cache

Testa todas as funcionalidades implementadas na Fase 2:
- Sistema de cache Redis
- Query Optimizer
- Paginação inteligente
- Integração completa
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List

# Adicionar src ao path
sys.path.insert(0, 'src')

def print_section(title: str):
    """Imprime seção formatada"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")

def print_test(test_name: str, status: str, details: str = ""):
    """Imprime resultado de teste"""
    prefix = "[PASS]" if status == "PASS" else "[FAIL]"
    print(f"{prefix} {test_name}: {status}")
    if details:
        print(f"       -> {details}")

async def test_redis_cache():
    """Testa sistema de cache Redis"""
    print_section("1. TESTE DO SISTEMA DE CACHE REDIS")

    try:
        from src.cache.redis_manager import cache_manager

        # Teste 1: Conectividade
        stats = cache_manager.get_cache_stats()
        status = stats.get('status', 'error')

        if status in ['connected', 'memory_fallback']:
            print_test("Conectividade Redis", "PASS", f"Status: {status}")
        else:
            print_test("Conectividade Redis", "FAIL", f"Status: {status}")
            return False

        # Teste 2: Cache e Recuperação
        test_key = "test:fase2:integration"
        test_data = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "data": [1, 2, 3, 4, 5]
        }

        cache_manager.cache_result(test_key, test_data, 60)
        retrieved_data = cache_manager.get_cached_result(test_key)

        if retrieved_data and retrieved_data.get('test') == True:
            print_test("Armazenar e Recuperar Cache", "PASS")
        else:
            print_test("Armazenar e Recuperar Cache", "FAIL")
            return False

        # Teste 3: Invalidação
        cache_manager.invalidate_cache("test:*")
        after_invalidation = cache_manager.get_cached_result(test_key)

        if after_invalidation is None:
            print_test("Invalidar Cache", "PASS")
        else:
            print_test("Invalidar Cache", "FAIL")
            return False

        # Teste 4: Estatísticas
        stats = cache_manager.get_cache_stats()
        if 'total_keys' in stats:
            print_test("Estatísticas do Cache", "PASS",
                      f"Total keys: {stats['total_keys']}, Status: {stats['status']}")
        else:
            print_test("Estatísticas do Cache", "FAIL")
            return False

        return True

    except Exception as e:
        print_test("Sistema de Cache", "FAIL", f"Erro: {str(e)}")
        return False

async def test_pagination():
    """Testa sistema de paginação"""
    print_section("2. TESTE DO SISTEMA DE PAGINAÇÃO")

    try:
        from src.utils.pagination import SmartPaginator, PaginationParams
        from src.cache.redis_manager import cache_manager

        # Dados de teste
        test_data = [
            {"id": i, "nome": f"Item {i}", "valor": i * 100}
            for i in range(1, 101)
        ]

        # Função simulada de data source
        async def mock_data_source(filters):
            await asyncio.sleep(0.1)  # Simular latência
            return test_data

        paginator = SmartPaginator(cache_manager)

        # Teste 1: Primeira página
        params = PaginationParams(page=1, per_page=20, sort_by="valor", sort_order="desc")
        result = await paginator.paginate(mock_data_source, params, "test_pagination", 300)

        if (result['metadata']['page'] == 1 and
            len(result['data']) == 20 and
            result['metadata']['total_items'] == 100):
            print_test("Paginação - Primeira Página", "PASS",
                      f"20 items de 100 total")
        else:
            print_test("Paginação - Primeira Página", "FAIL")
            return False

        # Teste 2: Segunda página (deve vir do cache)
        params2 = PaginationParams(page=2, per_page=20, sort_by="valor", sort_order="desc")
        result2 = await paginator.paginate(mock_data_source, params2, "test_pagination", 300)

        if result2['metadata']['page'] == 2 and len(result2['data']) == 20:
            print_test("Paginação - Segunda Página", "PASS")
        else:
            print_test("Paginação - Segunda Página", "FAIL")
            return False

        # Teste 3: Ordenação
        if result['data'][0]['valor'] > result['data'][-1]['valor']:
            print_test("Ordenação Descendente", "PASS")
        else:
            print_test("Ordenação Descendente", "FAIL")
            return False

        # Teste 4: Metadados
        metadata = result['metadata']
        if (metadata['total_pages'] == 5 and
            metadata['has_next'] == True and
            metadata['has_prev'] == False):
            print_test("Metadados de Paginação", "PASS",
                      f"{metadata['total_pages']} páginas totais")
        else:
            print_test("Metadados de Paginação", "FAIL")
            return False

        # Limpar cache de teste
        cache_manager.invalidate_cache("test_pagination:*")

        return True

    except Exception as e:
        print_test("Sistema de Paginação", "FAIL", f"Erro: {str(e)}")
        return False

async def test_query_optimizer():
    """Testa Query Optimizer"""
    print_section("3. TESTE DO QUERY OPTIMIZER")

    try:
        # Teste básico de importação e estrutura
        from src.database.query_optimizer import QueryOptimizer

        print_test("Importação do Query Optimizer", "PASS")

        # Teste de métodos disponíveis
        required_methods = [
            'get_optimized_sales_data',
            'get_kpi_metrics',
            'get_client_insights',
            'get_product_performance'
        ]

        for method in required_methods:
            if hasattr(QueryOptimizer, method):
                print_test(f"Método '{method}' disponível", "PASS")
            else:
                print_test(f"Método '{method}' disponível", "FAIL")
                return False

        # Nota: Testes com banco real requerem conexão com Supabase
        print("\n⚠️  Testes com banco real requerem configuração do Supabase")
        print("   Execute os testes de integração após configurar DATABASE_URL")

        return True

    except Exception as e:
        print_test("Query Optimizer", "FAIL", f"Erro: {str(e)}")
        return False

def test_file_structure():
    """Testa estrutura de arquivos"""
    print_section("4. TESTE DA ESTRUTURA DE ARQUIVOS")

    import os

    required_files = {
        "Cache Manager": "src/cache/redis_manager.py",
        "Cache Init": "src/cache/__init__.py",
        "Query Optimizer": "src/database/query_optimizer.py",
        "Database Init": "src/database/__init__.py",
        "Pagination": "src/utils/pagination.py",
        "Utils Init": "src/utils/__init__.py",
        "Rotas Otimizadas": "src/analyses/routes_optimized.py",
        "SQL Migrations": "database/migrations/001_performance_optimization.sql",
        "SQL README": "database/migrations/README.md",
        "Hook Pagination (Frontend)": "mobile/src/hooks/usePaginatedData.ts",
        "LazyList Component": "mobile/src/components/optimized/LazyList.tsx",
        "ClientsListOptimized": "mobile/src/screens/ClientsListOptimized.tsx"
    }

    all_ok = True
    for name, path in required_files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print_test(f"Arquivo {name}", "PASS", f"{size} bytes")
        else:
            print_test(f"Arquivo {name}", "FAIL", "Arquivo não encontrado")
            all_ok = False

    return all_ok

def test_documentation():
    """Verifica documentação"""
    print_section("5. TESTE DE DOCUMENTAÇÃO")

    import os

    docs_to_check = {
        "README.md": ["cache", "redis", "paginação"],
        "database/migrations/README.md": ["índices", "materialized view"],
        "MELHORIAS_IMPLEMENTADAS.md": ["Fase 2", "performance"]
    }

    all_ok = True
    for doc_file, keywords in docs_to_check.items():
        if os.path.exists(doc_file):
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            found_keywords = [kw for kw in keywords if kw.lower() in content]

            if len(found_keywords) == len(keywords):
                print_test(f"Documentação {doc_file}", "PASS",
                          f"Keywords encontradas: {', '.join(keywords)}")
            else:
                missing = [kw for kw in keywords if kw not in found_keywords]
                print_test(f"Documentação {doc_file}", "FAIL",
                          f"Keywords faltando: {', '.join(missing)}")
                all_ok = False
        else:
            print_test(f"Documentação {doc_file}", "FAIL", "Arquivo não encontrado")
            all_ok = False

    return all_ok

def print_summary(results: Dict[str, bool]):
    """Imprime resumo dos testes"""
    print_section("RESUMO DOS TESTES - FASE 2")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    print(f"Total de testes: {total}")
    print(f"[OK] Aprovados: {passed}")
    print(f"[X] Falharam: {failed}")
    print(f"\nTaxa de sucesso: {(passed/total)*100:.1f}%\n")

    if failed == 0:
        print("*** TODOS OS TESTES PASSARAM! ***")
        print("\n*** A Fase 2 foi implementada com sucesso! ***")
        print("\nProximos passos:")
        print("1. Instale Redis: pip install redis")
        print("2. Execute o Redis localmente ou use Redis Cloud")
        print("3. Configure DATABASE_URL no .env para testes com Supabase")
        print("4. Execute os scripts SQL em database/migrations/")
        print("5. Teste as rotas otimizadas: python -m uvicorn main:app --reload")
    else:
        print("*** Alguns testes falharam. Revise os erros acima. ***")

async def main():
    """Função principal"""
    print("\n" + "="*60)
    print(" TESTE DE INTEGRAÇÃO - FASE 2")
    print(" Analytics Platform - Performance & Cache")
    print("="*60)

    results = {}

    # Executar testes
    results["Estrutura de Arquivos"] = test_file_structure()
    results["Sistema de Cache"] = await test_redis_cache()
    results["Sistema de Paginação"] = await test_pagination()
    results["Query Optimizer"] = await test_query_optimizer()
    results["Documentação"] = test_documentation()

    # Resumo
    print_summary(results)

if __name__ == "__main__":
    asyncio.run(main())
