import { useState } from 'react';
import '../styles/Agents.css';

const Agents = () => {
  const [messages, setMessages] = useState([]);

  return (
    <div className="agents-container">
      <div className="page-header">
        <h1>Agentes Inteligentes</h1>
        <p>Obtenha insights rápidos através de conversas com IA</p>
      </div>

      <div className="coming-soon-card">
        <div className="coming-soon-icon">🤖</div>
        <h2>Em Breve!</h2>
        <p>Esta funcionalidade está em desenvolvimento</p>
        <div className="features-preview">
          <h3>O que você poderá fazer:</h3>
          <ul>
            <li>✅ Conversar com assistentes de IA especializados</li>
            <li>✅ Fazer perguntas sobre seus dados</li>
            <li>✅ Receber insights automatizados</li>
            <li>✅ Gerar relatórios com linguagem natural</li>
            <li>✅ Automatizar tarefas repetitivas</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Agents;
