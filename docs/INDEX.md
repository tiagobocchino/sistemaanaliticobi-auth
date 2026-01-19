# 📚 Índice de Documentação - Analytics Platform

Guia para navegar pela documentação do projeto.

## 📋 Estrutura da Documentação

### 🚀 Documentação Principal

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[../README.md](../README.md)** | Visão geral do projeto | Primeira leitura, entender o que é o projeto |
| **[../INSTALL.md](../INSTALL.md)** | Guia completo de instalação | Ao instalar o sistema pela primeira vez |
| **[../ARCHITECTURE.md](../ARCHITECTURE.md)** | Arquitetura técnica | Para entender como o sistema funciona internamente |

### 🎯 Guias Práticos

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[QUICK_START.md](QUICK_START.md)** | Início rápido | Para começar rapidamente |
| **[CONFIGURACAO.md](CONFIGURACAO.md)** | Configuração detalhada | Para configurar todas as partes do sistema |
| **[AI_AGENT_SETUP.md](AI_AGENT_SETUP.md)** | Setup dos agentes IA | Para configurar e usar os agentes de IA |

### 🔒 Segurança e Testes

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)** | Auditoria de segurança | Para entender aspectos de segurança |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | Guia de testes | Para executar e escrever testes |

### 🔧 Documentação Técnica

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[API_INTEGRATIONS_SETUP.md](API_INTEGRATIONS_SETUP.md)** | Integração com APIs externas | Para integrar CVDW, Sienge, etc. |
| **[INSTRUCOES_RLS.md](INSTRUCOES_RLS.md)** | Row Level Security | Para entender permissões no banco |
| **[INSTRUCOES_SUPABASE_TRIGGER.md](INSTRUCOES_SUPABASE_TRIGGER.md)** | Triggers do Supabase | Para entender sincronização de usuários |
| **[INSTRUCOES_TESTE.md](INSTRUCOES_TESTE.md)** | Instruções de teste | Para testar funcionalidades específicas |

### 📖 Documentação de Contexto

| Documento | Descrição | Quando Usar |
|-----------|-----------|-------------|
| **[CLAUDE.md](CLAUDE.md)** | Contexto completo do projeto | Para entender a história e contexto |
| **[AGENTS_PLANNING.md](AGENTS_PLANNING.md)** | Planejamento dos agentes | Para entender a evolução dos agentes IA |
| **[CREDENCIAIS.md](CREDENCIAIS.md)** | Informações de credenciais | ⚠️ **PRIVADO** - Não commitar! |

### 📝 Documentos Legados (Referência)

| Documento | Descrição | Status |
|-----------|-----------|--------|
| **[../JORNADA.md](../JORNADA.md)** | Diário de desenvolvimento | Histórico |
| **[../MELHORIAS_IMPLEMENTADAS.md](../MELHORIAS_IMPLEMENTADAS.md)** | Melhorias implementadas | Histórico |
| **[../RESUMO_SESSAO_19-12-2025.md](../RESUMO_SESSAO_19-12-2025.md)** | Resumo de sessão | Histórico |
| **[../CORRECOES_AGENTE_RAG.md](../CORRECOES_AGENTE_RAG.md)** | Correções do agente RAG | Histórico |

---

## 🎯 Fluxos de Leitura Recomendados

### Para Novos Desenvolvedores

1. **[README.md](../README.md)** - Entender o projeto
2. **[INSTALL.md](../INSTALL.md)** - Instalar o sistema
3. **[QUICK_START.md](QUICK_START.md)** - Começar a usar
4. **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Entender a arquitetura

### Para Configurar o Sistema

1. **[INSTALL.md](../INSTALL.md)** - Instalação base
2. **[CONFIGURACAO.md](CONFIGURACAO.md)** - Configuração detalhada
3. **[AI_AGENT_SETUP.md](AI_AGENT_SETUP.md)** - Configurar agentes IA
4. **[API_INTEGRATIONS_SETUP.md](API_INTEGRATIONS_SETUP.md)** - Integrações

### Para Entender Segurança

1. **[SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)** - Auditoria
2. **[INSTRUCOES_RLS.md](INSTRUCOES_RLS.md)** - Row Level Security
3. **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Seção de Segurança

### Para Desenvolver Novas Features

1. **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Arquitetura do sistema
2. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Como testar
3. **[CLAUDE.md](CLAUDE.md)** - Contexto completo

---

## 🔍 Busca Rápida

### Por Tópico

#### Autenticação
- **Como funciona**: [ARCHITECTURE.md](../ARCHITECTURE.md#fluxo-de-autenticação)
- **Como configurar**: [INSTALL.md](../INSTALL.md#configuração-do-backend)
- **Troubleshooting**: [INSTALL.md](../INSTALL.md#troubleshooting)

#### Agentes IA
- **O que são**: [README.md](../README.md#agentes-ia-avançados)
- **Como configurar**: [AI_AGENT_SETUP.md](AI_AGENT_SETUP.md)
- **Arquitetura**: [ARCHITECTURE.md](../ARCHITECTURE.md#sistema-de-agentes-ia)

#### Banco de Dados
- **Schema**: [ARCHITECTURE.md](../ARCHITECTURE.md#banco-de-dados)
- **Setup**: [INSTALL.md](../INSTALL.md#configuração-do-banco-de-dados)
- **RLS**: [INSTRUCOES_RLS.md](INSTRUCOES_RLS.md)

#### Integrações
- **APIs externas**: [API_INTEGRATIONS_SETUP.md](API_INTEGRATIONS_SETUP.md)
- **CVDW**: [API_INTEGRATIONS_SETUP.md](API_INTEGRATIONS_SETUP.md#cvdw-crm)
- **Sienge**: [API_INTEGRATIONS_SETUP.md](API_INTEGRATIONS_SETUP.md#sienge-erp)

#### Performance
- **Cache**: [ARCHITECTURE.md](../ARCHITECTURE.md#performance-e-cache)
- **Otimizações**: [ARCHITECTURE.md](../ARCHITECTURE.md#otimizações)
- **Métricas**: [ARCHITECTURE.md](../ARCHITECTURE.md#monitoramento-e-logs)

---

## 📞 Suporte

Se você não encontrar o que procura:

1. **Verifique os logs**: `logs/audit/`
2. **Consulte o histórico**: [JORNADA.md](../JORNADA.md)
3. **Revise a configuração**: [CONFIGURACAO.md](CONFIGURACAO.md)

---

**Última atualização:** 2025-12-19  
**Mantido por:** Equipe de Desenvolvimento
