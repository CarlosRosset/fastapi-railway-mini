# Migrações com Alembic no Template FastAPI

## Introdução

Alembic é uma ferramenta de migração de banco de dados que trabalha em conjunto com SQLAlchemy para gerenciar alterações no esquema do banco de dados de maneira controlada e versionada. No contexto do template FastAPI, o Alembic é fundamental para garantir que o esquema do banco de dados evolua de forma consistente, rastreável e segura ao longo do desenvolvimento do projeto.

## Por que Usar Migrações de Banco de Dados?

O uso de migrações traz diversos benefícios ao desenvolvimento:

1. **Controle de versão para esquemas**: Histórico completo das mudanças no banco de dados
2. **Rollback seguro**: Possibilidade de reverter alterações problemáticas
3. **Implantação consistente**: Garante que todos os ambientes tenham a mesma estrutura de banco
4. **Colaboração facilitada**: Múltiplos desenvolvedores podem fazer alterações sem conflitos
5. **Automação**: Integração com pipelines CI/CD para atualizações automáticas
6. **Documentação**: As migrações servem como documentação autoexplicativa das mudanças no esquema

## Estrutura do Alembic no Template

No template FastAPI, o Alembic está configurado com a seguinte estrutura:

```
fastapi/
├── alembic/
│   ├── versions/             # Arquivos de migração versionados
│   │   ├── 3dee83604016_initial_migration.py
│   │   └── ef2910566747_add_users_table.py
│   ├── env.py                # Configuração do ambiente Alembic
│   └── script.py.mako        # Template para novos arquivos de migração
├── alembic.ini               # Configuração principal do Alembic
└── api/
    └── core/
        └── database.py       # Definição do SQLAlchemy Base
```

### Configuração do Alembic

#### alembic.ini

Este arquivo contém as configurações gerais do Alembic, incluindo a URI de conexão com o banco de dados (que será sobrescrita pelo env.py) e configurações de logging:

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/hero_db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console
qualname =

[logger_sqlalchemy]
level = ERROR
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = ERROR
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### env.py

O arquivo `env.py` é responsável por configurar o ambiente de execução do Alembic. No template, ele foi configurado para:

1. Importar automaticamente todos os modelos SQLAlchemy
2. Utilizar a URL de banco de dados definida nas configurações da aplicação (config.py)
3. Configurar o suporte para migrações assíncronas

Aqui estão os pontos principais do `env.py`:

```python
# Importação automática de modelos
src_path = Path(__file__).parent.parent / "api" / "src"
for path in src_path.rglob("*.py"):
    if path.name != "__init__.py":
        module_path = str(path.relative_to(Path(__file__).parent.parent)).replace(
            os.sep, "."
        )[:-3]
        try:
            importlib.import_module(module_path)
        except Exception as e:
            print(f"Failed to import {module_path}: {e}")

# Configuração da URL do banco de dados
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Definição do metadata para autogeneração
target_metadata = Base.metadata

# Suporte a migrações assíncronas
async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()
```

## Ciclo de Trabalho com Migrações

### 1. Inicialização (Já Realizada no Template)

O template já vem com o Alembic inicializado e configurado. Isso inclui:
- Diretório `alembic` criado
- Arquivo de configuração `alembic.ini`
- Ambiente configurado em `env.py`
- Migrações iniciais para as tabelas heroes e users

### 2. Desenvolvimento de Novos Modelos

Quando você desenvolve novos modelos SQLAlchemy, siga este fluxo:

