# Analytics Platform

Plataforma empresarial completa para análise de dados com autenticação, dashboards Power BI, agentes IA avançados e integrações com sistemas externos.

## 🎯 Visão Geral

O **Analytics Platform** é uma solução completa que integra:
- **Autenticação e Autorização** robusta via Supabase
- **Dashboards Power BI** embedded com controle de acesso
- **Agentes IA** com RAG (Retrieval-Augmented Generation) para insights inteligentes
- **Integrações** com sistemas externos (CVDW CRM, Sienge ERP)
- **Sistema de Cache** híbrido para performance
- **Frontend Multiplataforma** (React Native Web via Expo)

## ✨ Características Principais

### 🔐 Autenticação & Autorização
- JWT tokens com renovação automática
- 5 níveis de acesso (Master=5 → Analista=1)
- Row Level Security (16 políticas)
- Proteção de rotas frontend + backend

### 🤖 Agentes IA Avançados
- **11 Tools disponíveis** para análises inteligentes
- RAG (Recuperação de contexto de documentos)
- Memória contextual de conversas
- Análise de tendências com ML
- Previsões futuras com intervalos de confiança
- Detecção automática de anomalias
- Sumários executivos automáticos

### 📊 Análises e Dashboards
- 3 dashboards Power BI embedded
- Sistema de análises customizadas
- Controle de acesso baseado em cargos e divisões

### ⚡ Performance
- Cache híbrido (Redis + In-Memory)
- Paginação otimizada
- Queries com índices
- Audit logging completo

### 🔗 Integrações
- **CVDW CRM**: Import diário automático
- **Sienge ERP**: Cliente implementado
- **Power BI**: Dashboards embedded

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- Ollama (para LLM local) ou credenciais Groq/OpenAI
- Conta no Supabase

### Instalação Rápida

1. **Clone o repositório**
```bash
git clone <repo-url>
cd sistemaanalitico
```

2. **Configure o ambiente**
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend-rn
npm install
cd ..
```

3. **Configure as variáveis de ambiente**
```bash
# Copie .env.example para .env e preencha com suas credenciais
cp .env.example .env
```

4. **Execute o setup do banco de dados**
```bash
# Execute no Supabase SQL Editor:
database/reset_from_scratch.sql
```

5. **Inicie o sistema**
```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
cd frontend-rn
set EXPO_OFFLINE=1  # Windows
npx expo start --web --port 8085
```

6. **Acesse a aplicação**
- Frontend: http://localhost:8085
- API Docs: http://localhost:8000/docs

## 📚 Documentação

A documentação está organizada de forma clara e acessível:

### 📖 Documentos Principais

- **[INSTALL.md](INSTALL.md)** - ✅ **NOVO** - Guia completo de instalação passo a passo
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - ✅ **NOVO** - Arquitetura técnica detalhada do sistema
- **[docs/INDEX.md](docs/INDEX.md)** - ✅ **NOVO** - Índice completo de toda a documentação

### 🚀 Guias Rápidos

- **[docs/QUICK_START.md](docs/QUICK_START.md)** - Início rápido
- **[docs/CONFIGURACAO.md](docs/CONFIGURACAO.md)** - Configuração detalhada
- **[docs/AI_AGENT_SETUP.md](docs/AI_AGENT_SETUP.md)** - Setup dos agentes IA

### 🔒 Segurança e Testes

- **[docs/SECURITY_AUDIT_REPORT.md](docs/SECURITY_AUDIT_REPORT.md)** - Auditoria de segurança
- **[docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)** - Guia de testes

### 📝 Documentação Técnica

Consulte **[docs/INDEX.md](docs/INDEX.md)** para lista completa de todos os documentos disponíveis.

## 🏗️ Estrutura do Projeto

```
sistemaanalitico/
├── src/                    # Backend FastAPI
│   ├── agents/            # Sistema de Agentes IA
│   ├── analyses/          # Sistema de Análises
│   ├── auth/              # Autenticação
│   ├── integrations/      # APIs CVDW/Sienge
│   ├── users/             # Gestão de usuários
│   ├── cache/             # Sistema de cache
│   └── database/          # Cliente Supabase
├── frontend-rn/           # Frontend React Native Web
│   ├── src/
│   │   ├── screens/      # Telas da aplicação
│   │   ├── components/   # Componentes reutilizáveis
│   │   ├── context/      # Contextos (Auth, etc)
│   │   └── api/          # Cliente API
├── database/              # Scripts SQL
│   ├── migrations/       # Migrações do banco
│   └── scripts/          # Scripts utilitários
├── docs/                  # Documentação técnica
├── tests/                 # Testes automatizados
└── scripts/               # Scripts auxiliares
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Com coverage
pytest tests/ --cov=src --cov-report=html

