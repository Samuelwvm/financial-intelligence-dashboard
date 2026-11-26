# Decisões técnicas da V2

Formato: **decisão** · motivo · alternativas consideradas.

## Arquitetura

1. **Site estático (Next.js `output: "export"`) + JSON pré-calculados, sem servidor.** Serviços gratuitos de API hibernam e deixariam o site lento. Os dados mudam uma vez por dia, então um servidor 24h não traz nenhum ganho. *Alternativas:* FastAPI no Render/Fly (descartado: hibernação e cotas); manter Streamlit (descartado pelo escopo).
2. **SQLite continua como fonte da verdade.** É simples, transacional, cabe em ~1 MB e é o que a V1 já usava. O export JSON é uma *visão* do banco gerada no fim do pipeline.
3. **Métricas calculadas uma vez, no pipeline (`pipeline/metrics.py`).** O site só formata. Isso elimina o N+1 da V1 e garante o mesmo número em todas as telas. O teste `test_export_vs_sqlite.py` recalcula tudo direto no SQLite e compara.
4. **Catálogo único de ativos (`pipeline/assets.py`).** A V1 tinha duas listas divergentes, e 4 ativos ficaram 8 meses sem atualizar.
5. **Coleta "janela inteira + upsert"** (400 dias por ativo, todo dia). É o mesmo número de requisições da coleta de 1 dia da V1, mas recupera dias perdidos, corrige o preço gravado antes do fechamento e mantém o ajuste de dividendos coerente com a fonte. Também é **idempotente**: rodar duas vezes dá o mesmo banco.
6. **Tudo ou nada na gravação.** As séries são coletadas antes de gravar. Se mais da metade falhar, nada é gravado e o job falha. Linhas `NaN`/≤0/futuras são descartadas. O export escreve num diretório temporário e troca de uma vez, então nunca fica pela metade.
7. **Período em dias corridos ancorado na última data de cada ativo** (fórmulas em `auditoria-v1.md` §5). A V1 contava *registros*, o que fazia "30 dias" de uma ação equivaler a cerca de 6 semanas. O retorno do card é igual ao último ponto do gráfico base 100.
8. **"Hoje"** = variação do último pregão. O gráfico, a volatilidade e a máx/mín usam a janela de 7 dias, como o gráfico "Hoje" da V1.
9. **Carteira** = média simples das curvas base 100, alinhadas por data com preenchimento para a frente, renormalizadas no primeiro dia em que todos os ativos têm preço. Pesos iguais, como a comparação base 100 da V1. A seleção fica no `localStorage`: sem conta e sem servidor.
10. **Volatilidade com √252 para todos os ativos, inclusive cripto.** Reproduz a V1. A troca para √365 em cripto foi registrada em `ideias-futuras.md`.

## Dados e automação

11. **Banco guardado como arquivo da release `data-latest`** (`gh release upload --clobber`), mais um artefato de 30 dias por execução. A V1 publicava código + banco numa branch órfã com `git push --force` diário. Isso funcionava, mas conflita com a regra de nunca forçar push e misturava código com dado. Com a release: zero histórico acumulado no git, nenhum force-push e restauração com um comando. Na primeira execução da V2, o banco é restaurado da branch `deploy` da V1. *Alternativas:* manter a branch órfã (descartado pela regra); commitar os JSON na `main` todo dia (descartado: ruído no histórico e crescimento contínuo).
12. **Cron `17 1 * * 2-6`** (seg–sex 22h17 BRT). A V1 rodava dom–qui, pulava a sexta e sofria atrasos de 4 a 8 h por agendar no minuto 00, o pico de carga do GitHub.
13. **Saúde em job separado.** O deploy acontece com o que foi coletado, e depois o job `health` falha se algum ativo estiver sem dado novo além do limite (4 pregões; cripto 2 dias; IPCA 80 dias). O GitHub envia e-mail na falha. O site mostra a data de cada dado.
14. **Build falha** se um JSON quebrar o contrato Zod (`web/lib/schema.ts`), se uma referência apontar para ativo inexistente ou se o dado mais recente tiver mais de 7 dias (`RADAR_MAX_DATA_AGE_DAYS`).
15. **API do BCB:** o endpoint por período às vezes responde `304` com corpo vazio. A V2 exige `200`, pede `no-cache` e, se falhar, usa `ultimos/20` (o upsert preserva o histórico). Esse problema apareceu no teste do pipeline "do zero".
16. **Versões fixas** no pipeline (`pipeline/requirements.txt`) e `package-lock.json` no site. O Dependabot propõe atualizações semanais em grupo.

