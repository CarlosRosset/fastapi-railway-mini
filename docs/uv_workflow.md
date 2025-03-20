# UV Workflow: Gerenciamento Moderno de Ambientes Python

## Introdução ao UV

UV é uma ferramenta de gerenciamento de pacotes Python ultrarrápida, escrita em Rust, que oferece uma alternativa mais eficiente e moderna ao pip tradicional e gerenciadores de ambientes virtuais. No contexto do nosso template FastAPI, o UV desempenha um papel crucial na gestão de dependências e ambientes de desenvolvimento.

## Por que UV?

O UV apresenta várias vantagens significativas sobre ferramentas tradicionais:

1. **Velocidade superior**: Instalação de pacotes até 10-100x mais rápida que pip+venv
2. **Resolução de dependências determinística**: Garantia de ambientes consistentes entre diferentes máquinas
3. **Gerenciamento unificado**: Combinação de funcionalidades de pip, virtualenv e pip-tools em uma única ferramenta
4. **Melhor tratamento de conflitos**: Detecção e resolução de conflitos de dependências aprimorada
5. **Integração com pyproject.toml**: Suporte nativo para o formato moderno de definição de projetos Python

## Instalação do UV

Antes de utilizar nosso template, é necessário instalar o UV globalmente:

### Linux/macOS
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
# PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```

Verifique a instalação com:
```bash
uv --version
```

## Configuração do Ambiente no Template

O template FastAPI é configurado para utilizar o UV como principal ferramenta de gerenciamento de pacotes e ambientes. Os arquivos essenciais para esta configuração são:

1. **pyproject.toml**: Define as dependências do projeto e configurações de ferramentas
2. **start.sh**: Script de inicialização que configura o ambiente automaticamente

### O arquivo pyproject.toml

O arquivo `pyproject.toml` substitui os tradicionais `requirements.txt` e `setup.py`, oferecendo uma abordagem mais moderna e abrangente para a definição de projetos Python:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "hero-api"
version = "0.1.0"
description = "A modern, production-ready FastAPI template"
requires-python = ">=3.8"
dependencies = [
    "fastapi>=0.103.1",
    "uvicorn>=0.23.2",
    "sqlalchemy>=2.0.20",
    "alembic>=1.12.0",
    "asyncpg>=0.28.0",
    "pydantic>=2.3.0",
    "pydantic-settings>=2.0.3",
    "python-jose>=3.3.0",
    "passlib>=1.7.4",
    "python-multipart>=0.0.6",
    "bcrypt>=4.0.1",
]

[project.optional-dependencies]
dev = [
    "black>=23.7.0",
    "isort>=5.12.0",
    "pytest>=7.4.1",
    "pytest-asyncio>=0.21.1",
    "httpx>=0.24.1",
    "pre-commit>=3.3.3",
]

[tool.black]
line-length = 88
target-version = ["py38", "py39", "py310", "py311"]

[tool.isort]
profile = "black"
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
asyncio_mode = "auto"
```

### Principais Seções do pyproject.toml

1. **[build-system]**: Especifica o sistema de build utilizado para pacotes Python
2. **[project]**: Metadados do projeto e dependências principais
   - `name`: Nome do pacote
   - `version`: Versão atual
   - `description`: Breve descrição
   - `requires-python`: Versão mínima do Python necessária
   - `dependencies`: Lista de dependências principais com versões mínimas
3. **[project.optional-dependencies]**: Dependências opcionais organizadas por grupos
   - `dev`: Ferramentas de desenvolvimento e teste
4. **[tool.*]**: Configurações específicas para ferramentas como black, isort e pytest

## Comandos UV Essenciais

### Criação e Ativação de Ambiente Virtual

```bash
# Criar um ambiente virtual na pasta .venv
uv venv

# Ativar o ambiente virtual (Linux/macOS)
source .venv/bin/activate

# Ativar o ambiente virtual (Windows PowerShell)
.venv\Scripts\Activate.ps1
```

### Instalação de Dependências

```bash
# Instalar todas as dependências do projeto
uv pip install -e .

# Instalar com dependências de desenvolvimento
uv pip install -e ".[dev]"

# Alternativa rápida para instalar todas as dependências
uv sync
```

### Adição de Novas Dependências

Para adicionar uma nova dependência ao projeto:

1. Adicione a dependência ao arquivo `pyproject.toml` na seção apropriada
2. Execute `uv sync` para atualizar o ambiente

### Execução de Comandos Python no Ambiente Virtual

```bash
# Executar um script ou módulo Python
uv run python script.py

# Executar o servidor uvicorn
uv run uvicorn api.main:app --reload
```

## Script de Inicialização (start.sh)

O template inclui um script `start.sh` que automatiza a configuração do ambiente:

```bash
#!/bin/bash

# Cores para saída no terminal
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se o UV está instalado
if ! command -v uv &> /dev/null
then
    echo -e "${RED}UV não está instalado!${NC}"
    echo -e "Por favor, instale o UV primeiro:"
    echo -e "${YELLOW}curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

