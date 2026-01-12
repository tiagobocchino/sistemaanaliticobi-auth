# Analytics Platform

Plataforma empresarial completa com autenticação, dashboards Power BI, agentes IA avançados e integrações com CVDW/Sienge.

## 🎉 MARCO HISTÓRICO - v2.1 (2025-12-19)

**PRIMEIRO AGENTE RAG FUNCIONANDO END-TO-END!**

Hoje alcançamos o marco mais importante do projeto:
- ✅ Agente IA respondeu pela primeira vez no frontend
- ✅ Sistema completo Backend + Frontend + LLM + RAG operacional
- ✅ Ollama integrado com retry automático e warm-up
- ✅ RAG recuperando contexto (3 documentos/query)
- ✅ Testes end-to-end 100% funcionais

**Veja a jornada completa:** `JORNADA.md` - Documentação histórica do zero ao RAG funcional

---

## Novidades - v2.0 (2025-12-17)

### Agentes IA Aprimorados
- **6 Novas Ferramentas Avançadas**:
  - `analyze_trends`: Análise de tendências temporais com regressão linear
  - `compare_periods`: Comparação detalhada entre períodos
  - `forecast_future`: Previsões futuras com intervalos de confiança
  - `detect_anomalies`: Detecção estatística de anomalias (Z-score)
  - `generate_alerts`: Alertas automáticos de performance
  - `create_summary_report`: Sumários executivos automáticos

### Performance & Cache
- **Sistema de Cache Híbrido**: Redis + In-Memory com fallback automático
- **Memória Contextual**: Histórico de conversas (últimas 10 mensagens)
- **Paginação Inteligente**: Queries otimizadas com offset e order_by
- **Audit Logging**: Registro completo de operações (logs/audit/)

### Monitoramento
- **Performance Monitor**: Métricas de tempo de resposta (avg, p95, p99)
- **Usage Tracker**: Rastreamento de uso de APIs externas
- **Alertas Automáticos**: Detecção de anomalias e quedas de performance

## Como rodar (dev)

### 1. Backend
```bash
cd C:\Users\tiago\OneDrive\Desktop\analytcs
python main.py
```

### 2. Frontend (React Native Web via Expo)
```bash
cd C:\Users\tiago\OneDrive\Desktop\analytcs\frontend-rn
set EXPO_OFFLINE=1
npx expo start --web --port 8085
```

### 3. Acessar
- URL: http://localhost:8085/?platform=web
- Login: tiago.bocchino@4pcapital.com.br / Admin123!@#
- API Docs: http://localhost:8000/docs

## Requisitos
- Python 3.14+
- Node 18+
- Ollama com modelo `llama3.2` (ou GROQ_API_KEY/OPENAI_API_KEY)
- Redis (opcional, mas recomendado para produção)
- RAG local (BM25) com índice em `data/rag_index.json` (sem dependências externas)

## Instalar Dependências

```bash
# Backend
pip install -r requirements.txt

# Redis (opcional)
pip install redis

# Testar sistema
python test_melhorias.py

# RAG: gerar índice local a partir dos docs
python scripts/build_rag_index.py
```

## RAG (recuperacao de contexto)
- Índice BM25 local em `data/rag_index.json` (sem dependências externas).
- Gerar/atualizar: `python scripts/build_rag_index.py`.
- Variáveis: `RAG_ENABLED=true|false`, `RAG_TOP_K` (padrão 3), `RAG_INDEX_PATH` (padrão data/rag_index.json).
- Respostas do agente podem incluir `rag_sources` (debug) com as fontes retornadas pelo RAG.
- LLM direto (sem Agno): `AGENT_USE_AGNO=false` para usar chamada direta ao Ollama (recomendado).

## DNS (quando o dominio estiver pronto)
- Se o DNS do Supabase ou do dominio interno nao resolver na rede, use:
  `powershell -ExecutionPolicy Bypass -File scripts/configure_hosts.ps1 -Domain seu-dominio -IPAddress x.x.x.x`
- Depois execute `ipconfig /flushdns`.

## Estrutura
```
analytcs/
  src/
    agents/           # Sistema de Agentes IA
      trend_analyzer.py         # Análise de tendências
      predictive_insights.py    # Previsões e insights
      alert_generator.py        # Alertas e anomalias
      report_summarizer.py      # Sumários executivos
      cache_manager.py          # Sistema de cache híbrido
      monitoring.py             # Audit logging
      agno_agent.py            # Agente principal (integrado)
    analyses/         # Sistema de Análises
    auth/            # Autenticação
    integrations/    # APIs CVDW/Sienge
    users/           # Gestão de usuários
  frontend-rn/       # Frontend Expo React Native
  docs/             # Documentação
  database/         # Scripts SQL
  logs/audit/       # Logs de auditoria
  test_melhorias.py # Testes das melhorias
  MELHORIAS_IMPLEMENTADAS.md # Documentação completa das melhorias
```

