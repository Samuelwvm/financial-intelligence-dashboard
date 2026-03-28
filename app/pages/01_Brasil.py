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
    fmt_price, plotly_layout, PLOTLY_CONFIG, SYMBOL_LABEL,
)

st.set_page_config(page_title="Brasil · Radar Financeiro", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


# ─── QUERIES CACHEADAS ─────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_br_stocks() -> pd.DataFrame:
    db = DatabaseManager()
    conn = db.get_connection()
    df = pd.read_sql(
        "SELECT symbol, name FROM assets_metadata WHERE category = ? ORDER BY name",
        conn, params=('Ação BR',))
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
        "SELECT date, price, variation FROM assets_history "
        "WHERE symbol = ? AND date >= date('now', ?) "
        "ORDER BY date",
        conn, params=(symbol, f'-{chart_days} days'))
    conn.close()
    return df


@st.cache_data(ttl=3600)
def get_macro_detail() -> dict:
    db   = DatabaseManager()
    conn = db.get_connection()

    # SELIC: série 11 retorna taxa diária → anualizamos (base 252)
    df_selic = pd.read_sql(
        "SELECT price FROM assets_history WHERE symbol = ? ORDER BY date DESC LIMIT 1",
        conn, params=('SELIC',))
    selic_daily  = float(df_selic['price'].iloc[0]) if not df_selic.empty else 0.0
    selic_annual = round(((1 + selic_daily / 100) ** 252 - 1) * 100, 2)

    # CDI: série 4389 já retorna taxa anual diretamente
    df_cdi = pd.read_sql(
        "SELECT price FROM assets_history WHERE symbol = ? ORDER BY date DESC LIMIT 1",
        conn, params=('CDI',))
    cdi_annual = round(float(df_cdi['price'].iloc[0]), 2) if not df_cdi.empty else 0.0

    # IPCA: último mensal + acumulado 12m por composição
    df_ipca = pd.read_sql(
        "SELECT price FROM assets_history WHERE symbol = ? ORDER BY date DESC LIMIT 12",
        conn, params=('IPCA',))
    conn.close()

    ipca_monthly = round(float(df_ipca['price'].iloc[0]), 2) if not df_ipca.empty else 0.0
    if len(df_ipca) >= 2:
        ipca_12m = round((df_ipca['price'].apply(lambda x: 1 + x / 100).prod() - 1) * 100, 2)
    else:
        ipca_12m = ipca_monthly

    return {
        'selic_annual': selic_annual,
        'selic_daily':  round(selic_daily, 4),
        'cdi_annual':   cdi_annual,
        'ipca_monthly': ipca_monthly,
        'ipca_12m':     ipca_12m,
    }


# ─── INTERFACE ─────────────────────────────────────────────────────────────

PERIOD_OPT = {'Hoje': 2, '7 dias': 7, '30 dias': 30, '90 dias': 90, '1 ano': 365}
current_period_label = st.session_state.get('global_period', '30 dias')
selected_days = PERIOD_OPT[current_period_label]

if current_period_label == 'Hoje':
    short_lbl = 'hoje'
else:
    short_lbl = current_period_label.replace(' dias', 'd').replace(' ano', 'a')

# ── Cabeçalho ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="pg-title">Mercado Brasileiro</div>'
    '<div class="pg-subtitle">Empresas listadas na B3 e indicadores macroeconômicos</div>',
    unsafe_allow_html=True,
)

# ── 1. Cards de ações ────────────────────────────────────────────────────
st.markdown(sec_header('Ações B3', 'Lista de elite', '#4caf7d'), unsafe_allow_html=True)

stocks_df = get_br_stocks()
cards = ''
for _, row in stocks_df.iterrows():
    sym        = row['symbol']
    price, var = get_latest(sym)
    ret, vol   = get_stats(sym, days=selected_days)
    label      = SYMBOL_LABEL.get(sym, sym.replace('.SA', ''))
    r_cls      = 'up' if ret >= 0 else 'down'
    r_sign     = '+' if ret >= 0 else ''
    cards += (
        f'<div class="scard">'
        f'<div class="scard-top">{avatar_html(sym)}'
        f'<div><div class="scard-name">{label}</div>'
        f'<div class="scard-sub">{row["name"]}</div></div></div>'
        f'<div style="margin-bottom:8px;">'
        f'<span style="font-size:16px;font-weight:700;color:#d0d8f0;">R$&nbsp;{price:,.2f}</span>'
        f'&nbsp;&nbsp;{change_span(var)}</div>'
        f'<div style="display:flex;gap:6px;">'
        f'<div class="sstat"><div class="sstat-label">retorno {short_lbl}</div>'
        f'<div class="sstat-val {r_cls}">{r_sign}{ret}%</div></div>'
        f'<div class="sstat"><div class="sstat-label">volatil.</div>'
        f'<div class="sstat-val" style="color:#6a7890;">{vol}%</div></div>'
        f'</div></div>'
    )
