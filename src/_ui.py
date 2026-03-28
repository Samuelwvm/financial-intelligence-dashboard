"""
src/_ui.py — Estilos e helpers compartilhados entre todas as páginas.
Coloque este arquivo em: seu_projeto/src/_ui.py
"""

# ─── PALETA ────────────────────────────────────────────────────────────────
SECTOR_COLORS = {
    'Financeiro': '#1a3a6e',
    'Energia':    '#4a1e0e',
    'Mineração':  '#1e3a1a',
    'Consumo':    '#2a1e5e',
    'Industrial': '#1e2e5e',
    'Tecnologia': '#2a1e4e',
    'Automotivo': '#3a1e1e',
    'Cripto':     '#3a2a0e',
    'Moeda':      '#1e3a3a',
    'Índice':     '#1e1e3a',
    'default':    '#2a2a3a',
}

SYMBOL_SECTOR = {
    'ITUB4.SA':'Financeiro','PETR4.SA':'Energia','VALE3.SA':'Mineração',
    'BPAC11.SA':'Financeiro','ABEV3.SA':'Consumo','WEGE3.SA':'Industrial',
    'BBDC4.SA':'Financeiro','BBAS3.SA':'Financeiro','SANB11.SA':'Financeiro',
    'AAPL':'Tecnologia','GOOGL':'Tecnologia','MSFT':'Tecnologia',
    'AMZN':'Tecnologia','NVDA':'Tecnologia','TSLA':'Automotivo',
    'META':'Tecnologia','NU':'Financeiro','2222.SR':'Energia',
    'BTC-USD':'Cripto','ETH-USD':'Cripto',
    'USDBRL=X':'Moeda','EURBRL=X':'Moeda',
    '^BVSP':'Índice','^GSPC':'Índice','^DJI':'Índice',
}

SYMBOL_LABEL = {
    'ITUB4.SA':'ITUB4','PETR4.SA':'PETR4','VALE3.SA':'VALE3',
    'BPAC11.SA':'BPAC11','ABEV3.SA':'ABEV3','WEGE3.SA':'WEGE3',
    'BBDC4.SA':'BBDC4','BBAS3.SA':'BBAS3','SANB11.SA':'SANB11',
    'AAPL':'AAPL','GOOGL':'GOOGL','MSFT':'MSFT','AMZN':'AMZN',
    'NVDA':'NVDA','TSLA':'TSLA','META':'META','NU':'NU',
    '2222.SR':'ARAMCO','BTC-USD':'BTC','ETH-USD':'ETH',
    'USDBRL=X':'USD/BRL','EURBRL=X':'EUR/BRL',
    '^BVSP':'IBOV','^GSPC':'S&P500','^DJI':'DOW',
}

