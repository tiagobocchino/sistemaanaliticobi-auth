import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './AnalysisView.css';

// Power BI Dashboards configuration (temporary import - should be from API)
const POWERBI_DASHBOARDS = {
  "compras": {
    "nome": "Dashboard - Compras - DW",
    "descricao": "Dashboard de compras do Data Warehouse",
    "tipo": "powerbi",
    "embed_url": "https://app.powerbi.com/reportEmbed?reportId=32dfd7cf-1c98-4667-aac0-792638f9b675&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea",
    "iframe_html": '<iframe title="Dashboard - Compras - DW (1)" width="1140" height="541.25" src="https://app.powerbi.com/reportEmbed?reportId=32dfd7cf-1c98-4667-aac0-792638f9b675&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea" frameborder="0" allowFullScreen="true"></iframe>',
    "publico": false,
    "divisoes_permitidas": ["FIN"],
    "nivel_acesso_minimo": 4
  },
  "sdrs": {
    "nome": "Dashboard - SDRs (TV) v2.0",
    "descricao": "Dashboard de acompanhamento dos SDRs de TV",
    "tipo": "powerbi",
    "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiZWFjNWE1M2UtOGJmZi00YmU4LWIzNjAtYmE0OTY3YWIwOGY4IiwidCI6IjU1MjVhN2E4LTNlMzgtNDYwZC04OTY3LWM1MjYwYWY4ZTllYSJ9",
    "iframe_html": '<iframe title="Dashboard - SDRs (TV) v2.0" width="600" height="373.5" src="https://app.powerbi.com/view?r=eyJrIjoiZWFjNWE1M2UtOGJmZi00YmU4LWIzNjAtYmE0OTY3YWIwOGY4IiwidCI6IjU1MjVhN2E4LTNlMzgtNDYwZC04OTY3LWM1MjYwYWY4ZTllYSJ9" frameborder="0" allowFullScreen="true"></iframe>',
    "publico": false,
    "divisoes_permitidas": ["COM"],
    "nivel_acesso_minimo": 4
  },
  "pastas": {
    "nome": "Dashboard - Contratos",
    "descricao": "Dashboard de contratos e pastas",
    "tipo": "powerbi",
    "embed_url": "https://app.powerbi.com/reportEmbed?reportId=40da54e1-9a7d-466d-8f60-c5efe35bd69e&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea",
    "iframe_html": '<iframe title="Dashboard Contratos - 2.0v-19nov" width="1140" height="541.25" src="https://app.powerbi.com/reportEmbed?reportId=40da54e1-9a7d-466d-8f60-c5efe35bd69e&autoAuth=true&ctid=5525a7a8-3e38-460d-8967-c5260af8e9ea" frameborder="0" allowFullScreen="true"></iframe>',
    "publico": false,
    "divisoes_permitidas": ["COM"],
    "nivel_acesso_minimo": 4
  }
};

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

      // First, check if it's a Power BI dashboard key
      if (POWERBI_DASHBOARDS[analysisId]) {
        // Verify user has access to this Power BI dashboard
        try {
          const accessResponse = await api.get('/analyses/powerbi-dashboards');
          if (accessResponse.data[analysisId]) {
            setAnalysis({
              id: analysisId,
              ...POWERBI_DASHBOARDS[analysisId]
            });
            setError('');
            setLoading(false);
            return;
          } else {
            setError('Você não tem permissão para acessar este dashboard.');
            setLoading(false);
            return;
          }
        } catch (accessErr) {
          console.error('Error checking dashboard access:', accessErr);
          setError('Erro ao verificar permissões de acesso.');
          setLoading(false);
          return;
        }
      }

      // If not a Power BI dashboard, try to fetch from database
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