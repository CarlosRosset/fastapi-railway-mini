# Template Railway FastAPI 🚀
Template para deploy de aplicações FastAPI no Railway com PostgreSQL - Uma solução moderna e pronta para produção.

## Funcionalidades ✨
- 🔄 Operações CRUD completas para heróis
- 📊 SQLAlchemy assíncrono com PostgreSQL
- 🔄 Migrações automáticas com Alembic
- 🏗️ Arquitetura limpa com padrão de repositório
- ⚠️ Tratamento personalizado de exceções
- 🔍 Pipeline de CI e testes
- 🧹 Configuração de linter com hooks de pre-commit
- 🚂 Deploy com um clique no Railway

## Faça o Deploy Agora! 🚀
[![Deploy no Railway](https://railway.com/button.svg)](https://railway.com/template/wbTudS?referralCode=beBXJA)

## Estrutura do Projeto 📁
```
api/
├── core/              # Funcionalidades principais
│   ├── config.py      # Configuração de ambiente e aplicação
│   ├── database.py    # Conexão e sessões do banco de dados
│   ├── exceptions.py  # Manipuladores globais de exceções
│   ├── logging.py     # Configuração de log
│   └── security.py    # Autenticação e segurança
├── src/
│   ├── heroes/        # Módulo de heróis
│   │   ├── models.py      # Modelos de banco de dados
│   │   ├── repository.py  # Camada de acesso a dados
│   │   ├── routes.py      # Endpoints da API
│   │   └── schemas.py     # Modelos Pydantic
│   └── users/         # Módulo de usuários
│       ├── models.py      # Modelos de usuários
│       ├── repository.py  # Acesso a dados de usuários
│       ├── routes.py      # Endpoints de usuários
│       └── schemas.py     # Schemas de usuários
├── utils/            # Funções utilitárias
└── main.py          # Ponto de entrada da aplicação
```

## Requisitos 📋
- Python 3.8+
- PostgreSQL

## Documentação 📚
Este template vem com documentação abrangente para ajudá-lo a começar rapidamente:

- [**Instalação e Execução**](docs/instalacao_execucao.md) - Configure seu ambiente com UV
- [**Gerenciamento de Dependências**](docs/gerenciamento_dependencias.md) - Gerencie pacotes Python com UV
- [**Guia de Banco de Dados**](docs/banco_de_dados_passo_a_passo.md) - Guia passo a passo para configuração do banco de dados
- [**Criação de Rotas**](docs/criacao_rotas.md) - Aprenda como adicionar novos endpoints
- [**Migrações com Alembic**](docs/alembic_migracao.md) - Fluxos de trabalho de migração de banco de dados
- [**Autenticação**](docs/autenticacao_jwt.md) - Configuração de autenticação JWT
- [**Testes**](docs/testes.md) - Escrevendo e executando testes
- [**Boas Práticas**](docs/boas_praticas.md) - Padrões e normas de código
- [**Índice Completo da Documentação**](docs/index.md) - Lista completa de recursos de documentação

## Configuração 🛠️
1. Instale o uv (siga as instruções [aqui](https://docs.astral.sh/uv/#getting-started))

2. Clone o repositório:
```bash
git clone https://github.com/CarlosRosset/template-railway-fastapi.git
cd template-railway-fastapi
```

3. Instale as dependências com uv:
```bash
uv sync
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais de banco de dados
```

> 💡 **Importante**: 
> - A DATABASE_URL deve começar com `postgresql+asyncpg://` (ex: `postgresql+asyncpg://usuario:senha@localhost:5432/nomebanco`)
> - Após atualizar as variáveis de ambiente, feche e reabra o VS Code para recarregar a configuração adequadamente. O VS Code ativará automaticamente o ambiente virtual quando você reabrir.

5. Inicie a aplicação:

Usando o terminal:
```bash
uv run uvicorn api.main:app
```

Usando o VS Code:
> 💡 Se você estiver usando o VS Code, incluímos configurações de execução na pasta `.vscode`. Basta pressionar `F5` ou usar o painel "Executar e Depurar" para iniciar a aplicação!

6. (Opcional) Habilite hooks de pre-commit para linting:
```bash
uv run pre-commit install
```
> 💡 Isso habilitará a formatação automática de código e verificações de linting antes de cada commit

## Criando uma Migração 🔄
1. Faça alterações em seus modelos
2. Gere a migração:
```bash
alembic revision --autogenerate -m "sua mensagem de migração"
```

Observação: As migrações serão aplicadas automaticamente quando você iniciar a aplicação - não é necessário executar `alembic upgrade head` manualmente!

## Endpoints da API 📊
### Heróis
- `GET /heroes` - Listar todos os heróis
- `GET /heroes/{id}` - Obter um herói específico
- `POST /heroes` - Criar um novo herói
- `PATCH /heroes/{id}` - Atualizar um herói
- `DELETE /heroes/{id}` - Excluir um herói

### Autenticação
- `POST /auth/register` - Registrar um novo usuário
- `POST /auth/login` - Fazer login e obter token de acesso
- `GET /auth/me` - Obter perfil do usuário atual

## Exemplo de Uso 📝
Criar um novo herói:
```bash
curl -X POST "http://localhost:8000/heroes/" -H "Content-Type: application/json" -d '{
    "name": "Peter Parker",
    "alias": "Homem-Aranha",
    "powers": "Escalar paredes, super força, sentido aranha"
}'
```
