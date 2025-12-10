# Analytics Platform

Plataforma para administração de acessos às análises da empresa.

[![Status](https://img.shields.io/badge/Status-Produção%20Ready-green.svg)]()
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)]()
[![React](https://img.shields.io/badge/React-18+-blue.svg)]()
[![Supabase](https://img.shields.io/badge/Supabase-Cloud-orange.svg)]()

## Início Rápido

1) Limpar cache
```
./scripts/LIMPAR_TUDO.bat
```

2) Iniciar sistema
```
./scripts/INICIAR_SISTEMA.bat
```

3) Acessar
- URL: http://localhost:5173/login
- Email: tiago.bocchino@4pcapital.com.br
- Senha: Admin123!@#

4) Agentes IA
- Pré-requisito: Ollama com `llama3.2` (`ollama pull llama3.2`) ou `OPENAI_API_KEY`/`GROQ_API_KEY`.
- Frontend: http://localhost:5173/agents
- Backend: POST /agents/chat (usar token JWT de login)

## Estrutura do Projeto
```
analytcs/
  docs/          # Documentação
  scripts/       # Scripts de inicialização e utilitários
  database/      # SQL e migrações
  tests/         # Testes automatizados
  frontend/      # React + Vite
  src/           # Backend FastAPI
  static/        # Arquivos estáticos
  lastro/        # Arquivos obsoletos/backup (não usados em runtime)
```

## Documentação
- [CLAUDE.md](docs/CLAUDE.md) – Contexto e arquitetura
- [CREDENCIAIS.md](docs/CREDENCIAIS.md) – Acessos e logins
- [SECURITY_AUDIT_REPORT.md](docs/SECURITY_AUDIT_REPORT.md) – Auditoria
- [TESTING_GUIDE.md](docs/TESTING_GUIDE.md) – Guia de testes
- [AI_AGENT_SETUP.md](docs/AI_AGENT_SETUP.md) – Guia do agente IA

## Funcionalidades
- Autenticação completa (Supabase Auth + JWT)
- Gestão de usuários (admin)
- Dashboards Power BI (Compras, SDRs, Pastas) com controle por cargo/divisão
- Chat de Agentes IA em `/agents` consumindo `/agents/chat`
- Testes automatizados (backend + E2E)

## Stack
- Backend: Python 3.8+, FastAPI, Supabase (PostgreSQL + Auth), Pydantic, Pytest
- Frontend: React 18, Vite, React Router, Axios com interceptors, CSS

## Deploy/Produção
- CORS restrito a 3000/5173/5174/8000
- Variáveis sensíveis em .env / api_credentials.env (não versionar)
- Agentes IA: usar Ollama ou chaves OpenAI/Groq

## Suporte
- Criado por: Grok Code Assistant
- Data: Dezembro 2025
- Status: SISTEMA COMPLETO E FUNCIONAL
