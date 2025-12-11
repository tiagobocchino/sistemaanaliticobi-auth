import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../../theme/colors';

interface Props {
  role: 'user' | 'assistant';
  content: string;
  toolsUsed?: string[];
}

const ChatBubble: React.FC<Props> = ({ role, content, toolsUsed }) => {
  const isUser = role === 'user';
  return (
    <View style={[styles.wrapper, isUser && styles.wrapperUser]}>
      <View style={[styles.bubble, isUser ? styles.user : styles.agent]}>
        <Text style={styles.meta}>{isUser ? 'Você' : 'Agente'}{toolsUsed?.length ? ` · Tools: ${toolsUsed.join(', ')}` : ''}</Text>
        <Text style={styles.text}>{content}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: { marginBottom: 12, alignItems: 'flex-start' },
  wrapperUser: { alignItems: 'flex-end' },
  bubble: {
    maxWidth: '90%',
    padding: 12,
    borderRadius: 12,
  },
  agent: {
    backgroundColor: colors.accentMid,
    borderWidth: 1,
    borderColor: colors.border,
  },
  user: {
    backgroundColor: colors.primary,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.2)',
  },
  text: { color: colors.white },
  meta: { color: colors.gray400, marginBottom: 4, fontSize: 12 },
});

export default ChatBubble;
