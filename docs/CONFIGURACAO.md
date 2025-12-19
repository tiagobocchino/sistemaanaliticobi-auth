# 🔧 GUIA DE CONFIGURAÇÃO - Analytics Platform

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Supabase](#supabase)
- [LLM (Ollama/Groq/OpenAI)](#llm-ollamagroqopenai)
- [Integrações](#integrações)
- [Segurança](#segurança)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Pré-requisitos

Antes de começar, você precisa ter instalado:

- ✅ Python 3.11+ ([Download](https://www.python.org/downloads/))
- ✅ Node.js 18+ ([Download](https://nodejs.org/))
- ✅ Git ([Download](https://git-scm.com/))
- ✅ Ollama ([Download](https://ollama.ai/download)) - Recomendado para LLM local

---

## ⚙️ Configuração do Ambiente

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/analytcs.git
cd analytcs
```

### 2. Crie o Arquivo .env

**IMPORTANTE:** Nunca commite o arquivo `.env` no git!

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas credenciais reais
# Windows:
notepad .env

# Linux/Mac:
nano .env
```

### 3. Instale as Dependências

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend-rn
npm install
cd ..
```

---

## 🗄️ Supabase

Supabase é nosso backend (banco de dados + autenticação).

### Como Obter as Credenciais:

1. **Acesse:** https://app.supabase.com/
2. **Login/Signup** com sua conta
3. **Crie um novo projeto** (se não tiver)
4. **Acesse:** Settings > API
5. **Copie:**
   - URL do projeto
   - Anon key (pública)
   - Service role key (PRIVADA - não compartilhe!)

### Preencha no .env:

```bash
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
```

### Database URL (Opcional - para migrações):

1. **Acesse:** Settings > Database
2. **Copie a senha** do banco (ou redefina se necessário)
3. **Formato:**
```bash
DATABASE_URL=postgresql://postgres:SUA-SENHA@db.seu-projeto.supabase.co:5432/postgres?sslmode=require
```

**ATENÇÃO:** Substitua `SUA-SENHA` pela senha real!

---

## 🤖 LLM (Ollama/Groq/OpenAI)

O agente IA precisa de um LLM (Large Language Model) para funcionar.

### Opção 1: Ollama (RECOMENDADO - Gratuito e Local)

**Vantagens:**
- ✅ Gratuito
- ✅ Roda localmente (privacidade total)
- ✅ Sem limite de requisições
- ✅ Rápido após carregar modelo

**Instalação:**

1. **Download:** https://ollama.ai/download
2. **Instale** o Ollama
3. **Baixe o modelo:**
```bash
ollama pull llama3.2
```
4. **Verifique se está rodando:**
```bash
curl http://localhost:11434/v1/models
```

**Configure no .env:**
```bash
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
AGENT_LLM_TIMEOUT_SECONDS=60
```

### Opção 2: Groq (OPCIONAL - Gratuito e Rápido)

**Vantagens:**
- ✅ Gratuito
- ✅ Muito rápido (sem cold start)
- ✅ Não precisa instalar nada

**Desvantagens:**
- ❌ Dados saem do seu servidor
- ❌ Limite de requisições (generoso, mas existe)

**Como obter:**
1. **Acesse:** https://console.groq.com/
2. **Signup/Login**
3. **API Keys** > Create API Key
4. **Copie a chave**

**Configure no .env:**
```bash
GROQ_API_KEY=gsk_...
GROQ_MODEL=mixtral-8x7b-32768
```

### Opção 3: OpenAI (OPCIONAL - Pago)

**Só use se:**
- ❌ Ollama não funcionar no seu servidor
- ❌ Groq estiver com limite

**Como obter:**
1. **Acesse:** https://platform.openai.com/api-keys
2. **Login** com conta OpenAI
3. **Create API Key**
4. **Copie a chave**

**Configure no .env:**
```bash
USE_OPENAI=true
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

---

## 🔗 Integrações

### CVDW CRM

Sistema de CRM para gestão de clientes e oportunidades.

**Como obter credenciais:**
1. Solicite ao **administrador do CVDW** da sua empresa
2. Você precisará de:
   - URL base da API
   - API Key
   - Email cadastrado
   - Account ID

**Configure no .env:**
```bash
CVDW_BASE_URL=https://sua-empresa.cvcrm.com.br/api/v1/cvdw
CVDW_API_KEY=3b10d5...
CVDW_EMAIL=seu-email@empresa.com.br
CVDW_ACCOUNT_ID=12345
```

### Sienge ERP (Opcional)

Sistema ERP para gestão empresarial.

**Como obter credenciais:**
1. Solicite ao **administrador do Sienge** da sua empresa
2. Você precisará de:
   - URL base da API
   - API Key (ou Username/Password)

**Configure no .env:**
```bash
# Descomente as linhas abaixo:
SIENGE_BASE_URL=https://api.sienge.com.br
SIENGE_API_KEY=sua-chave-aqui
```

---

## 🔒 Segurança

### Boas Práticas:

#### 1. SECRET_KEY

**NUNCA** use a chave padrão em produção!

**Gere uma chave segura:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Atualize no .env:**
```bash
SECRET_KEY=sua-chave-super-segura-gerada-aqui
```

#### 2. Arquivo .env

- ✅ **SIM:** Manter em `.gitignore`
- ❌ **NÃO:** Commitar no git
- ❌ **NÃO:** Compartilhar por email/slack
- ✅ **SIM:** Usar gerenciador de senhas para backup

#### 3. Permissões

- Use **SERVICE_ROLE_KEY** apenas no backend
- Nunca exponha chaves privadas no frontend
- Rotacione chaves regularmente em produção

#### 4. HTTPS em Produção

- Configure sempre HTTPS em produção
- Use certificados SSL válidos
- Configure CORS corretamente

---

## 🛠️ Troubleshooting

### Problema: "Supabase connection failed"

**Solução:**
1. Verifique se `SUPABASE_URL` está correta
2. Verifique se as chaves são válidas
3. Teste no Supabase Dashboard se o projeto está ativo

### Problema: "Ollama not responding"

**Solução:**
1. Verifique se Ollama está rodando:
```bash
curl http://localhost:11434/v1/models
```
2. Se não estiver, inicie:
```bash
ollama serve
```
3. Verifique se o modelo está baixado:
```bash
ollama list
```

### Problema: "CVDW API authentication failed"

**Solução:**
1. Verifique se `CVDW_API_KEY` está correta
2. Verifique se `CVDW_EMAIL` está cadastrado no sistema
3. Teste a API manualmente:
```bash
curl -H "X-API-Key: SUA-CHAVE" https://sua-empresa.cvcrm.com.br/api/v1/cvdw/clientes
```

### Problema: "Frontend não conecta no backend"

**Solução:**
1. Verifique se backend está rodando em `http://localhost:8000`
2. Verifique CORS no backend (`src/config.py`)
3. Verifique se frontend está usando a URL correta

---

## ✅ Checklist de Configuração

Antes de rodar o sistema, verifique:

- [ ] `.env` criado e preenchido
- [ ] Supabase configurado e testado
- [ ] Ollama instalado e rodando (ou Groq/OpenAI configurado)
- [ ] Dependências Python instaladas
- [ ] Dependências Node instaladas
- [ ] Banco de dados migrado (se necessário)
- [ ] SECRET_KEY gerada (não usar padrão)
- [ ] Integrações testadas (CVDW, Sienge se aplicável)

---

## 🚀 Próximos Passos

Após configurar tudo:

1. **Inicie o backend:**
```bash
python main.py
```

2. **Inicie o frontend:**
```bash
cd frontend-rn
set EXPO_OFFLINE=1  # Windows
export EXPO_OFFLINE=1  # Linux/Mac
npx expo start --web --port 8085
```

3. **Acesse:** http://localhost:8085

4. **Faça login** com credenciais de teste (se disponível) ou crie um novo usuário

---

## 📚 Documentação Adicional

- [JORNADA.md](../JORNADA.md) - História do projeto
- [CLAUDE.md](CLAUDE.md) - Contexto completo
- [README.md](../README.md) - Visão geral

---

## ❓ Precisa de Ajuda?

1. Verifique a [documentação completa](CLAUDE.md)
2. Revise os [logs de erro](../logs/)
3. Consulte o [histórico do projeto](../JORNADA.md)

---

**Última atualização:** 2025-12-19
**Versão:** 2.1.0
