# Auditoria da V1 (Streamlit) — Radar Financeiro

Data da auditoria: 23/11/2026 · commit auditado: `f8d50e0` (`main`) · banco auditado: `data/finance.db` da branch `deploy` (commit `3c662d0`, 23/11/2026).

Fase somente leitura: nada foi alterado na V1 durante a coleta de evidências. As correções estão na seção 5 e foram aplicadas na V2 (branch `v2-web`).

---

## 1. GitHub Actions (`.github/workflows/daily_update.yml`)

### 1.1 Execuções

Fonte: API pública `GET /repos/Samuelwvm/financial-intelligence-dashboard/actions/runs` (168 execuções no total, de 02/04/2026 a 23/11/2026).

| Métrica | Valor |
|---|---|
| Últimas 60 execuções | 60 sucesso, 0 falha (100%) |
| Todas as 168 execuções | 167 sucesso, 1 falha (99,4%) |
| Última execução com sucesso | 23/11/2026 08:34 UTC (agendada) |
| Única falha | 09/07/2026 (agendada). Logs já expirados (retenção de 90 dias) |
| Duração típica | 32–60 s (pico de 274 s em 01/10/2026) |
| Horário real de início | 04:00–08:50 UTC, embora o agendado seja 01:00 UTC |

**Leitura:** o workflow "passa" quase sempre, mas o verde não garante dados corretos. Veja a seção 2: 4 ativos e o IPCA estão parados há meses com o job verde.

### 1.2 Cron e fuso horário

- Atual: `cron: '0 1 * * 1-5'`, ou seja, seg–sex às 01:00 UTC = **dom–qui às 22:00 BRT**.
- **Problema:** roda no domingo à noite (sem pregão novo) e **não roda na sexta à noite**. O fechamento de sexta só entra na segunda às 01:00 UTC. As execuções confirmam: há runs às segundas (16/11, 23/11) e nenhum aos sábados.
- **Correto para "22h de Brasília em dias úteis":** `'17 1 * * 2-6'` (ter–sáb, 01:17 UTC). O minuto 17 evita o pico do início da hora: a documentação do GitHub avisa que agendamentos "can be delayed during periods of high loads… include the start of every hour". Isso explica os atrasos de 4 a 8 horas observados.

### 1.3 Configuração do workflow

| Item | V1 | Situação |
|---|---|---|
| `permissions` | ausente (usa o padrão do repositório) | ⚠️ definir o mínimo (`contents: write` só onde precisa) |
| `concurrency` | ausente | ⚠️ um `workflow_dispatch` manual pode rodar junto com o agendado e um sobrescrever o outro |
| `timeout-minutes` | ausente (padrão de 360 min) | ⚠️ |
| Cache do pip | ausente | ⚠️ |
| `actions/checkout@v4`, `actions/setup-python@v5`, Python 3.11 | ok | versões atuais e suportadas |
| `requirements.txt` sem versões fixas | `streamlit`, `yfinance`… sem pin | ⚠️ uma nova versão do yfinance pode quebrar a coleta sem aviso |
| Publicação | `git checkout --orphan` + `git push --force origin deploy-temp:deploy` | o banco e o código vão para a branch `deploy` como **um único commit sem histórico** (ver 2.4) |

### 1.4 Desativação por inatividade

- Regra atual da documentação oficial: em repositórios **públicos**, "scheduled workflows are automatically disabled when no repository activity has occurred in 60 days".
- O bot faz push na branch `deploy` todo dia útil, e o campo `pushed_at` do repositório é atualizado por ele (23/11/2026 08:35 UTC). Na prática esse push conta como atividade, mas a documentação não define "atividade" com precisão. **Mitigação na V2:** o passo de saúde falha o job (e o GitHub manda e-mail) se os dados pararem. Se o agendamento for desativado, o site mostra "Atualizado em…" com a data antiga e um aviso de dados desatualizados.

### 1.5 Falha parcial do Yahoo Finance

