# Correções do Agente RAG - 2025-12-19

## Problema Identificado

O agente RAG não estava respondendo adequadamente nas consultas, apresentando timeout constante mesmo com o Ollama rodando corretamente.

### Sintomas
- Timeout ao chamar o LLM (Ollama)
- Fallback para respostas baseadas em regras
- Mensagem de erro: `ReadTimeout`
- Agente aparentava estar processando mas não retornava respostas do LLM

### Causa Raiz

**Cold Start do Modelo Ollama**:
- Na primeira chamada (ou após período de inatividade), o Ollama precisa carregar o modelo na memória
- Este processo pode levar 30+ segundos
- O timeout original de 30s não era suficiente para o cold start
- Chamadas subsequentes são rápidas (~5s) com o modelo já carregado

## Soluções Implementadas

### 1. Aumento do Timeout Base
**Arquivo**: `src/config.py` e `.env`
- Timeout aumentado de 30s para 60s
- Permite tempo suficiente para cold start do modelo
- Chamadas normais continuam rápidas

```python
# Antes
agent_llm_timeout_seconds: int = 30

# Depois
agent_llm_timeout_seconds: int = 60  # Aumentado para 60s (cold start do modelo)
```

### 2. Sistema de Retry Inteligente
**Arquivo**: `src/agents/agno_agent.py:252-305`

Implementado retry automático com:
- Até 3 tentativas por consulta
- Timeout progressivo (60s → 90s → 135s)
- Delay entre tentativas (1s)
- Logging detalhado para debug

```python
async def _llm_direct_response(self, query: str, system_prompt: str, retry_count: int = 2) -> Optional[str]:
    for attempt in range(retry_count + 1):
        try:
            print(f"[INFO] Tentativa {attempt + 1}/{retry_count + 1} de chamar Ollama (timeout: {timeout_s}s)...")
            # ... código de chamada ...
            if content:
                print(f"[SUCCESS] Ollama respondeu com sucesso (tentativa {attempt + 1})")
            return content or None
        except httpx.ReadTimeout as e:
            if attempt < retry_count:
                timeout_s = int(timeout_s * 1.5)  # Aumenta timeout progressivamente
                await asyncio.sleep(1)
            else:
                print(f"[ERROR] Todas as {retry_count + 1} tentativas falharam")
```

### 3. Warm-up Automático na Inicialização
**Arquivo**: `src/agents/agno_agent.py:896-921`

Adicionado warm-up do modelo ao iniciar o servidor:
- Faz uma chamada simples de teste
- Carrega o modelo na memória do Ollama
- Primeira requisição real do usuário já encontra modelo carregado
- Reduz latência percebida pelo usuário

```python
async def initialize(self):
    # ... código existente ...

    # Warm-up do modelo LLM (carrega na memoria)
    if self.llm:
        print("\n[INFO] Fazendo warm-up do modelo LLM...")
        try:
            warmup_response = await self._llm_direct_response(
                query="ola",
                system_prompt="Voce e um assistente. Responda apenas 'ok'.",
                retry_count=1
            )
            if warmup_response:
                print("[SUCCESS] Modelo LLM aquecido e pronto para uso!")
```

### 4. Logging Aprimorado

Adicionado logs informativos em cada etapa:
- `[INFO]`: Tentativas de conexão
- `[WARN]`: Timeouts (com número da tentativa)
- `[SUCCESS]`: Respostas bem-sucedidas
- `[ERROR]`: Falhas definitivas

Facilita debug e monitoramento do comportamento do agente.

## Resultados dos Testes

### Antes das Correções
```
[ERROR] LLM direto falhou: ReadTimeout:
Success: True
Tools usadas: ['fallback_rule_based']
```

### Depois das Correções
```
[INFO] Tentativa 1/3 de chamar Ollama (timeout: 60s)...
[WARN] Timeout na tentativa 1/3
[INFO] Aumentando timeout para 90s na proxima tentativa...
[INFO] Tentativa 2/3 de chamar Ollama (timeout: 90s)...
[SUCCESS] Ollama respondeu com sucesso (tentativa 2)
Success: True
Tools usadas: ['llm_direct']
RAG sources: 3 documentos
```

## Benefícios

1. **Resiliência**: Sistema lida graciosamente com cold start
2. **Performance**: Warm-up reduz latência percebida
3. **Debug**: Logs claros facilitam diagnóstico
4. **Fallback**: Se LLM falhar, ainda usa sistema baseado em regras
5. **Escalabilidade**: Timeout progressivo se adapta à carga

## Configuração Recomendada

### Variáveis de Ambiente (.env)
```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
AGENT_LLM_TIMEOUT_SECONDS=60  # Mínimo recomendado para cold start

# RAG Configuration (já existentes)
RAG_ENABLED=true
RAG_TOP_K=3
RAG_INDEX_PATH=data/rag_index.json
```

### Verificação de Saúde do Ollama

Sempre verificar se o Ollama está rodando antes de iniciar o servidor:

```bash
# Verificar se está rodando
curl http://localhost:11434/v1/models

# Verificar modelos disponíveis
# Deve retornar: {"object":"list","data":[{"id":"llama3.2:latest",...}]}
```

## Próximos Passos (Opcionais)

1. **Monitoramento**: Adicionar métricas de tempo de resposta do Ollama
2. **Cache de Modelo**: Manter modelo sempre carregado (script separado)
3. **Health Check**: Endpoint para verificar status do Ollama
4. **Fallback Inteligente**: Se Ollama falhar, tentar Groq/OpenAI automaticamente

## Arquivos Modificados

- `src/config.py` - Aumentado timeout padrão
- `.env` - Atualizado AGENT_LLM_TIMEOUT_SECONDS
- `src/agents/agno_agent.py` - Retry logic + warm-up + logging
  - Linha 252-305: `_llm_direct_response()` com retry
  - Linha 896-921: `initialize()` com warm-up

## Compatibilidade

- ✅ Mantém compatibilidade com fallback rule-based
- ✅ Não quebra funcionalidades existentes
- ✅ RAG continua funcionando normalmente
- ✅ Todas as 11 tools continuam disponíveis

## Status

- [x] Problema identificado
- [x] Solução implementada
- [x] Testes realizados
- [x] Documentação criada
- [x] Sistema funcionando corretamente

**Data**: 2025-12-19
**Versão**: 2.1 (patch)
**Status**: ✅ Resolvido e Testado
