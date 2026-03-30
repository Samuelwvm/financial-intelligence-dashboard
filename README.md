# Radar Financeiro

> Dashboard interativo de mercado financeiro para investidores iniciantes — dados reais, linguagem acessível.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automação_Diária-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)

---

## Sobre o projeto

O Radar Financeiro nasceu de uma necessidade real: entender o mercado financeiro sem precisar ser especialista. O projeto consolida dados de bolsas, moedas, criptoativos e indicadores macroeconômicos brasileiros em um único painel visual, atualizado automaticamente todo dia útil.

A premissa central é que **dados financeiros não precisam ser intimidadores**. Cada número tem contexto, cada variação tem explicação — e o dashboard foi construído com isso em mente.

---

## Funcionalidades

**Painel principal**
- Pulso do Mercado com Ibovespa, S&P 500, Dow Jones, Dólar e Euro em tempo real
- Carteira personalizável com seleção de ativos e análise de desempenho relativo (base 100)
- Gráfico de Risco vs Retorno para comparar ativos da carteira
- Indicadores macroeconômicos: SELIC, CDI e IPCA com dados oficiais do Banco Central

**Brasil**
- 10 ações da B3: Itaú, Petrobras, Vale, BTG, Ambev, WEG, Bradesco, Banco do Brasil, Santander, JBS
- Análise individual com gráfico histórico por período (hoje, 7d, 30d, 90d, 1 ano)
- Evolução do Ibovespa no período selecionado

**Mundo**
- 10 ações americanas e globais: Apple, Google, Microsoft, Amazon, NVIDIA, Tesla, Meta, Nubank, AMD, Saudi Aramco
- Câmbio USD/BRL e EUR/BRL com histórico
- Commodities e índices: Ouro, Petróleo, S&P 500, Dow Jones

**Cripto**
- Bitcoin e Ethereum com preço, variação, máxima, mínima e volatilidade do período
- Gráfico comparativo de desempenho (base 100)

**Entenda o Mercado**
- Glossário interativo com 20+ termos financeiros explicados em linguagem acessível
- Filtro por categoria: Mercado, Risco, Renda Fixa, Câmbio, Cripto, Indicadores

---

## Arquitetura

```
financial-intelligence-dashboard/
├── run_all.py                    # Pipeline diário (coleta → limpeza → analytics)
├── setup_historico.py            # Carga inicial de 1 ano de dados
│
├── .github/
│   └── workflows/
│       └── daily_update.yml      # Automação diária via GitHub Actions
│
├── app/                          # Frontend (Streamlit)
│   ├── Home.py                   # Painel principal
│   └── pages/
│       ├── 01_Brasil.py
│       ├── 02_Mundo.py
│       ├── 03_Cripto.py
│       └── 04_Entenda.py
│
├── src/                          # Backend
│   ├── collectors/
│   │   ├── yf_collector.py       # Yahoo Finance (ações, moedas, índices, cripto)
│   │   └── bcb_collector.py      # Banco Central do Brasil (SELIC, IPCA, CDI)
│   ├── database/
│   │   ├── schema.sql            # Definição das tabelas
│   │   ├── db_manager.py         # Gerenciador de conexões (context manager)
│   │   └── queries.py            # Central de queries cacheadas
│   └── processing/
│       ├── cleaners.py           # Remoção de duplicatas e normalização
│       └── analytics.py          # Cálculo de variações
│
├── data/
│   └── finance.db                # Banco SQLite (~600KB, ~32 ativos, 1 ano de histórico)
│
├── scripts/
│   ├── check_db.py               # Diagnóstico do banco
│   └── clean_assets.py           # Reset completo para nova carga
│
└── requirements.txt
```

---

## Decisões técnicas

**SQLite como banco de dados** — Para um dashboard pessoal com ~32 ativos e atualizações diárias, o SQLite é mais que suficiente. O banco fica versionado no próprio repositório, eliminando a necessidade de infraestrutura externa.

**`INSERT OR IGNORE` com `PRIMARY KEY (date, symbol)`** — Garante idempotência na coleta. O pipeline pode rodar múltiplas vezes no mesmo dia sem criar duplicatas.

**Context manager no `db_manager`** — Todas as conexões usam `with db.get_connection() as conn`, garantindo `commit` em caso de sucesso e `rollback + close` automático em qualquer exceção.

**Queries centralizadas com `@st.cache_data(ttl=3600)`** — Um único arquivo `queries.py` centraliza toda a comunicação com o banco. As páginas não definem queries próprias. O cache de 1 hora evita re-queries a cada interação do usuário.

**GitHub Actions para atualização diária** — O workflow roda todo dia útil às 22h (horário de Brasília), executa o pipeline completo e commita o banco atualizado de volta ao repositório. Fim de semana e feriados, o Yahoo Finance não retorna dados novos e nenhum commit é gerado.

---

## Fontes de dados

| Fonte | Dados | Frequência |
|---|---|---|
| [Yahoo Finance](https://finance.yahoo.com) | Ações, moedas, índices, cripto, commodities | Diária |
| [Banco Central do Brasil](https://www.bcb.gov.br) | SELIC (série 11), IPCA (série 433), CDI (série 4389) | Diária / Mensal |

---

## Como rodar localmente

**Pré-requisitos:** Python 3.11+

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/financial-intelligence-dashboard.git
cd financial-intelligence-dashboard

# 2. Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Inicializar o banco e carregar histórico (rodar apenas uma vez)
python src/database/db_manager.py
python setup_historico.py

# 5. Calcular variações e scores
python run_all.py

# 6. Subir o dashboard
streamlit run app/Home.py
```

---

## Stack

- **Frontend:** Streamlit, Plotly
- **Backend:** Python, Pandas, NumPy
- **Banco de dados:** SQLite
- **Coleta de dados:** yfinance, requests
- **Automação:** GitHub Actions
- **Deploy:** Streamlit Cloud