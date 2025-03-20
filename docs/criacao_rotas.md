# Criação de Rotas no Template FastAPI

## Introdução

A criação de rotas (endpoints) é um dos aspectos mais importantes no desenvolvimento de APIs com FastAPI. Este documento detalha a estrutura, padrões e melhores práticas para criar e organizar rotas no template, garantindo uma API consistente, bem documentada e fácil de manter.

## Arquitetura e Estrutura de Rotas

No template FastAPI, seguimos uma arquitetura modular que organiza rotas por domínio de negócio:

```
fastapi/
└── api/
    ├── main.py                 # Ponto de entrada da aplicação
    ├── core/                   # Configurações e componentes centrais
    └── src/                    # Código-fonte organizado por domínio
        ├── heroes/             # Módulo específico (exemplo)
        │   ├── __init__.py
        │   ├── models.py       # Modelos SQLAlchemy
        │   ├── repository.py   # Operações de banco de dados
        │   ├── routes.py       # Definição de rotas
        │   ├── schemas.py      # Schemas Pydantic
        │   └── service.py      # Lógica de negócio
        └── users/              # Outro módulo (exemplo)
            ├── __init__.py
            ├── models.py
            ├── repository.py
            ├── routes.py
            ├── schemas.py
            └── service.py
```

Esta estrutura promove:

1. **Separação clara de responsabilidades**: Cada arquivo tem um propósito específico
2. **Organização por domínio**: Código relacionado é mantido próximo
3. **Facilidade de manutenção**: Modificações podem ser feitas de forma isolada
4. **Escalabilidade**: Novos módulos podem ser adicionados sem complicações

## Fluxo de Trabalho para Criação de Rotas

### 1. Definição de Schemas (DTOs)

O primeiro passo é definir os schemas Pydantic que serão usados para validação de entrada e formatação de saída.

Exemplo em `api/src/heroes/schemas.py`:

```python
from pydantic import BaseModel, Field, ConfigDict

class HeroBase(BaseModel):
    """Schema base com atributos comuns para criação e leitura de heróis."""
    name: str = Field(..., min_length=1, max_length=100, description="Nome do herói")
    description: str = Field(None, max_length=500, description="Descrição do herói")
    power_level: int = Field(..., ge=1, le=100, description="Nível de poder (1-100)")

class HeroCreate(HeroBase):
    """Schema para criação de um novo herói."""
    pass

class HeroUpdate(BaseModel):
    """Schema para atualização de um herói existente."""
    name: str = Field(None, min_length=1, max_length=100, description="Nome do herói")
    description: str = Field(None, max_length=500, description="Descrição do herói")
    power_level: int = Field(None, ge=1, le=100, description="Nível de poder (1-100)")

class HeroResponse(HeroBase):
    """Schema para resposta com dados de um herói."""
    model_config = ConfigDict(from_attributes=True)
    id: int
```

### 2. Implementação do Repositório

Em seguida, implemente o repositório para operações de banco de dados.

Exemplo em `api/src/heroes/repository.py`:

```python
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.heroes.models import Hero
from api.src.heroes.schemas import HeroCreate, HeroUpdate

class HeroRepository:
    """Repositório para operações de banco de dados relacionadas a heróis."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, hero_data: HeroCreate) -> Hero:
        """Cria um novo herói no banco de dados."""
        hero = Hero(**hero_data.model_dump())
        self.session.add(hero)
        await self.session.commit()
        await self.session.refresh(hero)
        return hero

    async def get_by_id(self, hero_id: int) -> Optional[Hero]:
        """Busca um herói pelo ID."""
        result = await self.session.execute(select(Hero).where(Hero.id == hero_id))
        return result.scalars().first()

    async def get_all(self) -> List[Hero]:
        """Retorna todos os heróis."""
        result = await self.session.execute(select(Hero))
        return list(result.scalars().all())

    async def update(self, hero_id: int, hero_data: HeroUpdate) -> Optional[Hero]:
        """Atualiza um herói existente."""
        hero = await self.get_by_id(hero_id)
        if not hero:
            return None
            
        # Atualiza apenas os campos fornecidos
        update_data = hero_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(hero, key, value)
            
        await self.session.commit()
        await self.session.refresh(hero)
        return hero

    async def delete(self, hero_id: int) -> bool:
        """Remove um herói pelo ID."""
        hero = await self.get_by_id(hero_id)
        if not hero:
            return False
            
        await self.session.delete(hero)
        await self.session.commit()
        return True
```

