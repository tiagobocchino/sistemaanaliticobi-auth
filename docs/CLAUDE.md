# Claude Context Guide - Analytics Platform

## Atualizacao 2025-12-17 (Resumo Rapido) - v2.0

- **Frontend Principal**: Expo React Native + TypeScript em `frontend-rn/` (roda via `npx expo start --web --port 8085` com `EXPO_OFFLINE=1`)
- **Backend**: FastAPI em `src/` (Python 3.14+); CORS liberado para 3000/5173/5174/8000/8082/8084/8085
- **Frontend Legacy**: React/Vite arquivado na branch `lastro`
- **Credenciais Dev**: tiago.bocchino@4pcapital.com.br / Admin123!@#
- **Agente IA**: Preferir Ollama `llama3.2` em http://localhost:11434/v1 (fallback: GROQ/OpenAI)
  - **11 Tools disponíveis** (6 novas avançadas + 5 existentes)
  - Memória contextual de conversas
  - Cache híbrido (Redis + In-Memory)
  - Audit logging completo
- **Integrações**: CVDW CRM + Sienge ERP + Power BI Dashboards
- **CI/CD**: GitHub Actions para importação diária CVDW às 3h UTC
- **Novidades v2.0**: Agentes IA Avançados + Performance & Cache + Monitoramento

---

## Visao Geral do Projeto

**Nome**: Analytics Platform
**Objetivo**: Plataforma empresarial completa para:

1. **Controle de Acesso Granular**: Gerenciar quem pode ver quais análises baseado em cargo e divisão
2. **Power BI Embedded**: Dashboards corporativos (SDRs, Compras, Pastas) com iframe
3. **Análises Python Nativas**: Sistema planejado para análises customizadas
4. **Agentes IA**: Chatbot conversacional com ferramentas especializadas (Agno framework)
5. **Integrações APIs**: CVDW CRM, Sienge ERP, Power BI

---

## Stack Tecnologica Completa

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Autenticação**: Supabase Auth (JWT tokens)
- **Banco de Dados**: Supabase (PostgreSQL) com Row Level Security
- **Validação**: Pydantic v2
- **HTTP Client**: httpx (async) + requests (sync)
- **Agentes IA**: Agno framework (>=1.1.1) + OpenAI API
- **LLM Providers**: Ollama (local), Groq, OpenAI
- **Data Analysis**: Pandas, Matplotlib, Plotly

### Frontend
- **Framework**: React Native + Expo SDK 54
- **Linguagem**: TypeScript
- **Navegação**: React Navigation (Drawer + Stack)
- **HTTP Client**: Axios com interceptors
- **Storage**: AsyncStorage
- **UI**: Componentes customizados + Expo Vector Icons

### Database
- **PostgreSQL** (via Supabase)
- **Row Level Security**: 16 políticas implementadas
- **Triggers**: Sincronização automática auth.users → public.usuarios
- **Tabelas principais**: usuarios, cargos, divisoes, analyses

### DevOps
- **CI/CD**: GitHub Actions
- **Testes**: Pytest (48 testes, 87.5% acurácia)
- **Coverage**: 46% do código backend
- **Deploy**: Local (desenvolvimento)

---

## Estrutura do Projeto ATUAL (2025-12-12)

