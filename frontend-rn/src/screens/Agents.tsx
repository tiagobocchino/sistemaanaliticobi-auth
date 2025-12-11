import React, { useRef, useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import Screen from '../components/Layout/Screen';
import Card from '../components/Layout/Card';
import ChatBubble from '../components/Chat/ChatBubble';
import ChatInput from '../components/Chat/ChatInput';
import api from '../api/client';
import { colors } from '../theme/colors';
import { useAuth } from '../context/AuthContext';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  toolsUsed?: string[];
}

const Agents = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Olá! Sou seu agente de análises. Pergunte sobre vendas, financeiro, clientes ou dashboards Power BI.' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<ScrollView>(null);

  const handleSend = async () => {
    const text = input.trim();
    if (!text) return;
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    setLoading(true);
    try {
      const res = await api.post('/agents/chat', { message: text });
      const reply = res.data?.message || 'Não consegui responder agora.';
      const tools = res.data?.tools_used;
      setMessages((prev) => [...prev, { role: 'assistant', content: reply, toolsUsed: tools }]);
    } catch (e) {
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Erro ao processar sua solicitação.' }]);
    } finally {
      setLoading(false);
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
    }
  };

  return (
    <Screen>
      <View style={styles.header}>
        <Text style={styles.title}>Agentes Inteligentes</Text>
        <Text style={styles.subtitle}>Faça perguntas em linguagem natural e receba respostas dos seus dados.</Text>
        {user?.email ? <Text style={styles.chip}>{user.email}</Text> : null}
      </View>
      <Card style={{ flex: 1 }}>
        <ScrollView ref={scrollRef} style={{ flex: 1 }} contentContainerStyle={{ paddingVertical: 8 }}>
          {messages.map((m, i) => (
            <ChatBubble key={i} role={m.role} content={m.content} toolsUsed={m.toolsUsed} />
          ))}
        </ScrollView>
        <ChatInput value={input} onChange={setInput} onSend={handleSend} loading={loading} />
      </Card>
    </Screen>
  );
};

const styles = StyleSheet.create({
  header: { marginBottom: 12 },
  title: { color: colors.white, fontSize: 22, fontWeight: '700' },
  subtitle: { color: colors.text, marginVertical: 4 },
  chip: {
    alignSelf: 'flex-start',
    backgroundColor: 'rgba(200,168,106,0.15)',
    color: colors.white,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
  },
});

export default Agents;
