# Testes no Template FastAPI

## Introdução

Testes automatizados são um componente essencial para garantir a qualidade e confiabilidade de qualquer aplicação. No contexto do template FastAPI, implementamos uma estrutura de testes abrangente que utiliza pytest como framework principal e oferece suporte a diferentes níveis de testes, desde testes unitários até testes de integração completos.

Este documento apresenta a estratégia de testes adotada no template, as ferramentas utilizadas, os tipos de testes implementados e exemplos práticos de como criar e executar testes para diferentes componentes da aplicação.

## Estrutura de Testes

### Organização dos Diretórios

Os testes no template FastAPI seguem uma estrutura organizada que reflete a estrutura da aplicação:

```
fastapi/
├── tests/
│   ├── conftest.py           # Configurações e fixtures compartilhadas
│   ├── test_main.py          # Testes para a aplicação principal
│   ├── unit/                 # Testes unitários
│   │   ├── test_security.py  # Testes para funcionalidades de segurança
│   │   └── ...
│   ├── api/                  # Testes de API/integração
│   │   ├── test_heroes.py    # Testes para rotas de heróis
│   │   ├── test_auth.py      # Testes para autenticação
│   │   └── ...
│   └── conftest.py           # Configurações específicas para a API
```

Esta estrutura permite:
- Separação clara entre diferentes tipos de testes
- Fácil localização de testes relacionados a componentes específicos
- Uso adequado de fixtures compartilhadas ou específicas

## Ferramentas e Bibliotecas de Teste

O template utiliza um conjunto moderno de ferramentas para testes:

1. **pytest**: Framework principal de testes
2. **pytest-asyncio**: Suporte para testes assíncronos
3. **httpx**: Cliente HTTP para testar endpoints da API
4. **SQLAlchemy**: Suporte a banco de dados em testes
5. **pytest-cov**: Relatórios de cobertura de código

Essas dependências estão incluídas no grupo `dev` no `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.1",
    "pytest-asyncio>=0.21.1",
    "httpx>=0.24.1",
    "pytest-cov>=4.1.0",
    # outras dependências de desenvolvimento
]
```

## Configuração de Testes

### Banco de Dados de Teste

A configuração para testes em `tests/conftest.py` inclui a criação de um banco de dados de teste isolado:

```python
import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from api.core.config import settings
from api.core.database import Base, get_session
from api.main import app

# URL para o banco de dados de teste
TEST_DATABASE_URL = settings.DATABASE_URL + "_test"

@pytest.fixture(scope="session")
def event_loop():
    """Cria um novo event loop para os testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Cria e configura o engine de banco de dados para testes."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )
    
    # Cria todas as tabelas no banco de teste
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Limpa o banco de dados ao final da sessão de testes
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    """Fornece uma sessão de banco de dados para cada teste."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    """Fornece um cliente de teste HTTP para chamar os endpoints da API."""
    
    # Sobrescreve a dependência de sessão do banco para usar a sessão de teste
    app.dependency_overrides[get_session] = lambda: db_session
    
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Remove a sobrescrita após o teste
    app.dependency_overrides.clear()
```

### Fixtures de Dados

Para facilitar os testes, definimos fixtures que fornecem dados de teste:

```python
@pytest.fixture
async def test_user(db_session):
    """Cria um usuário de teste."""
    from api.src.users.models import User
    from api.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user

@pytest.fixture
async def test_hero(db_session):
    """Cria um herói de teste."""
    from api.src.heroes.models import Hero
    
    hero = Hero(
        name="Test Hero",
        description="Hero for testing",
        power_level=75
    )
    db_session.add(hero)
    await db_session.commit()
    await db_session.refresh(hero)
    yield hero
```

### Autenticação em Testes

Para testar rotas protegidas, precisamos de uma fixture que forneça tokens de autenticação:

```python
@pytest.fixture
async def token_header(test_user):
    """Cria um token JWT para o usuário de teste."""
    from api.core.security import create_access_token
    
    access_token = create_access_token(
        subject=str(test_user.id)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
async def authenticated_client(client, token_header):
    """Cliente HTTP com token de autenticação."""
    client.headers.update(token_header)
    return client
```

