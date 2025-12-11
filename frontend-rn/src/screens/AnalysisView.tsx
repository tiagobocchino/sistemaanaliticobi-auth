import React from 'react';
import { View, Text } from 'react-native';
import Screen from '../components/Layout/Screen';
import { colors } from '../theme/colors';

const AnalysisView = () => (
  <Screen>
    <View>
      <Text style={{ color: colors.white, fontSize: 20, fontWeight: '700' }}>Visualização de Análise</Text>
      <Text style={{ color: colors.text }}>Detalhes do dashboard/relatório selecionado.</Text>
    </View>
  </Screen>
);

export default AnalysisView;
