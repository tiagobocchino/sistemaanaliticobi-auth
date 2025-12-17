// mobile/src/screens/ClientsListOptimized.tsx
/**
 * Tela de lista de clientes otimizada com lazy loading
 * Exemplo de uso do componente LazyList
 * Fase 2 - Performance & Cache
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  TextInput,
} from 'react-native';
import { LazyList } from '../components/optimized/LazyList';
import { useNavigation } from '@react-navigation/native';

interface Client {
  id: string;
  nome: string;
  total_compras: number;
  valor_total: number;
  ticket_medio: number;
  ultima_compra: string;
  ranking: number;
  status_atividade?: string;
}

export function ClientsListOptimized() {
  const navigation = useNavigation();
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('valor_total');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Handler para pressionar item
  const handleClientPress = useCallback(
    (client: Client) => {
      navigation.navigate('ClientDetails', { clientId: client.id });
    },
    [navigation]
  );

  // Renderizar cada item da lista
  const renderClientItem = useCallback(
    ({ item, index }: { item: Client; index: number }) => (
      <TouchableOpacity
        style={styles.clientCard}
        onPress={() => handleClientPress(item)}
        activeOpacity={0.7}
      >
        <View style={styles.rankingBadge}>
          <Text style={styles.rankingText}>#{item.ranking}</Text>
        </View>

        <View style={styles.clientInfo}>
          <Text style={styles.clientName}>{item.nome}</Text>

          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Total Compras</Text>
              <Text style={styles.statValue}>{item.total_compras}</Text>
            </View>

            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Valor Total</Text>
              <Text style={styles.statValue}>
                R$ {item.valor_total.toLocaleString('pt-BR')}
              </Text>
            </View>

            <View style={styles.statItem}>
              <Text style={styles.statLabel}>Ticket Médio</Text>
              <Text style={styles.statValue}>
                R$ {item.ticket_medio.toLocaleString('pt-BR')}
              </Text>
            </View>
          </View>

          <View style={styles.footer}>
            <Text style={styles.lastPurchase}>
              Última compra:{' '}
              {new Date(item.ultima_compra).toLocaleDateString('pt-BR')}
            </Text>

            {item.status_atividade && (
              <View
                style={[
                  styles.statusBadge,
                  {
                    backgroundColor:
                      item.status_atividade === 'ativo'
                        ? '#4CAF50'
                        : item.status_atividade === 'regular'
                        ? '#FF9800'
                        : '#F44336',
                  },
                ]}
              >
                <Text style={styles.statusText}>{item.status_atividade}</Text>
              </View>
            )}
          </View>
        </View>
      </TouchableOpacity>
    ),
    [handleClientPress]
  );

  // Key extractor
  const keyExtractor = useCallback(
    (item: Client, index: number) => `client-${item.id}-${index}`,
    []
  );

  // Toggle sort order
  const toggleSortOrder = useCallback(() => {
    setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
  }, []);

  // Header component
  const ListHeader = useCallback(() => {
    return (
      <View style={styles.header}>
        <Text style={styles.title}>Top Clientes</Text>

        {/* Search bar */}
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Buscar cliente..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>

        {/* Filtros */}
        <View style={styles.filtersRow}>
          <TouchableOpacity
            style={styles.filterButton}
            onPress={() => setSortBy('valor_total')}
          >
            <Text
              style={[
                styles.filterText,
                sortBy === 'valor_total' && styles.filterTextActive,
              ]}
            >
              Por Valor
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.filterButton}
            onPress={() => setSortBy('total_compras')}
          >
            <Text
              style={[
                styles.filterText,
                sortBy === 'total_compras' && styles.filterTextActive,
              ]}
            >
              Por Compras
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.filterButton}
            onPress={() => setSortBy('ticket_medio')}
          >
            <Text
              style={[
                styles.filterText,
                sortBy === 'ticket_medio' && styles.filterTextActive,
              ]}
            >
              Por Ticket
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.sortButton}
            onPress={toggleSortOrder}
          >
            <Text style={styles.sortText}>
              {sortOrder === 'desc' ? '↓' : '↑'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }, [searchQuery, sortBy, sortOrder, toggleSortOrder]);

  return (
    <View style={styles.container}>
      <LazyList<Client>
        endpoint="/analyses/clients/top"
        renderItem={renderClientItem}
        keyExtractor={keyExtractor}
        perPage={20}
        sortBy={sortBy}
        sortOrder={sortOrder}
        filters={{ search: searchQuery }}
        emptyMessage="Nenhum cliente encontrado"
        estimatedItemSize={150}
        ListHeaderComponent={ListHeader}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    backgroundColor: '#FFF',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  searchContainer: {
    marginBottom: 12,
  },
  searchInput: {
    backgroundColor: '#F5F5F5',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  filtersRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 8,
    backgroundColor: '#F5F5F5',
    borderRadius: 20,
  },
  filterText: {
    fontSize: 14,
    color: '#666',
  },
  filterTextActive: {
    color: '#007AFF',
    fontWeight: 'bold',
  },
  sortButton: {
    marginLeft: 'auto',
    padding: 8,
    backgroundColor: '#007AFF',
    borderRadius: 20,
    width: 36,
    height: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sortText: {
    fontSize: 18,
    color: '#FFF',
    fontWeight: 'bold',
  },
  clientCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 16,
    marginVertical: 8,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    flexDirection: 'row',
  },
  rankingBadge: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#007AFF',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  rankingText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 14,
  },
  clientInfo: {
    flex: 1,
  },
  clientName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  statsRow: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  statItem: {
    flex: 1,
  },
  statLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  lastPurchase: {
    fontSize: 12,
    color: '#666',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    color: '#FFF',
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
});