# ─── CSS BASE ──────────────────────────────────────────────────────────────
CSS = """
<style>
/* ── FUNDO ── */
.main .block-container {
    background-color: #0e1018 !important;
    padding-top: 2rem;
    max-width: 100%;
}

/* ── CABEÇALHO DE PÁGINA ── */
/* ── ESCONDE MENU PRINCIPAL ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

.pg-title {
    font-size: 30px !important;
    font-weight: 700 !important;
    color: #e8ecf8 !important;
    margin-bottom: 4px !important;
    letter-spacing: -0.3px;
}
.pg-subtitle {
    font-size: 14px !important;
    color: #454a60 !important;
    margin-bottom: 32px !important;
}

/* ── CABEÇALHO DE SEÇÃO ── */
.sec-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 32px 0 14px;
}
.sec-title {
    font-size: 16px !important;
    font-weight: 700 !important;
    color: #6a7890 !important;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-badge {
    font-size: 10px !important;
    color: #454a60 !important;
    background: #161922;
    border: 0.5px solid #272a38;
    padding: 4px 10px;
    border-radius: 5px;
}

/* ── PULSO DO MERCADO ── */
.market-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
}
.mcard {
    background: #161922;
    border: 0.5px solid #1f2333;
    border-radius: 10px;
    padding: 18px 20px;
}
.mcard-label {
    font-size: 10px !important;
    color: #454a60 !important;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 10px;
    font-weight: 600 !important;
}
.mcard-value {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #d0d8f0 !important;
    margin-bottom: 6px;
}
.mcard-desc {
    font-size: 12px !important;
    color: #5a6480 !important;
    margin-top: 8px;
    font-weight: 400 !important;
}

/* ── CARDS DE ATIVOS ── */
.stock-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
}
.scard {
    background: #161922;
    border: 0.5px solid #1f2333;
    border-radius: 10px;
    padding: 15px;
}
.scard-top {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}
.scard-name {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #b0b8d8 !important;
}
.scard-sub {
    font-size: 14px !important;
    color: #454a60 !important;
    margin-top: 2px;
}
.sstat {
    background: #0f1118;
    border-radius: 6px;
    padding: 8px 9px;
    flex: 1;
    text-align: center;
}
.sstat-label {
    font-size: 9px !important;
    color: #3a3f55 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600 !important;
}
.sstat-val {
    font-size: 14px !important;
    font-weight: 700 !important;
    margin-top: 2px;
}

/* ── ECONOMIA ── */
.eco-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}
.eco-card {
    background: #0f1929;
    border: 0.5px solid #1a2a40;
    border-radius: 10px;
    padding: 18px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.eco-label {
    font-size: 10px !important;
    color: #4a6080 !important;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 5px;
    font-weight: 600 !important;
}
.eco-value {
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #7eb8f7 !important;
}
.eco-desc {
    font-size: 12px !important;
    color: #4a6080 !important;
    margin-top: 5px;
    font-weight: 400 !important;
}
.eco-icon { font-size: 24px; opacity: 0.4; }

/* ── SEMÂNTICA ── */
.up   { color: #4caf7d !important; font-weight: 600 !important; }
.down { color: #e05a5a !important; font-weight: 600 !important; }

/* ── DIVISOR ── */
.divider { border: none; border-top: 0.5px solid #191c28; margin: 30px 0; }

/* ── SIDEBAR ── */

[data-testid="stSidebar"] {
    background: #13161f !important;
    border-right: 0.5px solid #1f2333 !important;
}
[data-testid="stSidebarNav"] a {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #6a7090 !important;
    border-radius: 7px !important;
    padding: 8px 12px !important;
    margin: 1px 4px !important;
    text-decoration: none !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: #1e2235 !important;
    color: #b0b8d8 !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: #1e2235 !important;
    color: #e0e4f8 !important;
    font-weight: 600 !important;
}
[data-testid="stSidebarHeader"] {
    padding-bottom: 8px !important;
    border-bottom: 0.5px solid #1f2333 !important;
    margin-bottom: 8px !important;
}

/* ── INPUTS ── */
div[data-testid="stMultiSelect"] > label,
div[data-testid="stSelectbox"]   > label,
div[data-testid="stTextInput"]   > label,
div[data-testid="stRadio"]       > label { display: none; }

div[data-testid="stTextInput"] input {
    background: #161922 !important;
    border: 0.5px solid #2a2d3a !important;
    border-radius: 8px !important;
    color: #d0d8f0 !important;
    font-size: 14px !important;
}

/* ── EXPANDER — seletores atualizados para Streamlit 1.30+ ── */
div[data-testid="stExpander"] {
    background: #161922 !important;
    border: 0.5px solid #1f2333 !important;
    border-radius: 10px !important;
    overflow: hidden;
    margin-bottom: 8px !important;
}
div[data-testid="stExpander"] details {
    background: #161922 !important;
}
div[data-testid="stExpander"] details > summary {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #c8d0e8 !important;
    padding: 14px 18px !important;
    list-style: none;
    cursor: pointer;
}
div[data-testid="stExpander"] details > summary:hover {
    color: #e8ecf8 !important;
    background: #1a1d2a !important;
}
div[data-testid="stExpander"] details > summary::marker,
div[data-testid="stExpander"] details > summary::-webkit-details-marker {
    display: none;
}
/* Conteúdo interno do expander */
div[data-testid="stExpander"] details > div {
    padding: 4px 18px 16px !important;
    border-top: 0.5px solid #1a1d28;
}
</style>
"""

# ─── HELPERS ───────────────────────────────────────────────────────────────
def _dot(color: str = '#5b8ef0') -> str:
    return (
        f'<svg width="8" height="8" viewBox="0 0 8 8" style="flex-shrink:0;">'
        f'<circle cx="4" cy="4" r="3" fill="{color}" opacity=".3"/>'
        f'<circle cx="4" cy="4" r="1.6" fill="{color}"/></svg>'
    )

def sec_header(title: str, badge: str = '', dot_color: str = '#5b8ef0') -> str:
    badge_html = f'<div class="sec-badge">{badge}</div>' if badge else ''
    return (
        f'<div class="sec-wrap">'
        f'<div class="sec-title">{_dot(dot_color)}{title}</div>'
        f'{badge_html}</div>'
    )

# ─── LOGOS ─────────────────────────────────────────────────────────────────
TICKER_LOGOS_CDN = "https://cdn.tickerlogos.com"