## Frontend e visual

17. **Mockup como fonte da verdade.** Os tokens foram copiados dos `.dc.html` para CSS variables + `@theme` do Tailwind v4, com `data-theme` no `<html>`. Um script inline aplica o tema antes da primeira pintura (sem flash). Sem JavaScript, vale o `prefers-color-scheme`.
18. **`line-height: normal`** no `<html>`, como o navegador usa no mockup (o Tailwind usa 1.5 por padrão). Sem isso, todos os cards ficavam cerca de 10% mais altos.
19. **Gráficos em SVG próprio** (sem Recharts). Visual idêntico ao mockup, sem dependência pesada. A largura é medida para o traço não distorcer. Linhas desenhadas com `pathLength`, toque/ponteiro mostra data e valor, `role="img"` com descrição textual.
20. **Entrada dos cards com CSS (`@keyframes rise`, a mesma do mockup), não com Motion.** Assim a animação começa antes da hidratação e não esconde o HTML pré-renderizado, o que protege o LCP. O Motion cuida do resto: indicador de aba com `layoutId`, `pathLength` dos gráficos, acordeão com `AnimatePresence`, painéis, contagem e transição entre páginas (250 ms, desligada na primeira carga).
21. **Contagem animada só nos números da carteira.** No preço do ativo ela atrasava o LCP para 6,6 s no Lighthouse. Sem ela, o LCP é 1,1 s.
22. **Animações e SSR:** os valores iniciais do Motion são sempre os mesmos no servidor e no cliente. Com movimento reduzido, a duração vira 0 (em vez de pular a animação, o que deixava a linha invisível).
23. **Logos da AllInvestView, baixados no build** (`web/scripts/fetch-logos.mjs`) e servidos pelo próprio site. Os termos permitem uso gratuito e cópia ("You may cache or proxy logos on your own servers"), exigindo um link visível e sem `nofollow` "Logos by AllInvestView", que fica no rodapé de todas as páginas. Baixar no build evita 404 no navegador (que pesaria no Lighthouse) e a dependência do CDN em tempo real. Os domínios ficam no catálogo do pipeline (`LOGO_DOMAINS`). Plano B em dois níveis, iniciais do ticker em círculo como na V1: (1) logo ausente no CDN (hoje só o Bradesco), (2) imagem que falha no navegador, inclusive antes da hidratação. Na tela do ativo, o logo só aparece para empresas e cripto; índices, câmbio e commodities ficam sem ícone.
24. **Pós-build `flatten-segments.mjs`.** O Next 16.4 grava os arquivos de prefetch em subpastas, mas o cliente os pede com nome achatado. Sem a cópia, cada prefetch gerava um 404 no console.
25. **`cacheComponents` desligado.** O scaffold do Next 16 vem com ele ligado, mas o export estático não precisa dele, e ele tornaria a leitura dos JSON "dinâmica".
26. **Hospedagem: GitHub Pages publicado pelo próprio Actions.** Detalhes e comparação em `hospedagem.md`.