```
analytcs/
├── .github/workflows/           # CI/CD
│   └── cvdw_import.yml         # Import CVDW diário 3h UTC
│
├── analyse_api/                # Scripts análise/importação
│   ├── import_cvdw_to_supabase.py
│   ├── sample_cvdw_fields.py
│   └── supabase_schema.sql
│
├── database/                   # SQL scripts e migrations
│   ├── migrations/
│   ├── scripts/
│   ├── reset_from_scratch.sql
│   ├── setup_rls.sql
│   ├── sync_users.sql
│   └── setup_user_permissions.sql
│
├── docs/                       # Documentação completa
│   ├── CLAUDE.md              # Este arquivo
│   ├── README.md
│   ├── QUICK_START.md
│   ├── AGENTS_PLANNING.md
│   ├── AI_AGENT_SETUP.md
│   ├── API_INTEGRATIONS_SETUP.md
│   ├── CREDENCIAIS.md
│   ├── SECURITY_AUDIT_REPORT.md
│   ├── TESTING_GUIDE.md
│   └── ROADMAP_PHASE3.md
│
├── frontend-rn/               # Frontend React Native (PRINCIPAL)
│   ├── src/
│   │   ├── api/              # Cliente API
│   │   │   └── client.ts
│   │   ├── components/       # Componentes reutilizáveis
│   │   │   ├── Buttons/
│   │   │   ├── Chat/         # Chat UI agentes
│   │   │   ├── Forms/
│   │   │   └── Layout/
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── navigation/
│   │   │   ├── AppDrawer.tsx
│   │   │   ├── AuthStack.tsx
│   │   │   └── index.tsx
│   │   ├── screens/          # Telas
│   │   │   ├── Login.tsx
│   │   │   ├── Signup.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── AnalysisList.tsx
│   │   │   ├── AnalysisView.tsx
│   │   │   ├── Users.tsx
│   │   │   ├── Agents.tsx
│   │   │   └── PythonAnalyses.tsx
│   │   └── App.tsx
│   ├── app.json              # Config Expo
│   ├── package.json
│   └── tsconfig.json
│
├── lastro/                   # Arquivos obsoletos/histórico
│   ├── docs/                # Docs de sessões antigas
│   └── tests/               # Testes rápidos antigos
│
├── scripts/
│   └── INICIO_RAPIDO.md
│
├── src/                      # Backend Python (CÓDIGO PRINCIPAL)
│   ├── agents/              # Sistema de Agentes IA
│   │   ├── agno_agent.py    # Agente principal (Agno) - 11 tools integradas
│   │   ├── analysis_explainer.py
│   │   ├── api_doc_reader.py
│   │   ├── chart_generator.py
│   │   ├── trend_analyzer.py         # NOVO: Análise de tendências
│   │   ├── predictive_insights.py    # NOVO: Previsões e padrões
│   │   ├── alert_generator.py        # NOVO: Alertas e anomalias
│   │   ├── report_summarizer.py      # NOVO: Sumários executivos
│   │   ├── cache_manager.py          # NOVO: Cache híbrido
│   │   ├── monitoring.py             # NOVO: Audit logging
│   │   ├── core.py
│   │   ├── models.py
│   │   └── routes.py        # /agents/chat, /capabilities, /health
│   │
│   ├── analyses/            # Sistema de Análises
│   │   ├── dependencies.py
│   │   ├── models.py
│   │   ├── powerbi_dashboards.py
│   │   ├── routes.py
│   │   └── service.py
│   │
│   ├── auth/                # Autenticação
│   │   ├── dependencies.py  # get_current_user, get_current_admin_user
│   │   ├── models.py
│   │   ├── routes.py        # /auth/signup, /signin, /refresh
│   │   └── service.py
│   │
│   ├── integrations/        # Integrações APIs
│   │   ├── base_client.py
│   │   ├── cvdw/           # CVDW CRM
│   │   │   ├── client.py
│   │   │   └── __init__.py
│   │   ├── sienge/         # Sienge ERP
│   │   │   ├── client.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── users/              # Gestão de Usuários
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── __init__.py
│   │
│   ├── config.py           # Configurações (Pydantic Settings)
│   ├── supabase_client.py  # Factory Supabase
│   └── __init__.py
│
├── static/                 # Arquivos estáticos
├── supabase/              # Configurações Supabase
│   └── functions/
├── templates/             # Templates HTML
│
├── tests/                 # Testes automatizados
│   ├── conftest.py       # Fixtures pytest + acurácia
│   ├── test_auth.py      # 23 testes autenticação
│   ├── test_users.py     # 19 testes usuários
│   ├── e2e/              # Testes E2E Selenium
│   └── README.md
│
├── .env                  # Variáveis de ambiente (gitignored)
├── .env.example
├── .gitignore
├── api_credentials.env   # Credenciais APIs (gitignored)
├── logs/                # Logs do sistema
│   └── audit/          # NOVO: Audit logs com rotação
├── main.py              # Entry point FastAPI
├── pytest.ini
├── README.md
├── requirements.txt
├── requirements-test.txt
├── samples_cvdw.json
├── test_melhorias.py    # NOVO: Testes das melhorias v2.0
└── MELHORIAS_IMPLEMENTADAS.md  # NOVO: Documentação das melhorias
```