### 3. Implementação do Serviço (Opcional)

Para lógica de negócio mais complexa, é recomendado criar uma camada de serviço:

Exemplo em `api/src/heroes/service.py`:

```python
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from api.src.heroes.models import Hero
from api.src.heroes.repository import HeroRepository
from api.src.heroes.schemas import HeroCreate, HeroUpdate

class HeroService:
    """Serviço para operações relacionadas a heróis."""
    
    def __init__(self, session: AsyncSession):
        self.repo = HeroRepository(session)

    async def create_hero(self, hero_data: HeroCreate) -> Hero:
        """Cria um novo herói."""
        # Aqui poderíamos adicionar lógica de negócio adicional
        return await self.repo.create(hero_data)

    async def get_hero(self, hero_id: int) -> Optional[Hero]:
        """Busca um herói pelo ID."""
        return await self.repo.get_by_id(hero_id)

    async def get_all_heroes(self) -> List[Hero]:
        """Retorna todos os heróis."""
        return await self.repo.get_all()

    async def update_hero(self, hero_id: int, hero_data: HeroUpdate) -> Optional[Hero]:
        """Atualiza um herói existente."""
        # Poderia incluir validações adicionais aqui
        return await self.repo.update(hero_id, hero_data)

    async def delete_hero(self, hero_id: int) -> bool:
        """Remove um herói pelo ID."""
        return await self.repo.delete(hero_id)
```

### 4. Definição das Rotas

Finalmente, defina as rotas da API:

Exemplo em `api/src/heroes/routes.py`:

```python
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.src.heroes.schemas import HeroCreate, HeroResponse, HeroUpdate
from api.src.heroes.service import HeroService

# Prefixo para todas as rotas neste router
router = APIRouter(prefix="/heroes", tags=["heroes"])

@router.post("/", response_model=HeroResponse, status_code=status.HTTP_201_CREATED)
async def create_hero(
    hero_data: HeroCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Cria um novo herói.
    
    - **name**: Nome do herói (1-100 caracteres)
    - **description**: Descrição opcional do herói
    - **power_level**: Nível de poder do herói (1-100)
    """
    service = HeroService(session)
    hero = await service.create_hero(hero_data)
    return hero

@router.get("/{hero_id}", response_model=HeroResponse)
async def get_hero(
    hero_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna os detalhes de um herói específico pelo ID.
    
    - **hero_id**: ID do herói a ser consultado
    """
    service = HeroService(session)
    hero = await service.get_hero(hero_id)
    
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Herói com ID {hero_id} não encontrado"
        )
        
    return hero

@router.get("/", response_model=List[HeroResponse])
async def get_heroes(
    session: AsyncSession = Depends(get_session)
):
    """Retorna a lista de todos os heróis."""
    service = HeroService(session)
    heroes = await service.get_all_heroes()
    return heroes

@router.patch("/{hero_id}", response_model=HeroResponse)
async def update_hero(
    hero_id: int,
    hero_data: HeroUpdate,
    session: AsyncSession = Depends(get_session)
):
    """
    Atualiza um herói existente. Apenas os campos fornecidos serão modificados.
    
    - **hero_id**: ID do herói a ser atualizado
    - **name**: Novo nome do herói (opcional)
    - **description**: Nova descrição do herói (opcional)
    - **power_level**: Novo nível de poder do herói (opcional)
    """
    service = HeroService(session)
    hero = await service.update_hero(hero_id, hero_data)
    
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Herói com ID {hero_id} não encontrado"
        )
        
    return hero

@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hero(
    hero_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Remove um herói pelo ID.
    
    - **hero_id**: ID do herói a ser removido
    """
    service = HeroService(session)
    deleted = await service.delete_hero(hero_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Herói com ID {hero_id} não encontrado"
        )
```

