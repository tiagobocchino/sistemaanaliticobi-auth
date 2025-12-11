import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, TouchableOpacityProps } from 'react-native';
import { colors } from '../../theme/colors';

interface Props extends TouchableOpacityProps {
  loading?: boolean;
  label: string;
}

const PrimaryButton: React.FC<Props> = ({ loading, label, style, disabled, ...rest }) => (
  <TouchableOpacity
    style={[styles.button, style, disabled ? styles.disabled : null]}
    disabled={disabled || loading}
    {...rest}
  >
    {loading ? (
      <ActivityIndicator color={colors.secondary} />
    ) : (
      <Text style={styles.label}>{label}</Text>
    )}
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  button: {
    backgroundColor: colors.primary,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(200,168,106,0.4)',
  },
  disabled: {
    opacity: 0.6,
  },
  label: {
    color: '#0b0b0b',
    fontWeight: '700',
    fontSize: 16,
  },
});

export default PrimaryButton;
