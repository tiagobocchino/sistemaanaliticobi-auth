# ⚡ EXECUTE ISSO AGORA (2 minutos)

## 🎯 Passo 1: Acesse o Supabase SQL Editor

**Link direto:**
```
https://supabase.com/dashboard/project/nzsnedvcggjvwydqpoqn/sql
```

---

## 📝 Passo 2: Cole Este Script SQL

```sql
CREATE INDEX IF NOT EXISTS idx_leads_raw ON leads USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_vendas_raw ON vendas USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_reservas_raw ON reservas USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_unidades_raw ON unidades USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_corretores_raw ON corretores USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_pessoas_raw ON pessoas USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_imobiliarias_raw ON imobiliarias USING GIN (raw);
CREATE INDEX IF NOT EXISTS idx_repasses_raw ON repasses USING GIN (raw);
```

---

## ▶️ Passo 3: Clique em "Run" ou pressione Ctrl+Enter

---

## ✅ Passo 4: Verificar (Opcional)

Cole e execute:
```sql
SELECT tablename, indexname
FROM pg_indexes
WHERE indexname LIKE 'idx_%_raw';
```

**Deve retornar 8 linhas** (uma para cada índice)

---

## 🎉 PRONTO!

Depois disso, teste o agente:
- "Quantos leads ativos temos?"

---

## ⏱️ Tempo total: 2 minutos
