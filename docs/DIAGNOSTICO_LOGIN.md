# 🔧 Guia de Diagnóstico - Login Quebrado

## Passo 1: Verificar se o Backend está Rodando

### Terminal 1 - Backend
```bash
cd c:\Users\tiago\OneDrive\Desktop\analytcs
python main.py
```

**O que você deve ver:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Se aparecer ERRO:**
- Verifique se o arquivo `.env` existe na raiz do projeto
- Verifique se as variáveis do Supabase estão corretas
- Execute: `python check_backend.py` para diagnóstico detalhado

---

## Passo 2: Verificar se o Frontend está Rodando

### Terminal 2 - Frontend
```bash
cd c:\Users\tiago\OneDrive\Desktop\analytcs\frontend
npm run dev
```

**O que você deve ver:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## Passo 3: Acessar a Página de Testes

Abra no navegador:
```
http://localhost:5173/test
```

Esta página vai testar automaticamente:
1. ✅ Conexão com o backend
2. ✅ Endpoints básicos
3. ✅ Teste de login
4. ✅ Endpoint de análises

---

## Passo 4: Verificar as Mensagens de Erro

### Se TODOS os testes falharam:

#### Erro: "Network Error" ou "ERR_CONNECTION_REFUSED"
**Problema:** Backend não está rodando
**Solução:**
1. Certifique-se de que o backend está rodando (Passo 1)
2. Verifique se está na porta 8000: `http://localhost:8000`
3. Tente acessar diretamente: `http://localhost:8000/health`

#### Erro: "CORS policy" ou "Blocked by CORS"
**Problema:** Backend não está permitindo requisições do frontend
**Solução:**
1. Verifique se o `CORS_ORIGINS` no `.env` inclui `http://localhost:5173`
2. Reinicie o backend após alterar o `.env`

#### Erro: "401 Unauthorized" no login
**Problema:** Credenciais inválidas ou usuário não existe
**Solução:**
1. Verifique se o usuário existe no Supabase
2. Tente criar o admin novamente: `python create_admin.py`
3. Senhas possíveis:
   - `4p@Supabase`
   - `Master123#`

#### Erro: "500 Internal Server Error"
**Problema:** Erro no backend (configuração, banco de dados, etc)
**Solução:**
1. Veja os logs no terminal do backend
2. Execute: `python check_backend.py`
3. Verifique se o `.env` está correto

---

## Passo 5: Executar Diagnóstico Completo

Execute o script de diagnóstico:
```bash
python check_backend.py
```

Este script vai verificar:
- ✅ Se o arquivo `.env` existe
- ✅ Se todas as variáveis estão configuradas
- ✅ Se os imports estão funcionando
- ✅ Se o backend está respondendo
- ✅ Se os endpoints estão funcionando

---

## Passo 6: Verificar o Arquivo .env

O arquivo `.env` deve estar na raiz do projeto e conter:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua_chave_anon_aqui
SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_aqui
SECRET_KEY=sua_secret_key_aleatoria_aqui
ENVIRONMENT=development
```

**⚠️ IMPORTANTE:**
- NUNCA commite o arquivo `.env` no Git
- As chaves do Supabase estão no painel do Supabase
- `SECRET_KEY` pode ser qualquer string aleatória (ex: `openssl rand -hex 32`)

---

## Passo 7: Testar Login Manualmente

### Via Navegador (Swagger)
1. Acesse: `http://localhost:8000/docs`
2. Vá para `/auth/signin`
3. Clique em "Try it out"
4. Preencha:
   ```json
   {
     "email": "tiago.bocchino@4pcapital.com.br",
     "password": "4p@Supabase"
   }
   ```
5. Execute e veja a resposta

### Via cURL
```bash
curl -X POST "http://localhost:8000/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"tiago.bocchino@4pcapital.com.br\",\"password\":\"4p@Supabase\"}"
```

---

## Passo 8: Verificar Console do Navegador

1. Abra o DevTools (F12)
2. Vá para a aba "Console"
3. Tente fazer login
4. Veja os erros no console

**Erros comuns:**
- `Failed to fetch` → Backend não está rodando
- `401 Unauthorized` → Credenciais inválidas
- `CORS error` → Problema de CORS no backend
- `Network Error` → Backend não está acessível

---

## Passo 9: Verificar Logs do Backend

No terminal onde o backend está rodando, você verá:
- ✅ Requisições bem-sucedidas
- ❌ Erros detalhados
- 🔍 Mensagens de debug

**Exemplo de log de erro:**
```
Login error for tiago.bocchino@4pcapital.com.br: Invalid credentials
```

---

## Checklist Final

Antes de reportar o problema, verifique:

- [ ] Backend está rodando (`python main.py`)
- [ ] Frontend está rodando (`npm run dev` no frontend/)
- [ ] Arquivo `.env` existe e está configurado
- [ ] Usuário existe no Supabase
- [ ] Porta 8000 está livre (backend)
- [ ] Porta 5173 está livre (frontend)
- [ ] Acessou `http://localhost:5173/test` e viu os resultados
- [ ] Executou `python check_backend.py` e viu os resultados

---

## Se NADA Funcionar

1. **Reinicie tudo:**
   ```bash
   # Pare o backend (Ctrl+C)
   # Pare o frontend (Ctrl+C)
   # Reinicie ambos
   ```

2. **Limpe e reinstale:**
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   rm -rf node_modules
   npm install
   ```

3. **Verifique a versão do Python:**
   ```bash
   python --version  # Deve ser 3.8 ou superior
   ```

4. **Verifique a versão do Node:**
   ```bash
   node --version  # Deve ser 16 ou superior
   ```

---

## Suporte

Se após seguir todos os passos o problema persistir:
1. Execute `python check_backend.py` e copie a saída completa
2. Acesse `http://localhost:5173/test` e copie todos os erros
3. Verifique os logs do backend e copie os erros
4. Envie todas essas informações para diagnóstico