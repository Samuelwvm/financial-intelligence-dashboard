"""Catálogo único de ativos e indicadores.

Fonte da verdade para coleta, metadados, export e saúde do pipeline.
A V1 tinha duas listas divergentes (setup_historico.py com 29 ativos e
run_all.py com 25), o que deixou ^DJI, AMD, JBSS32.SA e 2222.SR sem
atualização desde abril/2026 — ver docs/auditoria-v1.md §2.2.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    symbol: str          # símbolo no Yahoo Finance
    slug: str            # usado na URL /ativo/<slug>
    name: str            # nome de exibição
    ticker: str          # rótulo curto (ex.: PETR4, IBOV)
    category: str        # categoria da V1 (assets_metadata.category)
    sector: str
    group: str           # brasil | mundo | cripto
    kind: str            # acao | indice | moeda | commodity | cripto
    currency: str        # BRL | USD | SAR | PTS (pontos)
    market: str          # subtítulo da tela do ativo (ex.: "Brasil · B3")
    calendar: str = "weekdays"  # weekdays | sun-thu | daily


ASSETS: tuple[Asset, ...] = (
    # ── Brasil · B3 ────────────────────────────────────────────────────────
    Asset("ITUB4.SA", "itub4", "Itaú Unibanco", "ITUB4", "Ação BR", "Financeiro", "brasil", "acao", "BRL", "Brasil · B3"),
    Asset("PETR4.SA", "petr4", "Petrobras", "PETR4", "Ação BR", "Energia", "brasil", "acao", "BRL", "Brasil · B3"),
    Asset("VALE3.SA", "vale3", "Vale", "VALE3", "Ação BR", "Mineração", "brasil", "acao", "BRL", "Brasil · B3"),
    Asset("BPAC11.SA", "bpac11", "BTG Pactual", "BPAC11", "Ação BR", "Financeiro", "brasil", "acao", "BRL", "Brasil · B3"),
    Asset("ABEV3.SA", "abev3", "Ambev", "ABEV3", "Ação BR", "Consumo", "brasil", "acao", "BRL", "Brasil · B3"),
    Asset("WEGE3.SA", "wege3", "WEG", "WEGE3", "Ação BR", "Industrial", "brasil", "acao", "BRL", "Brasil · B3"),
    Asset("BBDC4.SA", "bbdc4", "Bradesco", "BBDC4", "Ação BR", "Financeiro", "brasil", "acao", "BRL", "Brasil · B3"),
    Asset("BBAS3.SA", "bbas3", "Banco do Brasil", "BBAS3", "Ação BR", "Financeiro", "brasil", "acao", "BRL", "Brasil · B3"),
    Asset("SANB11.SA", "sanb11", "Santander Brasil", "SANB11", "Ação BR", "Financeiro", "brasil", "acao", "BRL", "Brasil · B3"),
    Asset("JBSS32.SA", "jbss32", "JBS", "JBSS32", "Ação BR", "Alimentos", "brasil", "acao", "BRL", "Brasil · B3 (BDR)"),
    # ── Mundo · ações ──────────────────────────────────────────────────────
    Asset("AAPL", "aapl", "Apple", "AAPL", "Ação EUA", "Tecnologia", "mundo", "acao", "USD", "EUA · Nasdaq"),
    Asset("GOOGL", "googl", "Alphabet (Google)", "GOOGL", "Ação EUA", "Tecnologia", "mundo", "acao", "USD", "EUA · Nasdaq"),
    Asset("MSFT", "msft", "Microsoft", "MSFT", "Ação EUA", "Tecnologia", "mundo", "acao", "USD", "EUA · Nasdaq"),
    Asset("AMZN", "amzn", "Amazon", "AMZN", "Ação EUA", "Tecnologia", "mundo", "acao", "USD", "EUA · Nasdaq"),
    Asset("NVDA", "nvda", "NVIDIA", "NVDA", "Ação EUA", "Tecnologia", "mundo", "acao", "USD", "EUA · Nasdaq"),
    Asset("TSLA", "tsla", "Tesla", "TSLA", "Ação EUA", "Automotivo", "mundo", "acao", "USD", "EUA · Nasdaq"),
    Asset("META", "meta", "Meta", "META", "Ação EUA", "Tecnologia", "mundo", "acao", "USD", "EUA · Nasdaq"),
    Asset("NU", "nu", "Nubank", "NU", "Ação EUA", "Financeiro", "mundo", "acao", "USD", "EUA · NYSE"),
    Asset("AMD", "amd", "AMD", "AMD", "Ação EUA", "Tecnologia", "mundo", "acao", "USD", "EUA · Nasdaq"),
    Asset("2222.SR", "aramco", "Saudi Aramco", "ARAMCO", "Ação Mundo", "Energia", "mundo", "acao", "SAR", "Arábia Saudita · Tadawul", "sun-thu"),
    # ── Índices ────────────────────────────────────────────────────────────
    Asset("^BVSP", "ibovespa", "Ibovespa", "IBOV", "Índice", "Brasil", "brasil", "indice", "PTS", "Brasil · B3"),
    Asset("^GSPC", "sp500", "S&P 500", "S&P 500", "Índice", "EUA", "mundo", "indice", "PTS", "EUA · índice"),
    Asset("^DJI", "dow-jones", "Dow Jones", "DOW", "Índice", "EUA", "mundo", "indice", "PTS", "EUA · índice"),
    # ── Câmbio ─────────────────────────────────────────────────────────────
    Asset("USDBRL=X", "dolar", "Dólar", "USD/BRL", "Moeda", "Câmbio", "mundo", "moeda", "BRL", "Câmbio · comercial"),
    Asset("EURBRL=X", "euro", "Euro", "EUR/BRL", "Moeda", "Câmbio", "mundo", "moeda", "BRL", "Câmbio · comercial"),
    # ── Commodities ────────────────────────────────────────────────────────
    # CL=F é o contrato futuro de petróleo WTI (a V1 o rotulava como "Brent").
    Asset("CL=F", "petroleo-wti", "Petróleo WTI", "WTI", "Commodity", "Energia", "mundo", "commodity", "USD", "Commodity · barril"),
    Asset("GC=F", "ouro", "Ouro", "OURO", "Commodity", "Segurança", "mundo", "commodity", "USD", "Commodity · onça-troy"),
    # ── Cripto ─────────────────────────────────────────────────────────────
    Asset("BTC-USD", "bitcoin", "Bitcoin", "BTC", "Cripto", "Tecnologia", "cripto", "cripto", "USD", "Cripto · em dólar", "daily"),
    Asset("ETH-USD", "ethereum", "Ethereum", "ETH", "Cripto", "Tecnologia", "cripto", "cripto", "USD", "Cripto · em dólar", "daily"),
)


@dataclass(frozen=True)
class Indicator:
    bcb_code: int
    symbol: str
    name: str
    frequency: str  # daily | monthly


INDICATORS: tuple[Indicator, ...] = (
    Indicator(11, "SELIC", "Selic (taxa diária)", "daily"),
    Indicator(432, "SELIC_META", "Selic Meta", "daily"),
    Indicator(433, "IPCA", "IPCA (mensal)", "monthly"),
    Indicator(13522, "IPCA12M", "IPCA acumulado 12 meses", "monthly"),
    Indicator(4389, "CDI", "CDI", "daily"),
)

# Pulso do mercado (ordem do mockup web: Ibovespa, S&P 500, Dow Jones, Dólar, Euro).
PULSE: tuple[str, ...] = ("^BVSP", "^GSPC", "^DJI", "USDBRL=X", "EURBRL=X")

# Ativos que podem compor a carteira (mesma lista "elite" da V1).
PORTFOLIO_CANDIDATES: tuple[str, ...] = (
    "ITUB4.SA", "PETR4.SA", "VALE3.SA", "BPAC11.SA", "ABEV3.SA", "WEGE3.SA",
    "BBDC4.SA", "BBAS3.SA", "SANB11.SA", "JBSS32.SA",
    "AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "TSLA", "META", "NU", "2222.SR", "AMD",
    "BTC-USD", "ETH-USD",
)
# A V1 usava os 6 primeiros como seleção inicial.
DEFAULT_PORTFOLIO: tuple[str, ...] = PORTFOLIO_CANDIDATES[:6]

# Domínio usado pelo CDN de logos da AllInvestView (cdn.tickerlogos.com/<domínio>).
# Sem entrada (índices, câmbio, commodities) ou com logo ausente no CDN → iniciais.
# Atribuição obrigatória "Logos by AllInvestView" no rodapé do site.
LOGO_DOMAINS: dict[str, str] = {
    "ITUB4.SA": "itau.com.br", "PETR4.SA": "petrobras.com.br", "VALE3.SA": "vale.com",
    "BPAC11.SA": "btgpactual.com", "ABEV3.SA": "ambev.com.br", "WEGE3.SA": "weg.net",
    "BBDC4.SA": "bradesco.com.br", "BBAS3.SA": "bb.com.br", "SANB11.SA": "santander.com.br",
    "JBSS32.SA": "jbs.com.br",
    "AAPL": "apple.com", "GOOGL": "google.com", "MSFT": "microsoft.com", "AMZN": "amazon.com",
    "NVDA": "nvidia.com", "TSLA": "tesla.com", "META": "meta.com", "NU": "nubank.com.br",
    "AMD": "amd.com", "2222.SR": "aramco.com",
    "BTC-USD": "bitcoin.org", "ETH-USD": "ethereum.org",
}

BY_SYMBOL = {a.symbol: a for a in ASSETS}
BY_SLUG = {a.slug: a for a in ASSETS}

assert len(BY_SYMBOL) == len(ASSETS), "símbolo duplicado no catálogo"
assert len(BY_SLUG) == len(ASSETS), "slug duplicado no catálogo"
assert all(s in BY_SYMBOL for s in PULSE + PORTFOLIO_CANDIDATES)
assert all(s in BY_SYMBOL for s in LOGO_DOMAINS)