st.markdown(f'<div class="stock-grid">{cards}</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 2. Análise Individual ────────────────────────────────────────────────
st.markdown(sec_header('Análise Individual'), unsafe_allow_html=True)

name_map        = dict(zip(stocks_df['symbol'], stocks_df['name']))
col_sel, col_period = st.columns([3, 1], gap='medium')

with col_sel:
    sel_symbol = st.selectbox(
        '_', options=stocks_df['symbol'].tolist(),
        format_func=lambda s: f"{SYMBOL_LABEL.get(s, s)}  —  {name_map.get(s, '')}",
        label_visibility='collapsed',
    )
with col_period:
    period_lbl = st.selectbox(
        '_', list(PERIOD_OPT.keys()),
        key='global_period',
        label_visibility='collapsed',
    )
    days = PERIOD_OPT[period_lbl]

hist = get_history(sel_symbol, days)

if not hist.empty:
    col_chart, col_info = st.columns([3, 1], gap='medium')

    with col_chart:
        fig = px.area(hist, x='date', y='price', template='plotly_dark',
                      labels={'price': 'Preço (R$)', 'date': ''})
        fig.update_traces(
            line_color='#4caf7d', line_width=2,
            fillcolor='rgba(76,175,77,0.08)',
            hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>',
        )
        st.plotly_chart(plotly_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

    with col_info:
        price, var = get_latest(sel_symbol)
        ret, vol   = get_stats(sel_symbol, days=days)
        r_cls  = 'up' if ret >= 0 else 'down'
        r_sign = '+' if ret >= 0 else ''
        label  = SYMBOL_LABEL.get(sel_symbol, sel_symbol.replace('.SA', ''))
        st.markdown(f"""
        <div style="background:#161922;border:0.5px solid #1f2333;border-radius:10px;padding:20px;">
            <div style="font-size:10px;color:#454a60;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;">{label}</div>
            <div style="font-size:26px;font-weight:700;color:#d0d8f0;margin-bottom:5px;">R$&nbsp;{price:,.2f}</div>
            {change_span(var, size=13)}
            <hr style="border:none;border-top:0.5px solid #1f2333;margin:14px 0;">
            <div style="display:flex;gap:8px;">
                <div class="sstat"><div class="sstat-label">retorno {short_lbl}</div>
                <div class="sstat-val {r_cls}">{r_sign}{ret}%</div></div>
                <div class="sstat"><div class="sstat-label">volatil.</div>
                <div class="sstat-val" style="color:#6a7890;">{vol}%</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info('Dados históricos não disponíveis para este ativo.')

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 3. Ibovespa ──────────────────────────────────────────────────────────
st.markdown(sec_header('Ibovespa', current_period_label, '#7eb8f7'), unsafe_allow_html=True)

ibov = get_history('^BVSP', days=selected_days)
if not ibov.empty:
    fig3 = px.line(ibov, x='date', y='price', template='plotly_dark',
                   labels={'price': 'Pontos', 'date': ''})
    fig3.update_traces(
        line_color='#7eb8f7', line_width=2,
        hovertemplate='<b>%{x}</b><br>%{y:,.0f} pts<extra></extra>',
    )
    st.plotly_chart(plotly_layout(fig3), use_container_width=True, config=PLOTLY_CONFIG)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 4. Economia Brasil ───────────────────────────────────────────────────
st.markdown(sec_header('Economia Brasil', 'Dados oficiais BCB', '#7eb8f7'), unsafe_allow_html=True)

m = get_macro_detail()
eco_cards = [
    {
        'label':  'SELIC',
        'value':  f"{m['selic_annual']}%",
        'detail': f"Taxa diária: {m['selic_daily']}%",
        'desc':   'Taxa básica de juros (Meta)',
        'icon':   '&#127970;',
    },
    {
        'label':  'CDI',
        'value':  f"{m['cdi_annual']}%",
        'detail': '100% do CDI',
        'desc':   'Referência para Renda Fixa',
        'icon':   '&#128200;',
    },
    {
        'label':  'IPCA',
        'value':  f"{m['ipca_12m']}%",
        'detail': f"Mensal: {m['ipca_monthly']}%",
        'desc':   'Inflação oficial (12 meses)',
        'icon':   '&#129534;',
    },
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
st.markdown(f'<div class="eco-grid">{eco}</div>', unsafe_allow_html=True)