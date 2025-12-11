import React from 'react';
import { SafeAreaView, View, StyleSheet, ViewProps } from 'react-native';
import { colors } from '../../theme/colors';

interface Props extends ViewProps {
  children: React.ReactNode;
}

const Screen: React.FC<Props> = ({ children, style, ...rest }) => {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={[styles.container, style]} {...rest}>
        {children}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.secondary },
  container: {
    flex: 1,
    backgroundColor: colors.accentLight,
    padding: 16,
  },
});

export default Screen;
