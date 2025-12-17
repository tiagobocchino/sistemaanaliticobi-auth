// mobile/src/hooks/usePaginatedData.ts
/**
 * Hook customizado para paginação e lazy loading
 * Fase 2 - Performance & Cache
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/api';

interface PaginationMetadata {
  page: number;
  per_page: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

interface PaginatedResponse<T> {
  data: T[];
  metadata: PaginationMetadata;
  links: {
    first?: string;
    last?: string;
    next?: string;
    prev?: string;
    self?: string;
  };
}

interface UsePaginatedDataOptions {
  endpoint: string;
  initialPage?: number;
  perPage?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: Record<string, any>;
  autoLoad?: boolean;
}

interface UsePaginatedDataReturn<T> {
  data: T[];
  metadata: PaginationMetadata | null;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  loadMore: () => Promise<void>;
  refresh: () => Promise<void>;
  goToPage: (page: number) => Promise<void>;
  nextPage: () => Promise<void>;
  previousPage: () => Promise<void>;
  hasMore: boolean;
}

export function usePaginatedData<T = any>(
  options: UsePaginatedDataOptions
): UsePaginatedDataReturn<T> {
  const {
    endpoint,
    initialPage = 1,
    perPage = 20,
    sortBy,
    sortOrder = 'desc',
    filters = {},
    autoLoad = true,
  } = options;

  const [data, setData] = useState<T[]>([]);
  const [metadata, setMetadata] = useState<PaginationMetadata | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(initialPage);

  // Função para buscar dados
  const fetchData = useCallback(
    async (page: number, append: boolean = false) => {
      try {
        if (append) {
          setIsLoading(true);
        } else {
          setIsRefreshing(true);
        }
        setError(null);

        // Construir query params
        const params = new URLSearchParams({
          page: page.toString(),
          per_page: perPage.toString(),
          ...(sortBy && { sort_by: sortBy }),
          ...(sortOrder && { sort_order: sortOrder }),
          ...filters,
        });

        // Fazer requisição
        const response = await apiClient.get<PaginatedResponse<T>>(
          `${endpoint}?${params.toString()}`
        );

        if (response.status === 'success') {
          if (append) {
            // Lazy loading - adicionar ao final
            setData((prev) => [...prev, ...response.data]);
          } else {
            // Refresh - substituir tudo
            setData(response.data);
          }
          setMetadata(response.metadata);
          setCurrentPage(page);
        } else {
          throw new Error('Erro ao carregar dados');
        }
      } catch (err: any) {
        setError(err.message || 'Erro desconhecido');
        console.error('Erro ao buscar dados paginados:', err);
      } finally {
        setIsLoading(false);
        setIsRefreshing(false);
      }
    },
    [endpoint, perPage, sortBy, sortOrder, filters]
  );

  // Carregar mais (lazy loading)
  const loadMore = useCallback(async () => {
    if (metadata && metadata.has_next && !isLoading) {
      await fetchData(currentPage + 1, true);
    }
  }, [metadata, currentPage, isLoading, fetchData]);

  // Refresh (pull to refresh)
  const refresh = useCallback(async () => {
    setData([]);
    await fetchData(initialPage, false);
  }, [fetchData, initialPage]);

  // Ir para página específica
  const goToPage = useCallback(
    async (page: number) => {
      if (metadata && page >= 1 && page <= metadata.total_pages) {
        await fetchData(page, false);
      }
    },
    [metadata, fetchData]
  );

  // Próxima página
  const nextPage = useCallback(async () => {
    if (metadata && metadata.has_next) {
      await fetchData(currentPage + 1, false);
    }
  }, [metadata, currentPage, fetchData]);

  // Página anterior
  const previousPage = useCallback(async () => {
    if (metadata && metadata.has_prev) {
      await fetchData(currentPage - 1, false);
    }
  }, [metadata, currentPage, fetchData]);

  // Auto-load inicial
  useEffect(() => {
    if (autoLoad) {
      fetchData(initialPage, false);
    }
  }, [autoLoad, initialPage, fetchData]);

  return {
    data,
    metadata,
    isLoading,
    isRefreshing,
    error,
    loadMore,
    refresh,
    goToPage,
    nextPage,
    previousPage,
    hasMore: metadata?.has_next ?? false,
  };
}
