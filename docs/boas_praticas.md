# Boas Práticas de Desenvolvimento para o Template FastAPI

## Introdução

Este documento apresenta um conjunto de boas práticas e recomendações para o desenvolvimento de aplicações usando o template FastAPI. Seguir estas diretrizes ajudará a garantir um código limpo, eficiente, seguro e de fácil manutenção, bem como uma experiência de desenvolvimento consistente para todos os membros da equipe.

## Princípios Fundamentais

### 1. Clareza e Legibilidade

- **O código deve ser auto-explicativo**: Escreva código que possa ser entendido sem necessidade de comentários extensos
- **Nomes significativos**: Use nomes descritivos para variáveis, funções, classes e módulos
- **Funções pequenas e focadas**: Cada função deve fazer apenas uma coisa e fazê-la bem
- **Evite aninhamentos profundos**: Limite o nível de aninhamento para melhorar a legibilidade

### 2. Consistência

- **Siga as convenções do Python**: Adote o [PEP 8](https://peps.python.org/pep-0008/) e [PEP 257](https://peps.python.org/pep-0257/)
- **Mantenha um estilo consistente**: Utilize as ferramentas de formatação configuradas no template (black, isort)
- **Estruture projetos de maneira uniforme**: Siga o padrão de organização estabelecido no template

### 3. Manutenibilidade

- **DRY (Don't Repeat Yourself)**: Evite duplicação de código através de abstrações apropriadas
- **SOLID**: Aplique os princípios SOLID quando aplicável
- **Testes abrangentes**: Escreva testes para todos os componentes críticos

### 4. Segurança

- **Validação rigorosa de entrada**: Use os schemas Pydantic para validar todos os dados de entrada
- **Princípio do menor privilégio**: Limite o acesso apenas ao necessário
- **Gestão segura de dados sensíveis**: Nunca exponha dados sensíveis em logs ou resposta de API

## Práticas Específicas do FastAPI

### Organização de Código

#### Estrutura de Diretórios

Mantenha a estrutura de diretórios consistente, seguindo o padrão do template:

```
fastapi/
├── alembic/              # Configuração e scripts de migração
├── api/
│   ├── core/             # Componentes centrais (config, database, security)
│   ├── main.py           # Ponto de entrada da aplicação
│   └── src/              # Código-fonte organizado por domínio
│       ├── domain1/
│       │   ├── models.py      # Modelos SQLAlchemy
│       │   ├── repository.py  # Operações de banco de dados
│       │   ├── routes.py      # Endpoints da API
│       │   ├── schemas.py     # Schemas Pydantic
│       │   └── service.py     # Lógica de negócio
│       └── domain2/
├── tests/                # Testes automatizados
│   ├── conftest.py       # Configuração e fixtures para testes
│   └── ...
└── pyproject.toml        # Definição do projeto e dependências
```

#### Separação de Responsabilidades

Cada componente deve ter uma responsabilidade clara:

- **models.py**: Define a estrutura de dados e relações no banco
- **schemas.py**: Define a validação de entrada e formato de saída
- **repository.py**: Implementa operações de banco de dados
- **service.py**: Contém a lógica de negócio
- **routes.py**: Define os endpoints da API

### Desenvolvimento das Rotas

#### Nomenclatura e Verbos HTTP

Siga as convenções RESTful:

- **GET /resources**: Listar recursos
- **GET /resources/{id}**: Obter um recurso específico
- **POST /resources**: Criar um novo recurso
- **PUT /resources/{id}**: Atualizar completamente um recurso
- **PATCH /resources/{id}**: Atualizar parcialmente um recurso
- **DELETE /resources/{id}**: Remover um recurso

#### Versionamento da API

- Sempre prefixe rotas com a versão da API (ex: `/api/v1/resources`)
- Nunca altere o comportamento de endpoints existentes em uma versão
- Para mudanças incompatíveis, crie uma nova versão da API

#### Respostas e Códigos de Status

Use códigos de status HTTP apropriados:

- **2xx** para sucesso (200, 201, 204)
- **4xx** para erros do cliente (400, 401, 403, 404)
- **5xx** para erros do servidor (500)

```python
@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, session: AsyncSession = Depends(get_session)):
    """Obtém um item específico pelo ID."""
    item = await get_item_from_db(session, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item com ID {item_id} não encontrado"
        )
    return item
```

#### Documentação de API

Documente todas as rotas detalhadamente:

- Adicione docstrings explicativas a cada função de rota
- Descreva todos os parâmetros nos schemas Pydantic
- Inclua exemplos relevantes

```python
class UserCreate(BaseModel):
    """Schema para criação de um novo usuário."""
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="Nome de usuário entre 3 e 50 caracteres",
        example="johndoe"
    )
    email: EmailStr = Field(
        ...,
        description="Email válido do usuário",
        example="john.doe@example.com"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Senha com pelo menos 8 caracteres",
        example="SecureP@ssw0rd"
    )
```

### Manipulação de Banco de Dados

#### Operações Assíncronas

- Use sempre os métodos assíncronos do SQLAlchemy para todas as operações de banco de dados
- Evite bloqueios desnecessários com `await` em operações de IO
- Gerencie corretamente o ciclo de vida das sessões

```python
async def get_by_id(self, item_id: int) -> Optional[Item]:
    """Obtém um item pelo ID de forma assíncrona."""
    result = await self.session.execute(
        select(Item).where(Item.id == item_id)
    )
    return result.scalars().first()
```

#### Transações

- Use transações para operações que devem ser atômicas
- Implemente tratamento adequado de erros para garantir consistência

```python
async def transfer_funds(from_account_id: int, to_account_id: int, amount: float):
    """Transfere fundos entre contas em uma transação atômica."""
    async with self.session.begin():
        # Obter contas
        from_account = await self.get_account(from_account_id)
        to_account = await self.get_account(to_account_id)
        
        # Validar saldo
        if from_account.balance < amount:
            raise InsufficientFundsError()
            
        # Processar transferência
        from_account.balance -= amount
        to_account.balance += amount
        
        # Registrar transação
        transaction = Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount
        )
        self.session.add(transaction)
        
        # Commit ocorre automaticamente se não houver exceções
        # Rollback ocorre automaticamente em caso de exceção
```

#### Migrações

- Implemente alterações de esquema sempre através de migrações Alembic
- Verifique cuidadosamente os scripts de migração gerados automaticamente
- Teste migrações em ambiente de desenvolvimento antes de aplicar em produção
- Inclua tanto `upgrade()` quanto `downgrade()` em todas as migrações

### Validação de Dados

#### Schemas Pydantic

- Use schemas Pydantic para validar todos os dados de entrada e saída
- Defina restrições claras (min/max length, regex, etc.)
- Separe schemas de entrada (Create/Update) e saída (Response)
- Implemente validadores personalizados quando necessário

```python
from pydantic import BaseModel, Field, validator
from datetime import date

class PersonCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    birth_date: date
    email: EmailStr
    
    @validator('birth_date')
    def check_birth_date_not_future(cls, v):
        if v > date.today():
            raise ValueError('Data de nascimento não pode ser no futuro')
        return v
```

### Autenticação e Autorização

#### Segurança de Senhas

- Nunca armazene senhas em texto puro
- Use algoritmos de hash robustos (bcrypt) para senhas
- Implemente políticas de senha fortes

#### Controle de Acesso

- Implemente um sistema de controle de acesso baseado em papéis (RBAC)
- Aplique o princípio do menor privilégio
- Adicione verificações de autorização em todas as rotas sensíveis

```python
def get_admin_user(current_user: User = Depends(get_current_user)):
    """Verifica se o usuário autenticado é um administrador."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente"
        )
    return current_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session)
):
    """Endpoint para exclusão de usuário (apenas admin)."""
    # Implementação segura aqui
```

#### Tokens JWT

- Configure tempos de expiração adequados para tokens
- Implemente rotação de chaves secretas
- Considere usar refresh tokens para melhor segurança
- Valide sempre o conteúdo dos tokens

### Tratamento de Erros

#### Erros Esperados

- Use `HTTPException` com códigos de status apropriados para erros esperados
- Forneça mensagens de erro claras e úteis
- Evite expor informações sensíveis nas mensagens de erro

```python
if user_exists:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Nome de usuário já está em uso"
    )
```

#### Erros Inesperados

- Implemente um handler global para exceções não tratadas
- Registre erros inesperados em logs para análise posterior
- Retorne mensagens genéricas para o cliente em caso de erros internos

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas."""
    # Log detalhado do erro para diagnóstico interno
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    
    # Resposta genérica para o cliente
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocorreu um erro interno no servidor"}
    )
```

### Logging

#### Boas Práticas

- Configure níveis de log apropriados para diferentes ambientes
- Evite registrar dados sensíveis (senhas, tokens, etc.)
- Inclua contexto suficiente para diagnóstico de problemas
- Use IDs de correlação para rastrear requisições através do sistema

```python
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware para logging de requisições com ID de correlação."""
    correlation_id = str(uuid.uuid4())
    logger.info(
        f"Iniciando requisição {request.method} {request.url.path}",
        extra={"correlation_id": correlation_id}
    )
    
    try:
        response = await call_next(request)
        logger.info(
            f"Concluída requisição {request.method} {request.url.path} - Status: {response.status_code}",
            extra={"correlation_id": correlation_id}
        )
        return response
    except Exception as e:
        logger.error(
            f"Erro na requisição {request.method} {request.url.path}",
            exc_info=True,
            extra={"correlation_id": correlation_id}
        )
        raise
```

### Testes

#### Testes Unitários

- Teste cada componente isoladamente (serviços, repositórios, etc.)
- Use mocks/stubs para dependências externas
- Cubra todos os caminhos lógicos importantes

```python
@pytest.mark.asyncio
async def test_user_service_create_user():
    # Arrange
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = User(id=1, email="test@example.com")
    
    service = UserService(mock_repo)
    user_data = UserCreate(email="test@example.com", password="password123")
    
    # Act
    result = await service.create_user(user_data)
    
    # Assert
    assert result.id == 1
    assert result.email == "test@example.com"
    mock_repo.get_by_email.assert_called_once_with("test@example.com")
    mock_repo.create.assert_called_once()
```

#### Testes de Integração

- Teste a integração entre componentes
- Use um banco de dados de teste real
- Configure fixtures para preparar e limpar o ambiente de teste

```python
@pytest.mark.asyncio
async def test_create_user_api(client, db_session):
    # Arrange
    user_data = {
        "email": "new_user@example.com",
        "username": "newuser",
        "password": "securepass123"
    }
    
    # Act
    response = await client.post("/api/v1/users/", json=user_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    
    # Verificar se o usuário foi realmente criado no banco
    result = await db_session.execute(
        select(User).where(User.email == user_data["email"])
    )
    user = result.scalars().first()
    assert user is not None
    assert user.username == user_data["username"]
```

#### Testes de Carga (Opcional)

- Use ferramentas como Locust ou k6 para testar performance
- Identifique gargalos e problemas de concorrência
- Estabeleça uma linha de base para métricas de performance

### Desempenho

#### Otimização de Consultas

- Use índices apropriados no banco de dados
- Evite N+1 queries com joins/selectinload
- Considere a paginação para grandes conjuntos de dados
- Monitore e otimize consultas lentas

```python
async def get_users_with_posts(skip: int = 0, limit: int = 100):
    """Obtém usuários com seus posts, otimizado para evitar N+1 queries."""
    result = await self.session.execute(
        select(User)
        .options(selectinload(User.posts))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
```

#### Caching

- Implemente caching para dados frequentemente acessados e que mudam pouco
- Use Redis ou outro mecanismo de cache distribuído
- Defina políticas de invalidação de cache apropriadas

```python
async def get_product(product_id: int):
    """Obtém um produto com cache."""
    # Tentar obter do cache primeiro
    cache_key = f"product:{product_id}"
    cached_data = await redis.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    # Se não estiver em cache, buscar do banco
    product = await product_repo.get_by_id(product_id)
    
    if product:
        # Armazenar no cache por 1 hora
        await redis.set(
            cache_key,
            json.dumps(product.dict()),
            ex=3600
        )
    
    return product
```

### Depuração e Monitoramento

#### Depuração em Desenvolvimento

- Configure adequadamente o VSCode para depuração (já configurado no template)
- Use ferramentas como `ipdb` para depuração interativa quando necessário
- Implemente logs detalhados em desenvolvimento

#### Monitoramento em Produção

- Implemente métricas de aplicação (Prometheus, StatsD, etc.)
- Configure alertas para problemas críticos
- Monitore tempos de resposta, taxas de erro e utilização de recursos

## UV e Gerenciamento de Dependências

### Práticas com UV

- Mantenha todas as dependências definidas no `pyproject.toml`
- Use versões específicas para dependências de produção
- Agrupe dependências de desenvolvimento separadamente
- Execute `uv sync` após alterações no `pyproject.toml`

### Atualizações de Dependências

- Atualize dependências de forma controlada e planejada
- Teste exaustivamente após atualizações
- Mantenha um registro de alterações de dependências

## Implantação e CI/CD

### Integração Contínua

- Execute testes automaticamente em cada pull request
- Verifique qualidade de código com linters
- Garanta cobertura de testes adequada

### Entrega Contínua

- Automatize o processo de build e implantação
- Implemente estratégias de implantação seguras (blue/green, canary)
- Mantenha configurações específicas de ambiente em variáveis de ambiente

### Docker

- Use a imagem Docker fornecida no template para ambientes consistentes
- Otimize imagens para reduzir tamanho e melhorar segurança
- Siga as melhores práticas para camadas Docker

## Revisão de Código

### Checklist

Antes de submeter código para revisão, verifique:

- [ ] O código segue os padrões de estilo (black, isort)
- [ ] Todos os testes passam
- [ ] Novas funcionalidades possuem testes adequados
- [ ] Documentação foi atualizada
- [ ] Não há problemas de segurança óbvios
- [ ] O código é eficiente e bem estruturado
- [ ] Migrações de banco de dados funcionam corretamente

### Processo de Revisão

- Revisões de código devem ser construtivas e respeitosas
- Foque em problemas substantivos, não apenas em estilo
- Use ferramentas automatizadas para verificar problemas comuns

## Documentação

### Código

- Adicione docstrings explicativas a todas as funções e classes
- Documente parâmetros, retornos e exceções
- Inclua exemplos de uso para funções complexas

```python
def calculate_discount(
    price: float, 
    discount_percentage: float, 
    min_price: float = 0.0
) -> float:
    """
    Calcula o preço com desconto.
    
    Args:
        price: Preço original
        discount_percentage: Percentual de desconto (0-100)
        min_price: Preço mínimo após desconto
        
    Returns:
        Preço com desconto aplicado
        
    Raises:
        ValueError: Se discount_percentage estiver fora do intervalo 0-100
        
    Examples:
        >>> calculate_discount(100.0, 20.0)
        80.0
        >>> calculate_discount(100.0, 90.0, min_price=20.0)
        20.0
    """
    if not 0 <= discount_percentage <= 100:
        raise ValueError("Percentual de desconto deve estar entre 0 e 100")
        
    discounted = price * (1 - discount_percentage / 100)
    return max(discounted, min_price)
```

### Projeto

- Mantenha um README.md atualizado e informativo
- Documente a arquitetura e decisões de design
- Inclua instruções claras para configuração, execução e testes

## Conclusão

Seguir estas boas práticas não apenas melhorará a qualidade do seu código, mas também tornará o processo de desenvolvimento mais eficiente e agradável para toda a equipe. O template FastAPI foi projetado para facilitar a adesão a estas práticas, fornecendo uma estrutura sólida e ferramentas apropriadas.

A consistência é fundamental: ao seguir estes princípios em todo o projeto, você cria uma base de código uniforme que é mais fácil de entender, manter e estender no futuro.

Lembre-se que estas práticas devem ser adaptadas às necessidades específicas do seu projeto e equipe, mantendo o equilíbrio entre pragmatismo e excelência técnica.

---

*[Voltar ao Índice](./index.md)*
