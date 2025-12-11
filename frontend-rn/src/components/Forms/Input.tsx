import React from 'react';
import { View, Text, TextInput, StyleSheet, TextInputProps } from 'react-native';
import { colors } from '../../theme/colors';

interface Props extends TextInputProps {
  label?: string;
  error?: string;
}

const Input: React.FC<Props> = ({ label, error, style, ...rest }) => {
  return (
    <View style={styles.container}>
      {label ? <Text style={styles.label}>{label}</Text> : null}
      <TextInput
        style={[styles.input, style]}
        placeholderTextColor={colors.gray500}
        {...rest}
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { marginBottom: 14 },
  label: { color: colors.white, marginBottom: 6, fontWeight: '600' },
  input: {
    backgroundColor: 'rgba(12,12,14,0.85)',
    borderWidth: 1,
    borderColor: colors.accentMid,
    borderRadius: 10,
    padding: 12,
    color: colors.white,
  },
  error: { color: '#f88', marginTop: 4 },
});

export default Input;
