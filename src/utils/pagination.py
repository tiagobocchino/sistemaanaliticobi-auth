# src/utils/pagination.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from src.cache.redis_manager import cache_manager

@dataclass
class PaginationParams:
    page: int = 1
    per_page: int = 20
    sort_by: Optional[str] = None
    sort_order: str = "desc"
    filters: Optional[Dict] = None

class SmartPaginator:
    """Sistema de paginação inteligente com cache"""

    def __init__(self, cache_mgr=None):
        self.cache = cache_mgr or cache_manager

    async def paginate(
        self,
        data_source: Any,  # Função assíncrona que retorna dados
        params: PaginationParams,
        cache_prefix: str = "pagination",
        cache_expiration: int = 300
    ) -> Dict:
        """Pagina dados de forma inteligente com cache"""

        # Gerar chave de cache baseada nos parâmetros
        cache_key = self.cache.generate_cache_key(
            cache_prefix,
            {
                'page': params.page,
                'per_page': params.per_page,
                'sort_by': params.sort_by,
                'sort_order': params.sort_order,
                'filters': params.filters
            }
        )

        # Tentar recuperar do cache
        cached_result = self.cache.get_cached_result(cache_key)
        if cached_result:
            return cached_result

        # Buscar dados
        all_data = await data_source(params.filters)

        # Aplicar ordenação
        if params.sort_by:
            all_data = self._apply_sorting(all_data, params.sort_by, params.sort_order)

        # Calcular paginação
        total_items = len(all_data)
        total_pages = (total_items + params.per_page - 1) // params.per_page

        # Validar página
        if params.page > total_pages:
            params.page = total_pages
        if params.page < 1:
            params.page = 1

        # Extrair página atual
        start_idx = (params.page - 1) * params.per_page
        end_idx = start_idx + params.per_page
        current_page_data = all_data[start_idx:end_idx]

        # Preparar metadados
        metadata = {
            'page': params.page,
            'per_page': params.per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': params.page < total_pages,
            'has_prev': params.page > 1,
            'sort_by': params.sort_by,
            'sort_order': params.sort_order
        }

        # Preparar links de navegação
        links = self._generate_navigation_links(params, total_pages)

        result = {
            'data': current_page_data,
            'metadata': metadata,
            'links': links
        }

        # Cachear resultado
        self.cache.cache_result(cache_key, result, cache_expiration)

        return result

    def _apply_sorting(self, data: List[Dict], sort_by: str, sort_order: str) -> List[Dict]:
        """Aplica ordenação aos dados"""

        reverse = sort_order.lower() == 'desc'

        def sort_key(item):
            value = item.get(sort_by)
            # Tratar valores nulos
            if value is None:
                return '' if not reverse else 'zzz'
            return value

        return sorted(data, key=sort_key, reverse=reverse)

    def _generate_navigation_links(self, params: PaginationParams, total_pages: int) -> Dict:
        """Gera links de navegação para paginação"""

        base_url = f"?per_page={params.per_page}&sort_by={params.sort_by}&sort_order={params.sort_order}"

        if params.filters:
            for key, value in params.filters.items():
                base_url += f"&{key}={value}"

        links = {
            'first': f"{base_url}&page=1",
            'last': f"{base_url}&page={total_pages}",
            'self': f"{base_url}&page={params.page}"
        }

        if params.page > 1:
            links['prev'] = f"{base_url}&page={params.page - 1}"

        if params.page < total_pages:
            links['next'] = f"{base_url}&page={params.page + 1}"

        return links

# Decorator para paginação automática
def paginated_endpoint(cache_prefix: str = "api", default_per_page: int = 20):
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            # Extrair parâmetros de paginação dos kwargs
            page = int(kwargs.pop('page', 1))
            per_page = int(kwargs.pop('per_page', default_per_page))
            sort_by = kwargs.pop('sort_by', None)
            sort_order = kwargs.pop('sort_order', 'desc')

            # Criar params
            params = PaginationParams(
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                sort_order=sort_order,
                filters=kwargs
            )

            # Obter instância do paginador
            paginator = SmartPaginator(cache_manager)

            # Executar função com paginação
            result = await paginator.paginate(
                lambda filters: func(self, filters),
                params,
                cache_prefix
            )

            return result
        return wrapper
    return decorator
