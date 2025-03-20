# Gerenciamento de Variáveis de Ambiente

## Introdução

O gerenciamento adequado de variáveis de ambiente é fundamental para manter a segurança e a flexibilidade de uma aplicação FastAPI. Este documento descreve como o template implementa o carregamento, validação e uso de variáveis de ambiente, seguindo as melhores práticas de desenvolvimento.

## Configuração com Pydantic

O template utiliza o Pydantic para validar e gerenciar configurações de ambiente, aproveitando seu sistema de validação de tipos para garantir que as variáveis de ambiente tenham os formatos corretos e fornecendo valores padrão apropriados.

### Arquivo `config.py`

O arquivo principal de configuração está localizado em `api/core/config.py` e define uma classe `Settings` que extende `BaseSettings` do Pydantic:

```python
from pydantic import BaseSettings, PostgresDsn, validator
from typing import Optional, Dict, Any

class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente.
    """
    PROJECT_NAME: str = "Heroes API"
    API_V1_PREFIX: str = "/api/v1"
    
    # Configuração do Banco de Dados
    DATABASE_URL: PostgresDsn
    
    # Configuração JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24 * 7  # 7 dias
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    @validator("CORS_ORIGINS")
    def parse_cors_origins(cls, v: str) -> list:
        """
        Converte a string CORS_ORIGINS em uma lista.
        """
        if v == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instância global de configurações
settings = Settings()
```

## Arquivo `.env`

O template utiliza um arquivo `.env` para definir variáveis de ambiente localmente durante o desenvolvimento. Este arquivo **não deve ser versionado** para evitar expor informações sensíveis.

Exemplo de arquivo `.env`:

```
# Banco de Dados
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/hero_db

# Segurança
JWT_SECRET=your_super_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Arquivo `.env.example`

O template inclui um arquivo `.env.example` que deve ser versionado e contém exemplos de todas as variáveis de ambiente necessárias, mas sem valores sensíveis:

```
# Banco de Dados
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/db_name

# Segurança
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Carregamento de Variáveis de Ambiente

O Pydantic's `BaseSettings` carrega automaticamente as variáveis de ambiente com base no nome dos campos da classe. O processo de carregamento segue esta ordem de prioridade:

1. Variáveis de ambiente (ex: `export DATABASE_URL=...`)
2. Arquivo `.env` (se existir)
3. Valores padrão definidos na classe

## Validação de Configurações

Pydantic garante que todas as configurações sejam validadas:

- Tipos são verificados e convertidos (strings para ints, URLs, etc.)
- Valores inválidos geram erros claros na inicialização
- Validadores personalizados permitem lógica adicional

### Validadores Personalizados

Os validadores personalizados do Pydantic são usados para processar valores específicos:

```python
@validator("DATABASE_URL", pre=True)
def validate_database_url(cls, v: Optional[str]) -> Any:
    """
    Validador para DATABASE_URL que permite override para testes.
    """
    if v and v.startswith("sqlite"):
        # SQLite não é recomendado para produção
        import warnings
        warnings.warn("SQLite não é recomendado para ambientes de produção")
    return v
```

## Uso das Configurações na Aplicação

A instância `settings` é importada e usada em toda a aplicação:

### Em `database.py`

```python
from api.core.config import settings

# Configuração do engine do SQLAlchemy
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)
```

### Em `security.py`

```python
from api.core.config import settings

# Criação de tokens JWT
def create_access_token(subject: str) -> str:
    """
    Cria um token JWT para o usuário especificado.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt
```

### Em `main.py`

