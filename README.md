# Analytics Platform API

Sistema de analytics com autenticação completa usando FastAPI e Supabase.

## Estrutura do Projeto

```
analytcs/
├── src/
│   ├── auth/              # Módulo de autenticação
│   │   ├── __init__.py
│   │   ├── models.py      # Modelos Pydantic
│   │   ├── service.py     # Serviço de autenticação
│   │   ├── routes.py      # Endpoints FastAPI
│   │   └── dependencies.py # Dependências/middleware
│   ├── users/             # Módulo de usuários
│   ├── dashboards/        # Módulo de dashboards
│   ├── analysis/          # Módulo de análises
│   │   ├── python/        # Análises Python
│   │   └── powerbi/       # Integração Power BI
│   ├── config.py          # Configurações da aplicação
│   └── supabase_client.py # Cliente Supabase
├── static/                # Arquivos estáticos
├── templates/             # Templates HTML
├── tests/                 # Testes
├── data/                  # Dados
├── main.py               # Aplicação principal
├── requirements.txt      # Dependências
├── .env                  # Variáveis de ambiente (não commitado)
└── .gitignore           # Arquivos ignorados pelo git
```

## Instalação

### 1. Criar ambiente virtual

```bash
python -m venv venv
```

### 2. Ativar ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

O arquivo `.env` já está configurado com suas credenciais do Supabase.

## Executar a Aplicação

```bash
python main.py
```

Ou usando uvicorn diretamente:

```bash
uvicorn main:app --reload
```

A API estará disponível em: `http://localhost:8000`

## Documentação da API

Após iniciar a aplicação, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Disponíveis

### Autenticação

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| POST | `/auth/signup` | Registrar novo usuário | Não |
| POST | `/auth/signin` | Login | Não |
| POST | `/auth/signout` | Logout | Sim |
| POST | `/auth/refresh` | Renovar token | Não |
| GET | `/auth/me` | Obter dados do usuário | Sim |
| POST | `/auth/reset-password` | Solicitar reset de senha | Não |
| POST | `/auth/update-password` | Atualizar senha | Sim |

### Outros

| Método | Endpoint | Descrição | Autenticação |
|--------|----------|-----------|--------------|
| GET | `/` | Root da API | Não |
| GET | `/health` | Health check | Não |
| GET | `/protected` | Exemplo de rota protegida | Sim |

## Exemplos de Uso

### 1. Registrar um usuário

```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com",
    "password": "senha123",
    "full_name": "João Silva"
  }'
```

### 2. Fazer login

```bash
curl -X POST "http://localhost:8000/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com",
    "password": "senha123"
  }'
```

Resposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "...",
  "user": {
    "id": "uuid",
    "email": "usuario@exemplo.com",
    "full_name": "João Silva"
  }
}
```

### 3. Acessar rota protegida

```bash
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

### 4. Obter dados do usuário

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

## Usando em Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Registrar
response = requests.post(f"{BASE_URL}/auth/signup", json={
    "email": "usuario@exemplo.com",
    "password": "senha123",
    "full_name": "João Silva"
})
data = response.json()
access_token = data["access_token"]

# 2. Headers com autenticação
headers = {
    "Authorization": f"Bearer {access_token}"
}

# 3. Acessar rota protegida
response = requests.get(f"{BASE_URL}/protected", headers=headers)
print(response.json())
```

## Recursos do Supabase

### Autenticação
- ✅ Registro de usuários
- ✅ Login com email/senha
- ✅ JWT tokens (access + refresh)
- ✅ Logout
- ✅ Renovação de tokens
- ✅ Reset de senha
- ✅ Atualização de senha
- ✅ Verificação de email (configurar no Supabase)

### Segurança
- ✅ Tokens JWT assinados
- ✅ Senhas hasheadas pelo Supabase
- ✅ CORS configurado
- ✅ Variáveis de ambiente protegidas
- ✅ Row Level Security (RLS) disponível no Supabase

## Estado Atual do Sistema ✅

### ✅ Implementado, Testado e Deployed
- **Sistema de Autenticação Completo**: Signup, login, logout, refresh tokens
- **Sistema de Roles**: Usuários comuns e administradores
- **Gestão de Usuários**: Interface completa para admins
- **Interface Responsiva**: Layout unificado com sidebar e navegação
- **Sistema de Testes Robusto**: 48 testes com 87.50% de acurácia
- **Arquitetura Organizada**: Todos os arquivos nas localizações corretas
- **Deploy Seguro**: Código versionado e seguro no Git
- **Segurança Verificada**: Sem dados sensíveis hardcoded

### 🔄 Próximas Fases Planejadas
1. **Power BI Integration**: Incorporação e controle de dashboards externos
2. **Análises Python**: Sistema para execução de scripts analíticos nativos
3. **Sistema de Agentes**: Chatbots inteligentes para insights rápidos
4. **Dashboard Rico**: Métricas e indicadores visuais customizados
5. **Perfil de Usuário**: Edição avançada de dados pessoais

## Tecnologias

- **Backend**: FastAPI
- **Autenticação**: Supabase Auth
- **Banco de Dados**: Supabase (PostgreSQL)
- **Validação**: Pydantic
- **Documentação**: OpenAPI/Swagger

## Suporte

Para problemas ou dúvidas, consulte:
- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Documentação Supabase](https://supabase.com/docs)
