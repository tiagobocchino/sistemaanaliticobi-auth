# src/analyses/routes_optimized.py
"""
Rotas otimizadas com cache, paginação e query optimizer
Fase 2 - Performance & Cache
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from src.cache.redis_manager import cache_manager, cache_decorator
from src.database.query_optimizer import QueryOptimizer
from src.utils.pagination import SmartPaginator, PaginationParams
from ..auth.dependencies import get_current_user
from ..database.supabase_client import get_supabase_client

router = APIRouter(prefix="/analyses", tags=["Análises Otimizadas"])

# Instâncias globais
_query_optimizer = None
_paginator = None

def get_query_optimizer():
    """Obtém instância do Query Optimizer"""
    global _query_optimizer
    if _query_optimizer is None:
        supabase = get_supabase_client()
        _query_optimizer = QueryOptimizer(supabase)
    return _query_optimizer

def get_paginator():
    """Obtém instância do Paginator"""
    global _paginator
    if _paginator is None:
        _paginator = SmartPaginator(cache_manager)
    return _paginator


@router.get("/kpis/{period}")
@cache_decorator(prefix="kpis", expiration=300)  # Cache de 5 minutos
async def get_kpis(
    period: str = "month",
    comparison: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna KPIs do período com cache e materialized views

    Periods: 'month', 'week', 'day'
    """
    try:
        optimizer = get_query_optimizer()
        kpis = await optimizer.get_kpi_metrics(
            period=period,
            comparison_period=comparison
        )

        return {
            "status": "success",
            "data": kpis,
            "cached": False,  # Will be True if from cache
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar KPIs: {str(e)}"
        )


@router.get("/sales/trends")
@cache_decorator(prefix="sales_trends", expiration=600)  # Cache de 10 minutos
async def get_sales_trends(
    start_date: str = Query(..., description="Data início (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data fim (YYYY-MM-DD)"),
    group_by: str = Query("daily", description="Agrupamento: daily, weekly, monthly"),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna tendências de vendas com cache
    """
    try:
        optimizer = get_query_optimizer()
        trends = await optimizer.get_optimized_sales_data(
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )

        return {
            "status": "success",
            "data": trends,
            "period": {
                "start": start_date,
                "end": end_date,
                "group_by": group_by
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar tendências: {str(e)}"
        )


@router.get("/clients/top")
async def get_top_clients(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query("valor_total", description="Campo para ordenação"),
    sort_order: str = Query("desc", description="Ordem: asc ou desc"),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna top clientes com paginação inteligente e cache
    """
    try:
        optimizer = get_query_optimizer()
        paginator = get_paginator()

        # Criar parâmetros de paginação
        params = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # Data source function
        async def fetch_clients(filters):
            return await optimizer.get_client_insights(limit=1000)

        # Paginar com cache
        result = await paginator.paginate(
            data_source=fetch_clients,
            params=params,
            cache_prefix="top_clients",
            cache_expiration=600
        )

        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar clientes: {str(e)}"
        )


@router.get("/clients/{client_id}/insights")
@cache_decorator(prefix="client_insights", expiration=300)
async def get_client_insights(
    client_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna insights detalhados de um cliente específico com cache
    """
    try:
        optimizer = get_query_optimizer()
        insights = await optimizer.get_client_insights(client_id=client_id)

        if not insights:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente {client_id} não encontrado"
            )

        return {
            "status": "success",
            "data": insights[0],
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar insights do cliente: {str(e)}"
        )


@router.get("/products/performance")
async def get_product_performance(
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna performance de produtos com filtros e paginação
    """
    try:
        optimizer = get_query_optimizer()
        paginator = get_paginator()

        # Preparar date_range
        date_range = None
        if start_date and end_date:
            date_range = {'start': start_date, 'end': end_date}

        # Criar parâmetros de paginação
        params = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by="receita_total",
            sort_order="desc",
            filters={'category': category} if category else None
        )

        # Data source function
        async def fetch_products(filters):
            return await optimizer.get_product_performance(
                category=filters.get('category') if filters else None,
                date_range=date_range
            )

        # Paginar com cache
        result = await paginator.paginate(
            data_source=fetch_products,
            params=params,
            cache_prefix="product_performance",
            cache_expiration=600
        )

        return {
            "status": "success",
            **result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar performance de produtos: {str(e)}"
        )


@router.post("/cache/invalidate")
async def invalidate_cache(
    pattern: str = Query(..., description="Padrão para invalidar (ex: kpis:*, sales_trends:*)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Invalida cache por padrão (apenas admin)
    """
    # Verificar se é admin
    if current_user.get('nivel_acesso', 0) < 5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem invalidar cache"
        )

    try:
        deleted_count = cache_manager.invalidate_cache(pattern)

        return {
            "status": "success",
            "message": f"Cache invalidado para padrão: {pattern}",
            "deleted_keys": deleted_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao invalidar cache: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna estatísticas do cache (apenas admin)
    """
    # Verificar se é admin
    if current_user.get('nivel_acesso', 0) < 5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem ver estatísticas do cache"
        )

    try:
        stats = cache_manager.get_cache_stats()

        return {
            "status": "success",
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar estatísticas: {str(e)}"
        )


@router.get("/performance/report")
@cache_decorator(prefix="performance_report", expiration=1800)  # Cache de 30 minutos
async def get_performance_report(
    period: str = Query("month", description="Período: day, week, month"),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna relatório completo de performance com múltiplas métricas
    """
    try:
        optimizer = get_query_optimizer()

        # Buscar todas as métricas em paralelo
        import asyncio

        kpis, top_clients, top_products = await asyncio.gather(
            optimizer.get_kpi_metrics(period=period, comparison_period=True),
            optimizer.get_client_insights(limit=10),
            optimizer.get_product_performance()
        )

        # Compilar relatório
        report = {
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "kpis": kpis,
            "top_clients": top_clients[:10],
            "top_products": top_products[:10] if top_products else [],
            "summary": {
                "total_clients": len(top_clients) if top_clients else 0,
                "total_products": len(top_products) if top_products else 0,
                "performance_grade": _calculate_performance_grade(kpis)
            }
        }

        return {
            "status": "success",
            "data": report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )


def _calculate_performance_grade(kpis: Dict) -> str:
    """Calcula grade de performance baseado nos KPIs"""
    try:
        if 'comparacao' in kpis:
            receita_current = kpis.get('receita_total', 0)
            receita_previous = kpis['comparacao'].get('receita_anterior', 1)

            growth = ((receita_current - receita_previous) / receita_previous) * 100

            if growth >= 20:
                return "A+"
            elif growth >= 10:
                return "A"
            elif growth >= 5:
                return "B+"
            elif growth >= 0:
                return "B"
            elif growth >= -5:
                return "C"
            else:
                return "D"
        return "N/A"
    except:
        return "N/A"
