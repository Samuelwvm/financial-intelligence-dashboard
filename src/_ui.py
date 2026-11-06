# src/_ui.py
# Tudo que é compartilhado entre as páginas fica aqui:
# paleta de cores, dicionários de lookup, CSS global e helpers de renderização.

# ─── PALETA E LOOKUP DE ATIVOS ─────────────────────────────────────────────

# Cor de fundo do avatar quando não tem logo na CDN (fallback com inicial).
# Cada setor tem um tom diferente para dar identidade visual nos cards.
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

# Mapeia símbolo → setor para alimentar SECTOR_COLORS no avatar_html().
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

# Nome de exibição de cada ativo — usado nos cards, gráficos e selectboxes.
# Centralizado aqui para não precisar corrigir em múltiplos lugares.
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

# ─── OPÇÕES DE PERÍODO ─────────────────────────────────────────────────────

# Centralizado aqui para que todas as páginas usem os mesmos valores e labels.
# O valor 2 para "Último dia" existe porque o banco sempre tem D-1;
# pedir apenas 1 dia volta vazio quando o mercado está fechado.
PERIOD_OPT = {'Último dia': 2, '7 dias': 7, '30 dias': 30, '90 dias': 90, '1 ano': 365}

# ─── CSS GLOBAL ────────────────────────────────────────────────────────────

# Injetado uma única vez no Home.py via st.markdown(CSS).
# As páginas filhas herdam automaticamente — não precisam importar.
CSS = """
<style>
.main .block-container {
    padding-top: 2rem;
    max-width: 100%;
}

/* Esconde os elementos padrão do Streamlit que não quero mostrar */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* ── Título e subtítulo de cada página ── */
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

/* ── Cabeçalho de seção (título + badge opcional) ── */
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

/* ── Grid de cards do Pulso do Mercado (5 colunas fixas) ── */
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

/* ── Grid de cards de ativos (auto-fill, mínimo 200px por card) ── */
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

/* ── Mini-stat dentro dos cards (retorno / volatilidade) ── */
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

/* ── Cards de economia (SELIC / CDI / IPCA) ── */
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

/* ── Classes semânticas de alta/queda usadas em change_span() ── */
.up   { color: #4caf7d !important; font-weight: 600 !important; }
.down { color: #e05a5a !important; font-weight: 600 !important; }

/* ── Divisor entre seções ── */
.divider { border: none; border-top: 0.5px solid #191c28; margin: 30px 0; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
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

/* ── Esconde os labels dos inputs (uso label='_' + label_visibility='collapsed') ── */
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

/* ── Expander — seletores válidos a partir do Streamlit 1.30 ── */
div[data-testid="stExpander"] {
    background: #161922 !important;
    border: 0.5px solid #1f2333 !important;
    border-radius: 10px !important;
    overflow: hidden;
    margin-bottom: 6px !important;
}
div[data-testid="stExpander"] details > summary {
    padding: 14px 18px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #b0b8d8 !important;
    list-style: none;
    cursor: pointer;
}
div[data-testid="stExpander"] details > summary::-webkit-details-marker {
    display: none;
}
div[data-testid="stExpander"] details > summary::after {
    content: '+';
    float: right;
    color: #454a60;
    font-size: 18px;
    font-weight: 300;
    line-height: 1;
}
div[data-testid="stExpander"] details[open] > summary::after {
    content: '−';
}
div[data-testid="stExpander"] details > div {
    padding: 4px 18px 16px !important;
    border-top: 0.5px solid #1a1d28;
}

/* ── Rodapé personalizado ── */
.block-container {
    padding-bottom: 2rem !important;
}
.page-footer {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 0.5px solid #191c28;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    text-align: center;
}
.footer-update {
    font-size: 11px !important;
    color: #4caf7d !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px;
}
.footer-disclaimer {
    font-size: 11px !important;
    color: #3a3f55 !important;
    line-height: 1.6;
    max-width: 720px;
}
.footer-attribution {
    font-size: 10px !important;
    color: #2a2f45 !important;
}
.footer-attribution a {
    color: #2a2f45 !important;
    text-decoration: none !important;
}

/* ═══════════════════════════════════════════════════════════════
   RESPONSIVIDADE
   768px → tablet  (2–3 colunas)
   480px → celular (1–2 colunas)
   ═══════════════════════════════════════════════════════════════ */

/* ── Tablet (≤ 768px) ── */
@media (max-width: 768px) {

    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1.25rem !important;
    }

    .pg-title   { font-size: 24px !important; }
    .pg-subtitle { font-size: 13px !important; margin-bottom: 20px !important; }

    .market-grid { grid-template-columns: repeat(3, 1fr) !important; }
    .mcard-value { font-size: 18px !important; }

    .eco-grid { grid-template-columns: repeat(2, 1fr) !important; }
    .eco-icon { display: none !important; } /* ocupa espaço desnecessário em telas pequenas */

    .cripto-grid { grid-template-columns: 1fr !important; }
    .sec-badge   { display: none !important; }
}

/* ── Celular (≤ 480px) ── */
@media (max-width: 480px) {

    .main .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    .pg-title    { font-size: 20px !important; }
    .market-grid { grid-template-columns: repeat(2, 1fr) !important; }

    .mcard       { padding: 14px 12px !important; }
    .mcard-value { font-size: 16px !important; }
    .mcard-desc  { display: none !important; } /* descrição some para não poluir o card */

    .stock-grid  { grid-template-columns: 1fr !important; }
    .eco-grid    { grid-template-columns: 1fr !important; }
    .eco-card    { padding: 14px 16px !important; }
    .eco-value   { font-size: 22px !important; }

    .sec-title   { font-size: 13px !important; letter-spacing: 1px; }

    div[data-testid="stExpander"] details > summary {
        padding: 12px 14px !important;
        font-size: 13px !important;
    }
    div[data-testid="stExpander"] details > div {
        padding: 4px 14px 14px !important;
    }
}
</style>
"""

