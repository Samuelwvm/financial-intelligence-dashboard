import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from src.database.queries import (
    get_br_stocks, get_latest, get_stats, get_history, get_macro_detail,
)
from src._ui import (
    CSS, sec_header, avatar_html, change_span,
    fmt_price, plotly_layout, PLOTLY_CONFIG, SYMBOL_LABEL,
)

st.set_page_config(page_title="Brasil · Radar Financeiro", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


# ─── INTERFACE ─────────────────────────────────────────────────────────────

PERIOD_OPT = {'Hoje': 2, '7 dias': 7, '30 dias': 30, '90 dias': 90, '1 ano': 365}

st.markdown(
    '<div class="pg-title">Mercado Brasileiro</div>'
    '<div class="pg-subtitle">Empresas listadas na B3 e indicadores macroeconômicos</div>',
    unsafe_allow_html=True,
)

# ── 1. Cards de ações ────────────────────────────────────────────────────
# O período é definido no seletor da Análise Individual (abaixo) e lido
# aqui via session_state. O Streamlit re-executa o script inteiro a cada
# interação, então o valor já está atualizado quando chega nesta linha.
st.markdown(sec_header('Ações B3', 'Lista de elite', '#4caf7d'), unsafe_allow_html=True)

period_lbl = st.session_state.get('global_period', '30 dias')
days       = PERIOD_OPT[period_lbl]
short_lbl  = period_lbl.lower().replace(' dias', 'd').replace(' ano', 'a')

stocks_df = get_br_stocks()
cards = ''
for _, row in stocks_df.iterrows():
    sym        = row['symbol']
    price, var = get_latest(sym)
    ret, vol   = get_stats(sym, days=days)
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

name_map = dict(zip(stocks_df['symbol'], stocks_df['name']))
col_sel, col_period = st.columns([3, 1], gap='medium')

with col_sel:
    sel_symbol = st.selectbox(
        '_', options=stocks_df['symbol'].tolist(),
        format_func=lambda s: f"{SYMBOL_LABEL.get(s, s)}  —  {name_map.get(s, '')}",
        label_visibility='collapsed',
    )
with col_period:
    period_lbl = st.selectbox(
        '_', list(PERIOD_OPT.keys()), index=2,
        key='global_period',
        label_visibility='collapsed',
    )
    days      = PERIOD_OPT[period_lbl]
    short_lbl = period_lbl.lower().replace(' dias', 'd').replace(' ano', 'a')

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
st.markdown(sec_header('Ibovespa', period_lbl, '#7eb8f7'), unsafe_allow_html=True)

ibov = get_history('^BVSP', days=days)
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
st.markdown(f'<div class="eco-grid">{eco}</div>', unsafe_allow_html=True)