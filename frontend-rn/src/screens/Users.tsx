import React from 'react';
import { View, Text } from 'react-native';
import Screen from '../components/Layout/Screen';
import { colors } from '../theme/colors';

const Users = () => (
  <Screen>
    <View>
      <Text style={{ color: colors.white, fontSize: 20, fontWeight: '700' }}>Gerenciar Usuários</Text>
      <Text style={{ color: colors.text }}>Em breve.</Text>
    </View>
  </Screen>
);

export default Users;
