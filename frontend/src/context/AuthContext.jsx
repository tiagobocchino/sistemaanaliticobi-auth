import { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Carrega o usuário do localStorage ao inicializar
  useEffect(() => {
    const loadUser = async () => {
      try {
        if (authService.isAuthenticated()) {
          const storedUser = authService.getStoredUser();
          setUser(storedUser);

          // Tenta buscar dados atualizados do usuário (com timeout para não travar)
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 segundos timeout
            
            const currentUser = await authService.getCurrentUser();
            clearTimeout(timeoutId);
            setUser(currentUser);
          } catch (error) {
            // Se falhar ao buscar, usa dados do localStorage
            // Não mostra erro se for timeout ou conexão - é esperado se backend não estiver rodando
            if (error.name !== 'AbortError' && !error.message.includes('fetch')) {
            console.error('Erro ao carregar usuário:', error);
            }
          }
        }
      } catch (error) {
        console.error('Erro ao inicializar AuthContext:', error);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  /**
   * Registra um novo usuário
   */
  const signup = async (userData) => {
    try {
      const response = await authService.signup(userData);
      setUser(response.user);
      return response;
    } catch (error) {
      throw error;
    }
  };

  /**
   * Faz login do usuário
   */
  const signin = async (credentials) => {
    try {
      const response = await authService.signin(credentials);
      setUser(response.user);
      return response;
    } catch (error) {
      throw error;
    }
  };

  /**
   * Faz logout do usuário
   */
  const signout = async () => {
    try {
      await authService.signout();
    } finally {
      setUser(null);
    }
  };

  /**
   * Atualiza dados do usuário
   */
  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const value = {
    user,
    loading,
    signup,
    signin,
    signout,
    updateUser,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook customizado para usar o contexto
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }

  return context;
};

export default AuthContext;