- `YFCollector.fetch_and_save` e `BCBCollector.fetch_bcb_data` **engolem todas as exceções** (`except Exception: print(...)`). O pipeline grava `Sucesso` em `update_logs` mesmo quando ativos falham. Todas as 169 linhas de `update_logs` dizem `Sucesso`.
- Não há retry nem backoff. Um rate limit pontual vira um dia perdido.
- Com `period="1d"`, um dia perdido **nunca é recuperado**. A falha de 09/07/2026 deixou o buraco de 08/07/2026 em PETR4, AAPL, USDBRL etc., visível até hoje (ver 2.2).
- Uma linha com `Close = NaN` (comum no pregão em andamento, por exemplo `2222.SR`) viola `price NOT NULL`. Isso aborta a transação **do ativo inteiro**, e a exceção é engolida.
- O job só falha se o último log for `Erro`, o que quase nunca acontece pelo motivo acima.

---

## 2. Banco SQLite (`data/finance.db`)

### 2.1 Estrutura e integridade

```
PRAGMA integrity_check   → ok
PRAGMA foreign_key_check → [] (nenhuma violação)
ANALYZE                  → ok
```

| Tabela | Linhas | Chave |
|---|---|---|
| `assets_metadata` | 34 | `symbol` PK |
| `assets_history` | 8.325 | PK `(date, symbol)`, FK → metadata |
| `update_logs` | 169 | `id` autoincrement |

- `schema.sql` = banco real (idênticos).
- **Índice:** a única chave de `assets_history` é `(date, symbol)`. As consultas filtram por `symbol` primeiro, o que obriga a percorrer o índice inteiro (seção 3.2). A V2 adiciona `CREATE INDEX idx_history_symbol_date ON assets_history(symbol, date)`.
- `PRAGMA foreign_keys` nunca é ligado nas conexões, então a FK é só decorativa.
- Datas são `TEXT` ISO (`YYYY-MM-DD`): ok.
- Macro (SELIC, CDI, IPCA…) mora na mesma tabela de preços, com `variation` calculada sem significado. É inofensivo, porque a variação de macro nunca é exibida.

### 2.2 Cobertura por símbolo (primeira/última data)

Achado mais grave da auditoria. Hoje é 23/11/2026:

| Símbolo | Última data | Situação |
|---|---|---|
| `^DJI` (Dow Jones, **card do Pulso**) | 02/04/2026 | 🔴 **parado há ~8 meses** |
| `AMD` | 02/04/2026 | 🔴 parado |
| `JBSS32.SA` (JBS) | 02/04/2026 | 🔴 parado |
| `2222.SR` (Saudi Aramco) | 02/04/2026 | 🔴 parado |
| `IPCA` (mensal) | 01/02/2026 | 🔴 parado: o site mostra IPCA 12m = **3,81%**, o BCB informa **4,63%** (out/2026) |
| `IPCA12M` | 01/02/2026 | 🔴 parado |
| Ações BR, `^BVSP`, SELIC, CDI | 19/11/2026 | ok (último pregão coletado) |
| Ações EUA, `^GSPC` | 20/11/2026 | ok |
| BTC, ETH, câmbio, commodities, SELIC_META | 23/11/2026 | ok |

**Causas:**
1. `run_all.py` tem a **própria lista** de 25 ativos, diferente da lista de 29 de `setup_historico.py`. `^DJI`, `AMD`, `JBSS32.SA` e `2222.SR` ficaram de fora da atualização diária desde a carga inicial.
2. O IPCA é uma série mensal datada no dia 1º do mês e publicada cerca de 40 dias depois. A coleta diária usa `days_back=5`, uma janela que nunca contém a data da observação nova. **O IPCA nunca é atualizado** depois da carga inicial.

Duplicatas `(date, symbol)`: 0 (garantido pela PK). Nulos: 0. Preços ≤ 0: 0. Datas futuras: 0. Símbolos no histórico sem cadastro: 0. Cadastros sem histórico: 0.

### 2.3 Lacunas e outliers

