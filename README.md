# Analytics Platform

Plataforma de autenticacao, dashboards Power BI e agente IA.

## Como rodar (dev)
1. Backend
```
cd C:\Users\tiago\OneDrive\Desktop\analytcs
python main.py
```
2. Frontend (React Native Web via Expo)
```
cd C:\Users\tiago\OneDrive\Desktop\analytcs\frontend-rn
set EXPO_OFFLINE=1
npx expo start --web --port 8085
```
3. Acessar
- URL: http://localhost:8085/?platform=web
- Login: tiago.bocchino@4pcapital.com.br / Admin123!@#

## Requisitos
- Python 3.8+
- Node 18+
- Ollama com modelo `llama3.2` (ou GROQ_API_KEY/OPENAI_API_KEY se preferir outro provedor)

## Estrutura
```
analytcs/
  src/           # backend FastAPI
  frontend-rn/   # frontend Expo React Native + TypeScript (web)
  docs/          # documentacao
  database/      # scripts SQL
  scripts/       # utilitarios
  lastro/        # arquivos obsoletos/backup
```

## CORS
Permitidos: http://localhost:3000, 5173, 5174, 8000, 8082, 8084, 8085.

## Branches
- main: backend + frontend-rn (atual)
- lastro: historico com frontend React/Vite legado

## Agente IA
- Endpoint: POST /agents/chat (usa token JWT de login)
- Modelo preferencial: Ollama `llama3.2` em http://localhost:11434/v1 (ou GROQ/OPENAI se configurados)

## Documentacao
- docs/CLAUDE.md (contexto)
- docs/CREDENCIAIS.md
- docs/SECURITY_AUDIT_REPORT.md
- docs/TESTING_GUIDE.md
- docs/AI_AGENT_SETUP.md
