import api from './api';

/**
 * Serviço de autenticação
 * Gerencia todas as chamadas relacionadas à autenticação
 */
const authService = {
  /**
   * Registra um novo usuário
   * @param {Object} userData - Dados do usuário (email, password, full_name, cargo_id, divisao_id)
   * @returns {Promise} Resposta da API com dados do usuário e tokens ou mensagem de confirmação
   */
  signup: async (userData) => {
    const response = await api.post('/auth/signup', userData);

    // Se não precisa confirmar email e tem tokens, salva
    if (!response.data.requires_email_confirmation && response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }

    return response.data;
  },

  /**
   * Faz login do usuário
   * @param {Object} credentials - Credenciais (email, password)
   * @returns {Promise} Resposta da API com dados do usuário e tokens
   */
  signin: async (credentials) => {
    try {
    const response = await api.post('/auth/signin', credentials);

    // Salva tokens no localStorage
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }

    return response.data;
    } catch (error) {
      // Log detalhado do erro para diagnóstico
      console.error('Signin error:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        url: error.config?.url
      });
      throw error;
    }
  },

  /**
   * Faz logout do usuário
   * @returns {Promise}
   */
  signout: async () => {
    try {
      await api.post('/auth/signout');
    } finally {
      // Limpa dados locais independentemente do resultado
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  /**
   * Obtém dados do usuário atual
   * @returns {Promise} Dados do usuário
   */
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');

    // Atualiza dados do usuário no localStorage
    localStorage.setItem('user', JSON.stringify(response.data));

    return response.data;
  },

  /**
   * Renova o token de acesso
   * @param {string} refreshToken - Token de refresh
   * @returns {Promise} Novo token de acesso
   */
  refreshToken: async (refreshToken) => {
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken,
    });

    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }

    return response.data;
  },

  /**
   * Solicita reset de senha
   * @param {string} email - Email do usuário
   * @returns {Promise}
   */
  resetPassword: async (email) => {
    const response = await api.post('/auth/reset-password', { email });
    return response.data;
  },

  /**
   * Atualiza a senha do usuário
   * @param {string} currentPassword - Senha atual
   * @param {string} newPassword - Nova senha
   * @returns {Promise}
   */
  updatePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/auth/update-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },

  /**
   * Verifica se o usuário está autenticado
   * @returns {boolean}
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Obtém o usuário do localStorage
   * @returns {Object|null} Dados do usuário ou null
   */
  getStoredUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};

export default authService;