SYMBOL_DOMAINS = {
    'ITUB4.SA': 'itau.com.br',
    'PETR4.SA': 'petrobras.com.br',
    'VALE3.SA': 'vale.com',
    'BPAC11.SA': 'btgpactual.com',
    'ABEV3.SA': 'ambev.com.br',
    'WEGE3.SA': 'weg.net',
    'SANB11.SA': 'santander.com.br',
    #'BBDC4.SA': 'bradesco.com.br',
    'BBAS3.SA': 'bb.com.br',
    'JBSS32.SA': 'jbs.com.br',
    'AAPL':      'apple.com',
    'MSFT':      'microsoft.com',
    'GOOGL':     'google.com',
    'NVDA':      'nvidia.com',
    'AMZN':      'amazon.com',
    'TSLA':      'tesla.com',
    'META':      'meta.com',
    #'NU':        'nubank.com',
    'BTC-USD':   'bitcoin.org',
    'ETH-USD':   'ethereum.org',
    '2222.SR':   'aramco.com',
    'AMD':       'amd.com',
}

def avatar_html(symbol: str, size: int = 36) -> str:
    """Versão simplificada e robusta do Avatar."""
    domain = SYMBOL_DOMAINS.get(symbol)
    label = symbol.replace('.SA', '')
    initial = label[0].upper()

    sector = SYMBOL_SECTOR.get(symbol, 'default')
    bg_color = SECTOR_COLORS.get(sector, SECTOR_COLORS['default'])

    if not domain:
        return (
            f'<div style="width:{size}px; height:{size}px; border-radius:8px; background:{bg_color}; '
            f'display:flex; align-items:center; justify-content:center; font-size:{size//2}px; '
            f'font-weight:700; color:#c8d0e8;">{initial}</div>'
        )

    logo_url = f"https://cdn.tickerlogos.com/{domain}"
    return (
        f'<div style="width:{size}px; height:{size}px; border-radius:8px; background:white; '
        f'display:flex; align-items:center; justify-content:center; overflow:hidden; '
        f'border:0.5px solid #2a3050; position:relative;">'
        f'<span style="position:absolute; color:#ccc; font-size:10px; z-index:1;">{initial}</span>'
        f'<img src="{logo_url}" style="width:100%; height:100%; object-fit:contain; '
        f'position:relative; z-index:2; background:white;"></div>'
    )

def get_attribution() -> str:
    """Rodapé com atribuição da fonte dos logos."""
    return (
        '<div style="font-size:10px; color:#454a60; text-align:center; margin-top:50px;">'
        'Logos by <a href="https://www.allinvestview.com/tools/ticker-logos/" '
        'style="color:#454a60; text-decoration:none;">AllInvestView</a></div>'
    )

def change_span(variation: float, size: int = 12) -> str:
    cls   = 'up'   if variation >= 0 else 'down'
    arrow = '&#9650;' if variation >= 0 else '&#9660;'
    return f'<span class="{cls}" style="font-size:{size}px;">{arrow} {abs(variation):.2f}%</span>'

def fmt_price(price: float, symbol: str) -> str:
    if 'BRL' in symbol or symbol.endswith('.SA'):
        return f'R$&nbsp;{price:,.2f}'
    if symbol in ('^BVSP', '^GSPC', '^DJI'):
        return f'{price:,.0f}'
    return f'$&nbsp;{price:,.2f}'

# ─── PLOTLY ────────────────────────────────────────────────────────────────

# Passar em TODOS os st.plotly_chart() — remove toolbar e zoom por scroll
PLOTLY_CONFIG = {
    'displayModeBar': False,  # Esconde a barra flutuante de ferramentas
    'scrollZoom': False,      # Desativa o zoom pelo scroll do mouse
    'responsive': True,
    'displaylogo': False,
}

def plotly_layout(fig, margin=(0, 0, 10, 0)):
    """Tema dark transparente padronizado para todos os gráficos."""
    fig.update_layout(
        margin=dict(l=margin[0], r=margin[1], t=margin[2], b=margin[3]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_title=None,
        font=dict(color='#8090b0', size=12),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02,
            xanchor='right', x=1, font=dict(size=11),
        ),
        hoverlabel=dict(
            bgcolor='#1e2235', bordercolor='#2a2d3a',
            font=dict(color='#d0d8f0', size=12),
        ),
        dragmode='pan',       # Clicar e arrastar move no tempo, não faz zoom
    )
    fig.update_xaxes(
        showgrid=False, color='#454a60', tickfont=dict(size=11),
        fixedrange=False,     # Permite navegar no eixo do tempo
    )
    fig.update_yaxes(
        showgrid=True, gridcolor='#1a1d28', gridwidth=0.5,
        color='#454a60', tickfont=dict(size=11),
        fixedrange=True,      # Trava o eixo do preço (evita o gráfico "sumir")
    )
    return fig