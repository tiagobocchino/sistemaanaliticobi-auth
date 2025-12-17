# Database Migrations - Performance Optimization

## Descrição
Este diretório contém scripts SQL para otimização de performance do banco de dados PostgreSQL no Supabase.

## Como Executar

### Opção 1: Via Supabase Dashboard
1. Acesse o Supabase Dashboard do seu projeto
2. Vá em "SQL Editor"
3. Clique em "New Query"
4. Copie e cole o conteúdo do arquivo `001_performance_optimization.sql`
5. Clique em "Run" para executar

### Opção 2: Via psql (linha de comando)
```bash
psql -h your-project.supabase.co -U postgres -d postgres -f 001_performance_optimization.sql
```

### Opção 3: Via Python (script automatizado)
```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

with open('001_performance_optimization.sql', 'r') as f:
    sql_script = f.read()
    # Execute via RPC ou diretamente
    supabase.rpc('exec_sql', {'query': sql_script})
```

## O que este script faz?

### 1. Índices Criados
- **vendas**: índices em data_venda, cliente_id, valor_venda, e compostos
- **produtos**: índices em categoria e nome (busca parcial)
- **clientes**: índices em divisao_id, status e nome
- **estoque**: índice em produto_id

### 2. Materialized Views
- **mv_kpis_mensais**: KPIs agregados por mês
- **mv_top_produtos**: Top 100 produtos por receita (90 dias)
- **mv_top_clientes**: Top 100 clientes por valor (180 dias)

### 3. Funções Úteis
- `refresh_kpis_mensais()`: Atualiza view de KPIs mensais
- `refresh_top_produtos()`: Atualiza view de top produtos
- `refresh_top_clientes()`: Atualiza view de top clientes
- `refresh_all_materialized_views()`: Atualiza todas as views

### 4. Views em Tempo Real
- **v_vendas_hoje**: Vendas do dia atual
- **v_alertas_estoque**: Alertas de estoque baixo

## Manutenção das Materialized Views

### Refresh Manual
```sql
-- Atualizar todas as views
SELECT refresh_all_materialized_views();

-- Ou individualmente
SELECT refresh_kpis_mensais();
SELECT refresh_top_produtos();
SELECT refresh_top_clientes();
```

### Agendamento Recomendado
- **mv_kpis_mensais**: Diariamente às 00:00
- **mv_top_produtos**: Semanalmente (domingo às 02:00)
- **mv_top_clientes**: Semanalmente (domingo às 03:00)

### Exemplo de Cronjob (via Supabase Edge Functions ou pg_cron)
```sql
-- Instalar pg_cron se disponível
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Agendar refresh diário de KPIs
SELECT cron.schedule(
    'refresh-kpis-daily',
    '0 0 * * *',
    'SELECT refresh_kpis_mensais();'
);

-- Agendar refresh semanal de produtos
SELECT cron.schedule(
    'refresh-produtos-weekly',
    '0 2 * * 0',
    'SELECT refresh_top_produtos();'
);

-- Agendar refresh semanal de clientes
SELECT cron.schedule(
    'refresh-clientes-weekly',
    '0 3 * * 0',
    'SELECT refresh_top_clientes();'
);
```

## Performance Esperada

### Antes da Otimização
- Query de KPIs mensais: ~2-5 segundos
- Query de top produtos: ~3-7 segundos
- Query de top clientes: ~4-8 segundos

### Após Otimização (com índices e materialized views)
- Query de KPIs mensais: ~50-100ms
- Query de top produtos: ~30-80ms
- Query de top clientes: ~30-80ms

**Ganho de Performance: 40-100x mais rápido**

## Monitoramento

### Verificar tamanho das views
```sql
SELECT
    schemaname,
    matviewname,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
FROM pg_matviews
WHERE matviewname LIKE 'mv_%'
ORDER BY pg_total_relation_size(schemaname||'.'||matviewname) DESC;
```

### Verificar último refresh
```sql
SELECT * FROM mv_refresh_log
ORDER BY refreshed_at DESC
LIMIT 10;
```

### Verificar uso de índices
```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

## Troubleshooting

### Erro: "relation already exists"
- Normal se você executar o script múltiplas vezes
- Use `IF NOT EXISTS` nas queries (já incluído no script)

### Erro: "permission denied"
- Certifique-se de estar usando o usuário correto (postgres ou service_role)

### View desatualizada
```sql
-- Force refresh
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_kpis_mensais;
```

### Performance ainda lenta
1. Verifique se os índices foram criados: `\di` no psql
2. Execute ANALYZE nas tabelas: `ANALYZE vendas;`
3. Verifique o plano de execução: `EXPLAIN ANALYZE SELECT ...`

## Rollback

Se precisar reverter as alterações:

```sql
-- Remover materialized views
DROP MATERIALIZED VIEW IF EXISTS mv_kpis_mensais CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_top_produtos CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_top_clientes CASCADE;

-- Remover índices
DROP INDEX IF EXISTS idx_vendas_data;
DROP INDEX IF EXISTS idx_vendas_cliente;
-- ... etc

-- Remover funções
DROP FUNCTION IF EXISTS refresh_kpis_mensais();
DROP FUNCTION IF EXISTS refresh_top_produtos();
DROP FUNCTION IF EXISTS refresh_top_clientes();
DROP FUNCTION IF EXISTS refresh_all_materialized_views();
```

## Próximos Passos

Após executar este script:
1. Execute o refresh inicial das views: `SELECT refresh_all_materialized_views();`
2. Configure o agendamento de refresh (cron)
3. Atualize sua aplicação para usar as materialized views
4. Monitore a performance e ajuste conforme necessário
