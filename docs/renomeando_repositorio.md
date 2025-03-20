# Guia para Renomear o Repositório GitHub

Este documento contém os passos necessários para renomear o repositório GitHub de `fastapi-railway-mini` para `template-railway-fastapi`, mantendo a consistência entre o nome do projeto e o nome do repositório.

## Passos na Interface do GitHub

1. Acesse o repositório em [https://github.com/CarlosRosset/fastapi-railway-mini](https://github.com/CarlosRosset/fastapi-railway-mini)
2. Clique na aba "Settings" (próximo a Insights, na parte superior da página)
3. Na primeira seção "General", role para baixo até encontrar o campo "Repository name"
4. Mude o nome de `fastapi-railway-mini` para `template-railway-fastapi`
5. Clique no botão vermelho "Rename" para confirmar a alteração

## Passos no Repositório Local

Após renomear o repositório no GitHub, você precisará atualizar a URL de origem no seu repositório local. Execute os seguintes comandos no terminal:

```bash
# Verifique a configuração atual do remote
git remote -v

# Atualize a URL do repositório remoto
git remote set-url origin git@github.com:CarlosRosset/template-railway-fastapi.git

# Se você usa HTTPS em vez de SSH, use este comando:
# git remote set-url origin https://github.com/CarlosRosset/template-railway-fastapi.git

# Verifique se a atualização foi bem-sucedida
git remote -v
```

## Verificação Final

1. Faça um teste de push para confirmar que a conexão com o repositório renomeado está funcionando:

```bash
git status
git commit --allow-empty -m "Teste após renomear repositório"
git push origin main
```

2. Visite o novo URL do repositório para confirmar que está tudo funcionando:
   [https://github.com/CarlosRosset/template-railway-fastapi](https://github.com/CarlosRosset/template-railway-fastapi)

## Considerações Adicionais

- Atualize quaisquer links em documentos que apontem para o repositório antigo
- Informe colaboradores sobre a mudança de nome
- Atualize quaisquer webhooks ou integrações que estejam configuradas para o repositório
