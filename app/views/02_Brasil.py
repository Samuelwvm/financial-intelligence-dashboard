# views/02_Brasil.py
# Página do mercado brasileiro — cards de ações B3, análise individual,
# Ibovespa e indicadores macroeconômicos.

import streamlit as st
import pandas as pd
import plotly.express as px

from src.database.queries import (
    get_br_stocks, get_latest, get_stats, get_history, get_macro_detail,
)
from src._ui import (
    sec_header, avatar_html, change_span,
    fmt_price, plotly_layout, PLOTLY_CONFIG, SYMBOL_LABEL, page_footer,
    PERIOD_OPT, render_eco_cards,
)


# ─── CABEÇALHO ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="pg-title">Mercado Brasileiro</div>'
    '<div class="pg-subtitle">Empresas listadas na B3 e indicadores macroeconômicos</div>',
    unsafe_allow_html=True,
)

# ── 1. CARDS DE AÇÕES ────────────────────────────────────────────────────
st.markdown(sec_header('Ações B3', 'Lista de elite', '#4caf7d'), unsafe_allow_html=True)

# O período dos cards vem do session_state porque o selectbox da seção 2
# usa key='global_period' — assim os cards já refletem o período escolhido
# mesmo antes do usuário rolar a página.
period_lbl = st.session_state.get('global_period', '30 dias')
days       = PERIOD_OPT.get(period_lbl, 30)
short_lbl  = period_lbl.lower().replace(' dias', 'd').replace(' ano', 'a').replace('último dia', '1d')

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
        f'<span style="font-size:16px;font-weight:700;color:#d0d8f0;">{fmt_price(price, sym)}</span>'
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

# ── 2. ANÁLISE INDIVIDUAL ────────────────────────────────────────────────
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
    # key='global_period' faz o selectbox sincronizar com os cards do topo via session_state
    period_lbl = st.selectbox(
        '_', list(PERIOD_OPT.keys()), index=2,
        key='global_period',
        label_visibility='collapsed',
    )
    days      = PERIOD_OPT[period_lbl]
    short_lbl = period_lbl.lower().replace(' dias', 'd').replace(' ano', 'a').replace('último dia', '1d')

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
            <div style="font-size:26px;font-weight:700;color:#d0d8f0;margin-bottom:5px;">{fmt_price(price, sel_symbol)}</div>
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

# ── 3. IBOVESPA ──────────────────────────────────────────────────────────
# Usa o mesmo período selecionado na análise individual
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

# ── 4. ECONOMIA BRASIL ───────────────────────────────────────────────────
st.markdown(sec_header('Economia Brasil', 'Dados oficiais BCB', '#7eb8f7'), unsafe_allow_html=True)

m = get_macro_detail()
st.markdown(render_eco_cards(m), unsafe_allow_html=True)

st.markdown(page_footer(), unsafe_allow_html=True)