### 5. Registro das Rotas na Aplicação Principal

Para que as rotas fiquem disponíveis, é necessário registrá-las na aplicação principal:

Em `api/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.src.heroes.routes import router as heroes_router
from api.src.users.routes import router as users_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos routers
app.include_router(heroes_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Rota raiz para verificação de saúde da API."""
    return {"message": "API Hero está online!"}
```

## Padrões de Rotas RESTful

O template segue padrões RESTful para criar uma API intuitiva e consistente:

| Método HTTP | URL                     | Ação                            | Código Status    |
|-------------|-------------------------|--------------------------------|-----------------|
| GET         | /api/v1/heroes          | Listar todos os heróis         | 200 OK          |
| GET         | /api/v1/heroes/{id}     | Obter um herói específico      | 200 OK          |
| POST        | /api/v1/heroes          | Criar um novo herói            | 201 Created     |
| PATCH       | /api/v1/heroes/{id}     | Atualizar parcialmente um herói| 200 OK          |
| PUT         | /api/v1/heroes/{id}     | Atualizar completamente um herói| 200 OK        |
| DELETE      | /api/v1/heroes/{id}     | Remover um herói               | 204 No Content  |

### Versionamento da API

Todas as rotas são prefixadas com `/api/v1/` para permitir futuras versões sem quebrar a compatibilidade:

```python
# Em api/core/config.py
API_V1_STR = "/api/v1"

# Em api/main.py
app.include_router(heroes_router, prefix=settings.API_V1_STR)
```

## Recursos Avançados de Rotas

### 1. Paginação

Para endpoints que retornam muitos itens, implemente paginação:

```python
@router.get("/", response_model=List[HeroResponse])
async def get_heroes(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna a lista de heróis com suporte a paginação.
    
    - **skip**: Número de itens para pular (offset)
    - **limit**: Número máximo de itens a retornar
    """
    service = HeroService(session)
    heroes = await service.get_heroes_paginated(skip=skip, limit=limit)
    return heroes
```

### 2. Filtragem

Adicione suporte a filtragem de resultados:

```python
@router.get("/", response_model=List[HeroResponse])
async def get_heroes(
    name: str = None,
    min_power: int = None,
    max_power: int = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna a lista de heróis com opções de filtragem.
    
    - **name**: Filtrar por nome (busca parcial)
    - **min_power**: Poder mínimo do herói
    - **max_power**: Poder máximo do herói
    """
    service = HeroService(session)
    heroes = await service.get_heroes_filtered(
        name=name,
        min_power=min_power,
        max_power=max_power
    )
    return heroes
```

### 3. Ordenação

Implemente ordenação de resultados:

```python
from enum import Enum

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/", response_model=List[HeroResponse])
async def get_heroes(
    sort_by: str = "name",
    order: SortOrder = SortOrder.asc,
    session: AsyncSession = Depends(get_session)
):
    """
    Retorna a lista de heróis com opções de ordenação.
    
    - **sort_by**: Campo para ordenação (name, power_level)
    - **order**: Direção da ordenação (asc, desc)
    """
    service = HeroService(session)
    heroes = await service.get_heroes_sorted(sort_by=sort_by, order=order.value)
    return heroes
```

### 4. Proteção de Rotas

Para rotas que requerem autenticação, use a dependência `get_current_user`:

```python
from api.core.security import get_current_user
from api.src.users.models import User

@router.post("/", response_model=HeroResponse, status_code=status.HTTP_201_CREATED)
async def create_hero(
    hero_data: HeroCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Cria um novo herói. Requer autenticação.
    """
    service = HeroService(session)
    hero = await service.create_hero(hero_data)
    return hero
```

### 5. Verificação de Permissões

Para implementar verificação de permissões mais granular:

