# 📦 Guia de Instalação - Analytics Platform

Guia completo para instalação e configuração do sistema.

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Instalação Passo a Passo](#instalação-passo-a-passo)
- [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
- [Configuração do Backend](#configuração-do-backend)
- [Configuração do Frontend](#configuração-do-frontend)
- [Configuração do LLM](#configuração-do-llm)
- [Configuração de Integrações](#configuração-de-integrações)
- [Verificação e Teste](#verificação-e-teste)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

### Obrigatórios

- ✅ **Python 3.11+** ([Download](https://www.python.org/downloads/))
- ✅ **Node.js 18+** ([Download](https://nodejs.org/))
- ✅ **Git** ([Download](https://git-scm.com/))
- ✅ **Conta no Supabase** ([Criar conta](https://app.supabase.com/))

### Opcionais (mas recomendados)

- ✅ **Ollama** ([Download](https://ollama.ai/download)) - Para LLM local
- ✅ **Redis** - Para cache em produção

### Verificar Instalações

```bash
# Verificar Python
python --version  # Deve ser 3.11 ou superior

# Verificar Node.js
node --version  # Deve ser 18 ou superior

# Verificar npm
npm --version

# Verificar Git
git --version
```

---

## 🚀 Instalação Passo a Passo

### 1. Clonar o Repositório

```bash
git clone <repo-url>
cd sistemaanalitico
```

### 2. Criar Ambiente Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências do Backend

```bash
pip install -r requirements.txt
```

### 4. Instalar Dependências do Frontend

```bash
cd frontend-rn
npm install
cd ..
```

---

## 🗄️ Configuração do Banco de Dados

### 1. Criar Projeto no Supabase

1. Acesse https://app.supabase.com/
2. Faça login ou crie uma conta
3. Clique em "New Project"
4. Preencha:
   - **Name**: Nome do seu projeto
   - **Database Password**: Senha forte (salve em local seguro!)
   - **Region**: Escolha a região mais próxima
5. Aguarde a criação do projeto (pode levar alguns minutos)

### 2. Obter Credenciais do Supabase

1. No painel do Supabase, vá em **Settings > API**
2. Copie as seguintes informações:
   - **Project URL** (ex: `https://xxxxx.supabase.co`)
   - **anon public** key
   - **service_role** key (⚠️ MANTENHA SECRETO!)

### 3. Executar Setup do Banco

1. No painel do Supabase, vá em **SQL Editor**
2. Clique em **New Query**
3. Abra o arquivo `database/reset_from_scratch.sql` do projeto
4. Copie todo o conteúdo e cole no SQL Editor
5. Execute o script (botão Run ou F5)

**O que este script faz:**
- ✅ Cria todas as tabelas necessárias
- ✅ Insere dados iniciais (cargos, divisões)
- ✅ Configura Row Level Security (RLS)
- ✅ Cria triggers de sincronização
- ✅ Insere dashboards Power BI iniciais

### 4. Configurar Permissões de Usuários (Opcional)

Execute o script `database/setup_user_permissions.sql` se precisar configurar permissões específicas.

---

## ⚙️ Configuração do Backend

### 1. Criar Arquivo .env

Na raiz do projeto, crie um arquivo `.env`:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 2. Preencher Variáveis de Ambiente

Edite o arquivo `.env` e preencha:

```env
# Supabase (OBRIGATÓRIO)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...  # anon public key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...  # service_role key

# Aplicação
SECRET_KEY=gere-uma-chave-secreta-aqui  # Veja abaixo como gerar
ENVIRONMENT=development

# LLM (OBRIGATÓRIO - escolha uma opção)
# Opção 1: Ollama (recomendado para local)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
AGENT_USE_AGNO=false
AGENT_LLM_TIMEOUT_SECONDS=60

# Opção 2: Groq
# GROQ_API_KEY=gsk_...
# GROQ_MODEL=mixtral-8x7b-32768

# Opção 3: OpenAI
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o-mini

# RAG (Opcional)
RAG_ENABLED=true
RAG_TOP_K=3
RAG_INDEX_PATH=data/rag_index.json

# Redis (Opcional - para cache)
# REDIS_URL=redis://localhost:6379/0

# Integrações (Opcional)
# CVDW_BASE_URL=https://sua-empresa.cvcrm.com.br/api/v1/cvdw
# CVDW_API_KEY=xxx
# CVDW_EMAIL=seu-email@empresa.com.br
# CVDW_ACCOUNT_ID=12345

# SIENGE_BASE_URL=https://api.sienge.com.br
# SIENGE_API_KEY=xxx
```

### 3. Gerar SECRET_KEY

```bash
# Windows PowerShell
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Linux/Mac
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copie o resultado e cole no `.env` como valor de `SECRET_KEY`.

### 4. Testar Backend

```bash
python main.py
```

O backend deve iniciar em `http://localhost:8000`. Teste acessando:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 🎨 Configuração do Frontend

### 1. Verificar Configuração

O frontend já está configurado para se conectar ao backend em `http://localhost:8000`. Se precisar alterar, edite:

```typescript
// frontend-rn/src/api/client.ts
const API_BASE_URL = 'http://localhost:8000';
```

### 2. Gerar Índice RAG (Opcional)

Se você ativou RAG, gere o índice:

```bash
python scripts/build_rag_index.py
```

Isso criará o arquivo `data/rag_index.json` com os documentos indexados.

### 3. Iniciar Frontend

```bash
cd frontend-rn

# Windows
set EXPO_OFFLINE=1
npx expo start --web --port 8085

# Linux/Mac
export EXPO_OFFLINE=1
npx expo start --web --port 8085
```

O frontend estará disponível em `http://localhost:8085`.

---

## 🤖 Configuração do LLM

O sistema precisa de um LLM (Large Language Model) para os agentes IA funcionarem. Escolha uma das opções:

### Opção 1: Ollama (Recomendado para Desenvolvimento Local)

**Vantagens:**
- ✅ Gratuito
- ✅ Roda localmente (privacidade total)
- ✅ Sem limite de requisições
- ✅ Funciona offline

**Instalação:**

1. **Baixe e instale Ollama**: https://ollama.ai/download
2. **Baixe o modelo:**
```bash
ollama pull llama3.2
```
3. **Verifique se está funcionando:**
```bash
curl http://localhost:11434/v1/models
```
4. **Configure no .env:**
```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
AGENT_USE_AGNO=false
AGENT_LLM_TIMEOUT_SECONDS=60
```

### Opção 2: Groq (Recomendado para Produção)

**Vantagens:**
- ✅ Gratuito (com limites generosos)
- ✅ Muito rápido (sem cold start)
- ✅ Não precisa instalar nada

**Configuração:**

1. Acesse https://console.groq.com/
2. Crie uma conta e faça login
3. Vá em **API Keys** > **Create API Key**
4. Copie a chave gerada
5. **Configure no .env:**
```env
GROQ_API_KEY=gsk_...
GROQ_MODEL=mixtral-8x7b-32768
```

### Opção 3: OpenAI (Alternativa Paga)

**Configuração:**

1. Acesse https://platform.openai.com/api-keys
2. Crie uma API key
3. **Configure no .env:**
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

---

## 🔗 Configuração de Integrações

### CVDW CRM

Se você tem acesso ao CVDW CRM:

1. Solicite as credenciais ao administrador
2. Preencha no `.env`:
```env
CVDW_BASE_URL=https://sua-empresa.cvcrm.com.br/api/v1/cvdw
CVDW_API_KEY=xxx
CVDW_EMAIL=seu-email@empresa.com.br
CVDW_ACCOUNT_ID=12345
```

### Sienge ERP

Se você tem acesso ao Sienge:

1. Solicite as credenciais ao administrador
2. Preencha no `.env`:
```env
SIENGE_BASE_URL=https://api.sienge.com.br
SIENGE_API_KEY=xxx
```

---

## ✅ Verificação e Teste

### 1. Verificar Backend

```bash
# Deve retornar {"status": "healthy"}
curl http://localhost:8000/health

# Deve abrir a documentação Swagger
# Abra no navegador: http://localhost:8000/docs
```

### 2. Verificar Frontend

1. Abra http://localhost:8085
2. Deve carregar a tela de login
3. Tente criar uma conta ou fazer login

### 3. Testar Autenticação

```bash
# Criar usuário
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "password": "senha123456",
    "full_name": "Teste Usuario"
  }'

# Fazer login
curl -X POST "http://localhost:8000/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "password": "senha123456"
  }'
```

### 4. Testar Agente IA

```bash
# Teste simples (com token de autenticação)
curl -X POST "http://localhost:8000/agents/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "message": "Quantas vendas temos?"
  }'
```

### 5. Executar Testes Automatizados

```bash
# Todos os testes
pytest tests/ -v

# Apenas testes das melhorias
python test_melhorias.py
```

---

## 🔧 Troubleshooting

### Problema: "Supabase connection failed"

**Solução:**
1. Verifique se `SUPABASE_URL` está correto
2. Verifique se as chaves estão corretas
3. Teste no Supabase Dashboard se o projeto está ativo
4. Verifique sua conexão com a internet

### Problema: "Ollama not responding"

**Solução:**
1. Verifique se Ollama está rodando:
```bash
curl http://localhost:11434/v1/models
```
2. Se não estiver, inicie o serviço:
```bash
ollama serve
```
3. Verifique se o modelo está instalado:
```bash
ollama list
```
4. Se não estiver, baixe:
```bash
ollama pull llama3.2
```

### Problema: "Frontend não conecta no backend"

**Solução:**
1. Verifique se backend está rodando em `http://localhost:8000`
2. Verifique CORS no backend (`src/config.py`)
3. Verifique se não há firewall bloqueando
4. Tente acessar `http://localhost:8000/health` diretamente no navegador

### Problema: "Module not found" no Python

**Solução:**
1. Certifique-se de que o ambiente virtual está ativado
2. Reinstale as dependências:
```bash
pip install -r requirements.txt
```

### Problema: "npm install falha"

**Solução:**
1. Delete `node_modules` e `package-lock.json`:
```bash
cd frontend-rn
rm -rf node_modules package-lock.json
```
2. Reinstale:
```bash
npm install
```

### Problema: "Token expired" ou erros de autenticação

**Solução:**
1. Faça logout e login novamente
2. Verifique se os tokens estão sendo renovados automaticamente
3. Verifique o console do navegador para erros

---

## 📋 Checklist Final

Antes de considerar a instalação completa:

- [ ] Python 3.11+ instalado
- [ ] Node.js 18+ instalado
- [ ] Projeto Supabase criado
- [ ] Banco de dados configurado (reset_from_scratch.sql executado)
- [ ] Arquivo `.env` criado e preenchido
- [ ] SECRET_KEY gerada e configurada
- [ ] LLM configurado (Ollama/Groq/OpenAI)
- [ ] Backend iniciando sem erros
- [ ] Frontend iniciando sem erros
- [ ] Teste de autenticação funcionando
- [ ] Agente IA respondendo (se LLM configurado)

---

## 🚀 Próximos Passos

Após instalação completa:

1. **Leia a documentação:**
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Entender a arquitetura
   - [docs/AI_AGENT_SETUP.md](docs/AI_AGENT_SETUP.md) - Configurar agentes IA
   - [docs/QUICK_START.md](docs/QUICK_START.md) - Início rápido

2. **Explore o sistema:**
   - Crie alguns usuários de teste
   - Teste os dashboards Power BI
   - Experimente o agente IA

3. **Personalize:**
   - Configure integrações (CVDW, Sienge)
   - Adicione mais dashboards
   - Customize permissões

---

**Última atualização:** 2025-12-19  
**Versão:** 2.1.0
