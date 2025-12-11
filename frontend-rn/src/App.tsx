import 'react-native-gesture-handler';
import React from 'react';
import { AuthProvider } from './context/AuthContext';
import RootNavigation from './navigation';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AuthProvider>
        <RootNavigation />
      </AuthProvider>
    </GestureHandlerRootView>
  );
}
