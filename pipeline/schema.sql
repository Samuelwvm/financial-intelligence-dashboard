-- Schema da V2: idêntico ao da V1 + índice (symbol, date).
-- Compatível com o banco existente (CREATE ... IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS assets_metadata (
    symbol TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    sector TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS assets_history (
    date TEXT NOT NULL,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    variation REAL,
    FOREIGN KEY (symbol) REFERENCES assets_metadata (symbol),
    PRIMARY KEY (date, symbol)
);

-- As consultas filtram por symbol e ordenam por date (auditoria §3.2).
CREATE INDEX IF NOT EXISTS idx_history_symbol_date ON assets_history (symbol, date);

CREATE TABLE IF NOT EXISTS update_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT
);