---

## Funcionalidades Implementadas COMPLETAS

### Fase 1: Autenticacao (COMPLETA)
- JWT tokens com renovação automática
- Signup, signin, signout, refresh token
- Reset de senha
- Proteção de rotas (frontend + backend)
- Middleware de autenticação
- **Status**: 100% funcional

### Fase 2: Gestao de Usuarios (COMPLETA)
- CRUD completo de usuários
- Sistema de 5 níveis de cargo (Master=5, Diretor=4, Gerente=3, Coordenador=2, Analista=1)
- Divisões organizacionais (COM, FIN, TI, RH, etc)
- RLS (Row Level Security) implementado
- Trigger automático de sincronização
- Interface admin-only
- **Status**: 100% funcional

### Fase 3: Sistema de Analises Power BI (COMPLETA)
- 3 Dashboards Power BI integrados:
  - Dashboard Compras (Financeiro)
  - Dashboard SDRs (Comercial)
  - Dashboard Pastas (Comercial)
- Controle de permissões granular (cargo + divisão)
- Interface responsiva com iframe embed
- APIs REST completas (GET, POST, PUT, DELETE)
- **Status**: 100% funcional

### Fase 6: Agentes IA (IMPLEMENTADA)
- Agente conversacional com Agno framework
- **11 ferramentas especializadas**:
  - find_api_endpoints: Busca endpoints em documentação
  - fetch_data_from_api: Consulta APIs (Sienge/CVDW)
  - query_raw_data: Consulta dados RAW com paginação
  - explain_analysis: Explica análises
  - generate_charts: Gera gráficos
  - **analyze_trends**: Análise de tendências temporais (NOVO)
  - **compare_periods**: Comparação entre períodos (NOVO)
  - **forecast_future**: Previsões com intervalos de confiança (NOVO)
  - **detect_anomalies**: Detecção estatística de anomalias (NOVO)
  - **generate_alerts**: Alertas automáticos de performance (NOVO)
  - **create_summary_report**: Sumários executivos automáticos (NOVO)
- LLM providers: Ollama (preferência) → Groq → OpenAI
- Fallback rule-based sem LLM
- Memória contextual de conversas (últimas 10 mensagens)
- Interface de chat no frontend
- Integração com CVDW e Sienge
- **Status**: Funcional e Aprimorado

### Fase 7: Performance & Cache (IMPLEMENTADA - v2.0)
- **Sistema de Cache Híbrido**:
  - Redis cache com fallback para In-Memory
  - TTL configurável por namespace
  - Invalidação seletiva
  - Estatísticas de uso (hit rate, memory usage)
- **Memória Contextual**:
  - Histórico de conversas por usuário
  - Até 10 mensagens armazenadas
  - TTL de 24 horas
  - Contexto automático em consultas
- **Audit Logging**:
  - Logs estruturados em JSON
  - Rotação diária automática
  - Retenção de 30 dias
  - Eventos: api_call, data_access, agent_query, security, error
- **Performance Monitoring**:
  - Métricas de tempo (avg, min, max, p95, p99)
  - Contadores personalizados
  - Histórico das últimas 1000 medições
- **Usage Tracking**:
  - Rastreamento de uso de APIs externas
  - Monitoramento de custos
  - Rate limiting por usuário
  - Relatórios de uso
- **Paginação Inteligente**:
  - Queries com offset e order_by
  - Contagem total de registros
  - Informações de navegação (next_offset, has_more)
- **Status**: 100% Funcional

### Integrações APIs (PARCIAL)
- **CVDW CRM**: Cliente completo, import diário via GitHub Actions
- **Sienge ERP**: Cliente base implementado, endpoints planejados
- **Power BI**: Dashboards via iframe (sem Azure AD)
- **Status**: CVDW funcional, Sienge planejado

### Sistema de Testes (COMPLETO)
- 48 testes unitários (87.5% acurácia)
- 42 testes integração
- Coverage: 46% código backend
- Pytest + fixtures completas
- Sistema de avaliação automática (threshold 85%)
- **Status**: Funcional

