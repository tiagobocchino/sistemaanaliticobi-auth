import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext'; // Para usar o token
import api from '../services/api'; // Seu cliente Axios
import './Users.css';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Função para pegar token do localStorage (não do contexto useAuth)
  const getToken = () => localStorage.getItem('access_token');

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const token = getToken();
      const response = await api.get('/users', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUsers(response.data);
      setError('');
    } catch (err) {
      setError('Falha ao carregar usuários. Você tem permissão de administrador?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = getToken();
    if (token) {
      fetchUsers();
    }
  }, []);

  const handleInputChange = (userId, field, value) => {
    setUsers(
      users.map((user) =>
        user.id === userId ? { ...user, [field]: value } : user
      )
    );
  };

  const handleSave = async (userId) => {
    const userToUpdate = users.find((user) => user.id === userId);
    const data = {
      cargo: userToUpdate.cargo,
      divisao: userToUpdate.divisao,
    };

    try {
      await api.put(`/users/${userId}`, data, {
        headers: { Authorization: `Bearer ${token}` },
      });
      alert('Usuário atualizado com sucesso!');
      fetchUsers(); // Re-sincroniza com o banco de dados
    } catch (err) {
      alert('Falha ao atualizar usuário.');
      console.error(err);
    }
  };

  if (loading) return <p>Carregando usuários...</p>;
  if (error) return <p className="error-message">{error}</p>;

  return (
    <div className="users-container">
      <h3>Gerenciamento de Usuários</h3>
      <div className="users-table-wrapper">
        <table className="users-table">
          <thead>
            <tr>
              <th>Nome Completo</th>
              <th>Email</th>
              <th>Cargo</th>
              <th>Divisão</th>
              <th>Ação</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.full_name}</td>
                <td>{user.email}</td>
                <td><input type="text" value={user.cargo || ''} onChange={(e) => handleInputChange(user.id, 'cargo', e.target.value)} /></td>
                <td><input type="text" value={user.divisao || ''} onChange={(e) => handleInputChange(user.id, 'divisao', e.target.value)} /></td>
                <td><button onClick={() => handleSave(user.id)} className="save-button">Salvar</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Users;