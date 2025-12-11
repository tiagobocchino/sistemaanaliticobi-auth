import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Screen from '../components/Layout/Screen';
import { colors } from '../theme/colors';

const Signup = () => (
  <Screen>
    <View style={styles.center}>
      <Text style={styles.title}>Cadastro ainda não disponível</Text>
      <Text style={styles.subtitle}>Entre em contato com o administrador para criar uma conta.</Text>
    </View>
  </Screen>
);

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { color: colors.white, fontSize: 20, fontWeight: '700', marginBottom: 8 },
  subtitle: { color: colors.text, textAlign: 'center' },
});

export default Signup;