- **Dias úteis faltando** (de seg a sex, incluindo feriados de cada bolsa): PETR4 15, AAPL 11, USDBRL 8, BTC 1. A maioria são feriados legítimos (B3: 31/12, 01/01, carnaval, Tiradentes…; NYSE: Thanksgiving, Natal, MLK…). Lacunas que **não** são feriados: **08/07/2026** (todos os ativos: a falha de 09/07 nunca foi recuperada), 09/07/2026 (BTC) e 13, 15 e 17/07 (USDBRL).
- **Variações diárias acima de 20%:** BBAS3 −29,3% (26/10), BPAC11 −24,8% (26/10) e +22,5% (05/10), BBDC4 −21,7% (26/10). **Conferido contra o Yahoo hoje:** os preços batem com a fonte. Não é erro do pipeline. São movimentos (ou ajustes) da própria fonte.
- **Mistura de preço ajustado e não ajustado:** `yfinance.history()` usa `auto_adjust=True`, que ajusta o passado por dividendos e desdobramentos. Como a V1 só faz `INSERT OR IGNORE` do dia novo, o histórico antigo fica com o ajuste antigo. Exemplo: BBDC4 em 25/09/2026 está no banco como 17,88 e o Yahoo hoje informa 17,54. Pequenas diferenças também aparecem quando o preço do dia foi gravado antes do fechamento final (BPAC11 em 14/10: 78,30 no banco, 78,08 no Yahoo) e nunca é corrigido.

### 2.4 Tamanho e crescimento do repositório

- `finance.db`: 776 KiB (8.325 linhas, com limpeza de registros com mais de 400 dias).
- `.git` do clone: 746 KiB empacotado, 16 commits em `main`.
- **O banco não é commitado na `main`.** Desde o commit `e9f3277` ("move db para branch deploy"), ele vai para a branch `deploy` como commit órfão, com `push --force` diário. Resultado: **crescimento anual do repositório ≈ 0** (o GitHub descarta o objeto antigo na coleta de lixo). O risco de crescimento citado no briefing não se confirma.
- Efeito colateral: a premissa do item 6 da Fase 1 ("o bot commita `data/finance.db` na `main`") não vale. Não haverá conflito de banco ao fazer merge de `main` em `v2-web`.

### 2.5 Segredos

Busca em todo o histórico (`git log --all -p`) por `api_key|token|secret|password|ghp_|sk-`: **nada encontrado**. `.env.example` só contém `DB_PATH`, `APP_ENV` e `LOG_LEVEL`. Nenhuma chave é necessária: Yahoo e BCB são públicos.

---

## 3. Consultas (`src/database/queries.py`)

### 3.1 Mapa de queries × telas

| Função | Telas | SQL |
|---|---|---|
| `get_latest(symbol)` | Home, Brasil, Mundo, Cripto | `SELECT price, variation … WHERE symbol=? ORDER BY date DESC LIMIT 1` |
| `get_stats(symbol, days)` | Home, Brasil, Mundo | `SELECT price … WHERE symbol=? ORDER BY date DESC LIMIT ?` |
| `get_ohlc_stats(symbol, days)` | Cripto | igual a `get_stats` |
| `get_history(symbol, days)` | Brasil, Mundo, Cripto | `… WHERE symbol=? AND date >= date('now', '-N days')` |
| `get_portfolio_history(symbols, days)` | Home | `… WHERE symbol IN (?,…) AND date >= date('now','-N days')` |
| `get_elite_assets()` | Home | metadata `IN (…)` |
| `get_br_stocks()`, `get_us_stocks()`, `get_commodities_indices()` | Brasil, Mundo | metadata por categoria |
| `get_macro_detail()` | Home, Brasil | 5 × `… WHERE symbol='X' ORDER BY date DESC LIMIT 1` |

### 3.2 Problemas

- **Injeção de SQL:** nenhuma com entrada do usuário. `get_portfolio_history` monta `date('now','-{days} days')` com f-string, mas `days` vem de um dicionário fixo. Risco baixo, corrigido na V2 (que não monta SQL dinâmico).
- **`SELECT *`:** nenhum.
- **N+1:** cada card dispara 2 consultas (`get_latest` + `get_stats`). Na Home, o gráfico de risco chama `get_stats` **duas vezes por ativo** (uma para retorno, outra para volatilidade). O cache do Streamlit (`ttl=3600`) amortiza.
- **`EXPLAIN QUERY PLAN`:**

