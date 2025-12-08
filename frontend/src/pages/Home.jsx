import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Home.css';

const Home = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="home-container">
      <div className="home-content">
        <h1 className="home-title">Analytics Platform</h1>
        <p className="home-subtitle">
          Gerencie suas análises, dashboards e insights em um só lugar
        </p>

        <div className="features">
          <div className="feature">
            <h3>Power BI Integrado</h3>
            <p>Visualize seus dashboards com controle de acesso</p>
          </div>
          <div className="feature">
            <h3>Análises Python</h3>
            <p>Crie análises customizadas direto na plataforma</p>
          </div>
          <div className="feature">
            <h3>Agentes Inteligentes</h3>
            <p>Obtenha insights rápidos com IA</p>
          </div>
        </div>

        <div className="home-actions">
          {isAuthenticated ? (
            <Link to="/dashboard" className="btn btn-primary">
              Ir para Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className="btn btn-primary">
                Entrar
              </Link>
              <Link to="/signup" className="btn btn-secondary">
                Criar Conta
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;