## Tipos de Testes

### 1. Testes Unitários

Testes unitários focam em componentes individuais, como funções ou classes, isolados de suas dependências:

```python
# tests/unit/test_security.py
import pytest
from jose import jwt

from api.core.security import create_access_token, verify_password, get_password_hash
from api.core.config import settings

def test_password_hash():
    """Testa hash e verificação de senha."""
    password = "testpassword"
    hashed = get_password_hash(password)
    
    # O hash deve ser diferente da senha original
    assert hashed != password
    
    # A verificação deve funcionar com a senha correta
    assert verify_password(password, hashed) is True
    
    # A verificação deve falhar com senha incorreta
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    """Testa a criação de token JWT."""
    user_id = "123"
    token = create_access_token(subject=user_id)
    
    # Decodifica o token para verificar o conteúdo
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM]
    )
    
    # Verifica se o subject está correto
    assert payload["sub"] == user_id
    
    # Verifica se o token tem uma data de expiração
    assert "exp" in payload
```

### 2. Testes de Integração

Testes de integração verificam a interação entre diferentes componentes:

```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import AsyncMock, patch

from api.src.users.schemas import UserCreate
from api.src.users.service import UserService
from api.src.users.models import User

@pytest.mark.asyncio
async def test_user_service_create():
    """Testa a criação de usuário através do serviço."""
    # Configuração do repositório mock
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = User(
        id=1, 
        email="new@example.com", 
        username="newuser",
        hashed_password="hashedpassword"
    )
    
    # Cria o serviço com o repositório mock
    service = UserService(mock_repo)
    
    # Dados para criação de usuário
    user_data = UserCreate(
        email="new@example.com",
        username="newuser",
        password="password123"
    )
    
    # Executa o método a ser testado
    result = await service.create_user(user_data)
    
    # Verifica o resultado
    assert result.id == 1
    assert result.email == "new@example.com"
    assert result.username == "newuser"
    
    # Verifica que os métodos do repositório foram chamados corretamente
    mock_repo.get_by_email.assert_called_once_with("new@example.com")
    mock_repo.create.assert_called_once()
```

### 3. Testes de API

Testes de API (ou endpoint) verificam o comportamento completo dos endpoints HTTP:

```python
# tests/api/test_heroes.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_hero(authenticated_client: AsyncClient):
    """Testa a criação de um herói via API."""
    # Dados para o novo herói
    hero_data = {
        "name": "API Test Hero",
        "description": "Created via API test",
        "power_level": 85
    }
    
    # Faz a requisição POST
    response = await authenticated_client.post(
        "/api/v1/heroes/",
        json=hero_data
    )
    
    # Verifica o código de status
    assert response.status_code == 201
    
    # Verifica o conteúdo da resposta
    data = response.json()
    assert data["name"] == hero_data["name"]
    assert data["description"] == hero_data["description"]
    assert data["power_level"] == hero_data["power_level"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_hero(client: AsyncClient, test_hero):
    """Testa a obtenção de um herói específico."""
    # Faz a requisição GET
    response = await client.get(f"/api/v1/heroes/{test_hero.id}")
    
    # Verifica o código de status
    assert response.status_code == 200
    
    # Verifica o conteúdo da resposta
    data = response.json()
    assert data["id"] == test_hero.id
    assert data["name"] == test_hero.name
    assert data["power_level"] == test_hero.power_level

@pytest.mark.asyncio
async def test_get_nonexistent_hero(client: AsyncClient):
    """Testa a obtenção de um herói que não existe."""
    # Faz a requisição GET com ID inválido
    response = await client.get("/api/v1/heroes/999")
    
    # Verifica o código de status
    assert response.status_code == 404
```

### 4. Testes de Autenticação

Testes específicos para a autenticação e controle de acesso:

