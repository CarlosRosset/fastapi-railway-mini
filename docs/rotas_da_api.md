# Rotas da API do Template Railway FastAPI

## Introdução

Este documento centraliza todas as rotas disponíveis na API do Template Railway FastAPI. Ele serve como referência rápida para desenvolvedores e usuários da API.

> **Nota**: A documentação interativa da API está sempre disponível em `/docs` quando o servidor está em execução.

## Índice de Rotas

- [Rotas Principais (Default)](#rotas-principais)
- [Rotas de Autenticação (Auth)](#rotas-de-autenticação)
- [Rotas de Heróis (Heroes)](#rotas-de-heróis)

## Rotas Principais

Estas são as rotas básicas da API, incluindo as **rotas críticas** que funcionam mesmo quando o banco de dados está indisponível.

| Método | Rota | Descrição | Requer Auth | Resiliente |
|--------|------|-----------|-------------|------------|
| GET | `/` | Rota raiz da API, retorna informações básicas e links | Não | ✅ |
| GET | `/health` | Verifica a saúde da API e conexão com banco de dados | Não | ✅ |

### Detalhes

#### GET /

**Descrição**: Rota raiz que fornece informações básicas sobre a API.

**Resposta de Exemplo**:
```json
{
  "message": "Bem-vindo à API do template-railway-fastapi!",
  "docs": "/docs",
  "health": "/health",
  "version": "1.0.0"
}
```

#### GET /health

**Descrição**: Verifica o status da API e a conexão com o banco de dados.

**Resposta de Exemplo (Banco Disponível)**:
```json
{
  "api_status": "ok",
  "database_status": "connected",
  "version": "1.0.0"
}
```

**Resposta de Exemplo (Banco Indisponível)**:
```json
{
  "api_status": "ok",
  "database_status": "disconnected",
  "version": "1.0.0"
}
```

## Rotas de Autenticação

Estas rotas gerenciam o registro, login e informações de usuários.

| Método | Rota | Descrição | Requer Auth | Resiliente |
|--------|------|-----------|-------------|------------|
| POST | `/auth/register` | Registra um novo usuário | Não | ✅ |
| POST | `/auth/login` | Autentica um usuário e retorna um token JWT | Não | ✅ |
| GET | `/auth/me` | Retorna os dados do usuário autenticado | Sim | ✅ |

### Detalhes

#### POST /auth/register

**Descrição**: Registra um novo usuário no sistema.

**Resiliência**: Esta rota continua funcionando mesmo quando há problemas de conexão com o banco de dados, graças ao tratamento especial implementado no middleware.

**Payload**:
```json
{
  "email": "usuario@exemplo.com",
  "password": "senha123",
  "name": "Usuário Teste"
}
```

**Resposta (201 Created)**:
```json
{
  "email": "usuario@exemplo.com",
  "name": "Usuário Teste",
  "id": 1
}
```

#### POST /auth/login

**Descrição**: Autentica um usuário e retorna um token JWT.

**Resiliência**: Esta rota continua funcionando mesmo quando há problemas de conexão com o banco de dados, graças ao tratamento especial implementado no middleware.

**Payload** (form-data):
```
username: usuario@exemplo.com
password: senha123
```

**Resposta**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET /auth/me

**Descrição**: Retorna os dados do usuário autenticado.

**Headers**:
```
Authorization: Bearer {token}
```

**Resposta**:
```json
{
  "email": "usuario@exemplo.com",
  "name": "Usuário Teste",
  "id": 1
}
```

## Rotas de Heróis

Estas rotas gerenciam o CRUD de heróis, demonstrando as operações básicas de uma API RESTful.

| Método | Rota | Descrição | Requer Auth | Resiliente |
|--------|------|-----------|-------------|------------|
| GET | `/heroes/` | Lista todos os heróis | Sim | ✅ |
| POST | `/heroes/` | Cria um novo herói | Sim | ✅ |
| GET | `/heroes/{hero_id}` | Obtém um herói específico pelo ID | Sim | ✅ |
| PATCH | `/heroes/{hero_id}` | Atualiza parcialmente um herói | Sim | ✅ |
| DELETE | `/heroes/{hero_id}` | Remove um herói | Sim | ✅ |

### Detalhes

#### GET /heroes/

**Descrição**: Lista todos os heróis cadastrados.

**Headers**:
```
Authorization: Bearer {token}
```

**Resposta**:
```json
[
  {
    "id": 1,
    "name": "Homem-Aranha",
    "secret_name": "Peter Parker",
    "age": 23,
    "owner_id": 1
  },
  {
    "id": 2,
    "name": "Mulher-Maravilha",
    "secret_name": "Diana Prince",
    "age": 1000,
    "owner_id": 1
  }
]
```

#### POST /heroes/

**Descrição**: Cria um novo herói.

**Headers**:
```
Authorization: Bearer {token}
```

**Payload**:
```json
{
  "name": "Homem-Aranha",
  "secret_name": "Peter Parker",
  "age": 23
}
```

**Resposta**:
```json
{
  "id": 1,
  "name": "Homem-Aranha",
  "secret_name": "Peter Parker",
  "age": 23,
  "owner_id": 1
}
```

#### GET /heroes/{hero_id}

**Descrição**: Obtém detalhes de um herói específico pelo ID.

**Headers**:
```
Authorization: Bearer {token}
```

**Resposta**:
```json
{
  "id": 1,
  "name": "Homem-Aranha",
  "secret_name": "Peter Parker",
  "age": 23,
  "owner_id": 1
}
```

#### PATCH /heroes/{hero_id}

**Descrição**: Atualiza parcialmente os dados de um herói.

**Headers**:
```
Authorization: Bearer {token}
```

**Payload**:
```json
{
  "age": 24
}
```

**Resposta**:
```json
{
  "id": 1,
  "name": "Homem-Aranha",
  "secret_name": "Peter Parker",
  "age": 24,
  "owner_id": 1
}
```

#### DELETE /heroes/{hero_id}

**Descrição**: Remove um herói do sistema.

**Headers**:
```
Authorization: Bearer {token}
```

**Resposta**: Código 204 (No Content) sem corpo de resposta.

## Testando as Rotas

Para testar as rotas, você pode utilizar:

1. A interface interativa em `/docs` (Swagger UI)
2. Ferramentas como Postman ou Insomnia
3. Comandos curl no terminal

### Exemplos de Curl

#### Testar Rota Raiz
```bash
curl -s http://127.0.0.1:8000/ | jq
```

#### Testar Health Check
```bash
curl -s http://127.0.0.1:8000/health | jq
```

#### Registrar Usuário
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com",
    "password": "senha123",
    "name": "Usuário Teste"
  }'
```

#### Login
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=usuario@exemplo.com&password=senha123"
```

## Resiliência da API

**Atualização**: Todas as rotas da API agora funcionam com o mesmo nível de resiliência. O middleware foi aprimorado para tratar exceções de banco de dados apenas quando elas realmente ocorrem durante o processamento da requisição, em vez de bloquear previamente certas rotas.

As rotas marcadas como resilientes (✅) continuarão funcionando mesmo quando ocorrerem problemas temporários com o banco de dados. O sistema fará o melhor esforço para processar todas as requisições e só retornará mensagens de erro quando realmente não conseguir completar a operação solicitada.

Para mais detalhes sobre a resiliência da API, consulte a [documentação de resiliência](resiliencia_api.md).
