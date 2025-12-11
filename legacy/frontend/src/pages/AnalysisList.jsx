import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './AnalysisList.css';

const AnalysisList = () => {
  const [analyses, setAnalyses] = useState([]);
  const [powerbiDashboards, setPowerbiDashboards] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchAnalyses();
    fetchPowerBIDashboards();
  }, []);

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      const response = await api.get('/analyses');
      setAnalyses(response.data);
      setError('');
    } catch (err) {
      setError('Erro ao carregar análises. Tente novamente.');
      console.error('Error fetching analyses:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPowerBIDashboards = async () => {
    try {
      const response = await api.get('/analyses/powerbi-dashboards');
      setPowerbiDashboards(response.data);
    } catch (err) {
      console.error('Error fetching Power BI dashboards:', err);
      // Não mostrar erro para dashboards, apenas log
    }
  };

  const handleAnalysisClick = (analysisId) => {
    navigate(`/analyses/${analysisId}`);
  };

  const getTypeIcon = (tipo) => {
    switch (tipo) {
      case 'powerbi':
        return '📊';
      case 'python':
        return '🐍';
      case 'tableau':
        return '📈';
      default:
        return '📋';
    }
  };

  const getTypeLabel = (tipo) => {
    switch (tipo) {
      case 'powerbi':
        return 'Power BI';
      case 'python':
        return 'Python';
      case 'tableau':
        return 'Tableau';
      default:
        return tipo;
    }
  };

  if (loading) {
    return (
      <div className="analysis-list-container">
        <div className="loading">Carregando análises...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-list-container">
        <div className="error">{error}</div>
        <button onClick={fetchAnalyses} className="retry-btn">
          Tentar Novamente
        </button>
      </div>
    );
  }

  // Render Power BI Dashboards section
  const renderPowerBIDashboards = () => {
    const dashboardKeys = Object.keys(powerbiDashboards);

    if (dashboardKeys.length === 0) {
      return null;
    }

    return (
      <div className="powerbi-section">
        <h3>Dashboards Power BI</h3>
        <div className="powerbi-buttons">
          {dashboardKeys.map((key) => {
            const dashboard = powerbiDashboards[key];
            return (
              <button
                key={key}
                className="powerbi-btn"
                onClick={() => navigate(`/analyses/${key}`)}
              >
                <div className="powerbi-icon">📊</div>
                <div className="powerbi-info">
                  <div className="powerbi-name">{dashboard.nome}</div>
                  <div className="powerbi-desc">{dashboard.descricao}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="analysis-list-container">
      <div className="header">
        <h2>Análises Disponíveis</h2>
        <p>Explore os dashboards e relatórios da empresa</p>
      </div>

      {/* Power BI Dashboards Section */}
      {renderPowerBIDashboards()}

      {/* Regular Analyses Section */}
      {analyses.length > 0 && (
        <div className="analyses-section">
          <h3>Outras Análises</h3>
          <div className="analyses-grid">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                className="analysis-card"
                onClick={() => handleAnalysisClick(analysis.id)}
              >
                <div className="analysis-header">
                  <div className="analysis-icon">
                    {getTypeIcon(analysis.tipo)}
                  </div>
                  <div className="analysis-type">
                    {getTypeLabel(analysis.tipo)}
                  </div>
                </div>

                <div className="analysis-content">
                  <h3 className="analysis-title">{analysis.nome}</h3>
                  {analysis.descricao && (
                    <p className="analysis-description">{analysis.descricao}</p>
                  )}
                </div>

                <div className="analysis-footer">
                  <span className="view-btn">Visualizar →</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {analyses.length === 0 && Object.keys(powerbiDashboards).length === 0 && (
        <div className="empty-state">
          <h3>Nenhuma análise disponível</h3>
          <p>Não há análises disponíveis no momento ou você não tem acesso.</p>
        </div>
      )}
    </div>
  );
};

export default AnalysisList;