27. **Rodapé discreto:** o aviso legal da V1 (cálculos automáticos, não é recomendação de investimento, rentabilidade passada não garante retorno futuro) aparece **só na tela Entenda**, por escolha do dono do projeto. A atribuição "Logos by AllInvestView" aparece **em toda tela que mostra logos**, porque é condição dos termos de uso deles (não é exigência legal). Texto de 11px em cinza, depois do conteúdo.
28. **"Em linguagem simples" rotativo:** 8 dicas (3 com SELIC, CDI e IPCA do dia), trocando a cada 8 s. Todas ficam empilhadas na mesma célula do grid, então o card não muda de altura (CLS 0). Pontinhos mostram a posição e não há botões, por escolha do dono. Troca ao arrastar para o lado e pelas setas do teclado; pausa com mouse ou foco e com a aba em segundo plano; com movimento reduzido não gira sozinho.
29. **Carrossel "Todos os ativos"** no Painel, abaixo de SELIC/CDI/IPCA: uma faixa de rolagem de verdade, com duas cópias para o loop, que anda sozinha a ~30 px/s (`requestAnimationFrame` sobre `scrollLeft`). Arrastar com o dedo, o trackpad ou o mouse funciona em qualquer tela. Tocar ou arrastar pausa por 20 s; com ele andando, o 1º toque só pausa e o 2º abre o ativo. Há botão de pausar sem prazo (WCAG 2.2.2). Ativos da carteira têm borda verde e selo de check. Com movimento reduzido não anda sozinho.
30. **Risco x retorno refeito:** eixos com porcentagens e grade, linha do 0% destacada, o Ibovespa como ponto vazado de referência, rótulos sem colisão, detalhe ao tocar ou passar o mouse, legenda (alta/queda/referência) e uma frase explicando a leitura. Largura medida para o texto não distorcer.
31. **Deploy a cada merge na `main`:** o workflow também roda em `push` para a `main` (só reexporta e publica, sem coletar). Antes, um código mesclado só ia ao ar no próximo horário agendado.

32. **Interação por tamanho de tela (revisão de UX).** O mesmo gesto em todas as telas e o "1º toque pausa, 2º abre" eram padrões inventados e confusos:

    | | Celular / tablet (< 1024 px) | Computador (≥ 1024 px) |
    |---|---|---|
    | Em linguagem simples | arrastar para o lado; pontinhos só indicam; dica "Arraste para o lado…" | setas ‹ › (pontinhos só indicam); mouse em cima pausa; arrastar com o mouse não faz nada |
    | Carrossel de ativos | anda sozinho; o dedo pausa 20 s e arrasta (rolagem nativa); **toque abre direto** | anda sozinho; mouse em cima pausa; **clique abre direto**; setas ‹ › avançam dois cards (e pausam 20 s) |

    Nos dois tamanhos: setas do teclado nas dicas; o carrossel de ativos mantém um botão de pausa sem prazo (conteúdo que se move por mais de 5 s precisa de controle — WCAG 2.2.2; no celular não existe "mouse em cima"); movimento reduzido = nada anda sozinho. Um arraste não abre o ativo por engano.
33. **Risco x retorno:** a legenda (em alta / em queda / Ibovespa) fica na linha do título; a frase de leitura fica abaixo do gráfico, separada por uma linha, com respiro antes do botão "Editar ativos da carteira". O gráfico de desempenho ao lado passou para 240px para equilibrar a altura dos dois cards.
34. **Textos só para leitor de tela (`.sr-only`) com `top: 0; left: 0`.** Sem coordenadas, um elemento `position: absolute` fica na posição "estática" e, sem ancestral posicionado, escapa da rolagem dos carrosséis — com movimento reduzido a página ganhava ~250px de largura invisíveis. Teste e2e dedicado.