```python
# tests/api/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user):
    """Testa o login com credenciais válidas."""
    # Dados para o login (formato de form data do OAuth2)
    login_data = {
        "username": test_user.email,  # No OAuth2, username é o email
        "password": "testpassword"
    }
    
    response = await client.post(
        "/api/v1/auth/login",
        data=login_data,  # Form data, não JSON
    )
    
    # Verifica o código de status
    assert response.status_code == 200
    
    # Verifica o conteúdo da resposta
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user):
    """Testa o login com senha inválida."""
    login_data = {
        "username": test_user.email,
        "password": "wrongpassword"
    }
    
    response = await client.post(
        "/api/v1/auth/login",
        data=login_data,
    )
    
    # Deve retornar 401 Unauthorized
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route(
    client: AsyncClient,
    authenticated_client: AsyncClient
):
    """Testa acesso a rota protegida com e sem autenticação."""
    # Tentativa sem autenticação
    unauth_response = await client.get("/api/v1/auth/me")
    assert unauth_response.status_code == 401
    
    # Tentativa com autenticação
    auth_response = await authenticated_client.get("/api/v1/auth/me")
    assert auth_response.status_code == 200
    
    # Verifica se os dados do usuário foram retornados
    user_data = auth_response.json()
    assert user_data["email"] == "test@example.com"
    assert user_data["username"] == "testuser"
```

## Execução de Testes

### Executar Todos os Testes

Para executar todos os testes do projeto:

```bash
uv run pytest
```

### Executar com Cobertura de Código

Para gerar relatórios de cobertura de código:

```bash
uv run pytest --cov=api --cov-report=term --cov-report=html
```

Isso gera:
- Um relatório de cobertura no terminal
- Relatório HTML detalhado na pasta `htmlcov/`

### Executar Testes Específicos

Para executar apenas testes unitários:

```bash
uv run pytest tests/unit/
```

Para executar testes específicos de API:

```bash
uv run pytest tests/api/test_heroes.py
```

Para testes com um nome específico:

```bash
uv run pytest -k "test_login"
```

### Executar Testes em Modo Verbose

Para obter mais detalhes durante a execução dos testes:

```bash
uv run pytest -v
```

## Boas Práticas para Testes

### 1. Mantenha os Testes Independentes

Cada teste deve ser completamente independente de outros:
- Não confie em estado compartilhado entre testes
- Use fixtures para configurar e limpar o ambiente
- Evite dependências de ordem de execução

### 2. Teste um Conceito por Vez

Cada teste deve verificar um único conceito ou funcionalidade:
- Mantenha testes focados e pequenos
- Use nomes descritivos que indiquem o que está sendo testado
- Siga o padrão Arrange-Act-Assert (Configurar-Executar-Verificar)

### 3. Simule Dependências Externas

Para testes unitários, simule dependências externas:
- Use mocks para APIs externas
- Use bancos de dados em memória quando possível
- Isole o código que está sendo testado

```python
@pytest.mark.asyncio
async def test_external_service():
    # Simula resposta da API externa
    with patch("api.src.services.external.make_request") as mock_request:
        mock_request.return_value = {"data": "mocked response"}
        
        result = await external_service.get_data()
        
        assert result["data"] == "mocked response"
        mock_request.assert_called_once()
```

### 4. Teste Casos de Sucesso e Falha

Não teste apenas o caminho feliz:
- Teste entradas inválidas
- Teste condições de erro
- Teste limites e casos extremos

### 5. Use AAA (Arrange-Act-Assert)

Estruture seus testes seguindo o padrão AAA:

```python
@pytest.mark.asyncio
async def test_update_hero(db_session, test_hero):
    # Arrange - Configure o ambiente
    hero_id = test_hero.id
    update_data = {"name": "Updated Name", "power_level": 90}
    repo = HeroRepository(db_session)
    
    # Act - Execute a operação a ser testada
    updated_hero = await repo.update(hero_id, update_data)
    
    # Assert - Verifique os resultados
    assert updated_hero.id == hero_id
    assert updated_hero.name == "Updated Name"
    assert updated_hero.power_level == 90
    assert updated_hero.description == test_hero.description  # Não alterado
```