---

## Arquitetura Tecnica Detalhada

### Backend - Fluxos de Dados

#### Autenticacao Flow
1. **Signup**: POST /auth/signup → AuthService.sign_up() → Supabase Auth → Trigger cria perfil em public.usuarios
2. **Login**: POST /auth/signin → AuthService.sign_in() → Supabase Auth → Retorna JWT + User Data
3. **Refresh**: Interceptor detecta 401 → POST /auth/refresh → Novo access_token → Retenta requisição
4. **Protected Routes**: Header "Authorization: Bearer {token}" → get_current_user() → Valida JWT → Retorna UserResponse

#### Admin Authorization Flow
1. Rota protegida usa `Depends(get_current_admin_user)`
2. get_current_admin_user() chama get_current_user()
3. Busca nivel_acesso via LEFT JOIN com tabela cargos
4. Se nivel_acesso < 5: HTTPException 403
5. Se nivel_acesso >= 5: continua para endpoint

#### Agentes IA Flow
1. Usuário envia mensagem via POST /agents/chat
2. Sistema verifica permissões (cargo + divisão)
3. AgnoAgent determina intenção (vendas, financeiro, clientes)
4. Se LLM disponível: usa tools para consultar APIs
5. Se LLM indisponível: fallback rule-based
6. Retorna resposta + dados + gráficos + explicação

### Frontend - Fluxos de Dados

#### Estado Global (AuthContext)
```typescript
{
  user: { id, email, full_name, cargo_id, divisao_id, nivel_acesso } | null,
  loading: boolean,
  login: (credentials) => Promise,
  logout: () => Promise,
  signup: (userData) => Promise
}
```

#### Persistencia (AsyncStorage)
```typescript
access_token: string         // JWT access token
refresh_token: string        // JWT refresh token
user: JSON                   // Dados do usuário
```

#### Interceptor de Token (api/client.ts)
```typescript
Request Interceptor:
  - Adiciona header: Authorization: Bearer {access_token}

Response Interceptor:
  - Status 401?
    → Tenta refresh com refresh_token
    → Sucesso? Salva novo token e retenta
    → Falha? Limpa storage e navega para Login
```

### Database Schema (Supabase PostgreSQL)

#### Tabela: auth.users (Supabase Auth)
```sql
id: uuid (PK)
email: string
encrypted_password: string
email_confirmed_at: timestamp
created_at: timestamp
```

#### Tabela: public.usuarios
```sql
id: uuid (PK, FK -> auth.users.id)
email: string
full_name: string
cargo_id: int (FK -> cargos.id, nullable)
divisao_id: int (FK -> divisoes.id, nullable)
created_at: timestamp
updated_at: timestamp
```

#### Tabela: public.cargos
```sql
id: serial (PK)
nome: string (Master, Diretor, Gerente, Coordenador, Analista)
nivel_acesso: int (5, 4, 3, 2, 1)
ativo: boolean
```

#### Tabela: public.divisoes
```sql
id: serial (PK)
nome: string (Comercial, Financeiro, TI, RH, etc)
codigo: string (COM, FIN, TI, RH)
ativo: boolean
```

#### Tabela: public.analyses
```sql
id: serial (PK)
nome: string
descricao: text
tipo: string ('powerbi', 'python', 'tableau')
embed_url: text
divisao_restrita_id: int (FK -> divisoes.id, nullable)
publico: boolean
ativo: boolean
created_at: timestamp
```

#### Trigger: on_auth_user_created
```sql
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE FUNCTION handle_new_user();

-- Função: Cria perfil em public.usuarios automaticamente
-- Usa NULLIF para tratar cargo_id/divisao_id vazios
```

### Row Level Security (RLS)

**16 políticas implementadas** distribuídas em 4 tabelas:

#### Tabela cargos (2 políticas)
- `cargos_select`: Todos podem ler cargos ativos
- `cargos_manage`: Apenas nivel_acesso = 5 pode gerenciar