```python
async def check_hero_owner(
    hero_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Hero:
    """Verifica se o usuário tem permissão para acessar o herói."""
    service = HeroService(session)
    hero = await service.get_hero(hero_id)
    
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Herói com ID {hero_id} não encontrado"
        )
        
    if hero.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este herói"
        )
        
    return hero

@router.patch("/{hero_id}", response_model=HeroResponse)
async def update_hero(
    hero_data: HeroUpdate,
    hero: Hero = Depends(check_hero_owner),
    session: AsyncSession = Depends(get_session)
):
    """
    Atualiza um herói existente. Requer ser dono do herói ou administrador.
    """
    service = HeroService(session)
    updated_hero = await service.update_hero(hero.id, hero_data)
    return updated_hero
```

## Documentação Automática de Rotas

Uma das grandes vantagens do FastAPI é a documentação automática de API através do Swagger e ReDoc. 

### Melhorando a Documentação

Para melhorar a documentação automática:

1. **Adicione docstrings detalhadas** a cada função de rota
2. **Use o parâmetro description nos campos Pydantic** para documentar cada campo
3. **Adicione exemplos** aos schemas Pydantic
4. **Agrupe rotas com tags** para melhor organização

```python
class HeroCreate(BaseModel):
    """Schema para criação de um novo herói."""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Nome do herói",
        example="Super Man"
    )
    description: str = Field(
        None, 
        max_length=500, 
        description="Descrição do herói",
        example="O homem de aço"
    )
    power_level: int = Field(
        ..., 
        ge=1, 
        le=100, 
        description="Nível de poder (1-100)",
        example=95
    )
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Spider Man",
                "description": "O amigo da vizinhança",
                "power_level": 85
            }
        }
```

```python
# Adicione metadados ao router
router = APIRouter(
    prefix="/heroes",
    tags=["heroes"],
    responses={404: {"description": "Recurso não encontrado"}},
)
```

## Estrutura de Resposta Padrão

Para manter consistência, o template usa um formato padrão para respostas de erro:

```python
from fastapi import HTTPException, status

# Resposta de erro padronizada
def raise_not_found(resource_type: str, resource_id: int):
    """Função auxiliar para lançar erro 404 com mensagem padronizada."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource_type} com ID {resource_id} não encontrado"
    )
```

## Teste de Rotas

O template inclui configuração para testes de rotas com pytest:

Exemplo em `tests/api/test_heroes.py`:

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.main import app
from api.src.heroes.models import Hero
from api.src.heroes.schemas import HeroCreate

