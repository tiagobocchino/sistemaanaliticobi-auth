# 🚀 Guia de Deploy no Render - Analytics Platform

Guia completo para fazer deploy do backend no Render.

## 📋 Sobre o Plano Free do Render

✅ **Boa notícia:** O plano free do Render permite múltiplos serviços separados!

- ✅ Você pode ter vários serviços web rodando simultaneamente
- ✅ Cada serviço roda em uma instância separada
- ⚠️ Limitações do plano free:
  - Serviços podem "dormir" após 15 minutos de inatividade
  - Cold start pode levar alguns segundos
  - 750 horas grátis por mês (suficiente para 1 serviço 24/7)
  - 512 MB RAM por serviço
  - Sem SSL customizado (mas HTTPS é fornecido)

## 🎯 Pré-requisitos

1. ✅ Conta no Render (já tem)
2. ✅ Código no GitHub (já está em `tiagobocchino/sistemaanaliticobi-auth`)
3. ✅ Variáveis de ambiente preparadas

## 📝 Passo a Passo

### 1. Preparar o Repositório

Certifique-se de que todos os arquivos estão commitados e no GitHub:

```bash
git status
git add .
git commit -m "Preparar para deploy no Render"
git push origin main
```

### 2. Criar Novo Serviço Web no Render

1. **Acesse:** https://dashboard.render.com/
2. **Clique em:** "New +" → "Web Service"
3. **Conecte seu repositório:**
   - Se ainda não conectou, clique em "Connect GitHub"
   - Autorize o Render a acessar seus repositórios
   - Selecione: `tiagobocchino/sistemaanaliticobi-auth`
4. **Configure o serviço:**
   - **Name:** `sistema-analitico-api` (ou o nome que preferir)
   - **Region:** Escolha a mais próxima (ex: `Oregon (US West)`)
   - **Branch:** `main`
   - **Root Directory:** (deixe vazio - raiz do projeto)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Configurar Variáveis de Ambiente

No painel do Render, vá em **Environment** e adicione todas as variáveis:

#### Obrigatórias:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
SECRET_KEY=sua-chave-secreta-aqui
ENVIRONMENT=production
```

#### LLM (escolha uma opção):

**Opção 1: Ollama (se tiver servidor próprio)**
```env
OLLAMA_BASE_URL=http://seu-servidor-ollama:11434/v1
OLLAMA_MODEL=llama3.2
AGENT_USE_AGNO=false
AGENT_LLM_TIMEOUT_SECONDS=60
```

**Opção 2: Groq (recomendado para produção)**
```env
GROQ_API_KEY=gsk_...
GROQ_MODEL=mixtral-8x7b-32768
```

**Opção 3: OpenAI**
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

#### Opcionais:

```env
REDIS_URL=redis://... (se usar Redis externo)
RAG_ENABLED=true
RAG_TOP_K=3
RAG_INDEX_PATH=data/rag_index.json
```

#### CORS (importante para produção):

```env
CORS_ORIGINS=["https://seu-frontend.com","https://outro-dominio.com"]
```

⚠️ **IMPORTANTE:** No Render, você precisa configurar CORS manualmente. Veja seção abaixo.

### 4. Ajustar CORS para Produção

O código atual permite apenas `localhost`. Precisamos ajustar para aceitar o domínio do Render e do seu frontend.

**Opção A: Usar variável de ambiente (recomendado)**

Edite `src/config.py` para aceitar CORS via variável de ambiente:

```python
# Adicione no Settings:
cors_origins_production: list[str] = []

# E ajuste o CORS no main.py para usar:
if settings.environment == "production":
    origins = settings.cors_origins_production
else:
    origins = settings.cors_origins
```

**Opção B: Configurar manualmente no Render**

Adicione no Render Environment:
```env
CORS_ORIGINS=["https://seu-frontend.onrender.com","https://seu-dominio.com"]
```

### 5. Deploy Automático

1. **Clique em:** "Create Web Service"
2. O Render vai:
   - Clonar o repositório
   - Instalar dependências (`pip install -r requirements.txt`)
   - Iniciar o serviço (`uvicorn main:app`)
3. **Aguarde** o build completar (pode levar 2-5 minutos)
4. **Verifique** os logs para garantir que iniciou corretamente

### 6. Verificar Deploy

Após o deploy, você terá uma URL como:
```
https://sistema-analitico-api.onrender.com
```

Teste os endpoints:

```bash
# Health check
curl https://sistema-analitico-api.onrender.com/health