#### Tabela divisoes (2 políticas)
- `divisoes_select`: Todos podem ler divisões ativas
- `divisoes_manage`: Apenas nivel_acesso = 5 pode gerenciar

#### Tabela usuarios (6 políticas)
- `usuarios_own`: Ver próprio perfil
- `usuarios_high`: nivel_acesso >= 4 vê todos
- `usuarios_div`: Ver usuários da mesma divisão
- `usuarios_upd`: Atualizar apenas próprio perfil
- `usuarios_ins`: Apenas nivel_acesso = 5 pode criar
- `usuarios_del`: Apenas nivel_acesso = 5 pode deletar

#### Tabela analyses (6 políticas)
- `analyses_pub`: Todos veem análises públicas
- `analyses_div`: Ver análises da própria divisão
- `analyses_high`: nivel_acesso >= 4 vê todas
- `analyses_ins`: Apenas nivel_acesso = 5 pode criar
- `analyses_upd`: Apenas nivel_acesso = 5 pode atualizar
- `analyses_del`: Apenas nivel_acesso = 5 pode deletar

**CRÍTICO**: Todas as policies usam LEFT JOIN (não INNER JOIN) para tratar cargo_id/divisao_id NULL

---

## APIs Principais (FastAPI Endpoints)

### Autenticacao (/auth)
- `POST /auth/signup` - Registro de novos usuários
- `POST /auth/signin` - Login com email/senha
- `POST /auth/signout` - Logout
- `POST /auth/refresh` - Renovação de tokens JWT
- `GET /auth/me` - Dados do usuário autenticado
- `POST /auth/reset-password` - Solicitar reset de senha
- `POST /auth/update-password` - Atualizar senha

### Usuarios (/users) - Admin Only
- `GET /users` - Listar todos os usuários
- `PUT /users/{user_id}` - Atualizar cargo/divisão/role

### Analises (/analyses)
- `GET /analyses` - Listar análises acessíveis ao usuário
- `GET /analyses/{id}` - Visualizar análise específica
- `GET /analyses/powerbi-dashboards` - Dashboards Power BI
- `POST /analyses` - Criar análise (admin only)
- `PUT /analyses/{id}` - Atualizar análise (admin only)
- `DELETE /analyses/{id}` - Remover análise (admin only)

### Agentes IA (/agents)
- `POST /agents/chat` - Enviar mensagem ao agente
- `GET /agents/capabilities` - Listar capacidades do agente
- `GET /agents/health` - Status do agente

### Gerais
- `GET /` - Root da API
- `GET /health` - Health check
- `GET /docs` - Swagger UI (documentação)

---

## Integracoes Externas