# ─── HELPERS DE RENDERIZAÇÃO ───────────────────────────────────────────────

def _dot(color: str = '#5b8ef0') -> str:
    """SVG do ponto colorido que aparece antes do título de cada seção."""
    return (
        f'<svg width="8" height="8" viewBox="0 0 8 8" style="flex-shrink:0;">'
        f'<circle cx="4" cy="4" r="3" fill="{color}" opacity=".3"/>'
        f'<circle cx="4" cy="4" r="1.6" fill="{color}"/></svg>'
    )

def sec_header(title: str, badge: str = '', dot_color: str = '#5b8ef0') -> str:
    """Cabeçalho de seção com ponto colorido e badge opcional à direita."""
    badge_html = f'<div class="sec-badge">{badge}</div>' if badge else ''
    return (
        f'<div class="sec-wrap">'
        f'<div class="sec-title">{_dot(dot_color)}{title}</div>'
        f'{badge_html}</div>'
    )

def change_span(variation: float, size: int = 12) -> str:
    """Seta + variação percentual com cor semântica (up/down).
    Converte ponto para vírgula para seguir o padrão brasileiro."""
    cls    = 'up'      if variation >= 0 else 'down'
    arrow  = '&#9650;' if variation >= 0 else '&#9660;'
    val_br = f"{abs(variation):.2f}".replace(".", ",")
    return f'<span class="{cls}" style="font-size:{size}px;">{arrow} {val_br}%</span>'

def fmt_price(price: float, symbol: str) -> str:
    """Formata o preço conforme a moeda/tipo do ativo.

    BRL (.SA ou *BRL* no símbolo): padrão brasileiro — vírgula como decimal,
        ponto como milhar. O replace encadeado (→ X → , → .) evita colisão
        entre os dois separadores durante a conversão.
    ^BVSP: pontos sem casas decimais, milhar com ponto (ex: 134.521).
    ^GSPC / ^DJI: inteiros com vírgula americana (ex: $5,432).
    Demais: dólar com duas casas decimais.
    """
    if 'BRL' in symbol or symbol.endswith('.SA'):
        br_format = f"{price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f'R$&nbsp;{br_format}'

    if symbol == '^BVSP':
        return f"{price:,.0f}".replace(",", ".")

    if symbol in ('^GSPC', '^DJI'):
        return f"${price:,.0f}"

    return f'$&nbsp;{price:,.2f}'

# ─── LOGOS ─────────────────────────────────────────────────────────────────

# CDN gratuita que serve logos pelo domínio da empresa.
# Exige atribuição no rodapé — por isso o get_attribution() é obrigatório.
SYMBOL_DOMAINS = {
    'ITUB4.SA': 'itau.com.br',
    'PETR4.SA': 'petrobras.com.br',
    'VALE3.SA': 'vale.com',
    'BPAC11.SA': 'btgpactual.com',
    'ABEV3.SA': 'ambev.com.br',
    'WEGE3.SA': 'weg.net',
    'SANB11.SA': 'santander.com.br',
    #'BBDC4.SA': 'bradesco.com.br',  # retorna 404 na CDN — usando fallback com inicial
    'BBAS3.SA': 'bb.com.br',
    'JBSS32.SA': 'jbs.com.br',
    'AAPL':      'apple.com',
    'MSFT':      'microsoft.com',
    'GOOGL':     'google.com',
    'NVDA':      'nvidia.com',
    'AMZN':      'amazon.com',
    'TSLA':      'tesla.com',
    'META':      'meta.com',
    #'NU':        'nubank.com',       # retorna 404 na CDN — usando fallback com inicial
    'BTC-USD':   'bitcoin.org',
    'ETH-USD':   'ethereum.org',
    '2222.SR':   'aramco.com',
    'AMD':       'amd.com',
}

