import React, { useState } from 'react';
import {
  createDrawerNavigator,
  DrawerContentScrollView,
} from '@react-navigation/drawer';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import Dashboard from '../screens/Dashboard';
import AnalysisList from '../screens/AnalysisList';
import PythonAnalyses from '../screens/PythonAnalyses';
import Agents from '../screens/Agents';
import Users from '../screens/Users';
import { useAuth } from '../context/AuthContext';
import { colors } from '../theme/colors';

const Drawer = createDrawerNavigator();

const DrawerItem = ({
  label,
  onPress,
  collapsed,
}: {
  label: string;
  onPress: () => void;
  collapsed: boolean;
}) => (
  <TouchableOpacity style={styles.item} onPress={onPress}>
    <Text style={styles.itemIcon}>•</Text>
    {!collapsed && <Text style={styles.itemLabel}>{label}</Text>}
  </TouchableOpacity>
);

const CustomDrawerContent = (props: any) => {
  const { user } = useAuth();
  const { collapsed, setCollapsed } = props;

  return (
    <DrawerContentScrollView
      {...props}
      contentContainerStyle={[
        styles.drawerContent,
        { width: collapsed ? 80 : 260 },
      ]}
    >
      <View style={styles.header}>
        {!collapsed && <Text style={styles.logo}>Analytics</Text>}
        <TouchableOpacity
          onPress={() => setCollapsed(!collapsed)}
          style={styles.toggle}
        >
          <Text style={styles.toggleText}>{collapsed ? '›' : '‹'}</Text>
        </TouchableOpacity>
      </View>
      {!collapsed && (
        <Text style={styles.user}>{user?.email || 'Usuário'}</Text>
      )}

      <View style={styles.list}>
        <DrawerItem
          label="Dashboard"
          onPress={() => props.navigation.navigate('Dashboard')}
          collapsed={collapsed}
        />
        <DrawerItem
          label="Power BI"
          onPress={() => props.navigation.navigate('PowerBI')}
          collapsed={collapsed}
        />
        <DrawerItem
          label="Python"
          onPress={() => props.navigation.navigate('Python')}
          collapsed={collapsed}
        />
        <DrawerItem
          label="Agentes IA"
          onPress={() => props.navigation.navigate('Agents')}
          collapsed={collapsed}
        />
        {user?.role === 'admin' && (
          <DrawerItem
            label="Usuários"
            onPress={() => props.navigation.navigate('Users')}
            collapsed={collapsed}
          />
        )}
      </View>
    </DrawerContentScrollView>
  );
};

const AppDrawer = () => {
  const { user } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Drawer.Navigator
      initialRouteName="Dashboard"
      screenOptions={{
        headerShown: false,
        drawerType: 'permanent',
        drawerStyle: {
          backgroundColor: colors.secondary,
          borderRightColor: colors.border,
          borderRightWidth: 1,
          width: collapsed ? 80 : 260,
        },
        sceneContainerStyle: { backgroundColor: colors.accentLight },
      }}
      drawerContent={(props) => (
        <CustomDrawerContent
          {...props}
          collapsed={collapsed}
          setCollapsed={setCollapsed}
        />
      )}
    >
      <Drawer.Screen name="Dashboard" component={Dashboard} />
      <Drawer.Screen name="PowerBI" component={AnalysisList} />
      <Drawer.Screen name="Python" component={PythonAnalyses} />
      <Drawer.Screen name="Agents" component={Agents} />
      {user?.role === 'admin' && <Drawer.Screen name="Users" component={Users} />}
    </Drawer.Navigator>
  );
};

const styles = StyleSheet.create({
  drawerContent: {
    flex: 1,
    backgroundColor: colors.secondary,
    paddingTop: 16,
    paddingHorizontal: 12,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  logo: { color: colors.primary, fontSize: 18, fontWeight: '700' },
  user: { color: colors.text, marginBottom: 12, marginLeft: 4 },
  list: { gap: 6 },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  itemIcon: { color: colors.primary, fontSize: 14, marginRight: 8 },
  itemLabel: { color: colors.text, fontWeight: '600' },
  toggle: {
    width: 34,
    height: 34,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  toggleText: { color: colors.white, fontWeight: '700' },
});

export default AppDrawer;
