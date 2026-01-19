# 🏗️ Arquitetura do Sistema - Analytics Platform

Documentação técnica da arquitetura e design do sistema.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura de Alto Nível](#arquitetura-de-alto-nível)
- [Backend](#backend)
- [Frontend](#frontend)
- [Banco de Dados](#banco-de-dados)
- [Sistema de Agentes IA](#sistema-de-agentes-ia)
- [Integrações](#integrações)
- [Segurança](#segurança)
- [Performance e Cache](#performance-e-cache)
- [Monitoramento e Logs](#monitoramento-e-logs)

---

## 🎯 Visão Geral

O **Analytics Platform** segue uma arquitetura moderna baseada em microserviços, com separação clara entre frontend, backend e serviços externos.

### Stack Tecnológico

**Backend:**
- FastAPI (Python 3.11+)
- Supabase (PostgreSQL + Auth)
- Redis (Cache opcional)
- Ollama/Groq/OpenAI (LLMs)

**Frontend:**
- React Native (TypeScript)
- Expo
- React Navigation

**IA e Análises:**
- Agno Framework (Agentes)
- RAG (BM25)
- Plotly/Matplotlib

---

## 🏛️ Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT (Browser/Mobile)                │
│                    React Native Web (Expo)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS/REST
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    FASTAPI BACKEND                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Auth     │  │   Users    │  │  Analyses  │           │
│  │   Routes   │  │   Routes   │  │   Routes   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                             │
│  ┌────────────────────────────────────────────┐            │
│  │        Agentes IA (Agno Framework)         │            │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐   │            │
│  │  │  RAG    │  │  Tools  │  │   LLM   │   │            │
│  │  │  Store  │  │ (11)    │  │ Ollama  │   │            │
│  │  └─────────┘  └─────────┘  └─────────┘   │            │
│  └────────────────────────────────────────────┘            │
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Cache    │  │ Integration│  │ Monitoring │           │
│  │  (Redis)   │  │  Clients   │  │   & Logs   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼──────┐ ┌─────▼────────┐
│   Supabase   │ │   Redis   │ │   Ollama     │
│ (PostgreSQL) │ │  (Cache)  │ │    (LLM)     │
│   + Auth     │ │           │ │              │
└──────────────┘ └───────────┘ └──────────────┘
        │
        │
┌───────▼───────────────────────────────┐
│      External APIs                     │
│  ┌──────────┐    ┌──────────┐        │
│  │   CVDW   │    │  Sienge  │        │
│  │   CRM    │    │   ERP    │        │
│  └──────────┘    └──────────┘        │
└───────────────────────────────────────┘
```

---

## 🔧 Backend

### Estrutura de Módulos

```
src/
├── auth/              # Autenticação e autorização
│   ├── models.py      # Modelos Pydantic
│   ├── service.py     # Lógica de negócio
│   ├── routes.py      # Endpoints REST
│   └── dependencies.py # Dependências FastAPI
│
├── users/             # Gestão de usuários
│   ├── models.py
│   ├── routes.py
│   └── dependencies.py
│
├── analyses/          # Sistema de análises
│   ├── models.py
│   ├── service.py
│   ├── routes.py
│   └── powerbi_dashboards.py
│
├── agents/            # Sistema de agentes IA
│   ├── agno_agent.py      # Agente principal
│   ├── rag_store.py       # RAG (BM25)
│   ├── trend_analyzer.py  # Análise de tendências
│   ├── predictive_insights.py # Previsões
│   ├── alert_generator.py     # Alertas
│   ├── report_summarizer.py   # Sumários
│   ├── cache_manager.py       # Cache híbrido
│   └── monitoring.py          # Monitoramento
│
├── integrations/      # Clientes de APIs externas
│   ├── base_client.py
│   ├── cvdw/
│   └── sienge/
│
├── cache/             # Sistema de cache
│   └── redis_manager.py
│
├── database/          # Cliente Supabase
│   ├── supabase_client.py
│   └── query_optimizer.py
│
├── utils/             # Utilitários
│   └── pagination.py
│
└── config.py          # Configuração (Settings)
```

### Princípios de Design

1. **Separation of Concerns**: Cada módulo tem responsabilidade única
2. **Dependency Injection**: Uso de dependências FastAPI
3. **Type Safety**: Pydantic para validação de dados
4. **Async/Await**: Operações assíncronas para performance
5. **Error Handling**: Tratamento centralizado de erros

### Fluxo de Autenticação

```
1. Cliente → POST /auth/signin
2. Backend → Supabase Auth (valida credenciais)
3. Supabase → Retorna tokens (access + refresh)
4. Backend → Cria/atualiza registro em public.usuarios
5. Backend → Retorna tokens ao cliente
6. Cliente → Armazena tokens (AsyncStorage)
7. Cliente → Inclui token em requisições (Authorization header)
8. Backend → Valida token via dependency (get_current_user)
```

### Row Level Security (RLS)

O sistema usa RLS do Supabase para controle granular de acesso:

- **16 políticas** implementadas
- Baseado em `nivel_acesso` (cargo) e `divisao_id`
- Aplicado automaticamente pelo Supabase
- Backend usa `service_role_key` para operações admin

---

## 🎨 Frontend

### Estrutura de Componentes

```
frontend-rn/
├── src/
│   ├── screens/           # Telas da aplicação
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── AnalysisList.tsx
│   │   ├── Agents.tsx
│   │   └── Users.tsx
│   │
│   ├── components/        # Componentes reutilizáveis
│   │   ├── Buttons/
│   │   ├── Forms/
│   │   ├── Chat/
│   │   └── Layout/
│   │
│   ├── context/           # Contextos React
│   │   └── AuthContext.tsx
│   │
│   ├── api/               # Cliente API
│   │   └── client.ts      # Axios com interceptors
│   │
│   ├── navigation/        # Navegação
│   │   ├── AuthStack.tsx
│   │   └── AppDrawer.tsx
│   │
│   └── theme/             # Tema
│       ├── colors.ts
│       └── theme.ts
```

### Estado Global

- **AuthContext**: Gerencia autenticação e usuário logado
- **AsyncStorage**: Persistência de tokens
- **Interceptors Axios**: Renovação automática de tokens

### Fluxo de Navegação

```
Login Screen
    ↓ (autenticado)
Dashboard (Home)
    ↓
├─→ Analysis List → Analysis View
├─→ Agents (Chat IA)
├─→ Users (Admin only)
└─→ Python Analyses (Planejado)
```

---

## 🗄️ Banco de Dados

### Schema Principal

```sql
-- Tabelas principais
usuarios           # Usuários do sistema
cargos             # Cargos (níveis de acesso)
divisoes           # Divisões organizacionais
analyses           # Análises/dashboards
audit_logs         # Logs de auditoria

-- Relacionamentos
usuarios.cargo_id → cargos.id
usuarios.divisao_id → divisoes.id
analyses.divisao_id → divisoes.id (nullable)
```

### Row Level Security (RLS)

**Políticas por tabela:**

**usuarios:**
- Ver próprio perfil: Qualquer usuário autenticado
- Ver todos: `nivel_acesso >= 4`
- Ver divisão: Mesma divisão
- Criar/Atualizar/Deletar: `nivel_acesso = 5`

**analyses:**
- Ver públicas: Todos
- Ver divisão: Mesma divisão
- Ver todas: `nivel_acesso >= 4`
- Criar/Atualizar/Deletar: `nivel_acesso = 5`

### Triggers

**sync_users:**
- Sincroniza `auth.users` → `public.usuarios`
- Executa automaticamente após INSERT/UPDATE em `auth.users`

---

## 🤖 Sistema de Agentes IA

### Arquitetura do Agente

```
User Question
    ↓
┌─────────────────────────────────┐
│   Agno Agent (agno_agent.py)   │
│                                 │
│  ┌──────────────────────────┐  │
│  │  RAG Store (BM25)        │  │
│  │  → Recupera contexto     │  │
│  └──────────────────────────┘  │
│           ↓                     │
│  ┌──────────────────────────┐  │
│  │  Tool Selection          │  │
│  │  → Escolhe ferramenta    │  │
│  └──────────────────────────┘  │
│           ↓                     │
│  ┌──────────────────────────┐  │
│  │  LLM (Ollama/Groq)       │  │
│  │  → Gera resposta         │  │
│  └──────────────────────────┘  │
│           ↓                     │
│  ┌──────────────────────────┐  │
│  │  Response Formatter      │  │
│  │  → Formata saída         │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
    ↓
Response to User
```

### Tools Disponíveis (11)

1. **query_raw_data** - Query direta no banco
2. **explain_analysis** - Explica análises
3. **generate_chart** - Gera gráficos
4. **analyze_trends** - Análise de tendências
5. **compare_periods** - Comparação de períodos
6. **forecast_future** - Previsões futuras
7. **detect_anomalies** - Detecção de anomalias
8. **generate_alerts** - Geração de alertas
9. **create_summary_report** - Sumários executivos
10. **read_api_docs** - Leitura de documentação de APIs
11. **llm_direct** - Resposta direta do LLM

### RAG (Retrieval-Augmented Generation)

- **Indexação**: BM25 local (sem dependências externas)
- **Armazenamento**: `data/rag_index.json`
- **Top-K**: 3 documentos por query (configurável)
- **Fonte**: Documentação em `docs/` e `README.md`

### Memória Contextual

- Últimas 10 mensagens mantidas em memória
- Persistida no cache (Redis ou In-Memory)
- Usada para contexto conversacional

---

## 🔗 Integrações

### CVDW CRM

```python
# src/integrations/cvdw/client.py
- Cliente HTTP assíncrono
- Autenticação via API Key
- Rate limiting implementado
- Tratamento de erros
```

### Sienge ERP

```python
# src/integrations/sienge/client.py
- Cliente HTTP assíncrono
- Autenticação OAuth (se necessário)
- Cache de resultados
```

### Power BI

```python
# src/analyses/powerbi_dashboards.py
- URLs de embed configuradas
- Controle de acesso por cargo/divisão
- 3 dashboards disponíveis
```

---

## 🔒 Segurança

### Autenticação

- **JWT Tokens**: Access + Refresh tokens
- **Expiração**: 30 minutos (access), 7 dias (refresh)
- **Renovação Automática**: Via interceptor no frontend
- **Hashing**: Senhas hasheadas pelo Supabase (bcrypt)

### Autorização

- **Row Level Security**: 16 políticas no Supabase
- **Backend Validation**: Verificação adicional no backend
- **Frontend Guards**: Proteção de rotas no frontend

### Segurança de Dados

- **Variáveis de Ambiente**: Credenciais nunca no código
- **CORS**: Configurado para origens específicas
- **HTTPS**: Obrigatório em produção
- **Rate Limiting**: Implementado nas APIs

---

## ⚡ Performance e Cache

### Sistema de Cache Híbrido

```
Request
    ↓
┌──────────────────────┐
│  Cache Manager       │
│                      │
│  1. Redis?           │ ← Tenta Redis primeiro
│  2. In-Memory?       │ ← Fallback para memória
│  3. Database/API     │ ← Se não encontrado
└──────────────────────┘
```

**Estratégia:**
- **Redis**: Produção (persistente, compartilhado)
- **In-Memory**: Desenvolvimento (fallback)
- **TTL**: Configurável por tipo de dado

### Otimizações

- **Paginação**: Offset + limit em queries grandes
- **Índices**: Índices criados em colunas frequentemente consultadas
- **Query Optimization**: Query optimizer no Supabase
- **Lazy Loading**: Carregamento sob demanda no frontend

---

## 📊 Monitoramento e Logs

### Audit Logging

```python
# src/agents/monitoring.py
- Logs estruturados (JSON)
- Rotação diária de arquivos
- Armazenamento: logs/audit/
- Rastreamento: operações críticas
```

### Métricas

- **Performance Monitor**: Tempo de resposta (avg, p95, p99)
- **Usage Tracker**: Uso de APIs externas
- **Error Tracking**: Erros e exceções
- **Health Checks**: Endpoint `/health`

### Logs

- **Estruturados**: JSON format
- **Níveis**: DEBUG, INFO, WARNING, ERROR
- **Rotação**: Diária (logs/audit/YYYY-MM-DD.log)
- **Análise**: Facilita debugging e auditoria

---

## 🔄 Fluxos Principais

### 1. Fluxo de Autenticação

```
Login → Validar → Tokens → Armazenar → Usar em Requests
```

### 2. Fluxo de Análise

```
Request → Validar Auth → Verificar Permissões → Query DB → Cache → Response
```

### 3. Fluxo de Agente IA

```
Question → RAG → Tool Selection → LLM → Format → Response → Cache
```

---

## 📈 Escalabilidade

### Horizontal Scaling

- **Stateless Backend**: Pode rodar múltiplas instâncias
- **Redis Shared**: Cache compartilhado entre instâncias
- **Supabase**: Escala automaticamente

### Vertical Scaling

- **Cache**: Redis para reduzir carga no banco
- **Async Operations**: Não bloqueia requisições
- **Connection Pooling**: Gerenciamento eficiente de conexões

---

## 🔮 Próximas Melhorias

1. **Microserviços**: Separar agentes IA em serviço próprio
2. **Message Queue**: Para processamento assíncrono
3. **WebSockets**: Para atualizações em tempo real
4. **CDN**: Para assets estáticos
5. **Load Balancer**: Para distribuição de carga

---

**Última atualização:** 2025-12-19  
**Versão:** 2.1.0
