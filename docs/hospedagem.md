# Hospedagem gratuita — Radar Financeiro V2

## Recomendação

**Principal: GitHub Pages, publicado pelo próprio GitHub Actions.**
**Reserva: Cloudflare Pages.**

### Por quê

O site é 100% estático e é reconstruído uma vez por dia útil pelo workflow que já coleta os dados. Com o GitHub Pages, o mesmo job que gera os JSON publica o site: não é preciso outra conta, token, segredo nem commit diário de dados.

| Critério (conferido nas páginas oficiais em 23/11/2026) | GitHub Pages | Cloudflare Pages (Free) | Vercel (Hobby) |
|---|---|---|---|
| Custo | grátis (repositório público) | grátis | grátis |
| Builds/deploys | limite *soft* de 10 builds/hora, **que não se aplica a workflow próprio do Actions** | 500 builds/mês; 1 build por vez | 100 deploys/dia |
| Banda | limite *soft* de 100 GB/mês | sem limite publicado | 100 GB/mês de Fast Data Transfer incluídos |
| Tamanho | site até 1 GB | 20.000 arquivos; 25 MiB por arquivo | — |
| Termos para portfólio | permitido; proíbe uso como hospedagem de negócio/SaaS comercial | permitido | plano Hobby só para uso pessoal e não comercial |
| Conta/segredos extras | **nenhum** | conta Cloudflare + integração Git, ou token de API como segredo | conta Vercel + integração Git; os dados precisariam ser commitados todo dia para disparar o deploy |
| Previews de PR | não (o CI faz build e testes e anexa os relatórios) | sim | sim |
| HTTPS / domínio próprio | sim / sim | sim / sim | sim / sim |
| Subcaminho | `/financial-intelligence-dashboard` (já tratado com `basePath`) | raiz do domínio | raiz do domínio |

Fontes: [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), [Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits/), [Vercel limits](https://vercel.com/docs/limits) e [Vercel Hobby](https://vercel.com/docs/plans/hobby).

**Endereço final:** `https://samuelwvm.github.io/financial-intelligence-dashboard/`

---

## Passo a passo (para quem nunca fez deploy)

Tudo acontece no próprio GitHub. Não precisa criar conta nova.

### 1. Ligar o GitHub Pages no modo "GitHub Actions" (uma vez)

1. Abra `https://github.com/Samuelwvm/financial-intelligence-dashboard`.
2. Clique em **Settings** (engrenagem, no topo do repositório).
3. No menu da esquerda, clique em **Pages**.
4. Em **Build and deployment → Source**, escolha **GitHub Actions**. Não escolha "Deploy from a branch".
5. Pronto. Não há botão de salvar: a escolha vale na hora.

### 2. Publicar pela primeira vez

O workflow só roda a partir da `main`. Depois que o PR `v2-web` for aprovado e mesclado:

1. Abra a aba **Actions**.
2. Na lista da esquerda, clique em **Atualização diária e deploy**.
3. Clique em **Run workflow** (à direita) → branch `main` → **Run workflow**.
4. Espere ~3 a 5 minutos. Os jobs **Coletar, exportar e construir**, **Publicar no GitHub Pages** e **Saúde dos dados** ficam verdes.
5. O link do site aparece no job **Publicar no GitHub Pages** e em **Settings → Pages**.

Configurações já prontas no repositório (não precisa preencher nada):

| Item | Valor |
|---|---|
| Pasta do site | `web/` |
| Comando de build | `npm ci && npm run build` (o workflow roda antes `python -m pipeline.run`) |
| Pasta de saída | `web/out` |
| Variáveis | `NEXT_PUBLIC_BASE_PATH` e `NEXT_PUBLIC_SITE_URL`, preenchidas automaticamente pelo `actions/configure-pages`. **Nenhum segredo.** |

### 3. Como funciona o ciclo diário

```
ter–sáb 01:17 UTC (seg–sex 22h17 em Brasília)
  └─ workflow "Atualização diária e deploy"
       1. baixa o banco da release data-latest
       2. pipeline: coleta Yahoo + BCB (retry), upsert, métricas, export JSON
       3. build do Next.js estático (valida os JSON com Zod)
       4. guarda o banco de volta na release data-latest
       5. publica web/out no GitHub Pages            ← o site muda aqui
       6. saúde: falha (e o GitHub te manda e-mail) se algum ativo ficou sem dado novo
```

Além do horário agendado, **todo merge na `main` publica o site na hora** (o workflow roda em `push`, só reexportando os dados, sem coletar).

Nenhum commit é criado por esse ciclo. O histórico do repositório fica só com mudanças de código.

Se a coleta falhar de vez (por exemplo, o Yahoo fora do ar), o job falha **antes** de publicar e o site continua com a versão anterior. A data "Atualizado após o fechamento de …" no topo mostra a idade dos dados.

### 4. Domínio próprio (opcional)

1. Compre o domínio onde preferir.
2. **Settings → Pages → Custom domain**: digite o domínio (ex.: `radar.seudominio.com.br`) → **Save**.
3. No painel do seu domínio, crie um registro **CNAME** de `radar` apontando para `samuelwvm.github.io`.
4. Volte em **Settings → Pages**, espere a verificação e marque **Enforce HTTPS**.
5. Com domínio próprio, o site passa a ficar na raiz, sem o subcaminho. O `actions/configure-pages` ajusta o `basePath` sozinho na próxima execução.

### 5. Reverter um deploy

O site publicado é sempre o resultado de uma execução do workflow. Para voltar:

- **Rápido (dados ou visual com problema):** **Actions → Atualização diária e deploy** → abra uma execução antiga que estava boa → **Re-run all jobs**. Ela republica o mesmo código daquela execução com o banco atual.
- **Código com problema:** reverta o commit na `main` (`git revert <commit>` + PR) e rode o workflow manualmente (passo 2.3).
- **Banco com problema:** cada execução guarda uma cópia do banco como artefato (**Actions → execução → Artifacts → `finance-db-…`**, por 30 dias). Baixe, suba na release com `gh release upload data-latest finance.db --clobber` e rode o workflow com a opção **"Só reexportar e publicar"** marcada.

### 6. Pausar

**Actions → Atualização diária e deploy → "…" → Disable workflow.** O site continua no ar com os últimos dados.

> **Inatividade:** em repositórios públicos, o GitHub desativa agendamentos após 60 dias sem atividade no repositório. Na V2 não há commits diários, então, se o repositório ficar 60 dias sem nenhum push, o GitHub avisa por e-mail e o agendamento para. Para reativar, faça qualquer commit ou clique em **Enable workflow** na aba Actions.

---

## Reserva: Cloudflare Pages

Use se o GitHub Pages ficar indisponível ou se você quiser previews de PR.

1. Crie uma conta em `dash.cloudflare.com` → **Workers & Pages** → **Create** → **Pages** → **Connect to Git** → escolha o repositório.
2. Configuração do build:
   - **Root directory:** `web`
   - **Build command:** `npm ci && npm run build`
   - **Build output directory:** `out`
   - **Variáveis:** nenhuma (sem `NEXT_PUBLIC_BASE_PATH`: o site fica na raiz).
3. O build da Cloudflare **não roda o pipeline Python**. É preciso que os JSON estejam disponíveis. A forma mais simples é trocar o último passo do workflow por um upload direto com `npx wrangler pages deploy web/out --project-name=radar-financeiro`, usando um token de API salvo em **Settings → Secrets → Actions** como `CLOUDFLARE_API_TOKEN`, junto com `CLOUDFLARE_ACCOUNT_ID`.
