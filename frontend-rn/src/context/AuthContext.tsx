import React, { createContext, useContext, useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../api/client';

interface User {
  email: string;
  full_name?: string;
  role?: string;
}

interface AuthContextShape {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextShape>({
  user: null,
  loading: false,
  signIn: async () => {},
  signOut: async () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const token = await AsyncStorage.getItem('auth_token');
      if (token) {
        await fetchMe();
      }
      setLoading(false);
    })();
  }, []);

  const fetchMe = async () => {
    try {
      const res = await api.get('/auth/me');
      setUser(res.data);
    } catch (e) {
      await AsyncStorage.removeItem('auth_token');
      setUser(null);
    }
  };

  const signIn = async (email: string, password: string) => {
    const res = await api.post('/auth/signin', { email, password });
    const token = res.data?.access_token;
    if (token) {
      await AsyncStorage.setItem('auth_token', token);
      await fetchMe();
    }
  };

  const signOut = async () => {
    await AsyncStorage.removeItem('auth_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