echo -e "${GREEN}Configurando ambiente virtual...${NC}"

# Criar ambiente virtual se não existir
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual...${NC}"
    uv venv
fi

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar se ativação foi bem-sucedida
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao ativar o ambiente virtual!${NC}"
    exit 1
fi

# Instalar dependências
echo -e "${YELLOW}Instalando dependências...${NC}"
uv pip install -e ".[dev]"

# Verificar se instalação foi bem-sucedida
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao instalar dependências!${NC}"
    exit 1
fi

echo -e "${GREEN}Ambiente configurado com sucesso!${NC}"
echo -e "${YELLOW}Iniciando servidor FastAPI...${NC}"

# Iniciar o servidor FastAPI
uv run uvicorn api.main:app --reload
```

## UV vs. Ferramentas Tradicionais

| Funcionalidade | UV | Pip + Virtualenv | Poetry |
|----------------|----|--------------------|--------|
| Velocidade de instalação | Muito rápida (paralelizada) | Lenta | Média |
| Resolução de dependências | Determinística | Básica | Determinística |
| Lock files | Suporte integrado | Requer pip-tools | Suporte integrado |
| Formato de configuração | pyproject.toml | requirements.txt | pyproject.toml |
| Gerenciamento de ambiente virtual | Integrado | Separado | Integrado |
| Reprodutibilidade | Excelente | Limitada | Boa |
| Velocidade de resolução | Muito rápida | Lenta | Média |

## Integração com IDEs

### VSCode

O template FastAPI já inclui configurações otimizadas para o VSCode no diretório `.vscode`. Para utilizar o ambiente virtual UV com VSCode:

1. Abra o projeto no VSCode
2. O arquivo `.vscode/settings.json` já está configurado para detectar automaticamente o ambiente virtual `.venv`
3. Para executar/depurar, utilize as configurações predefinidas em `.vscode/launch.json`

### PyCharm

Para configurar o ambiente UV no PyCharm:

1. Vá para File > Settings > Project > Python Interpreter
2. Clique na engrenagem e selecione "Add..."
3. Escolha "Existing Environment" e navegue até `.venv/bin/python` (Linux/macOS) ou `.venv\Scripts\python.exe` (Windows)
4. Aplique as configurações

## Boas Práticas com UV

1. **Sempre utilize o arquivo pyproject.toml**: Mantenha todas as dependências centralizadas
2. **Específique versões mínimas**: Use `package>=version` para garantir compatibilidade
3. **Agrupe dependências por função**: Utilize opcional-dependencies para organizar pacotes
4. **Mantenha o ambiente isolado**: Instale pacotes globalmente apenas quando absolutamente necessário
5. **Use o comando sync regularmente**: Após alterações no pyproject.toml, execute `uv sync` para atualizar o ambiente
6. **Atualize dependências com cautela**: Teste cuidadosamente após atualizações

## Resolução de Problemas Comuns

### Conflitos de Dependências

Se ocorrerem conflitos de dependências, o UV geralmente fornecerá mensagens de erro detalhadas. Para resolver:

1. Verifique as versões específicas que estão em conflito
2. Ajuste as restrições de versão no pyproject.toml
3. Execute `uv sync` novamente

### Problemas de Ativação do Ambiente Virtual

Se houver problemas para ativar o ambiente virtual:

1. Verifique se o ambiente foi criado corretamente (`ls -la .venv`)
2. Recrie o ambiente virtual: `rm -rf .venv && uv venv`
3. Tente ativar novamente: `source .venv/bin/activate`

### Pacotes que Não São Instalados Corretamente

Para problemas com a instalação de pacotes específicos:

1. Tente instalar o pacote explicitamente: `uv pip install nome-do-pacote`
2. Verifique se há dependências de sistema necessárias (bibliotecas C, etc.)
3. Verifique conflitos potenciais com outros pacotes instalados

## Considerações para Produção

Quando estiver pronto para implantar em produção:

1. **Congele versões específicas**: Para ambientes de produção, use versões exatas em vez de faixas (`==` em vez de `>=`)
2. **Crie um ambiente limpo**: Inicie com um ambiente virtual novo para produção
3. **Documente os requisitos do sistema**: Liste quaisquer dependências do sistema operacional necessárias
4. **Considere containers**: Docker com UV pode fornecer ambientes ainda mais consistentes

## Conclusão

O uso do UV no template FastAPI representa um passo significativo para modernizar o fluxo de trabalho de desenvolvimento Python, proporcionando instalações mais rápidas, ambientes mais confiáveis e uma experiência de desenvolvimento mais fluida. 

A combinação de UV com o formato pyproject.toml coloca este template na vanguarda das práticas modernas de desenvolvimento Python, garantindo que você possa se concentrar na construção de recursos em vez de lidar com problemas de gerenciamento de dependências.

---

*[Voltar ao Índice](./index.md)*