1. **Crie ou modifique seus modelos SQLAlchemy**:
   
   Exemplo de um novo modelo em `api/src/products/models.py`:
   
   ```python
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

2. **Crie uma migração para as alterações**:
   
   ```bash
   uv run alembic revision --autogenerate -m "add products table"
   ```
   
   Este comando irá:
   - Detectar automaticamente as alterações entre o estado do banco de dados atual e os modelos SQLAlchemy
   - Gerar um novo arquivo de migração na pasta `alembic/versions/`
   - Preencher automaticamente as funções `upgrade()` e `downgrade()` com as alterações necessárias

3. **Verifique o arquivo de migração gerado**:
   
   É crucial revisar o arquivo de migração gerado antes de aplicá-lo:
   - Verifique se todas as alterações esperadas foram detectadas
   - Confirme que não há operações destrutivas não intencionais
   - Adicione manualmente quaisquer alterações que não tenham sido detectadas automaticamente

4. **Aplique a migração ao banco de dados**:
   
   ```bash
   uv run alembic upgrade head
   ```
   
   Ou, para uma revisão específica:
   
   ```bash
   uv run alembic upgrade +1  # Avança uma revisão
   ```
   
   Ou:
   
   ```bash
   uv run alembic upgrade <revision_id>  # Avança até a revisão específica
   ```

### 3. Aplicação Automática de Migrações

No template FastAPI, as migrações são aplicadas automaticamente na inicialização da aplicação. Isso é implementado no arquivo `api/main.py`:

```python
@app.on_event("startup")
async def apply_migrations():
    """Apply migrations at startup."""
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
```

Esta abordagem garante que o banco de dados esteja sempre atualizado quando a aplicação é iniciada, simplificando o processo de implantação.

## Casos de Uso Comuns

### Adicionar uma Nova Tabela

1. Crie o modelo SQLAlchemy em um módulo apropriado
2. Gere a migração: `uv run alembic revision --autogenerate -m "add new table"`
3. Verifique o arquivo de migração gerado
4. Aplique a migração: `uv run alembic upgrade head`

### Adicionar uma Nova Coluna a uma Tabela Existente

1. Adicione a nova coluna ao modelo SQLAlchemy
2. Gere a migração: `uv run alembic revision --autogenerate -m "add column to table"`
3. Verifique o arquivo de migração gerado
4. Aplique a migração: `uv run alembic upgrade head`

### Modificar uma Coluna Existente

1. Modifique a definição da coluna no modelo SQLAlchemy
2. Gere a migração: `uv run alembic revision --autogenerate -m "modify column"`
3. **Atenção**: Verifique cuidadosamente se a migração gerada é segura, especialmente em relação a potenciais perdas de dados
4. Aplique a migração: `uv run alembic upgrade head`

### Criar Relacionamentos Entre Tabelas

1. Adicione as relações nos modelos SQLAlchemy:
   - Chave estrangeira com `ForeignKey`
   - Relacionamento com `relationship`
2. Gere a migração: `uv run alembic revision --autogenerate -m "add relationships"`
3. Verifique o arquivo de migração gerado
4. Aplique a migração: `uv run alembic upgrade head`

### Reverter uma Migração (Rollback)

Para reverter para uma versão anterior:

```bash
# Voltar uma migração
uv run alembic downgrade -1

# Voltar para uma revisão específica
uv run alembic downgrade <revision_id>

# Voltar ao estado inicial (antes de qualquer migração)
uv run alembic downgrade base
```

## Migrações Manuais

Em alguns casos, você pode precisar escrever migrações manualmente:

1. Crie uma revisão vazia:
   ```bash
   uv run alembic revision -m "manual migration description"
   ```

2. Edite o arquivo gerado para adicionar as operações necessárias nas funções `upgrade()` e `downgrade()`:

   ```python
   def upgrade() -> None:
       # Operações manuais
       op.execute(
           """
           CREATE OR REPLACE FUNCTION update_modified_column()
           RETURNS TRIGGER AS $$
           BEGIN
               NEW.updated_at = now();
               RETURN NEW;
           END;
           $$ language 'plpgsql';
           """
       )
       
       op.execute(
           """
           CREATE TRIGGER update_hero_modtime
               BEFORE UPDATE ON heroes
               FOR EACH ROW
               EXECUTE PROCEDURE update_modified_column();
           """
       )
   
   def downgrade() -> None:
       # Operações para reverter as mudanças
       op.execute("DROP TRIGGER IF EXISTS update_hero_modtime ON heroes;")
       op.execute("DROP FUNCTION IF EXISTS update_modified_column();")
   ```

## Operações Avançadas

### Operações de Dados

O Alembic permite que você manipule dados como parte de uma migração:

```python
def upgrade() -> None:
    # Criar a tabela
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Inserir dados iniciais
    op.bulk_insert(
        sa.table('roles',
                sa.column('id', sa.Integer),
                sa.column('name', sa.String)),
        [
            {'id': 1, 'name': 'admin'},
            {'id': 2, 'name': 'user'},
            {'id': 3, 'name': 'guest'},
        ]
    )