```
get_latest            SCAN assets_history USING INDEX sqlite_autoindex_assets_history_1   ← full scan do índice
get_stats             SCAN assets_history USING INDEX sqlite_autoindex_assets_history_1   ← full scan
get_history           SEARCH … USING INDEX (date>?)
get_portfolio_history SEARCH … USING INDEX (date>?)
get_br_stocks         SCAN assets_metadata + TEMP B-TREE (34 linhas, irrelevante)
calculate_variations  SCAN assets_history + TEMP B-TREE (lê a tabela toda a cada execução)
```

  Com 8 mil linhas o custo é desprezível, mas o índice `(symbol, date)` resolve. Na V2 o problema desaparece para o usuário: as métricas são calculadas **uma vez** no pipeline e o site só lê JSON.
- `DataCleaner.normalize_names()` faz `UPDATE` da tabela inteira todo dia (sem efeito: os símbolos já são maiúsculos).
- **Glossário:** a categoria do filtro é `'Cambio'` (sem acento), mas os termos usam `'Câmbio'`. **O filtro "Cambio" mostra zero termos.**
- **Rótulo errado:** `CL=F` está cadastrado como "Petróleo Brent", mas `CL=F` é o contrato **WTI** (o Brent é `BZ=F`). O dado está certo e o nome está errado.

### 3.3 Fórmulas atuais (V1) e bugs

`PERIOD_OPT = {'Último dia': 2, '7 dias': 7, '30 dias': 30, '90 dias': 90, '1 ano': 365}`

| Métrica | Fórmula V1 | Problema |
|---|---|---|
| Variação diária (`variation`) | `pct_change()` entre registros consecutivos do símbolo × 100 | ok. Compara com o pregão anterior, ignorando dias sem pregão (correto) |
| Retorno do período (`get_stats`) | `(p[0] / p[N-1] − 1) × 100` sobre os **N últimos registros** | 🔴 **N é contado em registros, não em dias.** "30 dias" de uma ação = 30 pregões ≈ 6 semanas. "1 ano" = 365 registros, mas uma ação só tem cerca de 270, então usa todo o histórico (~13 meses). Para cripto (7 dias/semana), N registros ≈ N dias. Os períodos não são comparáveis entre ativos |
| Volatilidade | `std(pct_change(p)) × √252 × 100` (desvio amostral, ddof=1) sobre os mesmos N registros | herda o problema da janela |
| Máxima/mínima (Cripto) | `max/min(p)` dos N registros | herda o problema |
| Base 100 (gráficos) | `p / p_primeiro × 100`, janela `date >= date('now', '-N days')` | 🟠 a janela é em **dias corridos a partir de hoje (UTC)**, diferente da janela dos cards. O gráfico e o card de retorno mostram períodos diferentes. Se o dado estiver parado (caso do `^DJI`), o gráfico fica vazio |
| "Hoje" no gráfico | janela de 7 dias | ok (escolha de UX) |
| Risco × retorno | dispersão (`volatilidade`, `retorno`) de `get_stats` | herda o problema da janela |
| SELIC | `SELIC_META` (série BCB 432), % a.a. · "taxa diária" = série 11 | ok |
| CDI | série BCB 4389, % a.a. | ok |
| IPCA | 12m = série 13522 · mensal = série 433 | 🔴 parado (2.2) |

---

## 4. Problemas por severidade

