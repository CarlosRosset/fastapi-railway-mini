# Guia Prático de Testes Manuais para API FastAPI

Este guia fornece instruções detalhadas para testar manualmente a API do Template Railway FastAPI usando curl. Ele aborda os formatos corretos para solicitações, problemas comuns e soluções para ajudar iniciantes a validar o funcionamento da API tanto localmente quanto em produção.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Verificação do Status da API](#verificação-do-status-da-api)
3. [Autenticação](#autenticação)
   - [Registro de Usuário](#registro-de-usuário)
   - [Login](#login)
   - [Verificação de Usuário Autenticado](#verificação-de-usuário-autenticado)
4. [Operações com Heróis (CRUD)](#operações-com-heróis-crud)
   - [Listar Heróis](#listar-heróis)
   - [Criar Herói](#criar-herói)
   - [Buscar Herói Específico](#buscar-herói-específico)
   - [Atualizar Herói](#atualizar-herói)
   - [Excluir Herói](#excluir-herói)
5. [Erros Comuns e Soluções](#erros-comuns-e-soluções)
6. [Fluxo Completo de Testes](#fluxo-completo-de-testes)

## Pré-requisitos

- curl instalado no sistema
- jq (opcional, mas recomendado para formatação de saída JSON)
- Um servidor FastAPI em execução (local ou no Railway)

### Instalação de Ferramentas

```bash
# Ubuntu/Debian
sudo apt install curl jq

# Fedora/RHEL
sudo dnf install curl jq

# macOS (com Homebrew)
brew install curl jq
```

## Verificação do Status da API

Antes de iniciar os testes das rotas principais, é importante verificar se a API está funcionando corretamente.

### 1. Verificar endpoint raiz

```bash
curl -s http://localhost:8000/ | jq
# ou para produção
curl -s https://sua-api-railway.up.railway.app/ | jq
```

Resposta esperada:
```json
{
  "message": "Bem-vindo à API do template-railway-fastapi!",
  "docs": "/docs",
  "health": "/health",
  "version": "1.0.0"
}
```

### 2. Verificar a saúde da API

```bash
curl -s http://localhost:8000/health | jq
# ou para produção
curl -s https://sua-api-railway.up.railway.app/health | jq
```

Resposta esperada:
```json
{
  "api_status": "ok",
  "database_status": "connected",
  "version": "1.0.0"
}
```

> 💡 **Dica**: Se o status do banco de dados não for "connected", verifique se as variáveis de ambiente para o banco de dados estão configuradas corretamente.

## Autenticação

### Registro de Usuário

Para criar um novo usuário:

```bash
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "password": "senha123",
    "name": "Usuario Teste"
  }' | jq
```

Resposta esperada:
```json
{
  "email": "teste@exemplo.com",
  "id": 1
}
```

> ⚠️ **Atenção**: Certifique-se de usar um email que ainda não esteja cadastrado no sistema.

### Login

O login pode ser feito de duas formas:

#### 1. Usando application/x-www-form-urlencoded (recomendado)

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=teste@exemplo.com&password=senha123" | jq
```

#### 2. Usando application/json

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"teste@exemplo.com", "password":"senha123"}' | jq
```

> ⚠️ **Problema comum**: Ao usar JSON para login, os campos devem ser exatamente `username` (não `email`) e `password`.

Resposta esperada:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Verificação de Usuário Autenticado

Após o login, armazene o token em uma variável para uso em solicitações subsequentes:

```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -s http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq
```

Resposta esperada:
```json
{
  "email": "teste@exemplo.com",
  "id": 1
}
```

## Operações com Heróis (CRUD)

Todas as operações a seguir exigem autenticação.

### Listar Heróis

```bash
curl -s http://localhost:8000/heroes/ \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Criar Herói

```bash
curl -s -X POST http://localhost:8000/heroes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bruce Wayne",
    "alias": "Batman",
    "powers": "Inteligência, Artes Marciais, Rico"
  }' | jq
```

> ⚠️ **Problema comum**: O campo `powers` deve ser uma string, não uma lista. Por exemplo, use `"powers": "Força, Velocidade"` em vez de `"powers": ["Força", "Velocidade"]`.

Resposta esperada:
```json
{
  "name": "Bruce Wayne",
  "alias": "Batman",
  "powers": "Inteligência, Artes Marciais, Rico",
  "id": 1
}
```

### Buscar Herói Específico

```bash
curl -s http://localhost:8000/heroes/1 \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Atualizar Herói

```bash
curl -s -X PATCH http://localhost:8000/heroes/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "powers": "Inteligência, Artes Marciais, Rico, Tecnologia avançada"
  }' | jq
```

### Excluir Herói

```bash
curl -s -X DELETE http://localhost:8000/heroes/1 \
  -H "Authorization: Bearer $TOKEN" | jq
```

## Erros Comuns e Soluções

### 1. Erro: "Not Found" ao acessar rotas

**Problema**: A URL está incorreta ou a rota não existe.

**Solução**: Verifique a documentação OpenAPI em `/docs` para confirmar os endpoints disponíveis:

```bash
curl -s http://localhost:8000/openapi.json | jq '.paths | keys'
```

### 2. Erro: "Field required" durante o login

**Problema**: Formato incorreto no corpo da solicitação.

**Solução**: Certifique-se de usar exatamente os campos `username` e `password`. Para formulários URL-encoded, use `-d "username=email@exemplo.com&password=senha123"`.

### 3. Erro: "Input should be a valid string" ao criar um herói

**Problema**: O campo `powers` está sendo enviado como uma lista em vez de string.

**Solução**: Use uma string separada por vírgulas: `"powers": "Força, Velocidade"` em vez de um array.

### 4. Erro: "Unauthorized" ou "Not authenticated"

**Problema**: Token ausente ou inválido.

**Solução**:
1. Verifique se você está incluindo o cabeçalho `Authorization: Bearer {token}`
2. Confirme que o token não expirou (padrão é 30 minutos)
3. Obtenha um novo token fazendo login novamente

## Fluxo Completo de Testes

Aqui está um script bash que executa um fluxo completo de testes da API:

```bash
#!/bin/bash
# Substitua pela URL da sua API
API_URL="http://localhost:8000"
# API_URL="https://sua-api-railway.up.railway.app"

# 1. Verificar status da API
echo "Verificando status da API..."
curl -s $API_URL/health | jq

# 2. Registrar um usuário
echo -e "\nRegistrando usuário..."
curl -s -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "password": "senha123",
    "name": "Usuario Teste"
  }' | jq

# 3. Fazer login
echo -e "\nFazendo login..."
TOKEN=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=teste@exemplo.com&password=senha123" | jq -r '.access_token')

echo "Token obtido: ${TOKEN:0:15}..."

# 4. Verificar usuário autenticado
echo -e "\nVerificando usuário autenticado..."
curl -s $API_URL/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq

# 5. Criar um herói
echo -e "\nCriando um herói..."
HERO_ID=$(curl -s -X POST $API_URL/heroes/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Clark Kent",
    "alias": "Superman",
    "powers": "Voo, Super força, Visão de raio-x"
  }' | jq -r '.id')

echo "Herói criado com ID: $HERO_ID"

# 6. Listar heróis
echo -e "\nListando heróis..."
curl -s $API_URL/heroes/ \
  -H "Authorization: Bearer $TOKEN" | jq

# 7. Buscar herói por ID
echo -e "\nBuscando herói $HERO_ID..."
curl -s $API_URL/heroes/$HERO_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# 8. Atualizar herói
echo -e "\nAtualizando herói $HERO_ID..."
curl -s -X PATCH $API_URL/heroes/$HERO_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "powers": "Voo, Super força, Visão de raio-x, Sopro congelante"
  }' | jq

# 9. Excluir herói (opcional, comentado por padrão)
# echo -e "\nExcluindo herói $HERO_ID..."
# curl -s -X DELETE $API_URL/heroes/$HERO_ID \
#   -H "Authorization: Bearer $TOKEN" | jq

echo -e "\nTestes concluídos!"
```

Salve este script como `test_api.sh` e execute-o com `bash test_api.sh`.

## Referências

- [Documentação completa da API](/docs/rotas_da_api.md)
- [Testes automatizados](/docs/testes.md)
- [Deploy no Railway](/docs/deploy_railway.md)
