import { useState } from 'react';

function SystemTest() {
  const [message, setMessage] = useState('Pagina de testes carregada com sucesso!');
  const [loading, setLoading] = useState(false);

  const testBackend = async () => {
    setLoading(true);
    setMessage('Testando conexao com backend...');
    try {
      const response = await fetch('http://localhost:8000/health');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMessage(`Backend OK! Resposta: ${JSON.stringify(data)}`);
    } catch (error) {
      setMessage(`ERRO: ${error.message}. Verifique se o backend esta rodando em http://localhost:8000`);
    } finally {
      setLoading(false);
    }
  };

  const testLogin = async () => {
    setLoading(true);
    setMessage('Testando login...');
    try {
      const response = await fetch('http://localhost:8000/auth/signin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'tiago.bocchino@4pcapital.com.br',
          password: '4p@Supabase'
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setMessage(`Login OK! Token recebido: ${data.access_token ? 'SIM' : 'NAO'}`);
    } catch (error) {
      setMessage(`ERRO no login: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      padding: '40px', 
      fontFamily: 'Arial, sans-serif',
      maxWidth: '800px',
      margin: '0 auto'
    }}>
      <h1 style={{ color: '#333', borderBottom: '2px solid #667eea', paddingBottom: '10px' }}>
        Sistema de Testes - Analytics Platform
      </h1>
      
      <div style={{ 
        marginTop: '30px', 
        padding: '20px', 
        backgroundColor: '#f5f5f5', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <p style={{ fontSize: '18px', fontWeight: 'bold' }}>{message}</p>
      </div>

      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button 
          onClick={testBackend} 
          disabled={loading}
          style={{ 
            padding: '12px 24px', 
            fontSize: '16px',
            backgroundColor: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          {loading ? 'Testando...' : 'Testar Backend'}
        </button>
        
        <button 
          onClick={testLogin} 
          disabled={loading}
          style={{ 
            padding: '12px 24px', 
            fontSize: '16px',
            backgroundColor: '#764ba2',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          {loading ? 'Testando...' : 'Testar Login'}
        </button>
      </div>

      <div style={{ 
        marginTop: '30px', 
        padding: '20px', 
        backgroundColor: '#e8f4f8', 
        borderRadius: '8px'
      }}>
        <h2 style={{ marginTop: 0 }}>Status do Sistema:</h2>
        <ul style={{ lineHeight: '1.8' }}>
          <li><strong>Frontend:</strong> Rodando em {window.location.origin}</li>
          <li><strong>Backend esperado:</strong> http://localhost:8000</li>
          <li><strong>Teste:</strong> Clique nos botoes acima para verificar</li>
        </ul>
      </div>

      <div style={{ 
        marginTop: '30px', 
        padding: '20px', 
        backgroundColor: '#fff3cd', 
        borderRadius: '8px',
        border: '1px solid #ffc107'
      }}>
        <h3 style={{ marginTop: 0 }}>Se os testes falharem:</h3>
        <ol style={{ lineHeight: '1.8' }}>
          <li>Verifique se o backend esta rodando: <code>python main.py</code></li>
          <li>Teste diretamente no navegador: <a href="http://localhost:8000/health" target="_blank" rel="noopener noreferrer">http://localhost:8000/health</a></li>
          <li>Verifique se a porta 8000 esta livre</li>
        </ol>
      </div>
    </div>
  );
}

export default SystemTest;
