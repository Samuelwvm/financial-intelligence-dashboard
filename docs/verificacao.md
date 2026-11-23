# Verificação da V2 (Fase 6)

Data: 23/11/2026 · máquina local Windows 11, Node 26, Python 3.14 (CI: Ubuntu, Node 22, Python 3.12).

## 1. Pipeline do zero

```
RADAR_DB_PATH=<vazio> python -m pipeline.run
Coleta: 34 ok, 0 com falha
Saúde do pipeline: ok (todos os ativos e indicadores atualizados)
Export: 36 arquivos JSON em web/public/data
PRAGMA integrity_check → ok · foreign_key_check → []
```

A primeira tentativa pegou uma falha real da API do BCB (`304` com corpo vazio no IPCA). O export abortou **sem** sobrescrever os JSON anteriores. A correção está em `decisoes.md` §15.

## 2. Qualidade

| Verificação | Resultado |
|---|---|
| `ruff check pipeline` | ok |
| `pytest pipeline` | 22 passaram (métricas, idempotência, saúde, export × cálculo independente no SQLite real e sintético) |
| `npm run lint` / `npm run typecheck` | ok |
| `npm test` (Vitest) | 13 passaram (formatação pt-BR, carteira, contrato Zod) |
| `npm run build` | 36 páginas estáticas |
| `npm run test:e2e` (Playwright, 390×844 e 1440×900) | 32 passaram |
| Build com `basePath=/financial-intelligence-dashboard` servido em subpasta | navegação, dados sob demanda e aba ativa ok; nenhum 404 |

## 3. Capturas × mockup

`docs/screenshots/`: `<tela>-<mobile|web>-<light|dark>.png` (viewport) e `…-full.png` (página inteira), mais `mockup-*.png` nos mesmos tamanhos. Regerar com `cd web && npm run build && npm run screenshots`.

Ajustes feitos depois da comparação: altura de linha (`normal`), margem do carrossel, linha da carteira invisível com movimento reduzido, sobreposição de rótulos no risco × retorno, subtítulos em uma linha, glossário sem seta e sem contagem visível, gráfico de ativo com altura responsiva na web.

## 4. Lighthouse (mobile, CPU 4× e rede lenta simulada)

| Página | Performance | Acessibilidade | Boas práticas | SEO |
|---|---|---|---|---|
| Painel | 98 | 100 | 100 | 100 |
| Brasil | 99 | 100 | 100 | 100 |
| Mundo | 99 | 100 | 100 | 100 |
| Cripto | 99 | 100 | 100 | 100 |
| Entenda | 99 | 100 | 100 | 100 |
| Ativo (PETR4) | 99 (era 76: LCP 6,6 s → 1,1 s; ver `decisoes.md` §21) | 100 | 100 | 100 |
| Ativo (Bitcoin) | 99 | 100 | 100 | 100 |

Metas: Performance ≥ 90, Acessibilidade ≥ 95, Boas práticas ≥ 95, SEO ≥ 90. Relatórios JSON em `docs/lighthouse/`.

## 5. Movimento reduzido e JavaScript lento

- `prefers-reduced-motion: reduce`: teste e2e dedicado. Entrada dos cards desligada (`animation-name: none`), linhas desenhadas na hora, acordeão sem animação de altura.
- JS lento: o Lighthouse mede com CPU 4× mais lenta. O HTML é pré-renderizado com os números finais, a primeira carga não tem transição de página e nenhum conteúdo depende de JS para aparecer. Sem JS, só os seletores de período, a edição da carteira e o tema manual deixam de funcionar.

## 6. Links

- README: todos os links relativos apontam para arquivos que existem (verificado com script). Os links externos (V1 na tag `v1-streamlit`, Streamlit Cloud, GitHub Pages) dependem da publicação da tag e do deploy.
- V1: preservada intacta (e executável como antes) na tag `v1-streamlit` e na branch `v1-streamlit-archive`. Na `v2-web`, `legacy/streamlit/` guarda o mesmo código só como referência histórica: foi movido com `git mv`, sem edições, e não foi executado nesse novo caminho. Para rodar a V1, use a branch de arquivo.
