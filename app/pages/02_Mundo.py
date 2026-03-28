import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))
from src.database.db_manager import DatabaseManager
from src._ui import (
    CSS, sec_header, avatar_html, change_span,
    plotly_layout, PLOTLY_CONFIG, SYMBOL_LABEL,
)

st.set_page_config(page_title="Mundo · Radar Financeiro", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


# ─── QUERIES CACHEADAS ─────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_us_stocks() -> pd.DataFrame:
    db = DatabaseManager()
    conn = db.get_connection()
    df = pd.read_sql(
        "SELECT symbol, name FROM assets_metadata "
        "WHERE category IN ('Ação EUA', 'Ação Mundo') ORDER BY name",
        conn)
    conn.close()
    return df


@st.cache_data(ttl=3600)
def get_commodities_indices() -> pd.DataFrame:
    """Retorna commodities e índices disponíveis no banco."""
    db = DatabaseManager()
    conn = db.get_connection()
    df = pd.read_sql(
        "SELECT symbol, name, category FROM assets_metadata "
        "WHERE category IN ('Commodity', 'Índice') ORDER BY category, name",
        conn)
    conn.close()
    return df


@st.cache_data(ttl=3600)
def get_latest(symbol: str) -> tuple[float, float]:
    db = DatabaseManager()
    conn = db.get_connection()
    df = pd.read_sql(
        "SELECT price, variation FROM assets_history "
        "WHERE symbol = ? ORDER BY date DESC LIMIT 1",
        conn, params=(symbol,))
    conn.close()
    if df.empty:
        return 0.0, 0.0
    return float(df['price'].iloc[0]), float(df['variation'].iloc[0])


@st.cache_data(ttl=3600)
def get_stats(symbol: str, days: int = 30) -> tuple[float, float]:
    db = DatabaseManager()
    conn = db.get_connection()
    query_days = 2 if days <= 2 else days
    df = pd.read_sql(
        "SELECT price FROM assets_history WHERE symbol = ? "
        "ORDER BY date DESC LIMIT ?",
        conn, params=(symbol, query_days))
    conn.close()
    if len(df) < 2:
        return 0.0, 0.0
    ret = ((df['price'].iloc[0] / df['price'].iloc[-1]) - 1) * 100
    vol = df['price'].pct_change().std() * np.sqrt(252) * 100
    if pd.isna(vol):
        vol = 0.0
    return round(ret, 1), round(vol, 1)


@st.cache_data(ttl=3600)
def get_history(symbol: str, days: int = 30) -> pd.DataFrame:
    db = DatabaseManager()
    conn = db.get_connection()
    chart_days = 7 if days <= 2 else days
    df = pd.read_sql(
        "SELECT date, price FROM assets_history "
        "WHERE symbol = ? AND date >= date('now', ?) "
        "ORDER BY date",
        conn, params=(symbol, f'-{chart_days} days'))
    conn.close()
    return df


# ─── HELPERS ───────────────────────────────────────────────────────────────

PERIOD_OPT = {'Hoje': 2, '7 dias': 7, '30 dias': 30, '90 dias': 90, '1 ano': 365}


def _period_radio(key: str, index: int = 2) -> tuple[str, int]:
    """Seletor de período reutilizável — retorna (label, days)."""
    _, col_radio = st.columns([2.4, 1])
    with col_radio:
        lbl = st.radio(
            '_', list(PERIOD_OPT.keys()),
            horizontal=True, label_visibility='collapsed',
            key=key, index=index,
        )
    return lbl, PERIOD_OPT[lbl]


def _fmt_lbl(period_lbl: str) -> str:
    return period_lbl.lower().replace(' dias', 'd').replace(' ano', 'a')


def _info_card(symbol: str, days: int, period_lbl: str, currency: str = 'USD') -> None:
    """Card lateral padronizado com preço, retorno e volatilidade."""
    price, var = get_latest(symbol)
    ret, vol   = get_stats(symbol, days)
    r_cls      = 'up' if ret >= 0 else 'down'
    r_sign     = '+' if ret >= 0 else ''
    lbl        = SYMBOL_LABEL.get(symbol, symbol)
    lbl_period = _fmt_lbl(period_lbl)

    if currency == 'PTS':
        prefix, fmt_price = '', f'{price:,.0f}'
    elif currency == 'BRL':
        prefix, fmt_price = 'R$&nbsp;', f'{price:,.2f}'
    else:
        prefix, fmt_price = '$&nbsp;', f'{price:,.2f}'

    st.markdown(f"""
    <div style="background:#161922;border:0.5px solid #1f2333;border-radius:10px;padding:20px;">
        <div style="font-size:10px;color:#454a60;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;">{lbl}</div>
        <div style="font-size:26px;font-weight:700;color:#d0d8f0;margin-bottom:5px;">{prefix}{fmt_price}</div>
        {change_span(var, size=13)}
        <hr style="border:none;border-top:0.5px solid #1f2333;margin:14px 0;">
        <div style="display:flex;gap:8px;">
            <div class="sstat"><div class="sstat-label">retorno {lbl_period}</div>
            <div class="sstat-val {r_cls}">{r_sign}{ret}%</div></div>
            <div class="sstat"><div class="sstat-label">volatil.</div>
            <div class="sstat-val" style="color:#6a7890;">{vol}%</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── INTERFACE ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="pg-title">Mercado Global</div>'
    '<div class="pg-subtitle">Grandes empresas dos EUA, câmbio e indicadores internacionais</div>',
    unsafe_allow_html=True,
)

# ── 1. Referências Globais ───────────────────────────────────────────────
st.markdown(sec_header('Referências Globais', 'Atualizado hoje', '#4caf7d'), unsafe_allow_html=True)

REF = [
    ('^GSPC',    'S&P 500',   '500 maiores EUA',    'pts'),
    ('^DJI',     'Dow Jones', '30 gigantes EUA',    'pts'),
    ('USDBRL=X', 'Dólar',     'USD · comercial',    'brl'),
    ('EURBRL=X', 'Euro',      'EUR · zona do euro', 'brl'),
    ('GC=F',     'Ouro',      'XAU/USD',            'usd'),
]

ref_cards = ''
for sym, label, desc, kind in REF:
    price, var = get_latest(sym)
    val_str = (
        f'{price:,.0f}' if kind == 'pts'
        else f'R$&nbsp;{price:.2f}' if kind == 'brl'
        else f'$&nbsp;{price:,.2f}'
    )
    ref_cards += (
        f'<div class="mcard">'
        f'<div class="mcard-label">{label}</div>'
        f'<div class="mcard-value">{val_str}</div>'
        f'{change_span(var)}'
        f'<div class="mcard-desc">{desc}</div>'
        f'</div>'
    )
st.markdown(
    f'<div class="market-grid" style="grid-template-columns:repeat(5,1fr);">{ref_cards}</div>',
    unsafe_allow_html=True)
st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 2. Câmbio ───────────────────────────────────────────────────────────
st.markdown(sec_header('Câmbio vs Real', 'Histórico'), unsafe_allow_html=True)

period_cambio, days_cambio = _period_radio('radio_cambio', index=2)
lbl_cambio = _fmt_lbl(period_cambio)

col_usd, col_eur = st.columns(2, gap='medium')
for col, sym, name, color, fill, fmt in [
    (col_usd, 'USDBRL=X', 'Dólar (USD/BRL)', '#4caf7d', 'rgba(76,175,77,0.07)',  'R$ %{y:.4f}'),
    (col_eur, 'EURBRL=X', 'Euro (EUR/BRL)',  '#7eb8f7', 'rgba(94,142,240,0.07)', 'R$ %{y:.4f}'),
]:
    hist   = get_history(sym, days_cambio)
    p, _   = get_latest(sym)
    ret, _ = get_stats(sym, days_cambio)
    r_cls  = 'up' if ret >= 0 else 'down'
    r_sign = '+' if ret >= 0 else ''

    with col:
        st.markdown(
            f'<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:10px;">'
            f'<span style="font-size:13px;font-weight:700;color:#b0b8d8;">{name}</span>'
            f'<span style="font-size:12px;color:#6a7890;">'
            f'R$&nbsp;<strong style="color:#d0d8f0;font-size:17px;">{p:.2f}</strong>'
            f'&nbsp;&nbsp;<span class="{r_cls}">{r_sign}{ret}% ({lbl_cambio})</span></span></div>',
            unsafe_allow_html=True,
        )
        if not hist.empty:
            fig = px.area(hist, x='date', y='price', template='plotly_dark',
                          labels={'price': 'R$', 'date': ''})
            fig.update_traces(
                line_color=color, line_width=2, fillcolor=fill,
                hovertemplate=f'<b>%{{x}}</b><br>{fmt}<extra></extra>')
            st.plotly_chart(
                plotly_layout(fig, margin=(0, 0, 0, 0)),
                use_container_width=True, config=PLOTLY_CONFIG)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 3. Ações Globais — seletor de tempo independente ────────────────────
st.markdown(sec_header('Ações Globais', 'EUA · Mundo'), unsafe_allow_html=True)

period_acoes, days_acoes = _period_radio('radio_acoes', index=2)
lbl_acoes = _fmt_lbl(period_acoes)

stocks_df = get_us_stocks()
name_map  = dict(zip(stocks_df['symbol'], stocks_df['name']))
cards = ''

for _, row in stocks_df.iterrows():
    sym        = row['symbol']
    price, var = get_latest(sym)
    ret, vol   = get_stats(sym, days_acoes)
    label      = SYMBOL_LABEL.get(sym, sym)
    r_cls      = 'up' if ret >= 0 else 'down'
    r_sign     = '+' if ret >= 0 else ''

    cards += (
        f'<div class="scard">'
        f'<div class="scard-top">{avatar_html(sym)}'
        f'<div><div class="scard-name">{label}</div>'
        f'<div class="scard-sub">{row["name"]}</div></div></div>'
        f'<div style="margin-bottom:8px; font-size:16px; font-weight:700; color:#d0d8f0;">'
        f'$&nbsp;{price:,.2f}&nbsp;&nbsp;{change_span(var)}</div>'
        f'<div style="display:flex;gap:7px;">'
        f'<div class="sstat"><div class="sstat-label">retorno {lbl_acoes}</div>'
        f'<div class="sstat-val {r_cls}">{r_sign}{ret}%</div></div>'
        f'<div class="sstat"><div class="sstat-label">volatil.</div>'
        f'<div class="sstat-val" style="color:#6a7890;">{vol}%</div></div>'
        f'</div></div>'
    )
st.markdown(f'<div class="stock-grid">{cards}</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 4. Análise Individual · Ações ────────────────────────────────────────
st.markdown(sec_header('Análise Individual · Ações'), unsafe_allow_html=True)

col_sel, col_period = st.columns([3, 1], gap='medium')
with col_sel:
    sel_stock = st.selectbox(
        '_', options=stocks_df['symbol'].tolist(),
        format_func=lambda s: f"{SYMBOL_LABEL.get(s, s)}  —  {name_map.get(s, '')}",
        label_visibility='collapsed', key='sel_stock',
    )
with col_period:
    period_stock = st.selectbox(
        '_', list(PERIOD_OPT.keys()), index=2,
        label_visibility='collapsed', key='period_stock',
    )
    days_stock = PERIOD_OPT[period_stock]

hist_stock = get_history(sel_stock, days_stock)
if not hist_stock.empty:
    col_chart, col_info = st.columns([3, 1], gap='medium')
    with col_chart:
        fig = px.area(hist_stock, x='date', y='price', template='plotly_dark',
                      labels={'price': 'Preço (USD)', 'date': ''})
        fig.update_traces(
            line_color='#7eb8f7', line_width=2,
            fillcolor='rgba(94,142,240,0.08)',
            hovertemplate='<b>%{x}</b><br>$ %{y:,.2f}<extra></extra>')
        st.plotly_chart(plotly_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)
    with col_info:
        _info_card(sel_stock, days_stock, period_stock, currency='USD')
else:
    st.info('Dados históricos não disponíveis para este ativo.')

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 5. Análise Individual · Commodities & Índices ────────────────────────
st.markdown(sec_header('Análise Individual · Commodities & Índices', dot_color='#e0b84c'), unsafe_allow_html=True)

comm_df       = get_commodities_indices()
comm_name_map = dict(zip(comm_df['symbol'], comm_df['name']))
comm_cat_map  = dict(zip(comm_df['symbol'], comm_df['category']))


def _comm_label(s: str) -> str:
    cat  = comm_cat_map.get(s, '')
    name = comm_name_map.get(s, s)
    return f"{name}  ·  {cat}"


col_sel2, col_period2 = st.columns([3, 1], gap='medium')
with col_sel2:
    sel_comm = st.selectbox(
        '_', options=comm_df['symbol'].tolist(),
        format_func=_comm_label,
        label_visibility='collapsed', key='sel_comm',
    )
with col_period2:
    period_comm = st.selectbox(
        '_', list(PERIOD_OPT.keys()), index=2,
        label_visibility='collapsed', key='period_comm',
    )
    days_comm = PERIOD_OPT[period_comm]

# Cor e formato adaptados ao tipo de ativo (Índice vs Commodity)
is_index    = comm_cat_map.get(sel_comm, '') == 'Índice'
chart_color = '#7eb8f7' if is_index else '#e0b84c'
chart_fill  = 'rgba(94,142,240,0.08)' if is_index else 'rgba(224,184,76,0.08)'
hover_fmt   = '%{y:,.0f} pts' if is_index else '$ %{y:,.2f}'
price_label = 'Pontos' if is_index else 'USD'
currency    = 'PTS' if is_index else 'USD'

hist_comm = get_history(sel_comm, days_comm)
if not hist_comm.empty:
    col_chart2, col_info2 = st.columns([3, 1], gap='medium')
    with col_chart2:
        fig2 = px.area(hist_comm, x='date', y='price', template='plotly_dark',
                       labels={'price': price_label, 'date': ''})
        fig2.update_traces(
            line_color=chart_color, line_width=2,
            fillcolor=chart_fill,
            hovertemplate=f'<b>%{{x}}</b><br>{hover_fmt}<extra></extra>')
        st.plotly_chart(plotly_layout(fig2), use_container_width=True, config=PLOTLY_CONFIG)
    with col_info2:
        _info_card(sel_comm, days_comm, period_comm, currency=currency)
else:
    st.info('Dados históricos não disponíveis para este ativo.')