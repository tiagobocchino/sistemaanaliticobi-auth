# Guia Técnico do Sistema de Testes - Analytics Platform

## Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Configuração](#configuração)
4. [Sistema de Acurácia](#sistema-de-acurácia)
5. [Fixtures e Mocks](#fixtures-e-mocks)
6. [Tipos de Testes](#tipos-de-testes)
7. [Executando Testes](#executando-testes)
8. [Workflow de Desenvolvimento](#workflow-de-desenvolvimento)
9. [Troubleshooting](#troubleshooting)

---

## Visão Geral

Sistema robusto de testes automatizados com **avaliação de acurácia de 85%**. Cada nova funcionalidade deve ser testada e validada antes de avançar.

### Workflow de Desenvolvimento

```
1. Mapeamento do Processo
   ↓
2. Desenvolvimento + Testes
   ↓
3. Validação (Acurácia >= 85%)
   ↓
4. Deploy no Git
```

### Métricas Atuais

- **Total de Testes**: 48 testes unitários + 42 testes de integração + 3 testes Power BI
- **Acurácia Atual**: 87.50% ✅
- **Cobertura de Código**: 46%
- **Tempo de Execução**: ~2-5 minutos
- **Arquitetura**: 100% organizada ✅
- **Bugs Críticos**: 0 (todos resolvidos) ✅
- **Módulos**: Autenticação, Usuários, Power BI ✅

---

## Arquitetura do Sistema

### Estrutura de Diretórios

```
tests/
├── conftest.py                    # Configuração global pytest
├── mocks.py                       # Sistema de mocks para Supabase
├── test_unit_models.py           # Testes unitários de modelos
├── test_unit_endpoints.py        # Testes unitários de endpoints
├── test_auth.py                   # Testes de autenticação (integração)
├── test_users.py                  # Testes de usuários (integração)
├── e2e/                           # Testes End-to-End (Selenium)
│   ├── conftest.py                # Configuração E2E
│   ├── pages/                     # Page Objects
│   │   ├── base_page.py
│   │   ├── home_page.py
│   │   ├── login_page.py
│   │   ├── signup_page.py
│   │   ├── dashboard_page.py
│   │   └── users_page.py
│   ├── test_e2e_auth.py
│   └── test_e2e_users.py
└── README.md                      # Documentação de uso

Arquivos de Configuração:
├── pytest.ini                     # Configuração pytest
├── requirements-test.txt          # Dependências
├── run_tests.py                   # Script de execução
└── run_tests.bat                  # Script Windows
```

---

## Configuração

### pytest.ini - Explicação Linha a Linha

```ini
[pytest]
# Define onde estão os testes
testpaths = tests

# Padrões de descoberta de testes
python_files = test_*.py           # Arquivos que começam com test_
python_classes = Test*             # Classes que começam com Test
python_functions = test_*          # Funções que começam com test_

# Modo assíncrono automático
asyncio_mode = auto

# Opções de execução
addopts =
    -v                             # Verbose (mostra cada teste)
    --tb=short                     # Traceback curto em erros
    --strict-markers               # Requer markers definidos
    --cov=src                      # Cobertura do diretório src
    --cov-report=html              # Relatório HTML de cobertura
    --cov-report=term-missing      # Mostra linhas não cobertas
    --html=test_reports/report.html    # Relatório HTML
    --self-contained-html          # HTML standalone
    --json-report                  # Relatório JSON
    --json-report-file=test_reports/report.json

# Markers personalizados
markers =
    unit: Unit tests (no external dependencies)
    auth: Authentication tests
    users: User management tests
    admin: Admin-only tests
    e2e: End-to-end tests
    smoke: Smoke tests (critical paths)
    integration: Integration tests
    slow: Slow running tests
```

### Dependências (requirements-test.txt)

```
pytest==7.4.3              # Framework de testes
pytest-asyncio==0.21.1     # Suporte async
pytest-cov==4.1.0          # Cobertura de código
httpx>=0.26.0              # Cliente HTTP
selenium==4.16.0           # Testes E2E
webdriver-manager==4.0.1   # ChromeDriver automático
pytest-html==4.1.1         # Relatórios HTML
pytest-json-report==1.5.0  # Relatórios JSON
pytest-mock==3.12.0        # Mocking
```

---

## Sistema de Acurácia

### Implementação (conftest.py)

#### 1. Tracking de Resultados

```python
# Dicionário global para armazenar resultados
test_results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": 0
}
```

#### 2. Hook de Execução

```python
def pytest_runtest_logreport(report):
    """
    Hook chamado após cada teste

    Args:
        report: Objeto com resultado do teste
            - report.when: 'setup', 'call', 'teardown'
            - report.outcome: 'passed', 'failed', 'skipped'
    """
    # Só conta na fase 'call' (execução real do teste)
    if report.when == "call":
        if report.outcome == "passed":
            test_results["passed"] += 1
        elif report.outcome == "failed":
            test_results["failed"] += 1
        elif report.outcome == "skipped":
            test_results["skipped"] += 1
```

#### 3. Cálculo de Acurácia

```python
def pytest_sessionfinish(session, exitstatus):
    """
    Hook chamado ao final de todos os testes

    Args:
        session: Sessão pytest
        exitstatus: Código de saída
    """
    total = test_results["passed"] + test_results["failed"]

    if total > 0:
        # Fórmula: (Passados / Total) * 100
        accuracy = (test_results["passed"] / total) * 100

        # Exibe relatório
        print(f"\n{'='*60}")
        print(f"TEST ACCURACY REPORT")
        print(f"{'='*60}")
        print(f"Passed:   {test_results['passed']}")
        print(f"Failed:   {test_results['failed']}")
        print(f"Skipped:  {test_results['skipped']}")
        print(f"Total:    {total}")
        print(f"Accuracy: {accuracy:.2f}%")
        print(f"{'='*60}")

        # Avaliação
        if accuracy >= 85.0:
            print(f"[PASSED] - Accuracy >= 85% (Target: 85%)")
        else:
            print(f"[FAILED] - Accuracy < 85% (Target: 85%)")
        print(f"{'='*60}\n")
```

### Script de Execução (run_tests.py)

#### Classe TestRunner

```python
class TestRunner:
    """
    Orquestra execução de testes e avaliação de acurácia

    Attributes:
        accuracy_threshold: float - Mínimo de acurácia (padrão: 85%)
        results: dict - Resultados de backend, E2E e overall
    """

    def __init__(self, accuracy_threshold: float = 85.0):
        self.accuracy_threshold = accuracy_threshold
        self.results = {
            "backend": {},
            "e2e": {},
            "overall": {}
        }
```

#### Execução de Testes Backend

```python
def run_backend_tests(self) -> Dict[str, Any]:
    """
    Executa testes backend com pytest

    Returns:
        dict: {passed, failed, total, accuracy}
    """
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--ignore=tests/e2e/",  # Ignora E2E
        "-v",
        "--tb=short",
        "--json-report",
        "--json-report-file=test_reports/backend_report.json"
    ]

    subprocess.run(cmd, capture_output=True, text=True)

    # Lê relatório JSON gerado
    with open("test_reports/backend_report.json", 'r') as f:
        report = json.load(f)

        passed = report["summary"]["passed"]
        failed = report["summary"]["failed"]
        total = report["summary"]["total"]
        accuracy = (passed / total * 100) if total > 0 else 0

        return {"passed": passed, "failed": failed,
                "total": total, "accuracy": accuracy}
```

#### Avaliação Final

```python
def calculate_overall_accuracy(self):
    """
    Calcula acurácia geral combinando backend e E2E
    """
    backend = self.results.get("backend", {})
    e2e = self.results.get("e2e", {})

    total_passed = backend.get("passed", 0) + e2e.get("passed", 0)
    total_failed = backend.get("failed", 0) + e2e.get("failed", 0)
    total_tests = backend.get("total", 0) + e2e.get("total", 0)

    overall_accuracy = (total_passed / total_tests * 100) if total_tests > 0 else 0

    self.results["overall"] = {
        "passed": total_passed,
        "failed": total_failed,
        "total": total_tests,
        "accuracy": overall_accuracy
    }
```

---

## Fixtures e Mocks

### Fixtures Principais (conftest.py)

#### 1. TestClient

```python
@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """
    Cliente FastAPI para testes

    Scope: function - nova instância para cada teste

    Yields:
        TestClient: Cliente configurado com a app
    """
    with TestClient(app) as test_client:
        yield test_client
```

#### 2. Mock Supabase

```python
@pytest.fixture(scope="function", autouse=True)
def mock_supabase(monkeypatch):
    """
    Mock automático do Supabase para todos os testes

    autouse=True: Ativa automaticamente sem declarar

    Args:
        monkeypatch: Fixture pytest para patch de módulos

    Returns:
        MockSupabaseClient: Cliente mockado
    """
    # Cria mocks
    mock_client = MockSupabaseClient()
    mock_auth = MockSupabaseAuth()
    mock_client.auth = mock_auth

    # Aplica patches nos módulos
    import src.supabase_client
    monkeypatch.setattr(src.supabase_client, "supabase_client", mock_client)
    monkeypatch.setattr(src.supabase_client, "supabase_admin_client", mock_client)

    return mock_client
```

#### 3. Auth Headers

```python
@pytest.fixture(scope="function")
def auth_headers(client: TestClient, test_user_data: Dict[str, Any],
                 mock_supabase) -> Dict[str, str]:
    """
    Cria usuário, faz login e retorna headers de autenticação

    Args:
        client: TestClient FastAPI
        test_user_data: Dados do usuário teste
        mock_supabase: Cliente Supabase mockado

    Returns:
        dict: {"Authorization": "Bearer token"}
    """
    # Signup
    signup_response = client.post("/auth/signup", json=test_user_data)

    # Se sucesso, pega token
    if signup_response.status_code in [200, 201]:
        data = signup_response.json()
        if "tokens" in data and data["tokens"]:
            token = data["tokens"]["access_token"]
            return {"Authorization": f"Bearer {token}"}

    # Senão, faz login
    response = client.post("/auth/signin", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })

    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return {}
```

### Sistema de Mocks (mocks.py)

#### MockSupabaseAuth

```python
class MockSupabaseAuth:
    """
    Mock do Supabase Auth

    Simula autenticação sem chamadas HTTP reais
    """

    def __init__(self):
        self.users = {}  # Armazena usuários mockados

    def sign_up(self, credentials: Dict) -> Dict:
        """
        Mock de signup

        Args:
            credentials: {email, password, data: {full_name}}

        Returns:
            Mock response com user e session
        """
        user_id = str(uuid.uuid4())
        email = credentials.get("email")
        password = credentials.get("password")

        # Cria usuário mock
        user_data = {
            "id": user_id,
            "email": email,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "email_confirmed_at": datetime.now(timezone.utc).isoformat(),
            "full_name": credentials.get("data", {}).get("full_name", ""),
        }

        # Armazena para login futuro
        self.users[email] = {
            "password": password,
            "user_data": user_data
        }

        # Retorna mock response
        mock_response = MagicMock()
        mock_response.user = MagicMock(**user_data)
        mock_response.session = MagicMock(
            access_token=f"mock_access_token_{user_id}",
            refresh_token=f"mock_refresh_token_{user_id}",
            expires_in=3600
        )

        return mock_response

    def sign_in_with_password(self, credentials: Dict) -> Dict:
        """
        Mock de login

        Args:
            credentials: {email, password}

        Returns:
            Mock response se credenciais válidas

        Raises:
            Exception: Se credenciais inválidas
        """
        email = credentials.get("email")
        password = credentials.get("password")

        # Verifica se usuário existe
        if email not in self.users:
            raise Exception("Invalid login credentials")

        # Verifica senha
        if self.users[email]["password"] != password:
            raise Exception("Invalid login credentials")

        user_data = self.users[email]["user_data"]

        # Retorna mock response
        mock_response = MagicMock()
        mock_response.user = MagicMock(**user_data)
        mock_response.session = MagicMock(
            access_token=f"mock_access_token_{user_data['id']}",
            refresh_token=f"mock_refresh_token_{user_data['id']}",
            expires_in=3600
        )

        return mock_response
```

---

## Tipos de Testes

### 1. Testes Unitários de Modelos (test_unit_models.py)

**Objetivo**: Validar modelos Pydantic sem dependências externas

```python
@pytest.mark.unit
class TestAuthModels:
    """
    Testa validação de modelos Pydantic

    Marker: @pytest.mark.unit - Testes unitários puros
    """

    def test_user_signup_valid(self):
        """
        Testa criação de UserSignUp com dados válidos

        Valida:
        - Campos são corretamente atribuídos
        - Email é validado
        - Password é requerido
        """
        data = {
            "email": "test@example.com",
            "password": "SecurePass123#",
            "full_name": "Test User"
        }
        user = UserSignUp(**data)

        assert user.email == "test@example.com"
        assert user.password == "SecurePass123#"
        assert user.full_name == "Test User"

    def test_user_signup_invalid_email(self):
        """
        Testa que email inválido levanta ValidationError

        Comportamento esperado:
        - Pydantic deve rejeitar emails mal formatados
        - ValidationError deve ser levantado
        """
        data = {
            "email": "invalid-email",
            "password": "SecurePass123#"
        }

        with pytest.raises(ValidationError):
            UserSignUp(**data)
```

### 2. Testes Unitários de Endpoints (test_unit_endpoints.py)

**Objetivo**: Validar endpoints básicos e validação de inputs

```python
@pytest.mark.unit
@pytest.mark.smoke
class TestBasicEndpoints:
    """
    Testa endpoints que não dependem de Supabase

    Markers:
    - unit: Teste unitário
    - smoke: Teste crítico (deve sempre passar)
    """

    def test_health_endpoint_returns_200(self, client: TestClient):
        """
        Testa que /health retorna 200

        Args:
            client: FastAPI TestClient (fixture)

        Asserts:
        - Status code 200
        - Response contém "status": "healthy"
        """
        response = client.get("/health")

        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
```

### 3. Testes de Integração (test_auth.py, test_users.py)

**Objetivo**: Testar integração com Supabase (requer mock ou banco real)

```python
@pytest.mark.auth
class TestAuthentication:
    """
    Testes de autenticação com Supabase

    Marker: @pytest.mark.auth - Testes de autenticação

    Nota: Requerem mock de Supabase ou banco de teste
    """

    @pytest.mark.smoke
    def test_signin_valid_credentials(self, client: TestClient,
                                      test_user_data: Dict[str, Any]):
        """
        Testa login com credenciais válidas

        Fluxo:
        1. Signup (cria usuário)
        2. Login (autentica)
        3. Valida resposta

        Asserts:
        - Status 200
        - Retorna access_token
        - Retorna refresh_token
        - Retorna dados do usuário
        """
        # Signup
        client.post("/auth/signup", json=test_user_data)

        # Login
        response = client.post("/auth/signin", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
```

### 4. Testes E2E (test_e2e_auth.py, test_e2e_users.py)

**Objetivo**: Testar interface do usuário com Selenium

### 5. Testes Power BI (test_powerbi_basic.py)

**Objetivo**: Testar integração com Power BI (modo mock e real)

**Testes Unitários Power BI**:
```python
# Testa configuração
def test_powerbi_settings_creation(self)

# Testa modelos de dados
def test_dashboard_create_model(self)
def test_embed_token_request_model(self)

# Testa serviço (modo mock)
@pytest.mark.asyncio
async def test_generate_embed_token_mock(self)
```

**Testes de Integração Power BI**:
- ✅ Modo mock (sempre passa)
- 🔄 Modo real (requer credenciais Azure AD)
- 🔄 Testes E2E (requer Power BI ativo)

```python
@pytest.mark.e2e
@pytest.mark.smoke
class TestE2EAuthenticationFlow:
    """
    Testes End-to-End de autenticação

    Marker: @pytest.mark.e2e - Testes E2E

    Requer:
    - Backend rodando (localhost:8000)
    - Frontend rodando (localhost:5173)
    - Chrome instalado
    """

    def test_complete_auth_workflow(self, browser: webdriver.Chrome,
                                    test_user_credentials: dict):
        """
        Testa workflow completo: signup → login → dashboard → logout

        Args:
            browser: Chrome WebDriver (fixture)
            test_user_credentials: Credenciais de teste

        Fluxo:
        1. Navega para signup
        2. Preenche formulário
        3. Faz login
        4. Verifica dashboard
        5. Faz logout

        Asserts:
        - Cada etapa redireciona corretamente
        - Dashboard exibe informações do usuário
        - Logout retorna para home
        """
        # 1. Signup
        signup_page = SignupPage(browser)
        signup_page.navigate()
        signup_page.signup(
            test_user_credentials["full_name"],
            test_user_credentials["email"],
            test_user_credentials["password"],
            test_user_credentials["password"]
        )
        time.sleep(2)

        # 2. Login
        login_page = LoginPage(browser)
        login_page.navigate()
        login_page.login(
            test_user_credentials["email"],
            test_user_credentials["password"]
        )
        time.sleep(3)

        # 3. Verifica dashboard
        assert "/dashboard" in browser.current_url

        dashboard_page = DashboardPage(browser)
        assert dashboard_page.is_welcome_displayed()

        # 4. Logout
        dashboard_page.click_logout()
        time.sleep(2)

        assert "/" in browser.current_url or "/login" in browser.current_url
```

---

## Executando Testes

### Método 1: Script Automático (Recomendado)

```bash
# Windows
run_tests.bat

# Linux/Mac
python run_tests.py
```

### Método 2: Com Opções

```bash
# Apenas backend
python run_tests.py --backend-only

# Apenas E2E (requer servidores rodando)
python run_tests.py --e2e-only

# Threshold customizado
python run_tests.py --threshold 90.0

# Apenas testes unitários (rápido)
python -m pytest tests/test_unit_*.py -v
```

### Método 3: Pytest Direto

```bash
# Todos os testes
pytest tests/ -v

# Apenas backend (sem E2E)
pytest tests/ --ignore=tests/e2e/ -v

# Por marker
pytest -m unit -v          # Apenas unitários
pytest -m smoke -v         # Apenas críticos
pytest -m auth -v          # Apenas autenticação
pytest -m e2e -v           # Apenas E2E

# Com cobertura
pytest tests/ --cov=src --cov-report=html
```

---

## Workflow de Desenvolvimento

### Workflow Completo

```
┌─────────────────────────────────────────────────────────────┐
│ 1. MAPEAMENTO DO PROCESSO                                   │
│    - Entender requisito                                     │
│    - Planejar implementação                                 │
│    - Identificar casos de teste                             │
└───────────────────────┬─────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. DESENVOLVIMENTO + TESTES                                 │
│    - Escrever código                                        │
│    - Escrever testes unitários                              │
│    - Escrever testes de integração (se necessário)          │
└───────────────────────┬─────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. VALIDAÇÃO (Acurácia >= 85%)                              │
│    - Executar: python run_tests.py                          │
│    - Verificar acurácia                                     │
│    - Se < 85%: Corrigir bugs e voltar ao passo 2            │
│    - Se >= 85%: Prosseguir                                  │
└───────────────────────┬─────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. DEPLOY NO GIT                                            │
│    - Atualizar documentação (CLAUDE.md, README.md)         │
│    - Limpar código obsoleto                                 │
│    - git add .                                              │
│    - git commit -m "feat: descrição"                        │
│    - git push                                               │
└───────────────────────┬─────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. BACKUP LOCAL                                             │
│    - Criar pasta VersoesAnalytcs/v{X.X}                    │
│    - Copiar projeto completo para backup                    │
│    - Manter histórico local de versões                      │
└─────────────────────────────────────────────────────────────┘
```

### Exemplo Prático

#### Nova Funcionalidade: Adicionar Reset de Senha

**1. Mapeamento**
```
Requisito: Usuário pode resetar senha via email
Casos de teste:
- Requisição com email válido retorna 200
- Requisição com email inválido retorna 422
- Email é enviado (mock)
- Token de reset é válido
```

**2. Desenvolvimento**
```python
# 1. Implementar endpoint
@router.post("/reset-password")
async def reset_password(email: str):
    # Lógica aqui
    pass

# 2. Escrever teste unitário
def test_reset_password_valid_email(client):
    response = client.post("/auth/reset-password",
                           json={"email": "user@test.com"})
    assert response.status_code == 200

def test_reset_password_invalid_email(client):
    response = client.post("/auth/reset-password",
                           json={"email": "invalid"})
    assert response.status_code == 422
```

**3. Validação**
```bash
# Executar testes
python -m pytest tests/test_unit_endpoints.py -v

# Verificar acurácia
# Se >= 85%: Prosseguir
# Se < 85%: Corrigir e repetir
```

**4. Deploy**
```bash
# Atualizar documentação
# Editar CLAUDE.md: adicionar nova funcionalidade

# Git
git add .
git commit -m "feat: add password reset endpoint

- Adiciona endpoint POST /auth/reset-password
- Adiciona validação de email
- Adiciona testes unitários
- Acurácia: 87.50%"
git push
```

---

## Troubleshooting

### Problema: Testes falhando com erro de Supabase

**Sintoma**:
```
httpx.HTTPStatusError: Client error '400 Bad Request' for url 'https://...supabase.co/auth/v1/signup'
```

**Solução**:
1. Verificar se mock está ativo: `mock_supabase` fixture deve estar presente
2. Executar apenas testes unitários: `pytest tests/test_unit_*.py`
3. Para testes de integração, configurar Supabase de teste

### Problema: ChromeDriver não encontrado (E2E)

**Sintoma**:
```
selenium.common.exceptions.WebDriverException: chromedriver not found
```

**Solução**:
```bash
pip install --upgrade webdriver-manager
# Driver será baixado automaticamente na próxima execução
```

### Problema: Acurácia baixa (<85%)

**Sintoma**:
```
Accuracy: 60.00%
[FAILED] - Accuracy < 85%
```

**Solução**:
1. Ver quais testes falharam: `pytest -v`
2. Ver detalhes do erro: `pytest --tb=short`
3. Corrigir bugs identificados
4. Re-executar testes
5. Repetir até >= 85%

### Problema: Import errors

**Sintoma**:
```
ModuleNotFoundError: No module named 'src.auth'
```

**Solução**:
1. Verificar PYTHONPATH: Deve incluir raiz do projeto
2. Verificar que está executando do diretório raiz
3. conftest.py já adiciona ao path automaticamente

### Problema: Timeout nos testes E2E

**Sintoma**:
```
selenium.common.exceptions.TimeoutException
```

**Solução**:
1. Aumentar timeout em `tests/e2e/conftest.py`:
```python
driver.implicitly_wait(20)  # Default: 10
```
2. Verificar se backend e frontend estão rodando
3. Verificar conexão de rede

---

## Boas Práticas

### 1. Escrevendo Testes

```python
# ✅ BOM: Teste específico e descritivo
def test_signup_with_invalid_email_returns_422(client):
    """Testa que signup com email inválido retorna 422"""
    response = client.post("/auth/signup", json={"email": "invalid"})
    assert response.status_code == 422

# ❌ RUIM: Teste genérico
def test_signup(client):
    response = client.post("/auth/signup", json={})
    assert response.status_code != 500
```

### 2. Usando Markers

```python
# Marque testes críticos
@pytest.mark.smoke
def test_health_check(client):
    pass

# Marque testes lentos
@pytest.mark.slow
def test_generate_large_report(client):
    pass

# Marque por funcionalidade
@pytest.mark.auth
def test_login(client):
    pass
```

### 3. Fixtures

```python
# Reuse fixtures entre testes
@pytest.fixture
def sample_user():
    return {
        "email": "test@example.com",
        "password": "Test123#"
    }

def test_signup(client, sample_user):
    response = client.post("/auth/signup", json=sample_user)
    assert response.status_code in [200, 201]

def test_login(client, sample_user):
    response = client.post("/auth/signin", json=sample_user)
    assert response.status_code == 200
```

### 4. Asserts Claros

```python
# ✅ BOM: Asserts específicos
def test_user_response_structure(client):
    response = client.get("/auth/me", headers=auth_headers)
    data = response.json()

    assert "id" in data
    assert "email" in data
    assert "full_name" in data
    assert isinstance(data["id"], str)
    assert isinstance(data["email"], str)

# ❌ RUIM: Assert genérico
def test_user_response(client):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
```

---

## Referências

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Última Atualização**: 2024-12-08
**Versão**: 1.0.0
**Autor**: Sistema Analytics Platform
**Status**: Operacional ✅
