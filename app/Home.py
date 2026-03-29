import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from src.database.queries import (
    get_latest, get_stats, get_portfolio_history, get_elite_assets, get_macro_detail,
)
from src._ui import (
    CSS, sec_header, avatar_html, change_span,
    fmt_price, plotly_layout, PLOTLY_CONFIG, SYMBOL_LABEL,
)

st.set_page_config(page_title="Radar Financeiro", page_icon="", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


# ─── INTERFACE ─────────────────────────────────────────────────────────────

st.markdown(
    '<div class="pg-title">Radar Financeiro</div>'
    '<div class="pg-subtitle">Painel &nbsp;·&nbsp; visão consolidada do mercado global</div>',
    unsafe_allow_html=True,
)

# ── 1. PULSO DO MERCADO ───────────────────────────────────────────────────
st.markdown(sec_header('Pulso do Mercado', 'Atualizado hoje', '#4caf7d'), unsafe_allow_html=True)

PULSO = [
    ('IBOVESPA',  '^BVSP',    'Índice Brasil'),
    ('DOW JONES', '^DJI',     '30 gigantes EUA'),
    ('S&P 500',   '^GSPC',    '500 maiores EUA'),
    ('DOLAR',     'USDBRL=X', 'Comercial'),
    ('EURO',      'EURBRL=X', 'Zona do Euro'),
]
cards = ''
for label, sym, desc in PULSO:
    price, var = get_latest(sym)
    cards += (
        f'<div class="mcard"><div class="mcard-label">{label}</div>'
        f'<div class="mcard-value">{fmt_price(price, sym)}</div>'
        f'{change_span(var)}<div class="mcard-desc">{desc}</div></div>'
    )
st.markdown(f'<div class="market-grid">{cards}</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 2. MEUS ATIVOS ────────────────────────────────────────────────────────
st.markdown(sec_header('Meus Ativos'), unsafe_allow_html=True)

elite_df = get_elite_assets()
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
    PERIOD_OPT = {'Hoje': 2, '7 dias': 7, '30 dias': 30, '90 dias': 90, '1 ano': 365}

    _, col_radio = st.columns([2.4, 1])
    with col_radio:
        period_lbl = st.radio(
            '_',
            list(PERIOD_OPT.keys()),
            index=2,
            horizontal=True,
            label_visibility='collapsed',
            key='home_period',
        )
    days = PERIOD_OPT[period_lbl]

    cards = ''
    for sym in selected:
        price, _ = get_latest(sym)
        ret, vol  = get_stats(sym, days)

        if vol is None or (isinstance(vol, float) and np.isnan(vol)):
            display_vol = "0.0%"
        else:
            display_vol = f"{vol}%"

        label        = SYMBOL_LABEL.get(sym, sym.replace('.SA', ''))
        name         = name_map.get(sym, label)
        r_cls        = 'up' if ret >= 0 else 'down'
        r_sign       = '+' if ret >= 0 else ''
        lbl_display  = period_lbl.lower().replace(' dias', 'd')

        cards += (
            f'<div class="scard">'
            f'<div class="scard-top">{avatar_html(sym)}'
            f'<div><div class="scard-name">{label}</div>'
            f'<div class="scard-sub">{name}</div></div></div>'
            f'<div style="margin-bottom:8px; font-size:16px; font-weight:700; color:#d0d8f0;">'
            f'R$&nbsp;{price:,.2f}</div>'
            f'<div style="display:flex;gap:7px;">'
            f'<div class="sstat"><div class="sstat-label">retorno {lbl_display}</div>'
            f'<div class="sstat-val {r_cls}">{r_sign}{ret}%</div></div>'
            f'<div class="sstat"><div class="sstat-label">volatil.</div>'
            f'<div class="sstat-val" style="color:#6a7890;">{display_vol}</div></div>'
            f'</div></div>'
        )
    st.markdown(f'<div class="stock-grid">{cards}</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2], gap='medium')

    with col_l:
        st.markdown(sec_header('Desempenho Relativo', f'Base 100 - {period_lbl}'), unsafe_allow_html=True)
        hist = get_portfolio_history(tuple(selected), days)
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
                 'retorno': get_stats(s, days)[0],
                 'volatilidade': get_stats(s, days)[1]} for s in selected]
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

# ── 3. ECONOMIA BRASIL ────────────────────────────────────────────────────
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