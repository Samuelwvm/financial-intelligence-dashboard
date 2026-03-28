# 📈 Financial Intelligence Dashboard

Dashboard interativo para monitoramento de indicadores macroeconômicos e ativos financeiros (Brasil vs. Mundo), focado em fornecer clareza para investidores iniciantes.

## 🚀 Estrutura do Projeto
- **Brasil:** Selic, IPCA e Ibovespa.
- **Mundo:** S&P 500, Dólar e Euro.
- **Cripto:** Bitcoin e Ethereum.
- **Ativos:** 10 Brasil e 9 Mundo

## 🛠️ Tecnologias
- Python, Streamlit, Pandas, Plotly e SQLite.
- Dados: Banco Central do Brasil e Yahoo Finance.   


**Estrutura do projeto**
├── run_all.py               # Arquivo que roda os dois colelectors juntos (para facilitar na automação diária)
├── setup_historical.py      # Arquivo que contém a carga anual (Foi utilizado para popular o banco)
├── .github/workflows/       # Automação (Daily Update)
├── app/                     # Interface do Usuário (Frontend)
│   ├── Home.py              # Página Inicial (Resumo Geral)
│   └── pages/               # Menu Lateral Automático
│       ├── 01_🇧🇷_Brasil.py  # Selic, IPCA, Ibovespa
│       ├── 02_🌎_Mundo.py   # S&P500, Nasdaq, Dólar, Euro
│       ├── 03_₿_Cripto.py   # BTC, ETH e tendências
│       └── 04_📚_Entenda.py # Sua ideia: Explicação dos termos leigos
├── src/                     # O "Motor" (Backend)
│   ├── collectors/          # Buscadores de dados
│   │   ├── bcb_collector.py # Pega Selic/IPCA/CDI
│   │   └── yf_collector.py  # Pega tudo do Yahoo Finance
│   ├── database/            # Gestão do SQL
│   │   ├── schema.sql       # O desenho das tabelas
│   │   └── db_manager.py    # Grava e lê do banco
│   └── processing/          # Inteligência e Limpeza
│       ├── analytics.py     # Cálculos de rendimento e "scores" leigos
│       └── cleaners.py      # Padroniza nomes e datas
├── data/                    # Onde o arquivo .db vai morar
├── requirements.txt         # Lista de bibliotecas (incluindo yfinance)""
└── .gitignore               # O que o Git deve ignorar