```

### Migrações com Branches

Para projetos complexos, o Alembic suporta branches de migração:

```bash
# Criar uma nova branch a partir de uma revisão específica
uv run alembic revision --head=<parent_revision> -m "branch description"
```

Isso é útil quando múltiplas equipes estão trabalhando em diferentes recursos que afetam o esquema do banco.

### Merge de Branches

Quando você precisar mesclar branches:

```bash
uv run alembic merge -m "merge branches" <revision1> <revision2>
```

## Boas Práticas

### 1. Revisão de Migrações

Sempre revise cuidadosamente os arquivos de migração gerados automaticamente antes de aplicá-los, especialmente em ambientes de produção. O Alembic pode não detectar corretamente todas as alterações ou gerar operações que podem resultar em perda de dados.

### 2. Migrações Atômicas

Tente manter cada migração focada em uma única alteração lógica. Isso torna mais fácil entender, testar e, se necessário, reverter alterações específicas.

### 3. Testes

Teste suas migrações em um ambiente de desenvolvimento ou teste antes de aplicá-las em produção. Isso pode evitar surpresas desagradáveis durante implantações.

### 4. Evite Editar Migrações Aplicadas

Nunca edite um arquivo de migração que já foi aplicado a qualquer ambiente. Em vez disso, crie uma nova migração que corrige ou evolui a anterior.

### 5. Backup

Sempre faça backup do banco de dados antes de aplicar migrações em ambientes de produção.

### 6. Documentação

Adicione comentários descritivos aos seus arquivos de migração, explicando a razão das alterações e quaisquer considerações especiais.

## Solução de Problemas Comuns

### Falha ao Detectar Alterações

**Problema**: O Alembic não detecta alterações nos modelos.

**Solução**:
1. Verifique se o modelo foi corretamente importado no ambiente do Alembic
2. Confirme que o modelo herda de `Base`
3. Verifique se a tabela já existe no banco de dados
4. Considere criar uma migração manual

### Conflitos de Migração

**Problema**: Conflitos entre duas migrações que alteram a mesma tabela.

**Solução**:
1. Use `alembic merge` para mesclar branches conflitantes
2. Em casos complexos, pode ser necessário criar uma migração manual para resolver o conflito

### Erros durante Upgrade/Downgrade

**Problema**: Erros ao aplicar ou reverter migrações.

**Solução**:
1. Verifique o registro do Alembic para entender o ponto de falha
2. Corrija o problema no esquema ou no arquivo de migração
3. Em caso de emergência, considere `alembic stamp` para marcar uma revisão como aplicada sem executá-la

## Referências e Recursos

- [Documentação oficial do Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Tutoriais sobre Alembic e SQLAlchemy](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Alembic com SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

## Conclusão

O Alembic é uma ferramenta poderosa que, quando usada corretamente, proporciona um sistema robusto de gerenciamento de esquemas de banco de dados. No contexto do template FastAPI, ele oferece uma integração perfeita com SQLAlchemy para garantir que o banco de dados evolua de forma controlada e segura ao longo do ciclo de vida da aplicação.

A configuração automática de migrações na inicialização da aplicação simplifica o processo de implantação, garantindo que o banco de dados esteja sempre em sincronia com o código da aplicação.

---

*[Voltar ao Índice](./index.md)*
