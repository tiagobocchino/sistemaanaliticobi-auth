import { useEffect, useRef, useState } from 'react';
import '../styles/Agents.css';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const Agents = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        'Olá! Sou seu agente de análises. Pergunte sobre vendas, financeiro, clientes ou dashboards Power BI.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef(null);

  const scrollToBottom = () => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text) return;

    const userMessage = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/agents/chat', { message: text });
      const reply = response.data?.message || 'Não consegui responder agora.';
      const tools = response.data?.tools_used;

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: reply,
          toolsUsed: tools,
        },
      ]);
    } catch (err) {
      console.error('Agent error:', err);
      setError('Não foi possível obter resposta do agente. Tente novamente.');
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Desculpe, ocorreu um erro ao processar sua solicitação.',
        },
      ]);
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="agents-container">
      <div className="page-header">
        <h1>Agentes Inteligentes</h1>
        <p>Faça perguntas em linguagem natural e receba respostas dos seus dados.</p>
        {user?.email && <span className="user-chip">{user.email}</span>}
      </div>

      <div className="chat-card">
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`chat-message ${msg.role === 'user' ? 'user' : 'assistant'}`}
            >
              <div className="chat-meta">
                <span className="chat-role">
                  {msg.role === 'user' ? 'Você' : 'Agente'}
                </span>
                {msg.toolsUsed && (
                  <span className="chat-tools">Tools: {msg.toolsUsed.join(', ')}</span>
                )}
              </div>
              <div className="chat-bubble">{msg.content}</div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {error && <div className="chat-error">{error}</div>}

        <div className="chat-input">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Pergunte: 'Como está o pipeline de vendas?' ou 'Quais dashboards posso acessar?'"
            rows={3}
            disabled={loading}
          />
          <button onClick={handleSend} disabled={loading}>
            {loading ? 'Enviando...' : 'Enviar'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Agents;
