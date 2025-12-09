# Quick Start Guide - Analytics Platform

Guia rápido para iniciar o projeto completo (Backend + Frontend).

## Pré-requisitos

- Python 3.8+ instalado
- Node.js 18+ e npm instalados
- Conta no Supabase configurada

## 1. Configuração do Backend

### Instalar dependências Python

```bash
# Criar e ativar ambiente virtual (opcional mas recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### Configurar variáveis de ambiente

O arquivo `.env` já está configurado com:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
ENVIRONMENT=development
```

### Iniciar o backend

```bash
# Opção 1: usando o arquivo main.py
python main.py

# Opção 2: usando uvicorn diretamente
uvicorn main:app --reload
```

O backend estará rodando em: **http://localhost:8000**

Documentação da API: **http://localhost:8000/docs**

## 2. Configuração do Frontend

### Instalar dependências Node

```bash
cd frontend
npm install
```

### Configurar variáveis de ambiente

O arquivo `frontend/.env` já está configurado:
```env
VITE_API_URL=http://localhost:8000
```

### Iniciar o frontend

```bash
# Ainda dentro da pasta frontend
npm run dev
```

O frontend estará rodando em: **http://localhost:5173**

## 3. Testar a Aplicação

### Usando a Interface Web

1. Acesse http://localhost:5173
2. Clique em "Criar Conta"
3. Preencha o formulário de cadastro
4. Você será redirecionado para o dashboard
5. Teste o logout e login novamente

### Usando o Script de Testes Python

Em outro terminal (com o backend rodando):

```bash
python test_api.py
```

Este script testa todos os endpoints de autenticação.

## Estrutura de URLs

| Serviço | URL | Descrição |
|---------|-----|-----------|
| Frontend | http://localhost:5173 | Interface React |
| Backend API | http://localhost:8000 | API FastAPI |
| Docs API | http://localhost:8000/docs | Documentação Swagger |
| Health Check | http://localhost:8000/health | Status da API |

## Rotas do Frontend

| Rota | Tipo | Descrição |
|------|------|-----------|
| `/` | Pública | Página inicial |
| `/login` | Pública | Login |
| `/signup` | Pública | Cadastro |
| `/dashboard` | Protegida | Dashboard (requer autenticação) |

## Fluxo Completo de Teste

### 1. Criar uma conta

```bash
# Via curl
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "password": "senha123456",
    "full_name": "Teste Usuario"
  }'
```

### 2. Fazer login

```bash
curl -X POST "http://localhost:8000/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "password": "senha123456"
  }'
```

Resposta incluirá:
- `access_token`: Token JWT para autenticação
- `refresh_token`: Token para renovar o access_token
- `user`: Dados do usuário

### 3. Acessar rota protegida

```bash
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN_AQUI"
```

## Troubleshooting

### Backend não inicia

- Verifique se as credenciais do Supabase estão corretas no `.env`
- Verifique se a porta 8000 não está em uso
- Verifique se todas as dependências Python foram instaladas

### Frontend não inicia

- Verifique se o Node.js está instalado: `node --version`
- Delete `node_modules` e reinstale: `rm -rf node_modules && npm install`
- Verifique se a porta 5173 não está em uso

### Erro de CORS

- Certifique-se de que o backend está rodando
- Verifique se `VITE_API_URL` no frontend aponta para o backend correto

### Token expirado

- O sistema renova automaticamente os tokens expirados
- Se persistir, faça logout e login novamente

## Próximos Passos

Após confirmar que tudo está funcionando:

1. Explore a documentação da API em http://localhost:8000/docs
2. Teste todas as funcionalidades de autenticação
3. Verifique o console do navegador para possíveis erros
4. Leia o arquivo `claude.md` para entender a arquitetura do projeto

## Comandos Úteis

```bash
# Backend
python main.py                    # Iniciar servidor
python test_api.py                # Testar endpoints
uvicorn main:app --reload         # Dev mode com hot reload

# Frontend
cd frontend
npm run dev                       # Dev mode
npm run build                     # Build de produção
npm run preview                   # Preview do build

# Git
git status                        # Ver mudanças
git add .                         # Adicionar tudo
git commit -m "mensagem"          # Commit
```

---

**Data**: 2024-12-05
**Status**: Sistema de autenticação completo e funcional
