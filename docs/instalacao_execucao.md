# Instalação e Execução do Template FastAPI

Este guia fornece instruções detalhadas sobre como verificar pré-requisitos, instalar dependências e executar o template FastAPI em seu ambiente local. Seguindo estas etapas, você garantirá que o ambiente esteja corretamente configurado e que a aplicação funcione conforme o esperado.

> ⚠️ **IMPORTANTE: SEMPRE USE O AMBIENTE VIRTUAL**
> 
> Este template utiliza o UV para gerenciar o ambiente virtual Python. **TODOS os comandos Python** (exceto a verificação inicial de versão) devem ser executados dentro do ambiente virtual ativado.
> 
> ❌ **NUNCA** execute instalações com `pip install` ou comandos Python diretamente no sistema
> ✅ **SEMPRE** ative o ambiente virtual e use `uv run`, `uv pip` ou equivalentes

## Sumário

1. [Verificação de Pré-requisitos](#verificação-de-pré-requisitos)
2. [Instalação do UV](#instalação-do-uv)
3. [Configuração do Ambiente Virtual](#configuração-do-ambiente-virtual)
4. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
5. [Execução da Aplicação](#execução-da-aplicação)
6. [Verificação de Funcionamento](#verificação-de-funcionamento)
7. [Solução de Problemas Comuns](#solução-de-problemas-comuns)

## Verificação de Pré-requisitos

Antes de começar, verifique se o seu sistema atende aos seguintes requisitos:

### Python

O template requer Python 3.8 ou superior. Verifique sua versão do Python com:

```bash
python --version
# ou
python3 --version
```

Se você não tiver Python instalado ou se sua versão for anterior à 3.8, visite [python.org](https://www.python.org/downloads/) para baixar e instalar a versão mais recente.

> 📝 **Nota importante**: O Python do sistema é usado **APENAS** para verificar a versão inicial e instalar o UV. Uma vez que o ambiente virtual estiver configurado, **todo código Python será executado dentro deste ambiente isolado**, não no Python do sistema. Isso garante consistência e evita conflitos de dependências.

### PostgreSQL

O template usa PostgreSQL como banco de dados. Verifique se o PostgreSQL está instalado e em execução:

```bash
# Para verificar se o PostgreSQL está instalado
psql --version

# Para verificar se o serviço está em execução
# Para sistemas baseados em systemd (como Ubuntu recentes)
systemctl status postgresql

# Para outros sistemas
pg_isready
```

Se o PostgreSQL não estiver instalado, siga as instruções oficiais para seu sistema operacional:
- [PostgreSQL Downloads](https://www.postgresql.org/download/)

## Instalação do UV

O template utiliza UV para gerenciar dependências e ambientes virtuais. Vamos verificar se o UV está instalado e, se necessário, instalá-lo:

### Verificar instalação do UV

```bash
uv --version
```

### Instalar UV (caso não esteja instalado)

#### Para Linux/macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Para Windows (PowerShell):

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Após a instalação, feche e reabra o terminal para que as alterações no PATH entrem em vigor. Verifique novamente com `uv --version` para confirmar que a instalação foi bem-sucedida.

## Configuração do Ambiente Virtual

Agora vamos configurar o ambiente virtual e instalar as dependências do projeto:

### 1. Clone o repositório (se ainda não tiver feito)

```bash
git clone [URL_DO_REPOSITORIO]
cd [NOME_DO_DIRETORIO]
```

### 2. Criar ambiente virtual

```bash
uv venv
```

Isso criará um diretório `.venv` na pasta do projeto.

### 3. Ativar o ambiente virtual

#### Para Linux/macOS:

```bash
source .venv/bin/activate
```

#### Para Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

#### Para Windows (CMD):

```cmd
.venv\Scripts\activate.bat
```

Quando o ambiente virtual estiver ativado, você verá o nome do ambiente (geralmente `.venv`) no início do prompt de comando.

### 4. Instalar dependências

Há duas opções para instalar as dependências:

#### Opção 1: Usando o comando sync (recomendado)

```bash
uv sync
```

#### Opção 2: Instalando manualmente

```bash
# Para instalar apenas dependências de produção
uv pip install -e .

# Para instalar dependências de produção e desenvolvimento
uv pip install -e ".[dev]"
```

### 5. Verificar instalação das dependências

Você pode listar as dependências instaladas para verificar se tudo foi instalado corretamente:

```bash
uv pip list
```

Você deve ver um resultado que inclui pacotes como `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, etc.

> ⚠️ **Lembrete importante**: NUNCA instale pacotes diretamente com `pip install` no ambiente do sistema. Sempre use o ambiente virtual com `uv pip install` ou, preferencialmente, adicione as dependências ao arquivo `pyproject.toml` e execute `uv sync`. Veja mais detalhes no documento [Gerenciamento de Dependências](./gerenciamento_dependencias.md).

## Configuração do Banco de Dados

Antes de executar a aplicação, é necessário configurar as variáveis de ambiente para conectar ao banco de dados:

### 1. Criar arquivo de ambiente

Copie o arquivo de exemplo `.env.example` para criar seu próprio arquivo `.env`:

```bash
cp .env.example .env
```

### 2. Editar o arquivo .env

Abra o arquivo `.env` em seu editor preferido e atualize as configurações, especialmente:

```
DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/nome_do_banco
JWT_SECRET=sua_chave_secreta_aqui
```

Substitua `usuario`, `senha` e `nome_do_banco` pelos valores adequados para sua configuração do PostgreSQL.

### 3. Criar o banco de dados

Acesse o PostgreSQL e crie o banco de dados especificado na URL:

```bash
# Acessar o cliente PostgreSQL
psql -U postgres

# Dentro do psql, crie o banco de dados
CREATE DATABASE nome_do_banco;

# Saia do psql
\q
```

## Execução da Aplicação

Agora que o ambiente está configurado, vamos executar a aplicação:

### 1. Aplicar migrações do banco de dados

As migrações serão aplicadas automaticamente ao iniciar a aplicação, mas você pode aplicá-las manualmente com:

```bash
uv run alembic upgrade head
```

### 2. Iniciar o servidor de desenvolvimento

```bash
# Certifique-se de que o ambiente virtual está ativado
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate.bat  # Windows

# Execute o servidor usando uv
uv run uvicorn api.main:app --reload
```

> 💡 **Dica**: Note que usamos `uv run` para executar o comando, garantindo que ele use o Python e as dependências do ambiente virtual, não do sistema.

Se tudo estiver configurado corretamente, você verá uma saída similar a:

```
INFO:     Will watch for changes in these directories: ['/caminho/para/seu/projeto']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Verificação de Funcionamento

Vamos verificar se a aplicação está funcionando corretamente:

### 1. Acessar a documentação da API

Abra um navegador e acesse:

```
http://127.0.0.1:8000/docs
```

Você deverá ver a interface interativa Swagger da documentação da API.

### 2. Testar um endpoint público

Vamos testar o endpoint de status da API usando curl ou diretamente no navegador:

```bash
curl http://127.0.0.1:8000/api/v1/status
```

Ou acesse `http://127.0.0.1:8000/api/v1/status` no navegador.

Você deve receber uma resposta JSON indicando que a API está funcionando.

### 3. Testar autenticação (se aplicável)

Para testar a autenticação, primeiro crie um usuário:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "username": "usuarioteste",
    "password": "Senha123!"
  }'
```

Em seguida, faça login para obter um token:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=teste@exemplo.com&password=Senha123!"
```

### 4. Script de verificação completa

Para uma verificação completa do ambiente, você pode criar um script personalizado. Aqui está um exemplo que pode ser salvo como `verify_setup.sh`:

```bash
#!/bin/bash

# Cores para saída
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Verificando configuração do ambiente...${NC}"

# Verificar Python
python_version=$(python3 --version 2>&1)
if [[ $python_version == *"Python 3"* ]]; then
    echo -e "${GREEN}✓ Python instalado: $python_version${NC}"
else
    echo -e "${RED}✗ Python 3 não detectado. Por favor, instale Python 3.8 ou superior.${NC}"
    exit 1
fi

# Verificar UV
if command -v uv &> /dev/null; then
    uv_version=$(uv --version)
    echo -e "${GREEN}✓ UV instalado: $uv_version${NC}"
else
    echo -e "${RED}✗ UV não encontrado. Por favor, instale o UV.${NC}"
    echo -e "${YELLOW}curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

# Verificar ambiente virtual
if [[ -d ".venv" ]]; then
    echo -e "${GREEN}✓ Ambiente virtual encontrado${NC}"
else
    echo -e "${YELLOW}! Ambiente virtual não encontrado. Criando...${NC}"
    uv venv
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}✗ Falha ao criar o ambiente virtual${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Ambiente virtual criado${NC}"
fi

# Ativar ambiente virtual
source .venv/bin/activate
if [[ $? -ne 0 ]]; then
    echo -e "${RED}✗ Falha ao ativar o ambiente virtual${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Ambiente virtual ativado${NC}"

# Verificar dependências
echo -e "${YELLOW}Verificando dependências principais...${NC}"
for pkg in fastapi uvicorn sqlalchemy alembic pydantic; do
    if uv pip list | grep -q $pkg; then
        echo -e "${GREEN}✓ $pkg instalado${NC}"
    else
        echo -e "${YELLOW}! $pkg não encontrado. Instalando dependências...${NC}"
        uv sync
        if [[ $? -ne 0 ]]; then
            echo -e "${RED}✗ Falha ao instalar dependências${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Dependências instaladas${NC}"
        break
    fi
done

# Verificar arquivo .env
if [[ -f ".env" ]]; then
    echo -e "${GREEN}✓ Arquivo .env encontrado${NC}"
else
    echo -e "${YELLOW}! Arquivo .env não encontrado. Copiando de .env.example...${NC}"
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Arquivo .env criado. Por favor, edite-o com suas configurações.${NC}"
    else
        echo -e "${RED}✗ Arquivo .env.example não encontrado.${NC}"
        echo -e "${YELLOW}Crie manualmente um arquivo .env com as configurações necessárias.${NC}"
    fi
fi

echo -e "\n${GREEN}=== Verificação de ambiente concluída ===${NC}"
echo -e "${YELLOW}Para iniciar a aplicação, execute:${NC}"
echo -e "uv run uvicorn api.main:app --reload"
```

Torne o script executável e execute-o:

```bash
chmod +x verify_setup.sh
./verify_setup.sh
```

## Solução de Problemas Comuns

### Problema: Erro ao criar o ambiente virtual

**Sintoma:** Mensagem de erro ao executar `uv venv`.

**Solução:**
1. Verifique se você tem permissões de escrita no diretório.
2. Certifique-se de que o Python está instalado corretamente.
3. Tente remover qualquer diretório `.venv` existente: `rm -rf .venv`.

### Problema: Erro de conexão com o banco de dados

**Sintoma:** Erro como "could not connect to server: Connection refused"

**Solução:**
1. Verifique se o PostgreSQL está em execução: `systemctl status postgresql`.
2. Confirme se as credenciais no arquivo `.env` estão corretas.
3. Verifique se o banco de dados especificado existe: `psql -U postgres -c '\l'`.
4. Verifique se o usuário tem permissões para acessar o banco: `psql -U postgres -c '\du'`.

### Problema: ImportError ao iniciar a aplicação

**Sintoma:** Erro de importação quando você tenta iniciar a aplicação.

**Solução:**
1. Verifique se todas as dependências estão instaladas: `uv pip list`.
2. Reinstale as dependências: `uv sync`.
3. Certifique-se de que está executando o comando dentro do ambiente virtual ativado.

### Problema: Erro nas migrações

**Sintoma:** Erro ao aplicar migrações Alembic.

**Solução:**
1. Verifique se o banco de dados está criado e acessível.
2. Execute as migrações manualmente: `uv run alembic upgrade head`.
3. Se necessário, recrie as migrações: `rm -rf alembic/versions/* && uv run alembic revision --autogenerate -m "initial"`.

### Problema: UV não está disponível após instalação

**Sintoma:** Comando `uv` não é reconhecido após a instalação.

**Solução:**
1. Feche e reabra o terminal para recarregar o PATH.
2. Verifique se o diretório de instalação está no PATH: `echo $PATH`.
3. Adicione manualmente ao PATH se necessário.

## Conclusão

Se você seguiu todas as etapas acima e verificou que a aplicação está funcionando corretamente, parabéns! Você configurou com sucesso o ambiente de desenvolvimento para o template FastAPI. 

Agora você pode começar a desenvolver sua aplicação, adicionando novos recursos e adaptando o template às suas necessidades específicas.

Para informações mais detalhadas sobre o UV, consulte o documento [UV Workflow](./uv_workflow.md). Para entender a arquitetura do projeto, visite a [Visão Geral do Projeto](./visao_geral.md).

---

*[Voltar ao Índice](./index.md)*
