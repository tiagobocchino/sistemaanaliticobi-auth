import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator, Linking } from 'react-native';
import Screen from '../components/Layout/Screen';
import Card from '../components/Layout/Card';
import api from '../api/client';
import { colors } from '../theme/colors';

interface Analysis {
  id: string;
  nome: string;
  descricao?: string;
  tipo: string;
}

const AnalysisList = () => {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [powerbi, setPowerbi] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [a, p] = await Promise.all([
          api.get('/analyses'),
          api.get('/analyses/powerbi-dashboards'),
        ]);
        setAnalyses(a.data || []);
        setPowerbi(p.data || {});
      } catch (e) {
        // log
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <Screen>
        <View style={styles.center}><ActivityIndicator color={colors.primary} /></View>
      </Screen>
    );
  }

  const dashboards = Object.keys(powerbi);

  const handleOpen = (dash: any) => {
    const url = dash?.embed_url;
    if (url) {
      Linking.openURL(url);
    }
  };

  return (
    <Screen>
      <View style={styles.header}>
        <Text style={styles.h1}>Análises Disponíveis</Text>
        <Text style={styles.p}>Explore os dashboards e relatórios da empresa</Text>
      </View>

      {dashboards.length > 0 ? (
        <View style={{ marginBottom: 16 }}>
          <Text style={styles.h2}>Dashboards Power BI</Text>
          <FlatList
            data={dashboards}
            keyExtractor={(k) => k}
            renderItem={({ item }) => {
              const dash = powerbi[item];
              return (
                <TouchableOpacity onPress={() => handleOpen(dash)}>
                  <Card style={styles.powerbiCard}>
                    <Text style={styles.powerbiName}>{dash?.nome || 'Dashboard Power BI'}</Text>
                    <Text style={styles.powerbiDesc}>{dash?.descricao || 'Abrir dashboard'}</Text>
                    <Text style={styles.view}>Abrir dashboard →</Text>
                  </Card>
                </TouchableOpacity>
              );
            }}
            ItemSeparatorComponent={() => <View style={{ height: 10 }} />}
          />
        </View>
      ) : (
        <Card>
          <Text style={styles.p}>Nenhum dashboard Power BI disponível.</Text>
        </Card>
      )}
    </Screen>
  );
};

const styles = StyleSheet.create({
  header: { alignItems: 'center', marginBottom: 12 },
  h1: { color: colors.white, fontSize: 22, fontWeight: '700' },
  p: { color: colors.text, textAlign: 'center' },
  h2: { color: colors.white, fontSize: 18, fontWeight: '700', marginVertical: 10, textAlign: 'center' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  powerbiCard: {
    gap: 6,
  },
  powerbiName: { color: colors.white, fontSize: 16, fontWeight: '700' },
  powerbiDesc: { color: colors.text },
  view: { color: colors.primary, marginTop: 6, fontWeight: '600' },
});

export default AnalysisList;