35. **[DESATIVADA — ver §37] Carteira comparada ao CDI e à inflação (IPCA)** no gráfico de desempenho, além do Ibovespa. Todas as linhas começam em 100 no 1º dia da carteira (rebase no navegador) e cada referência liga/desliga pela legenda, que mostra quanto ela rendeu no período. Calculado no pipeline, sem fonte nova (as séries CDI 4389 e IPCA 433 já eram coletadas):
    - **CDI acumulado:** composto por dia útil, fator `(1 + taxa_anual)^(1/252)` (convenção do CDI). Dias úteis recentes ainda não publicados pelo BCB (atraso de 1–2 dias) usam a última taxa; feriados do histórico não rendem.
    - **IPCA acumulado:** pró-rata por dia corrido, `(1 + IPCA_mês)^(1/dias_do_mês)`; meses ainda não divulgados usam o último IPCA conhecido.
    - Conferência: IPCA acumulado de 1 ano = +4,62% × IPCA 12 meses oficial (série 13522) = 4,63%.
    - Cores novas (fora do mockup, que só tem positivo/texto): CDI azul e IPCA âmbar, com contraste AA nos dois temas e tracejado diferente em cada linha (não depende só de cor).
36. **Correção: indicadores podem ser zero ou negativos.** A limpeza descartava valores ≤ 0 também nos dados do BCB, e o IPCA de ago/2026 (−0,32%, deflação) era jogado fora. Preços continuam exigindo > 0; indicadores não.

37. **Por que a feature CDI/IPCA foi desativada (comentada no código).** Medido nos dados reais: as linhas percorrem só uma pequena parte da altura do gráfico, porque a bolsa varia muito mais que a renda fixa:

    | Período | CDI | IPCA |
    |---|---|---|
    | Hoje / 7d | 11% | 1,5% |
    | 30d (padrão) | 6% | 0,8% |
    | 90d | 13% | 4% |
    | 1 ano | 33% | 11% |

    No período padrão elas viravam linhas retas no topo, puro ruído visual. O código ficou comentado com a marcação `FEATURE DESATIVADA` (`web/components/Portfolio.tsx`, `web/lib/portfolio.ts`, `web/app/globals.css`, `pipeline/export.py` e os testes de contrato e e2e). As funções `cdi_index`/`ipca_index` continuam em `pipeline/metrics.py`, com testes ativos. Se um dia fizer sentido, as alternativas são: mostrar só no período de 1 ano, ou como número ("o CDI rendeu +1,1% no mesmo período") em vez de linha. A correção do §36 (IPCA negativo) continua ativa, porque é um bug independente.

38. **IBGE · SIDRA na tela Brasil** (API pública, sem chave): *inflação por grupo* (tabela 7060: variação no mês, peso e acumulado em 12 meses do índice geral e dos 9 grupos) e *desemprego* (tabela 6381: taxa de desocupação da PNAD Contínua, trimestre móvel, 24 meses).
    - **Tabela própria `ibge_series (series, date, value)`**, separada da tabela de preços, com upsert por `(series, date)`: idempotente e corrige revisões do IBGE. Cada coleta busca uma janela (13 meses do IPCA, 36 trimestres do desemprego), então a carga é incremental por natureza.
    - **Parse do formato do SIDRA:** o 1º item da resposta é o cabeçalho; os valores ausentes ou sigilosos ("...", "-", "X") são descartados; o período vem em `D3C` (`202610`) e vira a data do 1º dia do mês (no trimestre móvel, o último mês do trimestre).
    - **Impacto de cada grupo no IPCA do mês** = peso × variação ÷ 100 (convenção do IBGE). Conferência: a soma dos 9 impactos bate com o índice geral (teste de contrato). O IPCA geral de 12 meses do SIDRA (4,63%) bate com a série 13522 do Banco Central.
    - **Só descreve o dado:** as frases dizem qual grupo mais pressionou ou aliviou e qual mais ou menos subiu, sem causa nem projeção. As barras são neutras (inflação subir não é "verde") e partem do centro quando há grupos negativos.
    - **Saúde:** IPCA por grupo com no máximo 80 dias; desemprego com no máximo 120 (o trimestre móvel sai com cerca de 2 meses de atraso). Fonte e período visíveis em cada card ("IPCA · outubro de 2026 · Fonte: IBGE").
    - **Deploy:** o workflow passa a coletar também em `push` e no CI (antes só reexportava). Assim, uma fonte nova tem dados já no primeiro deploy, sem esperar a coleta noturna.
    - **Celular:** a barra fica numa linha própria, com a largura toda, embaixo do nome; na web, em três colunas.