```python
from api.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Variáveis Sensíveis

As variáveis sensíveis, como segredos e credenciais, devem ser tratadas com cuidado especial:

1. **Nunca** devem ser versionadas em repositórios
2. **Nunca** devem ser expostas em logs ou saídas
3. Devem ser diferentes para cada ambiente (dev, staging, prod)
4. Devem ser gerenciadas por um sistema seguro em produção

### Segredos em Produção

Em ambientes de produção, recomenda-se:

1. Usar um gerenciador de segredos como HashiCorp Vault, AWS Secrets Manager ou Azure Key Vault
2. Usar variáveis de ambiente definidas no nível do sistema/container
3. Implementar rotação regular de segredos

## Múltiplos Ambientes

Para suportar múltiplos ambientes (desenvolvimento, teste, produção), o template permite definir configurações específicas:

```python
class Settings(BaseSettings):
    # Configuração básica
    ENVIRONMENT: str = "development"
    
    # Outras configurações...
    
    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'development')}"
```

Isso permite ter arquivos diferentes como `.env.development`, `.env.testing` e `.env.production`.

## Configuração para Testes

Para testes, o template configura um banco de dados separado e sobrescreve algumas configurações:

```python
def get_settings_override():
    """
    Retorna configurações sobreescritas para testes.
    """
    return Settings(
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/test_db",
        JWT_SECRET="test_secret",
        ENVIRONMENT="testing"
    )
```

Em seguida, essas configurações sobrescritas são injetadas nos testes usando o sistema de dependências do FastAPI:

```python
app.dependency_overrides[get_settings] = get_settings_override
```

## Melhores Práticas

### 1. Segurança

- Nunca armazene secrets em código-fonte ou repositórios de código
- Use valores padrão apenas para configurações não sensíveis
- Gere segredos fortes e únicos para cada ambiente

### 2. Validação Rigorosa

- Valide todas as configurações na inicialização
- Forneça mensagens de erro claras para configurações inválidas
- Use tipos específicos (URLs, endereços de email, etc.) em vez de strings genéricas

### 3. Configurações por Ambiente

- Defina configurações diferentes para desenvolvimento, teste e produção
- Documente todas as variáveis necessárias para cada ambiente
- Verifique a presença de todas as variáveis necessárias antes da inicialização

### 4. Documentação

- Documente todas as variáveis de ambiente e seus propósitos
- Inclua exemplos de valores válidos
- Especifique quais variáveis são obrigatórias e quais são opcionais

## Variáveis de Ambiente Comuns

Abaixo está uma lista de variáveis de ambiente comumente usadas em aplicações FastAPI:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | URL de conexão com o banco de dados | `postgresql+asyncpg://user:pass@localhost/dbname` |
| `JWT_SECRET` | Chave secreta para tokens JWT | `supersecretkey123` |
| `JWT_ALGORITHM` | Algoritmo para tokens JWT | `HS256` |
| `LOG_LEVEL` | Nível de logging | `INFO` |
| `CORS_ORIGINS` | Origens permitidas para CORS | `http://localhost:3000,https://example.com` |
| `ENVIRONMENT` | Ambiente atual | `development`, `production` |
| `DEBUG` | Modo de debug | `True`, `False` |
| `API_V1_PREFIX` | Prefixo para endpoints da API v1 | `/api/v1` |

## Ferramentas de Gerenciamento

Além do mecanismo de `.env`, existem outras ferramentas que podem ser usadas para gerenciar variáveis de ambiente:

1. **direnv**: Carrega/descarrega variáveis de ambiente automaticamente ao entrar/sair de diretórios
2. **docker-compose**: Permite definir variáveis de ambiente para containers
3. **Kubernetes ConfigMaps/Secrets**: Para gerenciamento de configurações em clusters Kubernetes

## Conclusão

O gerenciamento adequado de variáveis de ambiente é fundamental para a segurança, flexibilidade e manutenção da aplicação. O template FastAPI implementa uma abordagem robusta, utilizando Pydantic para validação e configuração, garantindo que os valores estejam corretos e que informações sensíveis sejam adequadamente protegidas.

Seguindo as práticas descritas neste documento, você pode configurar sua aplicação de maneira segura e flexível, adaptando-a facilmente a diferentes ambientes e requisitos sem comprometer a segurança ou a funcionalidade.

---

*[Voltar ao Índice](./index.md)*
