import React, { useState } from 'react';
import { View, Text, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Screen from '../components/Layout/Screen';
import Card from '../components/Layout/Card';
import Input from '../components/Forms/Input';
import PrimaryButton from '../components/Buttons/PrimaryButton';
import { useAuth } from '../context/AuthContext';
import { colors } from '../theme/colors';

const Login = () => {
  const { signIn } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      await signIn(email.trim(), password);
    } catch (e: any) {
      setError('Não foi possível entrar. Verifique suas credenciais.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <LinearGradient colors={['#050505', '#0e0e11', '#0a0a0a']} style={{ flex: 1 }}>
        <Screen>
          <View style={styles.center}>
            <Card style={styles.card}>
              <Text style={styles.title}>Analytics Platform</Text>
              <Text style={styles.subtitle}>Faça login para continuar</Text>
              <Input label="Email" placeholder="seu@email.com" keyboardType="email-address" autoCapitalize="none" value={email} onChangeText={setEmail} />
              <Input label="Senha" placeholder="******" secureTextEntry value={password} onChangeText={setPassword} />
              {error ? <Text style={styles.error}>{error}</Text> : null}
              <PrimaryButton label="Entrar" onPress={handleLogin} loading={loading} style={{ marginTop: 8 }} />
              <Text style={styles.footer}>Não tem uma conta? Cadastre-se</Text>
            </Card>
          </View>
        </Screen>
      </LinearGradient>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  card: { width: '100%', maxWidth: 420 },
  title: { color: colors.white, fontSize: 24, fontWeight: '700', textAlign: 'center', marginBottom: 8 },
  subtitle: { color: '#e5ddc8', textAlign: 'center', marginBottom: 16 },
  error: { color: '#f88', marginTop: 8 },
  footer: { color: colors.primary, textAlign: 'center', marginTop: 16 },
});

export default Login;
