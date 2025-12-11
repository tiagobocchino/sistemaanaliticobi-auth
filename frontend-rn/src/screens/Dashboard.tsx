import React from 'react';
import { Text, StyleSheet } from 'react-native';
import Screen from '../components/Layout/Screen';
import Card from '../components/Layout/Card';
import { colors } from '../theme/colors';

const Dashboard = () => (
  <Screen>
    <Card>
      <Text style={styles.title}>Visão Geral</Text>
      <Text style={styles.subtitle}>Aqui ficarão os principais indicadores e cartões de atalho.</Text>
    </Card>
  </Screen>
);

const styles = StyleSheet.create({
  title: { color: colors.white, fontSize: 20, fontWeight: '700', marginBottom: 8 },
  subtitle: { color: colors.text },
});

export default Dashboard;