@pytest.mark.asyncio
async def test_create_hero(test_client: AsyncClient, db_session: AsyncSession):
    """Testa a criação de um novo herói."""
    hero_data = {
        "name": "Test Hero",
        "description": "Hero for testing",
        "power_level": 75
    }
    
    response = await test_client.post("/api/v1/heroes/", json=hero_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == hero_data["name"]
    assert data["power_level"] == hero_data["power_level"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_hero(test_client: AsyncClient, db_session: AsyncSession, test_hero: Hero):
    """Testa a recuperação de um herói pelo ID."""
    response = await test_client.get(f"/api/v1/heroes/{test_hero.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_hero.id
    assert data["name"] == test_hero.name

@pytest.mark.asyncio
async def test_update_hero(test_client: AsyncClient, db_session: AsyncSession, test_hero: Hero):
    """Testa a atualização de um herói existente."""
    update_data = {"name": "Updated Hero Name"}
    
    response = await test_client.patch(f"/api/v1/heroes/{test_hero.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_hero.id
    assert data["name"] == update_data["name"]
    assert data["power_level"] == test_hero.power_level  # Não deve ter mudado

@pytest.mark.asyncio
async def test_delete_hero(test_client: AsyncClient, db_session: AsyncSession, test_hero: Hero):
    """Testa a remoção de um herói."""
    response = await test_client.delete(f"/api/v1/heroes/{test_hero.id}")
    
    assert response.status_code == 204
    
    # Verifica se o herói foi realmente removido
    get_response = await test_client.get(f"/api/v1/heroes/{test_hero.id}")
    assert get_response.status_code == 404
```

## Suporte a Solicitações Assíncronas (Async) e Síncronas (Sync)

O template usa SQLAlchemy assíncrono para melhor performance, mas você pode combinar código síncrono e assíncrono quando necessário:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def sync_heavy_computation(data):
    """Função síncrona para processamento pesado."""
    # Código síncrono aqui...
    return processed_data

@router.post("/process")
async def process_data(data: dict, background_tasks: BackgroundTasks):
    """
    Endpoint que processa dados de forma assíncrona e síncrona.
    """
    # Para tarefas rápidas síncronas em endpoints assíncronos
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(executor, sync_heavy_computation, data)
    
    # Para tarefas em background
    background_tasks.add_task(async_long_running_task, data)
    
    return {"result": result, "status": "background processing started"}
```

## Ciclo de Vida de Criação de um Novo Recurso

### 1. Crie o Modelo SQLAlchemy

```python
# api/src/products/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from api.core.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    hero_id = Column(Integer, ForeignKey("heroes.id"))
    
    hero = relationship("Hero", back_populates="products")
```

### 2. Crie os Schemas Pydantic

```python
# api/src/products/schemas.py
from pydantic import BaseModel, Field, ConfigDict

class ProductBase(BaseModel):
    """Schema base para produtos."""
    name: str = Field(..., min_length=1, max_length=100, description="Nome do produto")
    description: str = Field(None, max_length=500, description="Descrição do produto")
    price: float = Field(..., gt=0, description="Preço do produto")
    hero_id: int = Field(..., description="ID do herói associado ao produto")

class ProductCreate(ProductBase):
    """Schema para criação de um novo produto."""
    pass

class ProductUpdate(BaseModel):
    """Schema para atualização de um produto."""
    name: str = Field(None, min_length=1, max_length=100)
    description: str = Field(None, max_length=500)
    price: float = Field(None, gt=0)
    hero_id: int = Field(None)

class ProductResponse(ProductBase):
    """Schema para resposta com dados do produto."""
    model_config = ConfigDict(from_attributes=True)
    id: int
```

### 3. Crie o Repositório

```python
# api/src/products/repository.py
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.products.models import Product
from api.src.products.schemas import ProductCreate, ProductUpdate

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, product_data: ProductCreate) -> Product:
        product = Product(**product_data.model_dump())
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    # Implemente outros métodos CRUD...
```

### 4. Crie o Serviço (opcional)

```python
# api/src/products/service.py
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from api.src.products.models import Product
from api.src.products.repository import ProductRepository
from api.src.products.schemas import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, session: AsyncSession):
        self.repo = ProductRepository(session)

    async def create_product(self, product_data: ProductCreate) -> Product:
        return await self.repo.create(product_data)

    # Implemente outros métodos...
```

### 5. Crie as Rotas

```python
# api/src/products/routes.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.src.products.schemas import ProductCreate, ProductResponse, ProductUpdate
from api.src.products.service import ProductService

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    session: AsyncSession = Depends(get_session)
):
    """Cria um novo produto."""
    service = ProductService(session)
    product = await service.create_product(product_data)
    return product

# Implemente outras rotas CRUD...
```

### 6. Registre o Router na Aplicação

```python
# api/main.py
from api.src.products.routes import router as products_router

# Adicione à lista de routers
app.include_router(products_router, prefix=settings.API_V1_STR)
```

### 7. Crie a Migração do Banco de Dados

```bash
uv run alembic revision --autogenerate -m "add products table"
uv run alembic upgrade head
```

## Conclusão

A criação de rotas no template FastAPI segue uma abordagem estruturada e modular, promovendo boas práticas de desenvolvimento:

1. **Separação clara de responsabilidades** entre models, repositories, services, schemas e routes
2. **Validação automática** de dados de entrada e saída com Pydantic
3. **Documentação automática** através do OpenAPI (Swagger)
4. **Rotas RESTful** para uma API intuitiva e consistente
5. **Suporte assíncrono** para melhor performance
6. **Testes automatizados** para garantir o correto funcionamento

Seguindo estas diretrizes, você pode expandir o template com novos recursos mantendo a coerência e qualidade da API.

---

*[Voltar ao Índice](./index.md)*
