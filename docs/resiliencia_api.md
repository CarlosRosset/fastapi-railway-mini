# Resiliência da API

## Introdução

A resiliência é um aspecto crucial em aplicações modernas, especialmente em APIs que precisam manter uma alta disponibilidade mesmo quando alguns componentes falham. Este documento explica como o template FastAPI implementa mecanismos de resiliência, com foco especial no tratamento de falhas de conexão com o banco de dados.

## Abordagem Unificada de Resiliência

**Atualização Importante**: Recentemente, revisamos e aprimoramos nossa abordagem de resiliência. Em vez de dividir as rotas em diferentes categorias, adotamos um tratamento mais consistente e uniforme para todas as rotas.

Apesar desta mudança, ainda é útil compreender os diferentes tipos de rotas em nossa API:

### Tipos de Rotas no Template

Todas as rotas agora tentam executar suas operações normalmente e só tratam erros quando eles realmente ocorrem:

| Tipo de Rota | Exemplos | Características |
|-------------|----------|-------------------|
| Rotas Básicas | `/`, `/health`, `/docs` | Não dependem do banco de dados para funcionalidade principal |
| Rotas de Autenticação | `/auth/login`, `/auth/register` | Lidam com autenticação e registro de usuários |
| Rotas de Recursos | `/heroes`, `/users` | Gerenciam recursos específicos e suas operações CRUD |

## Middleware de Resiliência

O template implementa um middleware especializado (`db_exception_handler`) na camada de aplicação que:

1. Tenta processar todas as requisições normalmente, independentemente do tipo de rota
2. Intercepta exceções relacionadas ao banco de dados quando elas realmente ocorrem
3. Fornece respostas de erro amigáveis e informativas quando não consegue completar a operação
4. Trata exceções de maneira consistente em toda a API

### Implementação do Middleware

O middleware está definido em `api/core/middleware.py` e captura exceções como:
- Falhas de conexão com o banco
- Timeouts em operações de banco de dados
- Erros de autenticação no banco de dados

## Comportamento da API com Banco de Dados Indisponível

### Rotas Críticas

As rotas críticas (`/` e `/health`) continuam funcionando normalmente:

```bash
# Exemplo de resposta da rota raiz quando o banco está indisponível
GET /
{
  "message": "Bem-vindo à API do template-railway-fastapi!",
  "docs": "/docs",
  "health": "/health",
  "version": "1.0.0"
}

# Exemplo de resposta da rota de health check quando o banco está indisponível
GET /health
{
  "api_status": "ok",
  "database_status": "error",
  "version": "1.0.0"
}
```

### Tratamento de Erros de Banco de Dados

Quando ocorre um problema real com o banco de dados durante o processamento de uma requisição, a API retorna uma mensagem de erro amigável:

```bash
# Exemplo de resposta quando ocorre um erro de banco de dados durante o processamento
GET /heroes/
{
  "detail": "Serviço de banco de dados indisponível",
  "message": "Não foi possível acessar o banco de dados. Este recurso está temporariamente indisponível.",
  "type": "database_unavailable"
}
```

## Migrações e Inicialização

O template também implementa resiliência no processo de inicialização:

1. As migrações de banco de dados são tentadas durante a inicialização da aplicação
2. Se as migrações falharem, a aplicação continua inicializando com capacidade limitada
3. Um log de aviso é emitido informando sobre a falha das migrações

Este comportamento permite que a API inicie mesmo quando o banco de dados não está disponível, mantendo as funcionalidades básicas operacionais.

## Benefícios desta Abordagem

- **Alta Disponibilidade**: A API permanece parcialmente funcional mesmo com falhas de componentes
- **Degradação Graciosa**: Em vez de falhar completamente, a API degrada de forma controlada
- **Melhor Experiência do Usuário**: Mensagens de erro claras e informativas
- **Facilidade de Diagnóstico**: Rotas como `/health` fornecem informações sobre o status dos componentes

## Testando a Resiliência

Para testar a resiliência da API em cenários de falha de banco de dados, você pode:

1. Configurar uma URL de banco de dados inválida no arquivo `.env`
2. Iniciar a API com essa configuração
3. Verificar se as rotas críticas continuam funcionando
4. Observar as mensagens de erro nas rotas dependentes de banco

Exemplo usando arquivos de ambiente alternados:

```bash
# Iniciar com banco válido
PYTHONPATH=. uvicorn api.main:app --reload --env-file .env.test

# Iniciar com banco inválido para testar resiliência
PYTHONPATH=. uvicorn api.main:app --reload --env-file .env.test_sem_db
```

## Conclusão

A implementação de mecanismos de resiliência é essencial para APIs robustas em ambiente de produção. O template FastAPI fornece uma base sólida para construir aplicações resilientes, com capacidade de lidar com falhas de componentes de forma controlada.

Com nossa abordagem unificada de tratamento de exceções, a API tenta processar todas as requisições normalmente e só trata erros quando eles realmente ocorrem. Isso resulta em um comportamento mais previsível e consistente para os usuários da API, independentemente do tipo de rota que estão acessando.
