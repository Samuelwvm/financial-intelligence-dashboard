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


class BrasilDashboard:
    def __init__(self):
        self.db = DatabaseManager()

    def get_br_stocks(self) -> pd.DataFrame:
        conn = self.db.get_connection()
        df = pd.read_sql(
            "SELECT symbol, name FROM assets_metadata WHERE category = 'Ação BR' ORDER BY name", conn)
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
            f"SELECT date, price, variation FROM assets_history "
            f"WHERE symbol = '{symbol}' AND date >= date('now','-{days} days') "
            "ORDER BY date", conn)
        conn.close()
        return df

    def get_macro(self) -> list:
        results = []
        for sym, label, desc in [
            ('SELIC', 'SELIC', 'taxa básica de juros'),
            ('IPCA',  'IPCA',  'inflação 12 meses'),
            ('CDI',   'CDI',   'referência renda fixa'),
        ]:
            conn = self.db.get_connection()
            df = pd.read_sql(
                f"SELECT price FROM assets_history WHERE symbol = '{sym}' "
                "ORDER BY date DESC LIMIT 1", conn)
            conn.close()
            val = float(df['price'].iloc[0]) if not df.empty else 0.0
            results.append((label, val, desc))
        return results


dash = BrasilDashboard()

# ── Cabeçalho ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="pg-title">Mercado Brasileiro</div>'
    '<div class="pg-subtitle">Empresas listadas na B3 e indicadores macroeconômicos</div>',
    unsafe_allow_html=True,
)

# ── 1. Cards de ações ────────────────────────────────────────────────────
st.markdown(sec_header('Ações B3', 'lista de elite', '#4caf7d'), unsafe_allow_html=True)

stocks_df = dash.get_br_stocks()
cards = ''
for _, row in stocks_df.iterrows():
    sym        = row['symbol']
    price, var = dash.get_latest(sym)
    ret, vol   = dash.get_stats(sym)
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
        f'<div class="sstat"><div class="sstat-label">retorno 30d</div>'
        f'<div class="sstat-val {r_cls}">{r_sign}{ret}%</div></div>'
        f'<div class="sstat"><div class="sstat-label">volatil.</div>'
        f'<div class="sstat-val" style="color:#6a7890;">{vol}%</div></div>'
        f'</div></div>'
    )
st.markdown(f'<div class="stock-grid">{cards}</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 2. Análise Individual ────────────────────────────────────────────────
st.markdown(sec_header('Análise Individual'), unsafe_allow_html=True)

name_map     = dict(zip(stocks_df['symbol'], stocks_df['name']))
col_sel, col_period = st.columns([3, 1], gap='medium')

with col_sel:
    sel_symbol = st.selectbox(
        '_', options=stocks_df['symbol'].tolist(),
        format_func=lambda s: f"{SYMBOL_LABEL.get(s, s)}  —  {name_map.get(s, '')}",
        label_visibility='collapsed',
    )
with col_period:
    period_opt = {'30 dias': 30, '90 dias': 90, '1 ano': 365}
    period_lbl = st.selectbox('_', list(period_opt.keys()), label_visibility='collapsed')
    days       = period_opt[period_lbl]

hist = dash.get_history(sel_symbol, days)

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
        price, var = dash.get_latest(sel_symbol)
        ret, vol   = dash.get_stats(sel_symbol)
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
                <div class="sstat"><div class="sstat-label">retorno {period_lbl[:6]}</div>
                <div class="sstat-val {r_cls}">{r_sign}{ret}%</div></div>
                <div class="sstat"><div class="sstat-label">volatil.</div>
                <div class="sstat-val" style="color:#6a7890;">{vol}%</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander('Ver dados brutos'):
            st.dataframe(
                hist.sort_values('date', ascending=False).rename(
                    columns={'date': 'Data', 'price': 'Preço', 'variation': 'Var%'}),
                use_container_width=True, hide_index=True,
            )
else:
    st.info('Dados históricos não disponíveis para este ativo.')

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 3. Ibovespa ──────────────────────────────────────────────────────────
st.markdown(sec_header('Ibovespa', '90 dias', '#7eb8f7'), unsafe_allow_html=True)

ibov = dash.get_history('^BVSP', days=90)
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
st.markdown(sec_header('Economia Brasil', 'dados oficiais BCB', '#7eb8f7'), unsafe_allow_html=True)

icons = {'SELIC': '&#127970;', 'IPCA': '&#129534;', 'CDI': '&#128200;'}
eco = ''
for label, val, desc in dash.get_macro():
    eco += (
        f'<div class="eco-card">'
        f'<div><div class="eco-label">{label}</div>'
        f'<div class="eco-value">{val:.2f}%</div>'
        f'<div class="eco-desc">{desc}</div></div>'
        f'<div class="eco-icon">{icons.get(label,"")}</div>'
        f'</div>'
    )
st.markdown(f'<div class="eco-grid">{eco}</div>', unsafe_allow_html=True)