### CVDW CRM (Completo)
- **Base URL**: https://bpincorporadora.cvcrm.com.br/api/v1/cvdw
- **Auth**: X-API-Key + email + token
- **Endpoints Implementados**:
  - /clientes - Base de clientes
  - /vendas, /oportunidades - Pipeline
  - /interactions - Histórico
  - /metrics/kpis - KPIs
  - /analytics/segmentation - Segmentação
  - /reports/* - Relatórios
- **Import Automático**: GitHub Actions diariamente às 3h UTC
- **Fallback**: Dados simulados se API falhar

### Sienge ERP (Planejado)
- **Base URL**: https://api.sienge.com.br
- **Auth**: Bearer token (Basic Auth alternativo)
- **Endpoints Planejados**:
  - /financeiro/contas-pagar
  - /financeiro/contas-receber
  - /vendas/pedidos
  - /estoque/produtos
  - /projetos
  - /relatorios

### Power BI Dashboards (Funcional)
- **Método**: Iframe embed direto (sem Azure AD)
- **Dashboards**:
  1. Dashboard Compras (Financeiro)
  2. Dashboard SDRs (Comercial)
  3. Dashboard Pastas (Comercial)
- **Controle**: Por cargo e divisão

---

## Configuracao de Ambiente

### Backend (.env)
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# Security
SECRET_KEY=xxx
ENVIRONMENT=development

# CVDW CRM
CVDW_BASE_URL=https://bpincorporadora.cvcrm.com.br/api/v1/cvdw
CVDW_API_KEY=xxx
CVDW_EMAIL=xxx
CVDW_ACCOUNT_ID=xxx

# Sienge ERP (opcional)
SIENGE_BASE_URL=https://api.sienge.com.br
SIENGE_API_KEY=xxx
SIENGE_USERNAME=xxx
SIENGE_PASSWORD=xxx

# Agentes IA (preferência: Ollama local)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
USE_OPENAI=false
OPENAI_API_KEY=xxx (opcional)
GROQ_API_KEY=xxx (opcional)
```

### Frontend (.env - frontend-rn)
```bash
EXPO_PUBLIC_API_URL=http://localhost:8000
```

---

## Como Executar o Sistema

### Backend
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
# ou
uvicorn main:app --reload

# Acesso: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Frontend (React Native + Expo)
```bash
cd frontend-rn

# Instalar dependências
npm install

# Executar (modo web)
EXPO_OFFLINE=1 npx expo start --web --port 8085

# Acesso: http://localhost:8085
```

### Testes
```bash
# Todos os testes
pytest tests/ -v

# Apenas backend
pytest tests/ --ignore=tests/e2e/ -v

# Apenas E2E
pytest tests/e2e/ -v

# Com coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Script automatizado
python run_tests.py
```

---

## Credenciais de Desenvolvimento

```
Email:  tiago.bocchino@4pcapital.com.br
Senha:  Admin123!@#

Cargo:   Administrador (nivel_acesso = 5)
Divisão: Comercial (COM)
```

---

## Proximas Fases (Planejadas)

### Fase 4: Analises Python Nativas
- Interface para criar análises Python customizadas
- Execução de scripts
- Visualização de resultados
- Editor de código integrado

### Fase 5: Dashboard Rico
- Dashboard com cards de métricas
- Gráficos e indicadores
- Widgets configuráveis
- Personalização por usuário

### Fase 7: Mais Integracoes
- Completar integração Sienge ERP
- Conectores com outros sistemas
- Sincronização de dados
- Automações e workflows

---

## Sistema de Testes Automatizados

### Estrutura
```
tests/
├── conftest.py              # Fixtures + sistema de acurácia
├── test_auth.py            # 23 testes autenticação
├── test_users.py           # 19 testes usuários
├── e2e/                    # Testes E2E Selenium
│   ├── conftest.py
│   ├── pages/              # Page Objects Pattern
│   ├── test_e2e_auth.py
│   └── test_e2e_users.py
└── README.md
```

### Métricas Atuais
- **Total de Testes**: 48 unitários + 42 integração + 10 melhorias = 100 testes
- **Acurácia**: 100% (melhorias v2.0) / 87.5% (geral)
- **Cobertura**: 46% código backend
- **Tempo**: ~2-5 minutos (testes gerais) / ~30s (melhorias)

### Workflow de Testes
```
1. Desenvolver funcionalidade
   ↓
2. Escrever testes
   ↓
3. Executar: python run_tests.py
   ↓
4. Avaliar acurácia
   ↓
5a. SE >= 85%: Prosseguir
5b. SE < 85%: Corrigir e voltar ao passo 3
```

---

## Historico de Mudancas Importantes

### 2025-12-12 - Migracao para React Native
- Frontend React/Vite arquivado na branch `lastro`
- Frontend-rn (Expo) se torna frontend principal
- Estrutura backend movida de `backend/` para `src/`
- Agentes IA implementados com Agno framework
- Integração CVDW CRM completa
- GitHub Actions para import automático

### 2024-12-09 - Sistema de Analises Power BI
- Implementadas 3 dashboards Power BI
- Sistema de permissões granular
- Interface de visualização com iframe
- APIs REST completas

### 2024-12-09 - Row Level Security
- 16 políticas RLS implementadas
- Correções críticas (LEFT JOIN, nivel_acesso)
- Trigger de sincronização automática
- Documentação completa de RLS

### 2024-12-08 - Sistema de Testes
- 48 testes unitários implementados
- Sistema de avaliação de acurácia (85%)
- Fixtures completas (backend + E2E)
- Page Objects Pattern para Selenium
- Scripts automatizados de execução

### 2024-12-05 - Gestao de Usuarios
- CRUD completo de usuários
- Sistema de roles (admin/user)
- Interface de gestão (admin-only)
- Middleware de autorização

### 2024-12-05 - Autenticacao Completa
- Sistema de autenticação end-to-end
- JWT com refresh automático
- Frontend React com rotas protegidas
- Backend FastAPI com Supabase Auth

---

## Convencoes de Codigo

### Backend (Python)
- PEP 8
- Type hints obrigatórios
- Docstrings em funções públicas
- Modelos Pydantic para validação
- Async/await para operações I/O

### Frontend (TypeScript)
- Componentes funcionais com hooks
- PascalCase para componentes
- camelCase para variáveis/funções
- Types explícitos sempre que possível
- Organização por features

---

## Documentacao Disponivel

### Principais
- **CLAUDE.md** - Este arquivo (contexto completo)
- **README.md** - Documentação geral
- **QUICK_START.md** - Guia de início rápido

### Técnica
- **TESTING_GUIDE.md** - Guia técnico de testes
- **SECURITY_AUDIT_REPORT.md** - Auditoria de segurança
- **API_INTEGRATIONS_SETUP.md** - Setup de integrações

### Setup
- **AI_AGENT_SETUP.md** - Setup dos agentes IA
- **AGENTS_PLANNING.md** - Planejamento detalhado
- **CREDENCIAIS.md** - Credenciais de acesso (gitignored)

### SQL
- **database/reset_from_scratch.sql** - Setup completo do zero
- **database/setup_rls.sql** - Políticas RLS
- **database/sync_users.sql** - Sincronização de usuários
- **database/setup_user_permissions.sql** - Permissões

---

## Status do Projeto

### Fases Completas
- Fase 1: Sistema de Autenticação
- Fase 2: Gestão de Usuários
- Fase 3: Sistema de Análises Power BI
- Fase 6: Agentes IA (básico)

### Em Desenvolvimento
- Integrações APIs (CVDW completo, Sienge em andamento)
- Agentes IA (melhorias e mais ferramentas)

### Planejadas
- Fase 4: Análises Python Nativas
- Fase 5: Dashboard Rico
- Fase 7: Mais Integrações

### Métricas
- **Linhas de código**: ~10k+ (backend + frontend)
- **Testes**: 90 testes (48 unit + 42 integration)
- **Acurácia**: 87.5%
- **Cobertura**: 46%
- **Arquivos Python**: ~30 módulos
- **Componentes React Native**: ~20 screens/components

---

## Regras de Trabalho (Nunca Quebrar)

1. **Nunca introduzir mudanças que quebrem funcionalidades estáveis**
   - Login, análises, dashboards, CORS devem sempre funcionar

2. **Ao ajustar novas features**
   - Preservar rotas/fluxos já validados
   - Preferir fallback seguro em caso de erro

3. **Sempre reiniciar backend/frontend após ajustes críticos**
   - Validar login e funcionalidades core

4. **Testes antes de deploy**
   - Acurácia >= 85% obrigatório
   - Testar fluxos completos end-to-end

5. **Documentação atualizada**
   - Manter CLAUDE.md sincronizado
   - Atualizar README quando necessário

---

## Workflow de Desenvolvimento Estabelecido

```
1. Mapeamento do Processo
   ↓
2. Desenvolvimento + Testes
   ↓
3. Validação (Acurácia >= 85%)
   ↓
4. Deploy no Git
   ↓
5. Backup Local (VersoesAnalytcs/v{X.X})
```

---

**Última Atualização**: 2025-12-12
**Atualizado por**: Claude (Sessão - Atualização Completa CLAUDE.md)
**Status Atual**: Sistema Validado e Funcionando

**Servidores**:
- Backend API: http://localhost:8000 (FastAPI + Supabase)
- Frontend React Native: http://localhost:8085 (Expo web)
- Documentação API: http://localhost:8000/docs (Swagger UI)

**Estado do Projeto**: PRODUÇÃO DESENVOLVIMENTO
- Sistema completo e funcional
- 3 fases principais implementadas
- Agentes IA operacionais
- Integrações CVDW funcionais
- CI/CD configurado
- Testes automatizados (87.5% acurácia)
- Pronto para expansão
