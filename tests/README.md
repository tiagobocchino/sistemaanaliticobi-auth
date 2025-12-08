# Analytics Platform - Test Suite

Sistema robusto de testes automatizados com avaliação de acurácia de 85%.

## Estrutura de Testes

```
tests/
├── conftest.py              # Configuração pytest e fixtures
├── test_auth.py             # Testes de autenticação (API)
├── test_users.py            # Testes de gestão de usuários (API)
├── e2e/                     # Testes End-to-End (Selenium)
│   ├── conftest.py          # Configuração Selenium
│   ├── pages/               # Page Objects
│   │   ├── base_page.py
│   │   ├── home_page.py
│   │   ├── login_page.py
│   │   ├── signup_page.py
│   │   ├── dashboard_page.py
│   │   └── users_page.py
│   ├── test_e2e_auth.py     # Testes E2E de autenticação
│   └── test_e2e_users.py    # Testes E2E de gestão
└── README.md                # Este arquivo
```

## Tipos de Testes

### 1. Testes de Backend (pytest)
- **Testes de API**: Validam endpoints REST
- **Testes de Autenticação**: Signup, Login, Logout, Refresh Token
- **Testes de Autorização**: Permissões e roles (admin)
- **Testes de Integração**: Workflows completos

### 2. Testes E2E (Selenium)
- **Testes de UI**: Validam interface do usuário
- **Testes de Fluxo**: Workflows completos do usuário
- **Testes de Navegação**: Rotas e redirecionamentos
- **Testes de Interação**: Formulários, botões, inputs

## Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements-test.txt
```

### 2. Configurar Chrome Driver

O Selenium usa `webdriver-manager` para baixar automaticamente o ChromeDriver.
Certifique-se de ter o Google Chrome instalado.

## Executando os Testes

### Método 1: Script Automático (Recomendado)

**Windows:**
```bash
run_tests.bat
```

**Linux/Mac:**
```bash
python run_tests.py
```

### Método 2: Pytest Direto

**Todos os testes:**
```bash
pytest tests/ -v
```

**Apenas backend:**
```bash
pytest tests/ --ignore=tests/e2e/ -v
```

**Apenas E2E:**
```bash
pytest tests/e2e/ -v
```

**Testes específicos:**
```bash
pytest tests/test_auth.py -v
pytest tests/e2e/test_e2e_auth.py -v
```

### Método 3: Por Marcadores

**Testes smoke:**
```bash
pytest -m smoke -v
```

**Testes de autenticação:**
```bash
pytest -m auth -v
```

**Testes admin:**
```bash
pytest -m admin -v
```

**Testes E2E:**
```bash
pytest -m e2e -v
```

## Pré-requisitos para E2E

**IMPORTANTE:** Para executar testes E2E, você precisa:

1. **Backend rodando em http://localhost:8000**
   ```bash
   python main.py
   ```

2. **Frontend rodando em http://localhost:5173**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Google Chrome instalado**

## Sistema de Avaliação de Acurácia

O sistema avalia automaticamente se os testes atingem **85% de acurácia**.

### Como Funciona

1. **Execução**: Todos os testes são executados
2. **Contagem**: Sistema conta testes passados/falhados
3. **Cálculo**: `Acurácia = (Passados / Total) * 100`
4. **Avaliação**: Compara com threshold de 85%
5. **Resultado**: ✅ PASSED ou ❌ FAILED

### Interpretando Resultados

```
✅ PASSED - Accuracy >= 85%
   → Pode prosseguir para próxima fase

❌ FAILED - Accuracy < 85%
   → Corrigir testes falhados antes de continuar
```

### Exemplo de Saída

```
============================================================
TEST ACCURACY REPORT
============================================================
Passed:   42
Failed:   5
Skipped:  2
Total:    47
Accuracy: 89.36%
============================================================
✅ PASSED - Accuracy >= 85% (Target: 85%)
============================================================
```

## Relatórios de Testes

Após execução, os relatórios são salvos em `test_reports/`:

- `backend_report.html` - Relatório visual backend
- `backend_report.json` - Dados backend (JSON)
- `e2e_report.html` - Relatório visual E2E
- `e2e_report.json` - Dados E2E (JSON)
- `summary.json` - Resumo geral com acurácia

## Fixtures Disponíveis

### Backend (conftest.py)

- `client` - FastAPI TestClient
- `async_client` - AsyncClient para testes async
- `test_user_data` - Dados de usuário teste
- `test_admin_data` - Dados de admin teste
- `auth_headers` - Headers com token autenticado
- `admin_headers` - Headers com token admin

### E2E (e2e/conftest.py)

- `browser` - Chrome WebDriver (com UI)
- `headless_browser` - Chrome WebDriver (headless)
- `logged_in_browser` - Browser com usuário logado
- `logged_in_admin_browser` - Browser com admin logado
- `test_user_credentials` - Credenciais de teste
- `admin_credentials` - Credenciais admin

## Escrevendo Novos Testes

### Teste de Backend

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.auth
def test_new_endpoint(client: TestClient, auth_headers: dict):
    """Test description"""
    response = client.get("/new-endpoint", headers=auth_headers)
    assert response.status_code == 200
```

### Teste E2E

```python
import pytest
from selenium import webdriver
from tests.e2e.pages.your_page import YourPage

@pytest.mark.e2e
def test_new_flow(browser: webdriver.Chrome):
    """Test description"""
    page = YourPage(browser)
    page.navigate()
    page.do_something()
    assert page.is_something_visible()
```

## Marcadores Disponíveis

- `@pytest.mark.auth` - Testes de autenticação
- `@pytest.mark.users` - Testes de usuários
- `@pytest.mark.admin` - Testes de admin
- `@pytest.mark.e2e` - Testes E2E
- `@pytest.mark.smoke` - Testes smoke (principais)
- `@pytest.mark.integration` - Testes de integração
- `@pytest.mark.slow` - Testes lentos

## Cobertura de Código

Visualizar cobertura:
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### Chrome Driver Não Encontrado
```bash
pip install --upgrade webdriver-manager
```

### Testes E2E Falhando
- Verifique se backend está rodando (localhost:8000)
- Verifique se frontend está rodando (localhost:5173)
- Verifique se Chrome está instalado

### Testes de Admin Falhando
- Certifique-se de que o usuário admin foi criado:
  ```bash
  python create_admin.py
  ```

### Timeout nos Testes
- Aumente o timeout no `conftest.py`:
  ```python
  driver.implicitly_wait(20)  # Default: 10
  ```

## Workflow de Desenvolvimento

1. **Desenvolver funcionalidade**
2. **Escrever testes**
3. **Executar testes**: `python run_tests.py`
4. **Verificar acurácia**: Deve ser >= 85%
5. **Se passou**: Prosseguir para próxima task
6. **Se falhou**: Corrigir bugs e repetir

## Integração Contínua (CI/CD)

Para integrar com CI/CD (GitHub Actions, GitLab CI, etc.):

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run tests
        run: python run_tests.py
```

## Contato e Suporte

Para dúvidas sobre os testes, consulte:
- CLAUDE.md (documentação do projeto)
- README.md (documentação geral)
- Logs em `test_reports/`