| # | Sev. | Problema | V2 |
|---|---|---|---|
| 1 | 🔴 Crítico | `^DJI`, `AMD`, `JBSS32.SA` e `2222.SR` sem atualização desde 02/04/2026 (lista duplicada e divergente) | **Corrigido:** um único catálogo de ativos (`pipeline/assets.py`) |
| 2 | 🔴 Crítico | IPCA/IPCA12M parados desde fev/2026 (janela de 5 dias em série mensal) | **Corrigido:** o BCB é sempre coletado com janela de 400 dias + upsert |
| 3 | 🔴 Crítico | Falhas de coleta engolidas: o job fica verde com dados parados | **Corrigido:** retry com backoff, falha explícita e passo de saúde que falha o job |
| 4 | 🟠 Alto | Retorno, volatilidade e máx/mín usam N **registros**, não N dias. "1 ano" de ações ≈ 13 meses | **Corrigido:** janela em dias corridos ancorada na última data do ativo (seção 5) |
| 5 | 🟠 Alto | Gráfico base 100 e cards usam janelas diferentes | **Corrigido:** a mesma janela para tudo |
| 6 | 🟠 Alto | Dia perdido nunca é recuperado (`period="1d"` + `INSERT OR IGNORE`). O preço gravado antes do fechamento nunca é corrigido | **Corrigido:** a coleta diária rebaixa os últimos 400 dias e faz upsert (o mesmo número de requisições) |
| 7 | 🟠 Alto | Mistura de histórico ajustado e não ajustado por dividendos | **Corrigido pelo item 6:** o histórico inteiro é regravado com o ajuste atual da fonte |
| 8 | 🟠 Alto | Linha `NaN` aborta o ativo inteiro | **Corrigido:** linhas sem fechamento são descartadas |
| 9 | 🟡 Médio | Cron roda dom–qui e pula a sexta; minuto 00 causa atrasos de horas | **Corrigido:** `17 1 * * 2-6` |
| 10 | 🟡 Médio | Sem `permissions`, `concurrency`, `timeout-minutes`, cache e versões fixas | **Corrigido** |
| 11 | 🟡 Médio | Filtro "Cambio" do glossário sempre vazio | **Corrigido** |
| 12 | 🟡 Médio | `CL=F` rotulado como "Petróleo Brent" (é WTI) | **Corrigido:** "Petróleo WTI" |
| 13 | 🟢 Baixo | Sem índice `(symbol, date)`; `normalize_names` reescreve a tabela; N+1 no Streamlit | **Corrigido** (índice; métricas pré-calculadas) |
| 14 | 🟢 Baixo | Nome do produto misturado ("Easy Finance" × "Radar Financeiro") | **Corrigido:** "Radar Financeiro" |
| 15 | 🟢 Baixo | Volatilidade de cripto anualizada com √252 (cripto negocia 365 dias) | **Mantido** como na V1 (convenção). Registrado em `ideias-futuras.md` |
| 16 | 🟢 Baixo | Macro na mesma tabela de preços | Mantido (funciona). Registrado em `ideias-futuras.md` |

---

## 5. Fórmulas da V2 (as da V1, com os bugs 4 e 5 corrigidos)

Para cada ativo, com `d_last` = a última data com preço:

- **Hoje**: retorno = variação do último pregão = `(p_last / p_anterior − 1) × 100`. Volatilidade, máxima e mínima usam a janela de 7 dias (a mesma do gráfico "Hoje" na V1).
- **7d / 30d / 90d / 1 ano** (N = 7, 30, 90, 365 dias corridos):
  - `início = d_last − N dias`. O **preço-base** é o último preço com data ≤ `início` (se não existir, o primeiro preço disponível).
  - Série do período = preço-base + todos os preços com data > `início`.
  - **Retorno** = `(p_last / p_base − 1) × 100`.
  - **Volatilidade** = `std(retornos diários da série, ddof=1) × √252 × 100` (a fórmula da V1).
  - **Máxima/mínima** = `max/min` dos preços da série.
  - **Base 100** = `p / p_base × 100` para cada ponto da série. O retorno do card é igual ao último ponto do gráfico − 100.
- **Carteira** (card "Minha carteira" e linha do gráfico): média simples (pesos iguais) das curvas base 100 dos ativos escolhidos, alinhadas por data com preenchimento para a frente. É a mesma comparação que a V1 mostrava, agregada numa linha só, como no mockup. Calculada no navegador a partir das séries base 100 já exportadas.
- Arredondamento só na exibição (pt-BR: retorno e volatilidade com 1 casa, variação diária com 2).

Teste de referência: `pipeline/tests/test_export_vs_sqlite.py` recalcula essas métricas direto do SQLite, de forma independente, e compara com os JSON exportados.

---

## 6. O que foi corrigido (atualizado ao fim da V2)

Ver a seção 4, coluna "V2". Detalhes de implementação em `docs/decisoes.md`.
