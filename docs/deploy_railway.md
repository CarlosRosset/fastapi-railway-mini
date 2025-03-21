# Deploy no Railway

## Introdução

Este guia explica como implantar o Template Railway FastAPI na plataforma Railway, garantindo uma configuração correta para o ambiente de produção com o banco de dados PostgreSQL integrado.

## Pré-requisitos

- Conta no [Railway](https://railway.app/)
- Conhecimento básico de Git
- Repositório do template já configurado

## Configuração do Railway

### 1. Iniciar um Novo Projeto

1. Faça login no Railway e clique em "New Project"
2. Selecione "Deploy from GitHub repo"
3. Conecte sua conta GitHub e selecione o repositório do template

### 2. Configurar Banco de Dados PostgreSQL

1. No projeto recém-criado, clique em "New"
2. Selecione "Database" e depois "PostgreSQL"
3. O Railway vai criar automaticamente uma instância PostgreSQL

### 3. Configurar Variáveis de Ambiente

No serviço da sua aplicação (não no banco de dados), configure as variáveis de ambiente conforme descrito abaixo.

#### Variáveis Obrigatórias:

```bash
# Variável de conexão com o banco de dados
# O Railway já fornece isso automaticamente quando você adiciona um PostgreSQL
DATABASE_URL="${{DATABASE_URL}}"

# Chave secreta para JWT - É OBRIGATÓRIO configurar manualmente
# Utilize uma string longa, aleatória e segura
JWT_SECRET="sua-chave-secreta-segura-aqui"
```

#### Variáveis Opcionais (com valores padrão):

```bash
# Nome descritivo do projeto (opcional)
# Default: "Template Railway FastAPI"
PROJECT_NAME="Template Railway FastAPI"

# Algoritmo JWT (opcional)
# Default: "HS256"
JWT_ALGORITHM="HS256"

# Tempo de expiração do JWT em minutos (opcional)
# Default: 30
JWT_EXPIRATION=30

# Modo de debug - Recomendado false em produção (opcional)
# Default: false
DEBUG=false
```

#### Notas importantes sobre variáveis de ambiente:

1. **DATABASE_URL**: 
   - O Railway já fornece esta variável automaticamente quando você adiciona um PostgreSQL
   - Você só precisa referenciar com a sintaxe `${{DATABASE_URL}}`
   - Não é necessário construir manualmente a string de conexão

2. **JWT_SECRET**:
   - Esta é a única variável que você precisa configurar manualmente
   - Crítica para a segurança do sistema de autenticação
   - Nunca use a mesma chave entre ambientes (desenvolvimento/produção)

3. **Variáveis opcionais**:
   - Só configure se precisar modificar o comportamento padrão
   - Para ambientes de produção, é recomendado definir `DEBUG=false`

### 4. Vincular Serviços

Para garantir que as referências entre serviços funcionem corretamente:

1. No painel do Railway, acesse o serviço da sua aplicação FastAPI
2. Na aba "Variables", clique em "Variable Reference"
3. Selecione o serviço PostgreSQL que você criou anteriormente
4. O Railway criará automaticamente referências para todas as variáveis do PostgreSQL

> **Importante**: Após vincular os serviços, o Railway permite que você acesse as variáveis do banco de dados usando a sintaxe `${{NomeDoServiço.NomeDaVariável}}` como mostrado na configuração do DATABASE_URL acima.

### 5. Verificar Configurações de Deploy

1. Certifique-se de que o Railway está usando o Procfile do projeto para iniciar a aplicação
2. Confirme que a porta está sendo configurada corretamente via variável PORT
3. Verifique se o Railway detectou corretamente o runtime.txt para a versão do Python

## Testando a Aplicação

Após o deploy ser concluído:

1. Clique no botão "View" para abrir a URL da aplicação
2. Acesse o endpoint `/docs` para verificar se a documentação Swagger está funcionando
3. Teste o endpoint `/health` para verificar se a aplicação está respondendo corretamente

## Solução de Problemas

### Erros Comuns e Soluções

#### Erro: "No module named 'template-railway-fastapi'"
- Verifique se o Procfile está configurado corretamente apontando para `api.main:app`

#### Erro de Conexão com Banco de Dados
- Confirme se a variável DATABASE_URL está no formato correto
- Verifique se as variáveis do PostgreSQL estão sendo injetadas corretamente

#### Erro ao Iniciar o Servidor
- Verifique os logs do Railway para identificar problemas específicos
- Confirme se todas as dependências estão sendo instaladas corretamente

## Otimizações

Para melhorar o desempenho da aplicação no Railway:

1. Configure o cache para reduzir a latência
2. Ajuste o número de workers do Uvicorn baseado na carga esperada
3. Considere adicionar compressão para respostas HTTP

## Próximos Passos

Após o deploy bem-sucedido:

1. Configure um domínio personalizado (se necessário)
2. Implemente monitoramento para a aplicação
3. Configure backups para o banco de dados
4. Implemente CI/CD para atualizações automáticas

---

Para mais informações, consulte a [documentação oficial do Railway](https://docs.railway.app/).