def avatar_html(symbol: str, size: int = 36) -> str:
    """Gera o avatar do ativo.

    Com domínio mapeado → logo da CDN sobre fundo branco.
    Sem domínio → quadrado colorido com a inicial do ticker (cor do setor).

    O onerror do JavaScript não funciona dentro do st.markdown() porque o
    Streamlit roda num iframe sandboxado — não tem como detectar 404 em tempo
    de execução. Por isso domínios problemáticos ficam comentados aqui.
    """
    domain   = SYMBOL_DOMAINS.get(symbol)
    label    = symbol.replace('.SA', '')
    initial  = label[0].upper()
    sector   = SYMBOL_SECTOR.get(symbol, 'default')
    bg_color = SECTOR_COLORS.get(sector, SECTOR_COLORS['default'])

    if not domain:
        return (
            f'<div style="width:{size}px; height:{size}px; border-radius:8px; '
            f'background:{bg_color}; display:flex; align-items:center; '
            f'justify-content:center; font-size:{size//2}px; '
            f'font-weight:700; color:#c8d0e8;">{initial}</div>'
        )

    logo_url = f"https://cdn.tickerlogos.com/{domain}"
    return (
        f'<div style="width:{size}px; height:{size}px; border-radius:8px; '
        f'background:white; display:flex; align-items:center; '
        f'justify-content:center; overflow:hidden; border:0.5px solid #2a3050;">'
        f'<img src="{logo_url}" alt="{initial}" '
        f'style="width:100%; height:100%; object-fit:contain;">'
        f'</div>'
    )

def get_attribution() -> str:
    """Atribuição obrigatória pelos termos de uso da CDN de logos."""
    return (
        '<div class="footer-attribution" style="margin-top:0px;">'
        'Logos by <a href="https://www.allinvestview.com/tools/ticker-logos/">AllInvestView</a>'
        '</div>'
    )

def page_footer() -> str:
    """Rodapé padrão — chamado na última linha de cada página."""
    return f"""
    <div class="page-footer">
        <div class="footer-update">
            🕐 Dados atualizados diariamente após o fechamento dos mercados (D-1)
        </div>
        <div class="footer-disclaimer">
            ⚠️ Os cálculos são automáticos, baseados em dados públicos
            (Yahoo Finance / Banco Central do Brasil), e não representam análise
            de valores mobiliários ou recomendação de investimento.
            Rentabilidade passada não é garantia de retorno futuro.
        </div>
        {get_attribution()}
    </div>
    """

def render_eco_cards(m: dict) -> str:
    """Renderiza os cards de SELIC, CDI e IPCA.
    Reutilizado em Home e Brasil — qualquer mudança de layout vale para os dois."""
    eco_cards = [
        {'label': 'SELIC', 'value': f"{m['selic_annual']}%", 'detail': f"Taxa diária: {m['selic_daily']}%",
         'desc': 'Taxa básica de juros (Meta)', 'icon': '&#127970;'},
        {'label': 'CDI',   'value': f"{m['cdi_annual']}%",   'detail': '100% do CDI',
         'desc': 'Referência para Renda Fixa',  'icon': '&#128200;'},
        {'label': 'IPCA',  'value': f"{m['ipca_12m']}%",     'detail': f"Mensal: {m['ipca_monthly']}%",
         'desc': 'Inflação oficial (12 meses)', 'icon': '&#129534;'},
    ]
    eco = ''
    for c in eco_cards:
        eco += (
            f'<div class="eco-card"><div>'
            f'<div class="eco-label">{c["label"]}</div>'
            f'<div class="eco-value" style="font-size:28px !important;">{c["value"]} '
            f'<span style="font-size:13px;color:#4a6080;font-weight:500;">a.a.</span></div>'
            f'<div style="font-size:11px;color:#5b7fa6;margin:4px 0 6px;font-weight:500;">{c["detail"]}</div>'
            f'<div class="eco-desc">{c["desc"]}</div>'
            f'</div><div class="eco-icon">{c["icon"]}</div></div>'
        )
    return f'<div class="eco-grid">{eco}</div>'

# ─── PLOTLY ────────────────────────────────────────────────────────────────

# Desabilito a toolbar do Plotly — no contexto de dashboard financeiro ela só
# atrapalha; o usuário não precisa exportar PNG nem fazer zoom livre.
PLOTLY_CONFIG = {
    'displayModeBar': False,
    'scrollZoom': False,
    'responsive': True,
    'displaylogo': False,
}

def plotly_layout(fig, margin=(0, 0, 10, 0)):
    """Aplica o tema dark transparente padrão em qualquer figura Plotly.
    fixedrange=True nos eixos impede zoom acidental no mobile."""
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
        dragmode='pan',
    )
    fig.update_xaxes(
        showgrid=False, color='#454a60', tickfont=dict(size=11),
        fixedrange=True,
    )
    fig.update_yaxes(
        showgrid=True, gridcolor='#1a1d28', gridwidth=0.5,
        color='#454a60', tickfont=dict(size=11),
        fixedrange=True,
    )
    return fig