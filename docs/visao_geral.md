# Visão Geral do Projeto FastAPI

## Introdução

O Template FastAPI é uma estrutura de projeto moderna e escalável para o desenvolvimento de APIs RESTful usando o framework FastAPI. Este template incorpora as melhores práticas de desenvolvimento de software, arquitetura limpa e padrões modernos de programação Python, proporcionando uma base sólida para aplicações robustas e de alto desempenho.

## Arquitetura do Projeto

O projeto segue uma arquitetura modular e bem organizada, inspirada em princípios de Clean Architecture e padrões de design como Repository Pattern. Esta abordagem facilita a manutenção, testabilidade e escalabilidade da aplicação.

### Estrutura de Diretórios

```
api/
├── core/              # Funcionalidades centrais
│   ├── config.py      # Configurações e variáveis de ambiente
│   ├── database.py    # Conexão e sessões de banco de dados
│   ├── exceptions.py  # Manipuladores de exceções globais
│   ├── logging.py     # Configuração de logging
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

### Camadas da Aplicação

O projeto é organizado nas seguintes camadas:

1. **API (Routes)**: Camada responsável por receber requisições HTTP, validar parâmetros de entrada e retornar respostas apropriadas.
2. **Schemas**: Modelos Pydantic que definem a estrutura dos dados de entrada e saída da API.
3. **Repository**: Camada que abstrai o acesso ao banco de dados, implementando operações CRUD e consultas específicas.
4. **Models**: Modelos SQLAlchemy que definem a estrutura das tabelas do banco de dados.
5. **Core**: Componentes fundamentais como configuração, conexão com banco de dados e segurança.

Este design em camadas proporciona:
- **Separação de responsabilidades**: Cada componente tem uma função bem definida
- **Testabilidade**: Fácil implementação de testes para cada camada
- **Manutenibilidade**: Alterações em uma camada têm impacto mínimo nas outras
- **Escalabilidade**: Novos recursos podem ser adicionados de forma modular

## Tecnologias Utilizadas

### Componentes Principais

- **Python 3.8+**: Linguagem base para o desenvolvimento
- **FastAPI**: Framework web de alta performance
- **Pydantic**: Validação de dados e configurações
- **SQLAlchemy**: ORM para acesso ao banco de dados
- **Alembic**: Sistema de migração de banco de dados
- **PostgreSQL**: Banco de dados relacional
- **AsyncPG**: Driver assíncrono para PostgreSQL
- **UV**: Gerenciador moderno de pacotes e ambientes Python
- **JWT**: JSON Web Tokens para autenticação
- **Pytest**: Framework para testes automatizados

### Recursos Destacados

1. **Operações Assíncronas**: Utilização intensiva de recursos assíncronos do Python para maximizar a performance.
2. **SQLAlchemy Assíncrono**: Conexões de banco de dados totalmente assíncronas através do SQLAlchemy 2.0 e AsyncPG.
3. **Injeção de Dependências**: Implementação do padrão de injeção de dependências nativo do FastAPI.
4. **Migrações Automáticas**: Sistema de migrações com Alembic para evolução segura do esquema de banco de dados.
5. **Autenticação JWT**: Sistema completo de autenticação baseado em tokens JWT.
6. **Exceções Personalizadas**: Tratamento global de exceções para respostas de erro consistentes.
7. **Pipeline CI**: Configuração para integração contínua com GitHub Actions.
8. **Deploy Simplificado**: Preparado para deploy na plataforma Railway com um clique.

## Fluxo de Trabalho de Desenvolvimento

### Desenvolvimento Local

O ambiente de desenvolvimento local foi projetado para ser rápido e fácil de configurar, utilizando UV para gerenciamento de dependências e ambientes virtuais.

#### Requisitos Básicos
- Python 3.8+
- PostgreSQL
- UV instalado globalmente

#### Passos para Configuração

1. **Clone o repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd <nome-do-diretorio>
   ```

2. **Instale as dependências**:
   ```bash
   uv sync
   ```
   Este comando utiliza o `pyproject.toml` para criar um ambiente virtual e instalar todas as dependências necessárias.

3. **Configure as variáveis de ambiente**:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com as configurações do seu ambiente
   ```

4. **Execute a aplicação**:
   ```bash
   uv run uvicorn api.main:app --reload
   ```
   Ou utilize a configuração de execução do VSCode (F5).

### Ciclo de Desenvolvimento

O ciclo típico de desenvolvimento segue estas etapas:

1. **Planejamento**: Definição de novos recursos ou correções
2. **Implementação**:
   - Criação/atualização de modelos de banco de dados
   - Geração de migrações com Alembic
   - Implementação de lógica de negócios
   - Criação de endpoints da API
3. **Testes**:
   - Testes unitários com Pytest
   - Testes de integração
   - Testes manuais via documentação interativa do Swagger
4. **Revisão**: Verificação de código com linters e formatadores
5. **Implantação**: Deploy automatizado via CI/CD

## Endpoints Disponíveis

O template inclui implementações completas para as seguintes operações:

### Heroes
- `GET /heroes` - Listar todos os heróis
- `GET /heroes/{id}` - Obter um herói específico
- `POST /heroes` - Criar um novo herói
- `PATCH /heroes/{id}` - Atualizar um herói
- `DELETE /heroes/{id}` - Deletar um herói

### Autenticação
- `POST /auth/register` - Registrar um novo usuário
- `POST /auth/login` - Login e obtenção de token de acesso
- `GET /auth/me` - Obter perfil do usuário atual

## Documentação Interativa

O FastAPI gera automaticamente documentação interativa para a API, acessível através dos seguintes endpoints:

- `/docs` - Documentação Swagger UI
- `/redoc` - Documentação ReDoc

## Considerações de Segurança

O template implementa várias práticas de segurança recomendadas:

1. **Autenticação segura**: Implementação de JWT com expiração de tokens
2. **Proteção de senhas**: Hashing seguro de senhas
3. **Validação de dados**: Validação rigorosa de entrada com Pydantic
4. **Variáveis de ambiente**: Configurações sensíveis armazenadas em variáveis de ambiente
5. **CORS configurável**: Controle de acesso de origem cruzada

## Conclusão

Este template FastAPI oferece uma base sólida para o desenvolvimento de APIs modernas, seguindo as melhores práticas de desenvolvimento e padrões da indústria. A arquitetura modular e bem estruturada facilita a manutenção e a expansão da aplicação, enquanto as ferramentas e técnicas modernas garantem alta performance e segurança.

Nos próximos documentos desta série, exploraremos em detalhes cada componente do sistema, com tutoriais práticos e exemplos concretos de implementação.

---

*[Voltar ao Índice](./index.md)*