39. **Juro real Brasil × EUA (tela Mundo)**, ex-post, mensal, 24 meses, pela conta de Fisher `(1 + juro) ÷ (1 + inflação) − 1`:
    - **Brasil:** SELIC meta vigente no último dia do mês (BCB 432) e IPCA 12 meses (BCB 13522).
    - **EUA (fontes oficiais sem chave):** EFFR do **New York Fed** (Markets API) e CPI-U sem ajuste sazonal (CUUR0000SA0) da **BLS API v1**. O CPI 12 meses só é calculado quando o mês e o mesmo mês do ano anterior existem: a BLS não publicou outubro/2025, então out/2025 e out/2026 ficam sem ponto e o card diz isso. A referência mais recente dos EUA fica um mês atrás da do Brasil.
    - Recusados: a API do FRED (exige chave), o `fredgraph.csv` (não documentado) e o DBnomics (agregador com atraso).
    - Texto só descritivo: *"juro real mais alto tende a atrair investimento estrangeiro — um dos fatores que influenciam o dólar, não o único"*.
    - Tabela `us_series (series, date, value)`, upsert idempotente; saúde: EFFR com no máximo 7 dias, CPI com no máximo 80. Os indicadores do BCB passam a guardar 800 dias (os preços seguem com 400) para cobrir 24 meses.
40. **Desemprego com filtro de período** (2 anos, 5 anos ou desde 2012): o SIDRA tem a série desde 2012 (175 trimestres móveis), toda exportada; a tela recorta. Em "Desde 2012", uma frase mostra o maior e o menor valor da série.
41. **Inflação × meta (tela Brasil, abaixo do Desemprego):** IPCA 12 meses (BCB) contra a meta contínua do **CMN**, 3,0% com tolerância de 1,5 ponto (faixa de 1,5% a 4,5%), desenhada como faixa no gráfico. A frase diz se o dado está "acima do teto", "abaixo do piso" ou "dentro do intervalo". A meta é uma constante documentada em `pipeline/macro.py` e precisa ser revista se o CMN mudar.

## Adaptações em relação ao mockup

- **Tela de ativo:** no lugar do eyebrow "RADAR FINANCEIRO" há o link "‹ BRASIL / MUNDO / CRIPTO", com o mesmo estilo (12px, 600, cor positiva) e alvo de toque de 44px. Sem ele, não haveria como voltar à lista.
- **Logos, rodapé e dicas rotativas:** pedidos depois do mockup (§23, §27, §28). Seguem os mesmos tokens.
- **Botão de tema:** o mockup não tem. Ele fica no topo à direita no mobile (ícone de 44px) e no rodapé da sidebar na web.
- **Indicador da tab bar:** um traço de 2px no topo do item ativo, deslizante (`layoutId`), pedido no briefing. O mockup só muda a cor.
- **Período "Hoje" em Cripto:** o mockup mostra 7d/30d/90d/1 ano, mas a V1 tinha "Último dia". Mantive os 5 períodos para não perder função.
- **Risco x retorno no mobile:** o botão do card da carteira abre um painel com o seletor de período, o gráfico de desempenho (carteira × Ibovespa) e a dispersão. São funções da V1 que o mockup mobile não mostra.
- **Glossário:** cada termo mostra definição e exemplo (conteúdo da V1). O mockup mostra só a definição. Foi incluído o termo "Base 100", que aparece no mockup.
- **Telas sem versão web no mockup** (Ativo, Brasil, Mundo, Cripto, Entenda): derivadas com o mesmo sistema (sidebar, largura máxima de 1200px, cards de raio 18/padding 20, grade de 2 colunas).
