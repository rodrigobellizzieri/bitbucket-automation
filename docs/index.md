# Bitbucket Automation

Ferramenta de automação que cria e configura novos repositórios Bitbucket com uma única execução de pipeline. Todo o processo é executado por um Docker pipe (`rodrigobellizzieri/bitbucket-automation`) acionado via Bitbucket Pipelines.

---

## O que a automação faz

Ao acionar o pipeline customizado `bitbucket-automation`, as seguintes etapas são executadas automaticamente na ordem abaixo:

| # | Etapa | Descrição |
|---|-------|-----------|
| 1 | **Criar repositório** | Cria o repositório via Bitbucket REST API com visibilidade e projeto definidos |
| 2 | **Clonar repositório** | Clona o repositório recém-criado via HTTPS com App Password |
| 3 | **Aplicar template** | Copia os arquivos do template selecionado para o repositório local |
| 4 | **Push do template** | Faz commit e push do template para o branch principal |
| 5 | **Criar branch PRD** | Cria o branch de produção via API a partir do `master` |
| 6 | **Criar branch DEV** | Cria o branch de desenvolvimento via API a partir do `master` |
| 7 | **Configurar branching model** | Define os branches de development e production no modelo de branches do Bitbucket |
| 8 | **Habilitar Pipelines** | Ativa o Pipelines no repositório criado |

Ao final, a URL do novo repositório é exibida no log do pipeline.

---

## Pré-requisitos

### OAuth Consumer

Crie um OAuth Consumer no Bitbucket com as seguintes permissões:

- **Projects** → Admin  
- **Repositories** → Admin  

Guarde o **Client ID** e o **Client Secret** gerados.

### App Password

Crie um App Password para o usuário de CI com permissão de leitura/escrita em repositórios. Ele é usado exclusivamente para o `git clone` via HTTPS.

### Variáveis de Workspace

Configure as variáveis abaixo nas configurações do **Workspace** no Bitbucket (não no pipeline):

| Variável | Descrição |
|----------|-----------|
| `BITBUCKET_WORKSPACE` | Slug do workspace Bitbucket |
| `CI_EMAIL` | E-mail do usuário de CI para commits |
| `CI_NAME` | Nome do usuário de CI para commits |
| `BITBUCKET_USER` | Username do Bitbucket para o clone HTTPS |
| `BITBUCKET_PASS` | App Password para o clone HTTPS |
| `OAUTH_CLIENT_ID` | Client ID do OAuth Consumer |
| `OAUTH_CLIENT_SECRET` | Client Secret do OAuth Consumer |

---

## Configuração do repositório central

O pipeline de automação deve ser hospedado em um **repositório central** dedicado. Esse repositório precisa ter a seguinte estrutura:

```
.
├── bitbucket-pipelines.yml   ← Copiado de Documentation/example/
└── templates/
    ├── golang/
    │   └── bitbucket-pipelines.yml
    ├── typescript/
    │   └── bitbucket-pipelines.yml
    ├── terraform/
    │   └── ...
    └── serverlessframework/
        └── ...
```

> O nome de cada subdiretório dentro de `templates/` deve corresponder **exatamente** ao nome listado em `allowed-values` da variável `TEMPLATE` no `bitbucket-pipelines.yml`.

### Configurar os projetos permitidos

No `bitbucket-pipelines.yml`, atualize o `allowed-values` da variável `PROJECT` com as chaves dos projetos do seu workspace:

```yaml
- name: PROJECT
  allowed-values:
    - DEVOPS
    - OPS
    - PUB
    - REP
```

As chaves de projeto são encontradas na página **Projects** do Bitbucket (campo `KEY`).

---

## Como usar

1. Acesse o repositório central no Bitbucket.
2. Vá em **Pipelines → Run pipeline**.
3. Selecione o pipeline customizado `bitbucket-automation`.
4. Preencha as variáveis solicitadas:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `PROJECT` | Chave do projeto Bitbucket | `DEVOPS` |
| `REPOSITORY` | Nome do novo repositório | `my-service-ms` |
| `PRIVATE` | Visibilidade do repositório | `Private` ou `Public` |
| `TEMPLATE` | Template a ser aplicado | `golang` |
| `PRD_BRANCHE` | Nome do branch de produção | `main` |
| `DEV_BRANCHE` | Nome do branch de desenvolvimento | `develop` |

5. Clique em **Run**. Ao final, a URL do repositório criado aparece nos logs.

---

## Arquitetura interna

Toda a lógica está em `Code/main.py`, um script linear sem CLI ou arquivos de configuração. O fluxo de execução é:

```
Env vars → Validação → OAuth token → createRepository
                                           ↓
                                    cloneRepository
                                           ↓
                                      setTemplate
                                           ↓
                                     pushTemplate
                                           ↓
                              createBranches(main_branche)
                                           ↓
                              createBranches(dev_branche)
                                           ↓
                                updateBrancheModel
                                           ↓
                                    enablePipeline
```

### APIs consumidas

Todas as chamadas REST usam `Bearer token` obtido via OAuth2 Client Credentials.

| Método | Endpoint | Função |
|--------|----------|--------|
| `POST` | `bitbucket.org/site/oauth2/access_token` | Obter Bearer token |
| `POST` | `api.bitbucket.org/2.0/repositories/{workspace}/{repo}` | Criar repositório |
| `POST` | `.../refs/branches` | Criar branch |
| `PUT` | `.../branching-model/settings` | Configurar branching model |
| `PUT` | `.../pipelines_config` | Habilitar pipelines |

---

## Publicação da imagem Docker

A imagem é publicada automaticamente no Docker Hub via GitHub Actions ao fazer push em uma branch `v*`:

```
rodrigobellizzieri/bitbucket-automation:latest
rodrigobellizzieri/bitbucket-automation:<tag>
```

Para build local:

```bash
docker build -t bitbucket-automation ./Code
```

Após publicar uma nova versão, atualize a tag da imagem no `bitbucket-pipelines.yml` do repositório central:

```yaml
- pipe: docker://rodrigobellizzieri/bitbucket-automation:v1.0.0
```

---

## Adicionando novos templates

1. Crie um subdiretório com o nome do template dentro de `templates/` no repositório central.
2. Adicione os arquivos do template nesse diretório.
3. Adicione o nome do diretório no `allowed-values` da variável `TEMPLATE` no `bitbucket-pipelines.yml`.

```yaml
- name: TEMPLATE
  allowed-values:
    - golang
    - typescript
    - meu-novo-template   ← adicionar aqui
```

---

## Referências

- [Bitbucket REST API v2.0](https://developer.atlassian.com/cloud/bitbucket/rest/intro/)
- [Bitbucket Pipes](https://support.atlassian.com/bitbucket-cloud/docs/pipes/)
- [Docker Hub — rodrigobellizzieri/bitbucket-automation](https://hub.docker.com/r/rodrigobellizzieri/bitbucket-automation)
- [GitHub — rodrigobellizzieri/bitbucket-automation](https://github.com/rodrigobellizzieri/bitbucket-automation)
