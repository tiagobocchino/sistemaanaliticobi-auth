import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Screen from '../components/Layout/Screen';
import Card from '../components/Layout/Card';
import { colors } from '../theme/colors';

const PythonAnalyses = () => (
  <Screen>
    <View style={{ marginBottom: 16 }}>
      <Text style={styles.title}>Análises Python</Text>
      <Text style={styles.subtitle}>Crie e execute análises customizadas usando Python</Text>
    </View>
    <Card>
      <Text style={styles.comingIcon}>🐍</Text>
      <Text style={styles.comingTitle}>Em Breve!</Text>
      <Text style={styles.subtitle}>Esta funcionalidade está em desenvolvimento</Text>
      <View style={styles.list}>
        {[
          '✅ Criar scripts Python personalizados',
          '✅ Executar análises de dados',
          '✅ Visualizar resultados interativos',
          '✅ Agendar execuções automáticas',
          '✅ Compartilhar análises com sua equipe',
        ].map((item) => (
          <Text key={item} style={styles.item}>{item}</Text>
        ))}
      </View>
    </Card>
  </Screen>
);

const styles = StyleSheet.create({
  title: { color: colors.white, fontSize: 20, fontWeight: '700' },
  subtitle: { color: colors.text, marginTop: 4, marginBottom: 12 },
  comingIcon: { fontSize: 48, textAlign: 'center', marginBottom: 8 },
  comingTitle: { color: colors.white, fontSize: 22, fontWeight: '700', textAlign: 'center' },
  list: { marginTop: 16, gap: 6 },
  item: { color: colors.text },
});

export default PythonAnalyses;