# Testes das melhorias
python test_melhorias.py
```

**Status dos Testes**: 100% sucesso ✅

## 🔧 Configuração

### Variáveis de Ambiente Principais

```env
# Supabase (obrigatório)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# LLM (obrigatório - escolha uma opção)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
# OU
GROQ_API_KEY=xxx
# OU
OPENAI_API_KEY=xxx

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0

# RAG
RAG_ENABLED=true
RAG_TOP_K=3
```

Para configuração detalhada, veja [docs/CONFIGURACAO.md](docs/CONFIGURACAO.md).

## 📊 Status do Projeto

### ✅ Implementado

- ✅ Fase 1: Autenticação (100%)
- ✅ Fase 2: Gestão de Usuários (100%)
- ✅ Fase 3: Análises Power BI (100%)
- ✅ Fase 6: Agentes IA Básico (100%)
- ✅ Fase 6.5: Agentes IA Avançados (100%)
- ✅ Fase 7: Performance & Cache (100%)
- ✅ Fase 8: RAG Funcionando End-to-End (100%)

### 🔄 Planejado

- 🔄 Fase 4: Análises Python Nativas
- 🔄 Fase 5: Dashboard Rico

## 📈 Métricas

- **Linhas de código**: ~15k+ (backend + frontend)
- **Testes**: 100+ testes (unit + integration)
- **Cobertura**: 46% código backend
- **APIs Integradas**: 3 (CVDW, Sienge, Power BI)
- **Tools IA**: 11 ferramentas especializadas
- **Performance**: < 3s resposta com cache

## 🛠️ Tecnologias

### Backend
- **FastAPI** - Framework web moderno
- **Supabase** - Backend-as-a-Service (PostgreSQL + Auth)
- **Pydantic** - Validação de dados
- **Redis** - Cache (opcional)
- **Ollama/Groq/OpenAI** - LLMs para agentes IA

### Frontend
- **React Native** - Framework multiplataforma
- **Expo** - Build e desenvolvimento
- **TypeScript** - Tipagem estática

### IA e Análises
- **Agno** - Framework de agentes IA
- **RAG (BM25)** - Recuperação de contexto
- **Plotly/Matplotlib** - Visualizações
- **Pandas** - Análise de dados

## 📝 Changelog

### [2.1.0] - 2025-12-19

#### 🎉 Marco Histórico
- ✅ Primeiro agente RAG funcionando end-to-end
- ✅ Sistema completo Backend + Frontend + LLM + RAG operacional
- ✅ Ollama integrado com retry automático e warm-up
- ✅ RAG recuperando contexto (3 documentos/query)

### [2.0.0] - 2025-12-17

#### Added
- 6 novas ferramentas para agentes IA
- Sistema de cache híbrido (Redis + In-Memory)
- Memória contextual de conversas
- Audit logging completo
- Performance monitoring
- Detecção automática de anomalias

#### Fixed
- Otimização de queries no Supabase
- Tratamento de encoding UTF-8 em logs
- Fallback gracioso quando Redis não disponível

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é propriedade da empresa. Todos os direitos reservados.

## 🆘 Suporte

Para problemas ou dúvidas:
- Consulte a [documentação completa](docs/)
- Verifique os [logs](logs/)
- Revise o [histórico do projeto](JORNADA.md)

---

**Versão**: 2.1.0  
**Última Atualização**: 2025-12-19  
**Status**: 🎉 Produção - RAG Funcionando End-to-End!
