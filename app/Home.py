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

st.set_page_config(page_title="Radar Financeiro", page_icon="📡", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


class HomeDashboard:
    def __init__(self):
        self.db = DatabaseManager()

    def get_latest(self, symbol):
        conn = self.db.get_connection()
        df = pd.read_sql(
            "SELECT price, variation FROM assets_history "
            f"WHERE symbol = '{symbol}' ORDER BY date DESC LIMIT 1", conn)
        conn.close()
        if df.empty:
            return 0.0, 0.0
        return float(df['price'].iloc[0]), float(df['variation'].iloc[0])

    def get_stats(self, symbol, days=30):
        conn = self.db.get_connection()
        df = pd.read_sql(
            f"SELECT price FROM assets_history WHERE symbol = '{symbol}' "
            f"ORDER BY date DESC LIMIT {days}", conn)
        conn.close()
        if len(df) < 2:
            return 0.0, 0.0
        ret = ((df['price'].iloc[0] / df['price'].iloc[-1]) - 1) * 100
        vol = df['price'].pct_change().std() * np.sqrt(252) * 100
        return round(ret, 1), round(vol, 1)

    def get_portfolio_history(self, symbols, days=30):
        if not symbols:
            return pd.DataFrame()
        conn = self.db.get_connection()
        syms = "','".join(symbols)
        df = pd.read_sql(
            f"SELECT date, symbol, price FROM assets_history "
            f"WHERE symbol IN ('{syms}') AND date >= date('now','-{days} days') "
            "ORDER BY date", conn)
        conn.close()
        return df

    def get_elite_assets(self):
        elite = [
            'ITUB4.SA','PETR4.SA','VALE3.SA','BPAC11.SA',
            'ABEV3.SA','WEGE3.SA','BBDC4.SA','BBAS3.SA','SANB11.SA',
            'AAPL','GOOGL','MSFT','AMZN','NVDA','TSLA','META','NU',
            '2222.SR','BTC-USD','ETH-USD',
        ]
        conn = self.db.get_connection()
        syms = "','".join(elite)
        df = pd.read_sql(
            f"SELECT symbol, name FROM assets_metadata WHERE symbol IN ('{syms}')", conn)
        conn.close()
        df['_order'] = df['symbol'].map({s: i for i, s in enumerate(elite)})
        return df.sort_values('_order').drop(columns='_order').reset_index(drop=True)


dash = HomeDashboard()

# Cabeçalho
st.markdown(
    '<div class="pg-title">Radar Financeiro</div>'
    '<div class="pg-subtitle">Painel &nbsp;·&nbsp; visão consolidada do mercado global</div>',
    unsafe_allow_html=True,
)

# 1. PULSO DO MERCADO
st.markdown(sec_header('Pulso do Mercado', 'atualizado agora', '#4caf7d'), unsafe_allow_html=True)
PULSO = [
    ('IBOVESPA',  '^BVSP',    'índice Brasil'),
    ('DOW JONES', '^DJI',     '30 gigantes EUA'),
    ('S&P 500',   '^GSPC',    '500 maiores EUA'),
    ('DOLAR',     'USDBRL=X', 'comercial'),
    ('EURO',      'EURBRL=X', 'zona do euro'),
]
cards = ''
for label, sym, desc in PULSO:
    price, var = dash.get_latest(sym)
    cards += (
        f'<div class="mcard"><div class="mcard-label">{label}</div>'
        f'<div class="mcard-value">{fmt_price(price, sym)}</div>'
        f'{change_span(var)}<div class="mcard-desc">{desc}</div></div>'
    )
st.markdown(f'<div class="market-grid">{cards}</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# 2. MEUS ATIVOS
st.markdown(sec_header('Meus Ativos'), unsafe_allow_html=True)
elite_df = dash.get_elite_assets()
name_map = dict(zip(elite_df['symbol'], elite_df['name']))
defaults = elite_df['symbol'].head(6).tolist()

selected = st.multiselect(
    label='_',
    options=elite_df['symbol'].tolist(),
    default=defaults,
    format_func=lambda s: f"{SYMBOL_LABEL.get(s, s)}  --  {name_map.get(s, '')}",
    placeholder='Adicionar ativo...',
    label_visibility='collapsed',
)

if selected:
    PERIOD_OPT = {'7 dias': 7, '30 dias': 30, '90 dias': 90, '1 ano': 365}
    _, col_radio = st.columns([3, 1])
    with col_radio:
        period_lbl = st.radio(
            '_', list(PERIOD_OPT.keys()), index=1,
            horizontal=True, label_visibility='collapsed', key='home_period',
        )
    days = PERIOD_OPT[period_lbl]

    cards = ''
    for sym in selected:
        price, _ = dash.get_latest(sym)
        ret, vol = dash.get_stats(sym, days)
        label    = SYMBOL_LABEL.get(sym, sym.replace('.SA', ''))
        name     = name_map.get(sym, label)
        r_cls    = 'up' if ret >= 0 else 'down'
        r_sign   = '+' if ret >= 0 else ''
        cards += (
            f'<div class="scard"><div class="scard-top">{avatar_html(sym)}'
            f'<div><div class="scard-name">{label}</div>'
            f'<div class="scard-sub">{name}</div></div></div>'
            f'<div style="display:flex;gap:7px;">'
            f'<div class="sstat"><div class="sstat-label">retorno {period_lbl}</div>'
            f'<div class="sstat-val {r_cls}">{r_sign}{ret}%</div></div>'
            f'<div class="sstat"><div class="sstat-label">volatil.</div>'
            f'<div class="sstat-val" style="color:#6a7890;">{vol}%</div></div>'
            f'</div></div>'
        )
    st.markdown(f'<div class="stock-grid">{cards}</div>', unsafe_allow_html=True)

    # 3. GRAFICOS
    st.markdown('<hr class="divider"/>', unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2], gap='medium')

    with col_l:
        st.markdown(sec_header('Desempenho Relativo', f'base 100 - {period_lbl}'), unsafe_allow_html=True)
        hist = dash.get_portfolio_history(selected, days)
        if not hist.empty:
            hist['base_100'] = hist.groupby('symbol')['price'].transform(
                lambda x: (x / x.iloc[0]) * 100)
            hist['ativo'] = hist['symbol'].map(lambda s: SYMBOL_LABEL.get(s, s))
            fig = px.line(hist, x='date', y='base_100', color='ativo',
                          template='plotly_dark',
                          labels={'base_100': 'retorno (%)', 'date': '', 'ativo': ''})
            fig.update_traces(
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Retorno: %{y:.1f}%<extra></extra>')
            st.plotly_chart(plotly_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

    with col_r:
        st.markdown(sec_header('Risco vs Retorno', period_lbl), unsafe_allow_html=True)
        rows = [{'ativo': SYMBOL_LABEL.get(s, s),
                 'retorno': dash.get_stats(s, days)[0],
                 'volatilidade': dash.get_stats(s, days)[1]} for s in selected]
        sdf = pd.DataFrame(rows)
        if not sdf.empty:
            fig2 = px.scatter(sdf, x='volatilidade', y='retorno', text='ativo',
                              template='plotly_dark',
                              labels={'volatilidade': 'Volatilidade (%)', 'retorno': 'Retorno (%)'})
            fig2.update_traces(
                textposition='top center', marker=dict(size=10, opacity=0.85),
                hovertemplate='<b>%{text}</b><br>Volatilidade: %{x:.1f}%<br>Retorno: %{y:.1f}%<extra></extra>')
            st.plotly_chart(plotly_layout(fig2, margin=(0, 10, 10, 0)),
                            use_container_width=True, config=PLOTLY_CONFIG)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# 4. ECONOMIA BRASIL
st.markdown(sec_header('Economia Brasil', 'dados oficiais BCB', '#7eb8f7'), unsafe_allow_html=True)
MACRO = [
    ('SELIC', 'SELIC', '&#127970;', 'taxa basica de juros'),
    ('IPCA',  'IPCA',  '&#129534;', 'inflacao acumulada 12 meses'),
    ('CDI',   'CDI',   '&#128200;', 'referencia renda fixa'),
]
eco = ''
for label, sym, icon, desc in MACRO:
    val, _ = dash.get_latest(sym)
    eco += (
        f'<div class="eco-card"><div>'
        f'<div class="eco-label">{label}</div>'
        f'<div class="eco-value">{val:.2f}%</div>'
        f'<div class="eco-desc">{desc}</div></div>'
        f'<div class="eco-icon">{icon}</div></div>'
    )
st.markdown(f'<div class="eco-grid">{eco}</div>', unsafe_allow_html=True)