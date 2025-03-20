# Gerenciamento de Dependências com UV e pyproject.toml

Este guia detalha como gerenciar corretamente as dependências Python no template FastAPI, garantindo que todas as instalações sejam feitas dentro do ambiente virtual e não afetem o sistema global.

## Sumário

1. [Conceitos Fundamentais](#conceitos-fundamentais)
2. [Como NÃO Instalar Pacotes](#como-não-instalar-pacotes)
3. [Adicionando Novas Dependências](#adicionando-novas-dependências)
   - [Dependências de Produção](#dependências-de-produção)
   - [Dependências de Desenvolvimento](#dependências-de-desenvolvimento)
4. [Atualizando Dependências](#atualizando-dependências)
5. [Verificando Dependências Instaladas](#verificando-dependências-instaladas)
6. [Exemplos Práticos](#exemplos-práticos)
7. [Solução de Problemas](#solução-de-problemas)

## Conceitos Fundamentais

### O Sistema de Gestão de Dependências

Este template utiliza duas ferramentas modernas para gerenciamento de dependências:

1. **UV** - Um instalador rápido de pacotes Python escrito em Rust
2. **pyproject.toml** - Um formato padronizado para definir metadados e dependências de projetos Python (PEP 621)

Esta combinação oferece várias vantagens:
- Instalações mais rápidas
- Dependências organizadas e centralizadas
- Determinismo nas instalações
- Facilidade para compartilhar ambientes entre desenvolvedores

### Estrutura do Ambiente Virtual

Quando você cria um ambiente virtual com UV, ele cria um diretório `.venv` na raiz do projeto que contém:

- Uma instalação isolada do Python
- Um diretório separado para pacotes instalados
- Scripts de ativação para diferentes shells

Este isolamento garante que os pacotes instalados não afetem o sistema global.

## Como NÃO Instalar Pacotes

> ⚠️ **IMPORTANTE**
> 
> **NUNCA** execute os seguintes comandos para instalar pacotes:
> 
> ❌ `pip install pacote`  
> ❌ `python -m pip install pacote`  
> 
> Esses comandos podem instalar pacotes globalmente ou no ambiente errado!

## Adicionando Novas Dependências

O fluxo correto para adicionar uma nova dependência ao projeto é:

### Dependências de Produção

1. **Edite o arquivo pyproject.toml** na seção `[project]` → `dependencies`:

```toml
[project]
# ... outras configurações ...
dependencies = [
    "fastapi>=0.103.1",
    "uvicorn>=0.23.2",
    # Adicione sua nova dependência aqui
    "novo-pacote>=1.0.0",
]
```

2. **Sincronize o ambiente virtual**:

```bash
# Certifique-se de que o ambiente virtual está ativado
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Sincronize as dependências
uv sync
```

### Dependências de Desenvolvimento

Para pacotes que são utilizados apenas durante o desenvolvimento (linters, ferramentas de teste, etc.):

1. **Edite o arquivo pyproject.toml** na seção `[project.optional-dependencies]` → `dev`:

```toml
[project.optional-dependencies]
dev = [
    "black>=23.7.0",
    "isort>=5.12.0",
    # Adicione sua nova dependência de desenvolvimento aqui
    "ferramenta-dev>=2.0.0",
]
```

2. **Sincronize o ambiente virtual com dependências de desenvolvimento**:

```bash
# Certifique-se de que o ambiente virtual está ativado
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Sincronize todas as dependências, incluindo as de desenvolvimento
uv pip install -e ".[dev]"

# Alternativamente, você pode usar
uv sync
```

## Atualizando Dependências

Para atualizar uma dependência existente:

1. **Edite o arquivo pyproject.toml** e atualize a versão da dependência desejada
2. **Sincronize o ambiente virtual**:

```bash
uv sync
```

## Verificando Dependências Instaladas

Para verificar quais pacotes estão instalados no ambiente virtual:

```bash
# Certifique-se de que o ambiente virtual está ativado
source .venv/bin/activate  # Linux/macOS

# Liste todos os pacotes instalados
uv pip list
```

Para verificar se uma dependência específica está instalada:

```bash
uv pip list | grep nome-do-pacote
```

## Exemplos Práticos

### Exemplo 1: Adicionar o pacote Pandas

Vamos adicionar o pacote `pandas` como uma dependência de produção:

1. Edite o arquivo `pyproject.toml`:

```toml
[project]
# ... outras configurações ...
dependencies = [
    "fastapi>=0.103.1",
    "uvicorn>=0.23.2",
    # ... outras dependências ...
    "pandas>=2.0.0",  # Adicione esta linha
]
```

2. Sincronize o ambiente:

```bash
uv sync
```

3. Verifique se o pandas foi instalado:

```bash
uv pip list | grep pandas
```

### Exemplo 2: Adicionar uma ferramenta de teste

Vamos adicionar o `pytest-cov` para análise de cobertura de testes:

1. Edite o arquivo `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "black>=23.7.0",
    "isort>=5.12.0",
    "pytest>=7.4.1",
    "pytest-asyncio>=0.21.1",
    "pytest-cov>=4.1.0",  # Adicione esta linha
]
```

2. Instale as dependências de desenvolvimento:

```bash
uv pip install -e ".[dev]"
# ou
uv sync
```

## Solução de Problemas

### Problema: "Pacote instalado, mas não encontrado ao executar o código"

**Causa possível**: O pacote pode ter sido instalado fora do ambiente virtual.

**Solução**:
1. Verifique se o ambiente virtual está ativado
2. Verifique se o pacote está listado em `pyproject.toml`
3. Execute `uv sync` para garantir que ele seja instalado no ambiente virtual

### Problema: "Conflito de dependências ao instalar um novo pacote"

**Causa possível**: O novo pacote tem requisitos incompatíveis com os pacotes já instalados.

**Solução**:
1. Verifique a compatibilidade de versões
2. Ajuste as versões em `pyproject.toml` para resolver conflitos
3. Se necessário, considere usar grupos de dependências separados

### Problema: "Ambiente virtual não ativado automaticamente no VS Code"

**Causa possível**: Configuração incorreta do VS Code.

**Solução**:
1. Verifique se o arquivo `.vscode/settings.json` contém:
   ```json
   {
     "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
   }
   ```
2. Reinicie o VS Code

## Integração com CI/CD

Em ambientes de CI/CD, você também deve usar UV para garantir instalações consistentes:

```yaml
# Exemplo para GitHub Actions
steps:
  - name: Setup Python
    uses: actions/setup-python@v4
    with:
      python-version: '3.10'
  
  - name: Install UV
    run: curl -LsSf https://astral.sh/uv/install.sh | sh
  
  - name: Install dependencies
    run: |
      uv venv
      source .venv/bin/activate
      uv sync
```

## Conclusão

Seguindo estas práticas, você garantirá que:

1. Todas as dependências sejam instaladas de forma isolada no ambiente virtual
2. O processo de instalação seja reproduzível em qualquer ambiente
3. Não haja contaminação do sistema global
4. As atualizações possam ser feitas de forma controlada e rastreável

O gerenciamento correto de dependências é fundamental para criar projetos Python robustos e compartilháveis, evitando problemas comuns como "funciona na minha máquina".

---

*[Voltar ao Índice](./index.md)*
