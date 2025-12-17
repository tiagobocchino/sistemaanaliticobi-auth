// mobile/src/components/optimized/LazyList.tsx
/**
 * Componente de lista otimizada com lazy loading e virtual scrolling
 * Fase 2 - Performance & Cache
 */

import React, { useCallback, memo } from 'react';
import {
  FlatList,
  View,
  Text,
  ActivityIndicator,
  RefreshControl,
  StyleSheet,
  ViewToken,
} from 'react-native';
import { usePaginatedData } from '../../hooks/usePaginatedData';

interface LazyListProps<T> {
  endpoint: string;
  renderItem: ({ item, index }: { item: T; index: number }) => JSX.Element;
  keyExtractor: (item: T, index: number) => string;
  perPage?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: Record<string, any>;
  emptyMessage?: string;
  onItemPress?: (item: T) => void;
  estimatedItemSize?: number;
  ListHeaderComponent?: React.ComponentType<any> | React.ReactElement | null;
  ListFooterComponent?: React.ComponentType<any> | React.ReactElement | null;
}

function LazyListComponent<T = any>(props: LazyListProps<T>) {
  const {
    endpoint,
    renderItem,
    keyExtractor,
    perPage = 20,
    sortBy,
    sortOrder = 'desc',
    filters = {},
    emptyMessage = 'Nenhum item encontrado',
    estimatedItemSize = 100,
    ListHeaderComponent,
    ListFooterComponent,
  } = props;

  // Hook de paginação
  const {
    data,
    metadata,
    isLoading,
    isRefreshing,
    error,
    loadMore,
    refresh,
    hasMore,
  } = usePaginatedData<T>({
    endpoint,
    perPage,
    sortBy,
    sortOrder,
    filters,
    autoLoad: true,
  });

  // Renderizar footer com loading
  const renderFooter = useCallback(() => {
    if (ListFooterComponent) {
      return <ListFooterComponent />;
    }

    if (!isLoading) return null;

    return (
      <View style={styles.footer}>
        <ActivityIndicator size="small" color="#007AFF" />
        <Text style={styles.footerText}>Carregando mais...</Text>
      </View>
    );
  }, [isLoading, ListFooterComponent]);

  // Renderizar empty state
  const renderEmpty = useCallback(() => {
    if (isLoading || isRefreshing) {
      return (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Carregando...</Text>
        </View>
      );
    }

    if (error) {
      return (
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>❌ {error}</Text>
          <Text style={styles.retryText} onPress={refresh}>
            Tentar novamente
          </Text>
        </View>
      );
    }

    return (
      <View style={styles.centerContainer}>
        <Text style={styles.emptyText}>{emptyMessage}</Text>
      </View>
    );
  }, [isLoading, isRefreshing, error, emptyMessage, refresh]);

  // Handle end reached (lazy loading)
  const handleEndReached = useCallback(() => {
    if (hasMore && !isLoading) {
      loadMore();
    }
  }, [hasMore, isLoading, loadMore]);

  // Viewability config para otimização
  const viewabilityConfig = {
    waitForInteraction: true,
    viewAreaCoveragePercentThreshold: 50,
  };

  // Callback quando items se tornam visíveis
  const onViewableItemsChanged = useCallback(
    ({ viewableItems }: { viewableItems: ViewToken[] }) => {
      // Aqui você pode implementar lógica adicional
      // Por exemplo, pré-carregar imagens dos items visíveis
      console.log('Viewable items:', viewableItems.length);
    },
    []
  );

  return (
    <View style={styles.container}>
      {/* Informações de paginação (opcional) */}
      {metadata && !isRefreshing && (
        <View style={styles.paginationInfo}>
          <Text style={styles.paginationText}>
            Mostrando {data.length} de {metadata.total_items} itens (Página{' '}
            {metadata.page} de {metadata.total_pages})
          </Text>
        </View>
      )}

      <FlatList
        data={data}
        renderItem={renderItem}
        keyExtractor={keyExtractor}
        ListHeaderComponent={ListHeaderComponent}
        ListFooterComponent={renderFooter}
        ListEmptyComponent={renderEmpty}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={refresh} />
        }
        onEndReached={handleEndReached}
        onEndReachedThreshold={0.5}
        getItemLayout={(data, index) => ({
          length: estimatedItemSize,
          offset: estimatedItemSize * index,
          index,
        })}
        removeClippedSubviews={true}
        maxToRenderPerBatch={10}
        updateCellsBatchingPeriod={50}
        initialNumToRender={10}
        windowSize={5}
        viewabilityConfig={viewabilityConfig}
        onViewableItemsChanged={onViewableItemsChanged}
        style={styles.list}
      />
    </View>
  );
}

// Memoizar componente para evitar re-renders desnecessários
export const LazyList = memo(LazyListComponent) as typeof LazyListComponent;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  list: {
    flex: 1,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    minHeight: 200,
  },
  footer: {
    paddingVertical: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  footerText: {
    marginTop: 10,
    fontSize: 14,
    color: '#666',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    textAlign: 'center',
    marginBottom: 10,
  },
  retryText: {
    fontSize: 16,
    color: '#007AFF',
    textDecorationLine: 'underline',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
    textAlign: 'center',
  },
  paginationInfo: {
    backgroundColor: '#FFF',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  paginationText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
});
