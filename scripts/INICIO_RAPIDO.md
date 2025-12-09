# ⚡ GUIA DE INÍCIO RÁPIDO - Analytics Platform

## 🚀 **COMEÇAR EM 3 PASSOS:**

### **1️⃣ LIMPAR CACHE (Primeira vez ou se houver problemas)**

```bash
scripts/LIMPAR_TUDO.bat
```

**Depois:**
- Feche TODOS os navegadores
- Feche o Cursor/VS Code
- Reabra o Cursor

---

### **2️⃣ INICIAR SISTEMA**

```bash
scripts/INICIAR_SISTEMA.bat
```

**Vai abrir 2 terminais automaticamente:**
- ✅ Terminal 1: Backend (Python)
- ✅ Terminal 2: Frontend (React)

**Aguarde aparecer:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

### **3️⃣ ACESSAR NO NAVEGADOR**

**URL:**
```
http://localhost:5173/login
```

**Credenciais:**
```
Email:  tiago.bocchino@4pcapital.com.br
Senha:  Admin123!@#
```

**Após login:**
1. Clique em "📈 Power BI" na sidebar
2. Veja os 3 dashboards:
   - Dashboard - Compras - DW
   - Dashboard - SDRs (TV) v2.0
   - Dashboard - Pastas
3. Clique em qualquer um para visualizar

---

## 🔧 **INICIALIZAÇÃO MANUAL (Se preferir)**

### **Terminal 1 - Backend:**
```bash
cd C:\Users\tiago\OneDrive\Desktop\analytcs
python main.py
```

### **Terminal 2 - Frontend:**
```bash
cd C:\Users\tiago\OneDrive\Desktop\analytcs\frontend
npm run dev
```

### **Navegador:**
```
http://localhost:5173/login
```

---

## 🧪 **TESTAR SE ESTÁ FUNCIONANDO:**

```bash
python test_backend_live.py
```

**Resultado esperado:**
```
✅ Backend RODANDO
✅ Login OK
✅ DASHBOARDS RETORNADOS: 3
```

---

## ❌ **PROBLEMAS COMUNS:**

### **"Backend não está rodando"**
**Solução:**
```bash
python main.py
```

### **"Credenciais inválidas"**
**Solução:**
```bash
python reset_password.py
```

### **"Dashboards não aparecem"**
**Solução:**
```bash
scripts/LIMPAR_TUDO.bat
# Fechar navegadores
# Fechar Cursor
# Reabrir Cursor
scripts/INICIAR_SISTEMA.bat
```

### **"Erro ao fazer login"**
**Verificar:**
1. Backend está rodando? (Terminal 1 aberto)
2. Frontend está rodando? (Terminal 2 aberto)
3. Console do navegador (F12) tem erros?

---

## 📊 **ENDPOINTS DISPONÍVEIS:**

| Endpoint | URL | Descrição |
|----------|-----|-----------|
| **Frontend** | http://localhost:5173 | Aplicação React |
| **Backend API** | http://localhost:8000 | API FastAPI |
| **Docs (Swagger)** | http://localhost:8000/docs | Documentação interativa |
| **ReDoc** | http://localhost:8000/redoc | Documentação alternativa |

---

## 📁 **ESTRUTURA:**

```
analytcs/
├── scripts/LIMPAR_TUDO.bat              ← Limpar cache
├── scripts/INICIAR_SISTEMA.bat    ← Iniciar tudo
├── main.py                      ← Backend
├── frontend/                    ← Frontend React
├── src/                         ← Código backend
├── CREDENCIAIS.md               ← Credenciais
└── SESSAO_09_DEZ_2024_FINAL.md  ← Resumo completo
```

---

## 🎯 **FLUXO TÍPICO:**

```
1. scripts/LIMPAR_TUDO.bat
2. Fechar tudo
3. Reabrir Cursor
4. scripts/INICIAR_SISTEMA.bat
5. Aguardar servidores iniciarem
6. Abrir http://localhost:5173/login
7. Login: tiago.bocchino@4pcapital.com.br / Admin123!@#
8. Clicar em "📈 Power BI"
9. Ver dashboards!
```

---

## 📞 **SUPORTE:**

**Documentação Completa:**
- `CLAUDE.md` - Contexto geral do projeto
- `README.md` - Documentação principal
- `SESSAO_09_DEZ_2024_FINAL.md` - Resumo da última sessão
- `CREDENCIAIS.md` - Credenciais de acesso

**Scripts de Teste:**
- `test_backend_live.py` - Testar backend
- `test_login.py` - Testar autenticação
- `test_permissions_flow.py` - Testar permissões
- `check_performance.py` - Medir performance

---

**Última atualização:** 09 de dezembro de 2024