## Features Principais

### Autenticação & Autorização
- JWT tokens com renovação automática
- 5 níveis de acesso (Master=5 → Analista=1)
- Row Level Security (16 políticas)
- Proteção de rotas frontend + backend

### Agentes IA Avançados
- **11 Tools disponíveis** (6 novas + 5 existentes)
- Memória contextual de conversas
- Análise de tendências com ML
- Previsões futuras com confiança
- Detecção automática de anomalias
- Sumários executivos automáticos
- Fallback rule-based sem LLM

### Integrações APIs
- **CVDW CRM**: Import diário automático (GitHub Actions)
- **Sienge ERP**: Cliente implementado
- **Power BI**: 3 dashboards embedded

### Performance
- Cache híbrido (Redis + In-Memory)
- Paginação otimizada
- Queries com índices
- Rate limiting
- Audit logging completo

### Monitoramento
- Logs estruturados (JSON)
- Métricas de performance (avg, p95, p99)
- Rastreamento de uso de APIs
- Alertas automáticos
- Dashboard de métricas

## CORS
Permitidos: http://localhost:3000, 5173, 5174, 8000, 8082, 8084, 8085

## Branches
- **main**: backend + frontend-rn (atual) + melhorias v2.0
- **lastro**: histórico com frontend React/Vite legado

## Testes

```bash
# Testes completos das melhorias
python test_melhorias.py

# Testes unitários
pytest tests/ -v

# Com coverage
pytest tests/ --cov=src --cov-report=html
```

**Status dos Testes**: 10/10 (100% sucesso) ✅

## Documentação Completa

- **docs/CLAUDE.md** - Contexto completo do projeto
- **MELHORIAS_IMPLEMENTADAS.md** - Detalhes técnicos das melhorias
- **docs/CREDENCIAIS.md** - Credenciais de acesso
- **docs/AI_AGENT_SETUP.md** - Setup dos agentes IA
- **docs/SECURITY_AUDIT_REPORT.md** - Auditoria de segurança
- **docs/TESTING_GUIDE.md** - Guia de testes

## Variáveis de Ambiente

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# Agentes IA
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2

# APIs Externas
CVDW_BASE_URL=https://bpincorporadora.cvcrm.com.br/api/v1/cvdw
CVDW_API_KEY=xxx
```

## Métricas do Projeto

- **Linhas de código**: ~15k+ (backend + frontend)
- **Testes**: 100 testes (48 unit + 42 integration + 10 melhorias)
- **Acurácia**: 100% (melhorias) / 87.5% (geral)
- **Cobertura**: 46% código backend
- **APIs Integradas**: 3 (CVDW, Sienge, Power BI)
- **Tools IA**: 11 ferramentas especializadas
- **Performance**: < 3s resposta com cache

## Status do Projeto

- ✅ Fase 1: Autenticação (100%)
- ✅ Fase 2: Gestão de Usuários (100%)
- ✅ Fase 3: Análises Power BI (100%)
- ✅ Fase 6: Agentes IA Básico (100%)
- ✅ **Fase 6.5: Agentes IA Avançados (100%)**
- ✅ **Fase 7: Performance & Cache (100%)**
- 🔄 Fase 4: Análises Python Nativas (Planejado)
- 🔄 Fase 5: Dashboard Rico (Planejado)

## Changelog v2.0

### [2.0.0] - 2025-12-17

#### Added
- 6 novas ferramentas para agentes IA (trend_analyzer, predictive_insights, alert_generator, report_summarizer)
- Sistema de cache híbrido (Redis + In-Memory)
- Memória contextual de conversas (últimas 10 mensagens)
- Audit logging completo com rotação diária
- Performance monitoring (métricas de tempo)
- Usage tracker para APIs externas
- Paginação inteligente com offset e order_by
- Detecção automática de anomalias (Z-score)
- Geração automática de alertas de performance
- Sumários executivos automáticos
- Previsões futuras com intervalos de confiança
- Análise de tendências com regressão linear

#### Fixed
- Otimização de queries no Supabase
- Tratamento de encoding UTF-8 em logs
- Fallback gracioso quando Redis não disponível
- Validação de dados antes de análises

#### Changed
- Agente IA agora tem 11 tools (6 novas + 5 existentes)
- Sistema de cache com fallback automático
- Logs estruturados em JSON
- Métricas de performance integradas

---

**Versão**: 2.1.0
**Data**: 2025-12-19
**Status**: 🎉 Produção Desenvolvimento - RAG Funcionando End-to-End!
**Última Atualização**: Marco Histórico - Primeiro Agente RAG Completo + Correções de Timeout
**Veja também**: `JORNADA.md` para o diário completo de desenvolvimento
