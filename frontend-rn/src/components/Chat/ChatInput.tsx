import React from 'react';
import { View, TextInput, StyleSheet } from 'react-native';
import { colors } from '../../theme/colors';
import PrimaryButton from '../Buttons/PrimaryButton';

interface Props {
  value: string;
  onChange: (text: string) => void;
  onSend: () => void;
  loading?: boolean;
}

const ChatInput: React.FC<Props> = ({ value, onChange, onSend, loading }) => (
  <View style={styles.container}>
    <TextInput
      style={styles.input}
      value={value}
      onChangeText={onChange}
      placeholder="Pergunte algo..."
      placeholderTextColor={colors.gray500}
      multiline
    />
    <PrimaryButton label={loading ? 'Enviando...' : 'Enviar'} onPress={onSend} loading={loading} />
  </View>
);

const styles = StyleSheet.create({
  container: { flexDirection: 'row', gap: 12, alignItems: 'flex-end' },
  input: {
    flex: 1,
    minHeight: 60,
    padding: 12,
    backgroundColor: 'rgba(15,15,18,0.9)',
    borderWidth: 1,
    borderColor: colors.accentMid,
    borderRadius: 10,
    color: colors.white,
  },
});

export default ChatInput;
