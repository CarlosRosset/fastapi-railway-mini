# Guia Passo a Passo: Banco de Dados e Migrações

Este guia oferece instruções detalhadas sobre como trabalhar com o banco de dados no template FastAPI, desde a criação de modelos até a gestão de migrações, com ênfase especial em como realizar atualizações corretamente e integrá-las com processos de CI/CD.

## Sumário

1. [Visão Geral do Sistema de Banco de Dados](#visão-geral-do-sistema-de-banco-de-dados)
2. [Criando Novos Modelos - Passo a Passo](#criando-novos-modelos---passo-a-passo)
3. [Alterando Modelos Existentes](#alterando-modelos-existentes)
4. [Fluxo Completo de Migrações](#fluxo-completo-de-migrações)
5. [Integração com CI/CD](#integração-com-cicd)
6. [Resolução de Problemas Comuns](#resolução-de-problemas-comuns)
7. [Operações Avançadas de Migração](#operações-avançadas-de-migração)

## Visão Geral do Sistema de Banco de Dados

O template FastAPI utiliza:

- **SQLAlchemy**: ORM (Object-Relational Mapping) para interação com o banco de dados
- **Alembic**: Ferramenta de migrações para controle de versão do esquema do banco
- **Pydantic**: Para validação de dados e conversão entre modelos ORM e esquemas de API
- **PostgreSQL**: Sistema de banco de dados relacional (mas outros podem ser usados)

### Estrutura de Arquivos Relacionados ao Banco de Dados

```
fastapi/
├── alembic/
│   ├── versions/             # Arquivos de migração gerados
│   ├── env.py                # Configuração do ambiente Alembic
│   └── script.py.mako        # Template para novos arquivos de migração
├── alembic.ini               # Configuração do Alembic
└── api/
    ├── core/
    │   └── database.py       # Configuração do SQLAlchemy
    └── src/
        └── module_name/
            ├── models.py     # Modelos SQLAlchemy
            └── schemas.py    # Esquemas Pydantic
```

## Criando Novos Modelos - Passo a Passo

Vamos criar uma nova entidade "Product" para demonstrar o processo completo:

### 1. Defina o Modelo SQLAlchemy

Crie ou edite o arquivo `api/src/products/models.py`:

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.core.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    hero_id = Column(Integer, ForeignKey("heroes.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamento com a tabela heroes
    hero = relationship("Hero", back_populates="products")
```

> 💡 **Dica**: Certifique-se de criar também o arquivo `__init__.py` vazio no diretório `products` para que ele seja reconhecido como um módulo Python.

### 2. Atualize os Relacionamentos em Outros Modelos (Se Necessário)

Em `api/src/heroes/models.py`, adicione o relacionamento inverso:

```python
from sqlalchemy.orm import relationship

# Dentro da classe Hero
products = relationship("Product", back_populates="hero", cascade="all, delete-orphan")
```

### 3. Crie os Esquemas Pydantic

Em `api/src/products/schemas.py`:

```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

# Esquema base para entrada de dados
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    hero_id: Optional[int] = None

# Esquema para criação
class ProductCreate(ProductBase):
    pass

# Esquema para atualização (todos os campos opcionais)
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    hero_id: Optional[int] = None

# Esquema para resposta
class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
```

### 4. Gere a Migração com Alembic

Agora gere automaticamente a migração para criar a nova tabela:

```bash
# Certifique-se de estar na raiz do projeto
cd /caminho/para/seu/projeto

# Ative o ambiente virtual
source .venv/bin/activate

# Gere a migração
uv run alembic revision --autogenerate -m "add products table"
```

Este comando:
1. Analisa seus modelos SQLAlchemy
2. Compara com o estado atual do banco de dados
3. Gera um arquivo de migração com as alterações necessárias

### 5. Verifique o Arquivo de Migração Gerado

Navegue até o diretório `alembic/versions/` e encontre o arquivo mais recente (formato: `hash_add_products_table.py`).

Revise cuidadosamente o arquivo, verificando:
- Se a tabela está sendo criada corretamente
- Se as colunas, tipos de dados e restrições estão corretos
- Se os índices e chaves estrangeiras estão configurados adequadamente

Exemplo do que você deve encontrar:

```python
# ... importações ...

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('hero_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['hero_id'], ['heroes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    # ### end Alembic commands ###
```

### 6. Aplique a Migração

Depois de revisar e confirmar que a migração está correta:

```bash
uv run alembic upgrade head
```

### 7. Verifique no Banco de Dados

Conecte-se ao seu banco de dados para verificar se a tabela foi criada corretamente:

```bash
psql -U seu_usuario -d seu_banco_de_dados

# No console do PostgreSQL
\dt  # Lista todas as tabelas
\d products  # Descreve a estrutura da tabela products
```

## Alterando Modelos Existentes

Para modificar uma tabela existente, siga este processo:

### 1. Atualize o Modelo SQLAlchemy

Por exemplo, para adicionar uma nova coluna `stock` à tabela `products`:

```python
# Em api/src/products/models.py
class Product(Base):
    # ... colunas existentes ...
    stock = Column(Integer, default=0, nullable=False)
    # ... resto do modelo ...
```

### 2. Atualize os Esquemas Pydantic

```python
# Em api/src/products/schemas.py
class ProductBase(BaseModel):
    # ... campos existentes ...
    stock: int = Field(0, ge=0)

# Atualize também ProductUpdate e Product
```

### 3. Gere a Migração

```bash
uv run alembic revision --autogenerate -m "add stock column to products"
```

### 4. Verifique e Modifique o Arquivo de Migração (Se Necessário)

Revise o arquivo gerado em `alembic/versions/`. Para este exemplo, você deve ver algo como:

```python
def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('stock', sa.Integer(), nullable=False, server_default='0'))
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'stock')
    # ### end Alembic commands ###
```

> ⚠️ **Importante**: Adicionar colunas `NOT NULL` a tabelas existentes requer um valor padrão (`server_default`). O Alembic geralmente adiciona isso automaticamente, mas sempre verifique.

### 5. Aplique a Migração

```bash
uv run alembic upgrade head
```

## Fluxo Completo de Migrações

Este diagrama ilustra o fluxo completo de trabalho com migrações:

```
┌────────────────────┐
│ 1. Alterar modelo  │
│   SQLAlchemy       │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ 2. Alterar esquema │
│    Pydantic        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ 3. Gerar migração  │
│ alembic revision   │
│ --autogenerate     │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ 4. Revisar arquivo │
│    de migração     │◄────┐
└─────────┬──────────┘     │
          │                │
          │                │
          ▼                │
    ┌───────────┐    Não   │
    │ Migração  ├──────────┘
    │ correta?  │
    └─────┬─────┘
          │ Sim
          ▼
┌────────────────────┐
│ 5. Aplicar         │
│    migração        │
│ alembic upgrade    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ 6. Testar no banco │
│    de dados        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ 7. Commit e push   │
│    das alterações  │
└────────────────────┘
```

## Integração com CI/CD

### CI: Verificação Automática de Migrações

Em seu pipeline de CI, você pode adicionar etapas para verificar se as migrações são válidas:

```yaml
# Exemplo para GitHub Actions
name: Database Migration Check

on:
  pull_request:
    branches: [ main ]
    paths:
      - 'api/src/**/models.py'
      - 'alembic/**'

jobs:
  migration-check:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh && echo "$HOME/.cargo/bin" >> $GITHUB_PATH
      
      - name: Install dependencies
        run: |
          uv venv
          source .venv/bin/activate
          uv sync
      
      - name: Run migrations
        run: |
          source .venv/bin/activate
          export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
          uv run alembic upgrade head
      
      - name: Check for new migrations
        run: |
          source .venv/bin/activate
          export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
          # Verifica se há alterações não migradas
          REVISION=$(uv run alembic revision --autogenerate -m "ci check")
          if [[ $REVISION == *"No changes detected"* ]]; then
            echo "No migration changes detected."
          else
            echo "Warning: Detected model changes without migrations."
            exit 1
          fi
```

### CD: Aplicação Automática de Migrações

Para ambientes de produção, as migrações podem ser aplicadas como parte do processo de implantação:

```yaml
# Exemplo para GitHub Actions - Deploy
name: Deploy with Migrations

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      # ... etapas de checkout e configuração ...
      
      - name: Apply migrations
        run: |
          source .venv/bin/activate
          uv run alembic upgrade head
        env:
          DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
      
      # ... etapas de implantação da aplicação ...
```

### Migrações Manuais em Produção

Se preferir executar migrações manualmente em produção (abordagem mais conservadora):

1. **Gere um script SQL a partir das migrações**:

```bash
uv run alembic upgrade head --sql > migration.sql
```

2. **Revise o script SQL gerado**

3. **Aplique o script durante uma janela de manutenção**:

```bash
psql -U usuario_producao -d banco_producao -f migration.sql
```

## Resolução de Problemas Comuns

### Problema: "Table already exists" ao aplicar migrações

**Causa**: A tabela já foi criada, mas o Alembic não tem registro dessa operação.

**Solução**:
1. Marque a migração como aplicada sem executá-la:
   ```bash
   uv run alembic stamp <revision_id>
   ```
2. Ou, se estiver começando do zero, use:
   ```bash
   uv run alembic stamp head
   ```

### Problema: Migração gerada incorretamente

**Causa**: O Alembic nem sempre detecta todas as alterações corretamente, especialmente para operações complexas.

**Solução**:
1. Edite manualmente o arquivo de migração para incluir as operações necessárias
2. Estude a [documentação de operações do Alembic](https://alembic.sqlalchemy.org/en/latest/ops.html) para entender como implementar operações específicas

### Problema: Erro de chave estrangeira ao aplicar migração

**Causa**: A ordem de criação/alteração das tabelas é importante devido às restrições de chave estrangeira.

**Solução**:
1. Edite a migração para ajustar a ordem das operações
2. Ou divida em múltiplas migrações (primeiro crie a tabela referenciada, depois a que tem a chave estrangeira)

### Problema: Dados perdidos em atualizações de coluna

**Causa**: Alterações de esquema podem levar à perda de dados se não forem cuidadosamente planejadas.

**Solução**:
1. Para renomear colunas, use `op.alter_column()` em vez de excluir e recriar
2. Para alterar tipos de dados, considere adicionar uma nova coluna, migrar os dados e depois remover a antiga

## Operações Avançadas de Migração

### Migração com Dados

Para migrações que envolvem manipulação de dados:

```python
def upgrade() -> None:
    # Criar nova coluna
    op.add_column('products', sa.Column('full_price', sa.Float(), nullable=True))
    
    # Migrar dados (copiar valores de 'price' para 'full_price')
    connection = op.get_bind()
    connection.execute(text("UPDATE products SET full_price = price"))
    
    # Tornar a coluna NOT NULL após preenchê-la
    op.alter_column('products', 'full_price', nullable=False)

def downgrade() -> None:
    op.drop_column('products', 'full_price')
```

### Adicionando Índices

```python
def upgrade() -> None:
    op.create_index(
        'ix_products_name',
        'products',
        ['name'],
        unique=False
    )

def downgrade() -> None:
    op.drop_index('ix_products_name', 'products')
```

### Migração Condicional

```python
def upgrade() -> None:
    # Verificar se a coluna já existe
    conn = op.get_bind()
    insp = inspect(conn)
    columns = insp.get_columns('products')
    
    if 'discount' not in [col['name'] for col in columns]:
        op.add_column('products', sa.Column('discount', sa.Float(), nullable=True))
```

### Renomeando Tabelas ou Colunas

```python
def upgrade() -> None:
    # Renomear tabela
    op.rename_table('old_table_name', 'new_table_name')
    
    # Renomear coluna
    op.alter_column('table_name', 'old_column_name', new_column_name='new_column_name')
```

## Conclusão

Um bom sistema de migrações de banco de dados é essencial para manter a integridade e a evolução do esquema ao longo do ciclo de vida da aplicação. Com o Alembic e o SQLAlchemy, o template FastAPI fornece uma solução robusta e flexível para gerenciar essas alterações de forma controlada e segura.

Seguindo as práticas e os passos descritos neste documento, você poderá:
- Criar novos modelos com confiança
- Alterar a estrutura do banco de dados sem perda de dados
- Garantir consistência entre ambientes de desenvolvimento e produção
- Integrar as migrações com seu pipeline de CI/CD

Lembre-se de que as migrações de banco de dados são operações potencialmente perigosas, especialmente em produção. Sempre teste suas migrações em ambientes de desenvolvimento e homologação antes de aplicá-las em produção.

---

*[Voltar ao Índice](./index.md)*
