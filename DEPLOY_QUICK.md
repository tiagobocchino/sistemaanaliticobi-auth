# ⚡ Deploy Rápido no Render

Guia rápido para deploy em 5 minutos.

## ✅ Checklist Rápido

- [ ] Código está no GitHub (`tiagobocchino/sistemaanaliticobi-auth`)
- [ ] Conta Render criada
- [ ] Variáveis de ambiente preparadas

## 🚀 Passos Rápidos

### 1. No Render Dashboard

1. **New +** → **Web Service**
2. Conecte repositório: `tiagobocchino/sistemaanaliticobi-auth`
3. Configure:
   - **Name:** `sistema-analitico-api`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2. Variáveis de Ambiente (Environment)

Adicione estas variáveis **obrigatórias**:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
SECRET_KEY=sua-chave-secreta
ENVIRONMENT=production
```

**LLM (escolha uma):**
```env
GROQ_API_KEY=gsk_...  # Recomendado
# OU
OLLAMA_BASE_URL=http://...
# OU
OPENAI_API_KEY=sk-...
```

**CORS (adicione seu frontend):**
```env
CORS_ORIGINS_PRODUCTION=https://seu-frontend.onrender.com,https://seu-dominio.com
```

### 3. Deploy

Clique em **Create Web Service** e aguarde!

### 4. Teste

Sua API estará em: `https://sistema-analitico-api.onrender.com`

Teste:
```bash
curl https://sistema-analitico-api.onrender.com/health
```

## 📚 Documentação Completa

Veja **[DEPLOY_RENDER.md](DEPLOY_RENDER.md)** para guia detalhado.

---

**Tempo estimado:** 5-10 minutos
