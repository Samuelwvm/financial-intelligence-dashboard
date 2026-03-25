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


class MundoDashboard:
    def __init__(self):
        self.db = DatabaseManager()

    def get_us_stocks(self) -> pd.DataFrame:
        conn = self.db.get_connection()
        df = pd.read_sql(
            "SELECT symbol, name FROM assets_metadata "
            "WHERE category IN ('Ação EUA', 'Ação Mundo') ORDER BY name", conn)
        conn.close()
        return df

    def get_latest(self, symbol: str) -> tuple[float, float]:
        conn = self.db.get_connection()
        df = pd.read_sql(
            "SELECT price, variation FROM assets_history "
            f"WHERE symbol = '{symbol}' ORDER BY date DESC LIMIT 1", conn)
        conn.close()
        if df.empty:
            return 0.0, 0.0
        return float(df['price'].iloc[0]), float(df['variation'].iloc[0])

    def get_stats(self, symbol: str) -> tuple[float, float]:
        conn = self.db.get_connection()
        df = pd.read_sql(
            f"SELECT price FROM assets_history WHERE symbol = '{symbol}' "
            "ORDER BY date DESC LIMIT 30", conn)
        conn.close()
        if len(df) < 2:
            return 0.0, 0.0
        ret = ((df['price'].iloc[0] / df['price'].iloc[-1]) - 1) * 100
        vol = df['price'].pct_change().std() * np.sqrt(252) * 100
        return round(ret, 1), round(vol, 1)

    def get_history(self, symbol: str, days: int = 30) -> pd.DataFrame:
        conn = self.db.get_connection()
        df = pd.read_sql(
            f"SELECT date, price FROM assets_history "
            f"WHERE symbol = '{symbol}' AND date >= date('now','-{days} days') "
            "ORDER BY date", conn)
        conn.close()
        return df


dash = MundoDashboard()

# ── Cabeçalho ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="pg-title">Mercado Global</div>'
    '<div class="pg-subtitle">Grandes empresas dos EUA, câmbio e indicadores internacionais</div>',
    unsafe_allow_html=True,
)

# ── 1. Referências Globais ───────────────────────────────────────────────
st.markdown(sec_header('Referências Globais', 'atualizado agora', '#4caf7d'), unsafe_allow_html=True)

REF = [
    ('^GSPC',    'S&P 500',   '500 maiores EUA',    'pts'),
    ('^DJI',     'Dow Jones', '30 gigantes EUA',    'pts'),
    ('USDBRL=X', 'Dólar',     'USD · comercial',    'brl'),
    ('EURBRL=X', 'Euro',      'EUR · zona do euro', 'brl'),
    ('GC=F',     'Ouro',      'XAU/USD',            'usd'),
]

ref_cards = ''
for sym, label, desc, kind in REF:
    price, var = dash.get_latest(sym)
    if kind == 'pts':
        val_str = f'{price:,.0f}'
    elif kind == 'brl':
        val_str = f'R$&nbsp;{price:.2f}'
    else:
        val_str = f'$&nbsp;{price:,.2f}'
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
    unsafe_allow_html=True,
)
st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 2. Câmbio — histórico Dólar e Euro ──────────────────────────────────
st.markdown(sec_header('Câmbio vs Real', 'histórico'), unsafe_allow_html=True)

period_opt_cambio = {'30 dias': 30, '90 dias': 90, '1 ano': 365}
period_cambio = st.radio(
    '_', list(period_opt_cambio.keys()),
    horizontal=True, label_visibility='collapsed', key='radio_cambio', index=1,
)
days_cambio = period_opt_cambio[period_cambio]

col_usd, col_eur = st.columns(2, gap='medium')

for col, sym, name, color, fill, fmt in [
    (col_usd, 'USDBRL=X', 'Dólar (USD/BRL)', '#4caf7d', 'rgba(76,175,77,0.07)',  'R$ %{y:.4f}'),
    (col_eur, 'EURBRL=X', 'Euro (EUR/BRL)',  '#7eb8f7', 'rgba(94,142,240,0.07)', 'R$ %{y:.4f}'),
]:
    hist  = dash.get_history(sym, days_cambio)
    p, v  = dash.get_latest(sym)
    ret, _ = dash.get_stats(sym)
    r_cls  = 'up' if ret >= 0 else 'down'
    r_sign = '+' if ret >= 0 else ''

    with col:
        st.markdown(
            f'<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:10px;">'
            f'<span style="font-size:13px;font-weight:700;color:#b0b8d8;">{name}</span>'
            f'<span style="font-size:12px;color:#6a7890;">'
            f'R$&nbsp;<strong style="color:#d0d8f0;font-size:17px;">{p:.2f}</strong>'
            f'&nbsp;&nbsp;<span class="{r_cls}">{r_sign}{ret}%</span></span></div>',
            unsafe_allow_html=True,
        )
        if not hist.empty:
            fig = px.area(hist, x='date', y='price', template='plotly_dark',
                          labels={'price': 'R$', 'date': ''})
            fig.update_traces(
                line_color=color, line_width=2, fillcolor=fill,
                hovertemplate=f'<b>%{{x}}</b><br>{fmt}<extra></extra>',
            )
            st.plotly_chart(plotly_layout(fig, margin=(0, 0, 0, 0)),
                            use_container_width=True, config=PLOTLY_CONFIG)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 3. Cards de ações EUA e Mundo ───────────────────────────────────────
