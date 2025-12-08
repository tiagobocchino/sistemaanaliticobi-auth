import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './AnalysisList.css';

const AnalysisList = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchAnalyses();
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

  return (
    <div className="analysis-list-container">
      <div className="header">
        <h2>Análises Disponíveis</h2>
        <p>Explore os dashboards e relatórios da empresa</p>
      </div>

      {analyses.length === 0 ? (
        <div className="empty-state">
          <h3>Nenhuma análise disponível</h3>
          <p>Não há análises disponíveis no momento ou você não tem acesso.</p>
        </div>
      ) : (
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
      )}
    </div>
  );
};

export default AnalysisList;