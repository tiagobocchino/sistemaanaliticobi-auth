# 🔧 Instruções para Testar o Sistema

## ⚠️ PROBLEMA: Erro -102 ou Página Não Carrega

O erro -102 significa que o **frontend não está rodando** ou não está acessível.

## ✅ SOLUÇÃO: Iniciar o Frontend

### Passo 1: Abrir Terminal para o Frontend

Abra um **NOVO terminal** (mantenha o backend rodando no outro terminal) e execute:

```bash
cd C:\Users\tiago\OneDrive\Desktop\analytcs\frontend
```

### Passo 2: Instalar Dependências (se necessário)

Se for a primeira vez ou se houve mudanças:

```bash
npm install
```

### Passo 3: Iniciar o Frontend

```bash
npm run dev
```

### Passo 4: Verificar se Iniciou Corretamente

Você deve ver algo como:

```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Se aparecer isso, o frontend está rodando! ✅

### Passo 5: Acessar a Página de Testes

Agora acesse no navegador:

```
http://localhost:5173/test
```

## 📋 Resumo: Você Precisa de 2 Terminais

### Terminal 1 - Backend (já está rodando)
```bash
cd C:\Users\tiago\OneDrive\Desktop\analytcs
python main.py
```
**Status esperado:** `INFO: Uvicorn running on http://0.0.0.0:8000`

### Terminal 2 - Frontend (PRECISA INICIAR)
```bash
cd C:\Users\tiago\OneDrive\Desktop\analytcs\frontend
npm run dev
```
**Status esperado:** `Local: http://localhost:5173/`

## 🧪 Testar Manualmente

### 1. Testar Backend Direto no Navegador

Abra: http://localhost:8000/health

Deve aparecer:
```json
{"status":"healthy","environment":"development"}
```

### 2. Testar Frontend

Abra: http://localhost:5173/

Deve aparecer a página inicial do sistema.

### 3. Testar Página de Testes

Abra: http://localhost:5173/test

Deve aparecer a página de testes.

## 🐛 Problemas Comuns

### Frontend não inicia

**Erro:** `npm: command not found`
- **Solução:** Instalar Node.js: https://nodejs.org/

**Erro:** `Cannot find module`
- **Solução:** Execute `npm install` dentro da pasta `frontend`

**Erro:** Porta 5173 em uso
- **Solução:** Feche outros programas usando a porta ou mude a porta no `vite.config.js`

### Backend não inicia

**Erro:** `ModuleNotFoundError`
- **Solução:** Execute `pip install -r requirements.txt`

**Erro:** Porta 8000 em uso
- **Solução:** Feche outros programas usando a porta ou pare outros servidores Python

### Página carrega mas dá erro

1. Abra o Console do Navegador (F12 → Console)
2. Veja os erros em vermelho
3. Envie os erros para diagnóstico

## ✅ Checklist Final

- [ ] Backend rodando em http://localhost:8000
- [ ] Frontend rodando em http://localhost:5173
- [ ] Pode acessar http://localhost:5173/ (página inicial)
- [ ] Pode acessar http://localhost:5173/test (página de testes)
- [ ] Backend responde em http://localhost:8000/health

Se todos os itens estão marcados, o sistema está funcionando! 🎉