## Testes Parametrizados

Para testar múltiplos casos com o mesmo código, use testes parametrizados:

```python
import pytest

@pytest.mark.parametrize(
    "input_value,expected",
    [
        (5, 25),
        (0, 0),
        (-5, 25),
        (10, 100)
    ]
)
def test_square_function(input_value, expected):
    """Testa a função square com múltiplos valores."""
    from api.utils.math import square
    
    result = square(input_value)
    assert result == expected
```

## Teste de Exceptions

Para testar exceções esperadas:

```python
import pytest
from fastapi import HTTPException

def test_get_hero_by_id_not_found():
    """Testa que uma exceção é lançada quando o herói não é encontrado."""
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = None
    
    service = HeroService(mock_repo)
    
    with pytest.raises(HTTPException) as excinfo:
        await service.get_hero_by_id(999)
    
    # Verifica detalhes da exceção
    assert excinfo.value.status_code == 404
    assert "não encontrado" in excinfo.value.detail
```

## CI/CD e Testes Automatizados

O template inclui configuração para executar testes automaticamente em pipelines CI/CD usando GitHub Actions:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: hero_db_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install uv
        uv pip install -e ".[dev]"
    
    - name: Run tests
      run: pytest --cov=api
      env:
        DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/hero_db
```

## Análise de Cobertura

A análise de cobertura de código ajuda a identificar partes do código que não estão sendo testadas adequadamente:

```bash
uv run pytest --cov=api --cov-report=xml
```

Isso gera um relatório XML que pode ser usado por ferramentas como SonarQube ou CodeCov para análise detalhada.

### Estabelecendo Metas de Cobertura

- Estabeleça metas realistas para cobertura de código (exemplo: 80-90%)
- Priorize áreas críticas para alta cobertura
- Integre verificações de cobertura no pipeline CI/CD

## Testes de Performance (Opcional)

Para aplicações que exigem alta performance, considere adicionar testes de carga:

```python
# tests/performance/test_load.py
import pytest
import asyncio
import time
from httpx import AsyncClient

@pytest.mark.performance
async def test_api_concurrent_requests(client: AsyncClient):
    """Testa o desempenho da API com múltiplas requisições concorrentes."""
    # Número de requisições concorrentes
    n_requests = 50
    
    async def make_request():
        start_time = time.time()
        response = await client.get("/api/v1/heroes/")
        end_time = time.time()
        return {
            "status_code": response.status_code,
            "time": end_time - start_time
        }
    
    # Executa requisições concorrentes
    tasks = [make_request() for _ in range(n_requests)]
    results = await asyncio.gather(*tasks)
    
    # Analisa os resultados
    success_count = sum(1 for r in results if r["status_code"] == 200)
    avg_time = sum(r["time"] for r in results) / n_requests
    
    # Verificações
    assert success_count == n_requests
    assert avg_time < 0.2  # 200ms é um limite aceitável para este exemplo
```

## Monitoramento Contínuo de Testes

Considere implementar ferramentas para monitoramento contínuo da qualidade de testes:

1. **SonarQube/SonarCloud**: Para análise estática e cobertura de código
2. **GitHub Actions**: Para execução de testes em cada pull request
3. **CodeCov**: Para visualização detalhada de cobertura de código
4. **JUnit XML reports**: Para integração com ferramentas de CI/CD

## Conclusão

Uma estratégia de testes abrangente é essencial para manter a qualidade e confiabilidade do código. O template FastAPI fornece uma base sólida para implementar diferentes tipos de testes, desde unitários até testes de integração completos.

Seguindo as práticas descritas neste documento e utilizando as ferramentas e configurações fornecidas no template, você pode garantir que sua aplicação FastAPI seja robusta, confiável e mantenha alta qualidade de código ao longo do tempo.

Lembre-se de que os testes não são um obstáculo ao desenvolvimento, mas sim um aliado que permite identificar problemas precocemente, refatorar com confiança e garantir que novas funcionalidades não quebrem o comportamento existente.

---

*[Voltar ao Índice](./index.md)*
