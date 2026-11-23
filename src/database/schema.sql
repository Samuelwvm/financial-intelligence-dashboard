-- 1. Tabela de Cadastro (O que é o quê?)
CREATE TABLE IF NOT EXISTS assets_metadata (
    symbol TEXT PRIMARY KEY,    -- Ex: 'PETR4.SA', 'AAPL', 'SELIC'
    name TEXT NOT NULL,         -- Ex: 'Petrobras', 'Apple', 'Taxa Selic'
    category TEXT NOT NULL,     -- Ex: 'Ação BR', 'Ação EUA', 'Moeda', 'Macro'
    sector TEXT,                -- Ex: 'Energia', 'Tecnologia', 'Bancário'
    description TEXT            -- Uma breve explicação para o usuário leigo
);

-- 2. Tabela de Preços e Valores (O histórico)
CREATE TABLE IF NOT EXISTS assets_history (
    date TEXT NOT NULL,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,        -- Valor de fechamento ou valor da taxa
    variation REAL,             -- Variação percentual do dia
    FOREIGN KEY (symbol) REFERENCES assets_metadata (symbol),
    PRIMARY KEY (date, symbol)
);

-- 3. Tabela de Logs (Para controle do robô)
CREATE TABLE IF NOT EXISTS update_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    status TEXT NOT NULL,       -- 'Sucesso' ou 'Erro'
    details TEXT
);