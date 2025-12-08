import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './AnalysisView.css';

const AnalysisView = () => {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalysis();
  }, [analysisId]);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/analyses/${analysisId}`);
      setAnalysis(response.data);
      setError('');
    } catch (err) {
      if (err.response?.status === 403) {
        setError('Você não tem permissão para acessar esta análise.');
      } else if (err.response?.status === 404) {
        setError('Análise não encontrada.');
      } else {
        setError('Erro ao carregar análise. Tente novamente.');
      }
      console.error('Error fetching analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/analyses');
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
      <div className="analysis-view-container">
        <div className="loading">Carregando análise...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analysis-view-container">
        <div className="error-section">
          <h2>Erro de Acesso</h2>
          <p>{error}</p>
          <button onClick={handleBack} className="back-btn">
            ← Voltar para Análises
          </button>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="analysis-view-container">
        <div className="error-section">
          <h2>Análise não encontrada</h2>
          <p>A análise solicitada não existe ou foi removida.</p>
          <button onClick={handleBack} className="back-btn">
            ← Voltar para Análises
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="analysis-view-container">
      {/* Header */}
      <div className="analysis-header">
        <button onClick={handleBack} className="back-btn">
          ← Voltar
        </button>

        <div className="analysis-info">
          <div className="analysis-meta">
            <div className="analysis-icon">
              {getTypeIcon(analysis.tipo)}
            </div>
            <div className="analysis-details">
              <h1 className="analysis-title">{analysis.nome}</h1>
              <div className="analysis-badges">
                <span className="type-badge">{getTypeLabel(analysis.tipo)}</span>
                {analysis.publico && <span className="public-badge">Público</span>}
              </div>
            </div>
          </div>

          {analysis.descricao && (
            <p className="analysis-description">{analysis.descricao}</p>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="analysis-content">
        <div className="iframe-container">
          <iframe
            src={analysis.embed_url}
            title={analysis.nome}
            className="analysis-iframe"
            frameBorder="0"
            allowFullScreen
          />
        </div>
      </div>
    </div>
  );
};

export default AnalysisView;