# Root
curl https://sistema-analitico-api.onrender.com/

# Docs
# Acesse: https://sistema-analitico-api.onrender.com/docs
```

## 🔧 Configurações Adicionais

### Auto-Deploy

Por padrão, o Render faz deploy automático quando você faz push para a branch `main`.

Para desabilitar:
- Settings → Auto-Deploy → Desabilitar

### Health Checks

O Render usa o endpoint `/health` para verificar se o serviço está rodando.

Se o serviço não responder em 90 segundos, ele é reiniciado automaticamente.

### Logs

Acesse os logs em tempo real:
- Dashboard → Seu Serviço → Logs

Ou via CLI:
```bash
render logs -s sistema-analitico-api
```

## ⚠️ Considerações Importantes

### 1. Cold Start

No plano free, após 15 minutos de inatividade, o serviço "dorme". O primeiro request após isso pode levar 30-60 segundos.

**Soluções:**
- Usar serviço de ping (ex: UptimeRobot) para manter ativo
- Considerar upgrade para plano pago se necessário

### 2. Variáveis de Ambiente Sensíveis

⚠️ **NUNCA** commite variáveis sensíveis no código!

- Use sempre Environment Variables no Render
- O arquivo `.env` deve estar no `.gitignore`
- Use `render.yaml` apenas para variáveis não-sensíveis

### 3. Banco de Dados

O Supabase já é externo, então não precisa configurar banco no Render.

### 4. Redis (Opcional)

Se usar Redis:
- Use um serviço externo (ex: Upstash Redis - tem plano free)
- Configure `REDIS_URL` nas variáveis de ambiente

### 5. RAG Index

Se usar RAG:
- O arquivo `data/rag_index.json` precisa estar no repositório
- Ou gere durante o build usando build command:
  ```bash
  pip install -r requirements.txt && python scripts/build_rag_index.py
  ```

## 🐛 Troubleshooting

### Problema: Build falha

**Solução:**
1. Verifique os logs do build
2. Certifique-se de que `requirements.txt` está correto
3. Verifique se todas as dependências são compatíveis com Python 3.11

### Problema: Serviço não inicia

**Solução:**
1. Verifique os logs em tempo real
2. Certifique-se de que todas as variáveis de ambiente estão configuradas
3. Verifique se o `startCommand` está correto

### Problema: CORS bloqueando requests

**Solução:**
1. Configure `CORS_ORIGINS` com o domínio do frontend
2. Verifique se o frontend está usando a URL correta da API
3. Teste com `curl` para verificar se a API responde

### Problema: Timeout no agente IA

**Solução:**
1. Aumente `AGENT_LLM_TIMEOUT_SECONDS` (máx recomendado: 120)
2. Use Groq em vez de Ollama (mais rápido)
3. Verifique se o LLM está acessível do Render

## 📊 Monitoramento

### Métricas Disponíveis

No dashboard do Render você pode ver:
- CPU usage
- Memory usage
- Request count
- Response times

### Alertas

Configure alertas para:
- Serviço offline
- Alta utilização de memória
- Erros frequentes

## 🔄 Atualizações

Para atualizar o serviço:

1. Faça push para `main` no GitHub
2. O Render detecta automaticamente e faz deploy
3. Ou clique em "Manual Deploy" no dashboard

## 💰 Custos

**Plano Free:**
- ✅ Grátis para sempre
- ✅ 750 horas/mês (suficiente para 1 serviço 24/7)
- ⚠️ Serviços podem dormir após inatividade

**Se precisar de mais:**
- Plano Starter: $7/mês por serviço
- Sem cold start
- Mais recursos

## 📚 Recursos Adicionais

- [Documentação Render](https://render.com/docs)
- [Render Python Guide](https://render.com/docs/deploy-python)
- [Environment Variables](https://render.com/docs/environment-variables)

---

**Última atualização:** 2025-12-19  
**Versão:** 2.1.0
