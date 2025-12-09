# 🔐 CREDENCIAIS DO SISTEMA - Analytics Platform

## ✅ CREDENCIAIS ATUALIZADAS

**Email:** `tiago.bocchino@4pcapital.com.br`
**Senha:** `Admin123!@#`

**Status:** ✅ TESTADO E FUNCIONANDO

---

## 🚀 COMO FAZER LOGIN

### 1. Inicie o Sistema

**Terminal 1 - Backend:**
```bash
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 2. Acesse a Aplicação

```
http://localhost:5173/login
```

### 3. Faça Login

- **Email:** `tiago.bocchino@4pcapital.com.br`
- **Senha:** `Admin123!@#`

### 4. Veja os Dashboards

Após o login:
1. Clique em "📈 Power BI" na sidebar
2. Você verá **3 dashboards**:
   - ✅ Dashboard - Compras - DW
   - ✅ Dashboard - SDRs (TV) v2.0
   - ✅ Dashboard - Pastas

3. Clique em qualquer dashboard para visualizá-lo

---

## 👥 OUTROS USUÁRIOS

### Segundo Usuário (Teste)
**Email:** `tiago.bocchino@gmail.com`
**Senha:** *(precisa ser resetada se necessário)*

**Para resetar:**
```bash
# Edite o arquivo reset_password.py
# Altere o email na linha 13
# Execute:
python reset_password.py
```

---

## 🔧 SCRIPTS ÚTEIS

### Resetar Senha
```bash
python reset_password.py
```

### Testar Login
```bash
python test_login.py
```

### Diagnosticar Dashboards
```bash
python test_dashboards_simple.py
```

### Testar API
```bash
python test_api_dashboards.py
# (requer backend rodando em localhost:8000)
```

---

## 📊 PERMISSÕES DO USUÁRIO

**Cargo:** Administrador (nível 5)
**Divisão:** Comercial (COM)

**Dashboards Acessíveis:**
- ✅ Dashboard Compras (acesso por nível alto)
- ✅ Dashboard SDRs (acesso por divisão COM)
- ✅ Dashboard Pastas (acesso por divisão COM)

---

## ⚠️ PROBLEMAS COMUNS

### "Credenciais inválidas"
**Solução:** Execute `python reset_password.py`

### "Nenhum dashboard aparece"
**Possíveis causas:**
1. Backend não está rodando
2. Frontend não consegue conectar ao backend
3. Usuário sem cargo/divisão atribuídos

**Diagnóstico:**
```bash
python test_dashboards_simple.py
```

### "Erro ao carregar análises"
**Solução:**
1. Verifique se o backend está rodando em `localhost:8000`
2. Verifique o console do navegador (F12)
3. Verifique os logs do backend

---

## 📝 ÚLTIMAS ATUALIZAÇÕES

**Data:** 09/12/2024

**Alterações:**
1. ✅ Senha resetada para `Admin123!@#`
2. ✅ Corrigida query SQL em `src/analyses/service.py`
3. ✅ Login testado e funcionando
4. ✅ Scripts de diagnóstico criados

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Faça login com as credenciais acima
2. ✅ Acesse a página de análises
3. ✅ Verifique se os 3 dashboards aparecem
4. ✅ Clique em um dashboard para visualizá-lo
5. ✅ Confirme que o iframe do Power BI carrega

**Se tudo funcionar:** Sistema está 100% operacional! 🎉

**Se houver problemas:** Execute os scripts de diagnóstico acima.

---

**Última atualização:** 09 de dezembro de 2024, 14:30