st.markdown(sec_header('Ações Globais', 'EUA · Mundo'), unsafe_allow_html=True)

stocks_df = dash.get_us_stocks()
name_map  = dict(zip(stocks_df['symbol'], stocks_df['name']))

cards = ''
for _, row in stocks_df.iterrows():
    sym        = row['symbol']
    price, var = dash.get_latest(sym)
    ret, vol   = dash.get_stats(sym)
    label      = SYMBOL_LABEL.get(sym, sym)
    r_cls      = 'up' if ret >= 0 else 'down'
    r_sign     = '+' if ret >= 0 else ''
    cards += (
        f'<div class="scard">'
        f'<div class="scard-top">{avatar_html(sym)}'
        f'<div><div class="scard-name">{label}</div>'
        f'<div class="scard-sub">{row["name"]}</div></div></div>'
        f'<div style="margin-bottom:8px;">'
        f'<span style="font-size:16px;font-weight:700;color:#d0d8f0;">$&nbsp;{price:,.2f}</span>'
        f'&nbsp;&nbsp;{change_span(var)}</div>'
        f'<div style="display:flex;gap:6px;">'
        f'<div class="sstat"><div class="sstat-label">retorno 30d</div>'
        f'<div class="sstat-val {r_cls}">{r_sign}{ret}%</div></div>'
        f'<div class="sstat"><div class="sstat-label">volatil.</div>'
        f'<div class="sstat-val" style="color:#6a7890;">{vol}%</div></div>'
        f'</div></div>'
    )
st.markdown(f'<div class="stock-grid">{cards}</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 4. Análise Individual ────────────────────────────────────────────────
st.markdown(sec_header('Análise Individual'), unsafe_allow_html=True)

col_sel, col_period = st.columns([3, 1], gap='medium')
with col_sel:
    sel_symbol = st.selectbox(
        '_', options=stocks_df['symbol'].tolist(),
        format_func=lambda s: f"{SYMBOL_LABEL.get(s, s)}  —  {name_map.get(s, '')}",
        label_visibility='collapsed',
    )
with col_period:
    period_opt = {'30 dias': 30, '90 dias': 90, '1 ano': 365}
    period_lbl = st.selectbox('_', list(period_opt.keys()),
                              label_visibility='collapsed', key='period_mundo')
    days = period_opt[period_lbl]

hist = dash.get_history(sel_symbol, days)
if not hist.empty:
    col_chart, col_info = st.columns([3, 1], gap='medium')
    with col_chart:
        fig = px.area(hist, x='date', y='price', template='plotly_dark',
                      labels={'price': 'Preço (USD)', 'date': ''})
        fig.update_traces(
            line_color='#7eb8f7', line_width=2,
            fillcolor='rgba(94,142,240,0.08)',
            hovertemplate='<b>%{x}</b><br>$ %{y:,.2f}<extra></extra>',
        )
        st.plotly_chart(plotly_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

    with col_info:
        price, var = dash.get_latest(sel_symbol)
        ret, vol   = dash.get_stats(sel_symbol)
        r_cls  = 'up' if ret >= 0 else 'down'
        r_sign = '+' if ret >= 0 else ''
        label  = SYMBOL_LABEL.get(sel_symbol, sel_symbol)
        st.markdown(f"""
        <div style="background:#161922;border:0.5px solid #1f2333;border-radius:10px;padding:20px;">
            <div style="font-size:10px;color:#454a60;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;">{label}</div>
            <div style="font-size:26px;font-weight:700;color:#d0d8f0;margin-bottom:5px;">$&nbsp;{price:,.2f}</div>
            {change_span(var, size=13)}
            <hr style="border:none;border-top:0.5px solid #1f2333;margin:14px 0;">
            <div style="display:flex;gap:8px;">
                <div class="sstat"><div class="sstat-label">retorno {period_lbl[:6]}</div>
                <div class="sstat-val {r_cls}">{r_sign}{ret}%</div></div>
                <div class="sstat"><div class="sstat-label">volatil.</div>
                <div class="sstat-val" style="color:#6a7890;">{vol}%</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info('Dados históricos não disponíveis.')