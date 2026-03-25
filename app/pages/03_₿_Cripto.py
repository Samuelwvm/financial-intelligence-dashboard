import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))
from src.database.db_manager import DatabaseManager
from src._ui import CSS, sec_header, change_span, plotly_layout, PLOTLY_CONFIG

st.set_page_config(page_title="Cripto · Radar Financeiro", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

st.markdown("""
<style>
    .cripto-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }
    .cripto-card {
        background:#161922; border:0.5px solid #1f2333;
        border-radius:12px; padding:22px 24px; position:relative; overflow:hidden;
    }
    .cripto-card::before {
        content:''; position:absolute; top:0; left:0; right:0; height:2px;
    }
    .cripto-card.btc::before { background: linear-gradient(90deg,#f7931a,#fbbf24); }
    .cripto-card.eth::before { background: linear-gradient(90deg,#627eea,#a78bfa); }
    .cripto-symbol { font-size:11px !important; font-weight:700 !important;
                     letter-spacing:1.5px; text-transform:uppercase; margin-bottom:4px; }
    .cripto-name   { font-size:12px !important; color:#454a60 !important; margin-bottom:14px; }
    .cripto-price  { font-size:30px !important; font-weight:700 !important;
                     color:#e8ecf8 !important; margin-bottom:5px; }
    .cripto-stats  { display:flex; gap:10px; margin-top:14px; }
    .cripto-stat   { background:#0f1118; border-radius:6px; padding:9px 12px; flex:1; }
    .cripto-stat-lbl { font-size:9px !important; color:#3a3f55 !important;
                       text-transform:uppercase; letter-spacing:.5px; font-weight:600 !important; }
    .cripto-stat-val { font-size:15px !important; font-weight:700 !important; margin-top:2px; }
    .badge-desc {
        display:inline-block; margin-top:12px; font-size:10px !important; color:#4a5068 !important;
        background:#0f1118; border:0.5px solid #1f2333; border-radius:4px; padding:3px 9px;
    }
</style>
""", unsafe_allow_html=True)


class CriptoDashboard:
    def __init__(self):
        self.db = DatabaseManager()

    def get_latest(self, symbol: str) -> tuple[float, float]:
        conn = self.db.get_connection()
        df = pd.read_sql(
            "SELECT price, variation FROM assets_history "
            f"WHERE symbol = '{symbol}' ORDER BY date DESC LIMIT 1", conn)
        conn.close()
        if df.empty:
            return 0.0, 0.0
        return float(df['price'].iloc[0]), float(df['variation'].iloc[0])

    def get_stats(self, symbol: str, days: int = 30) -> tuple[float, float, float, float]:
        conn = self.db.get_connection()
        df = pd.read_sql(
            f"SELECT price FROM assets_history WHERE symbol = '{symbol}' "
            f"ORDER BY date DESC LIMIT {days}", conn)
        conn.close()
        if len(df) < 2:
            return 0.0, 0.0, 0.0, 0.0
        ret = ((df['price'].iloc[0] / df['price'].iloc[-1]) - 1) * 100
        vol = df['price'].pct_change().std() * np.sqrt(252) * 100
        return round(ret, 1), round(vol, 1), round(df['price'].max(), 2), round(df['price'].min(), 2)

    def get_history(self, symbol: str, days: int = 30) -> pd.DataFrame:
        conn = self.db.get_connection()
        df = pd.read_sql(
            f"SELECT date, price FROM assets_history "
            f"WHERE symbol = '{symbol}' AND date >= date('now','-{days} days') "
            "ORDER BY date", conn)
        conn.close()
        return df


dash = CriptoDashboard()

# ── Cabeçalho ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="pg-title">Criptoativos</div>'
    '<div class="pg-subtitle">Bitcoin e Ethereum &nbsp;·&nbsp; preços em dólar americano</div>',
    unsafe_allow_html=True,
)

period_opt = {'7 dias': 7, '30 dias': 30, '90 dias': 90, '1 ano': 365}
period_lbl = st.radio('_', list(period_opt.keys()), horizontal=True,
                      label_visibility='collapsed', index=1)
days = period_opt[period_lbl]
st.markdown('<div style="margin-bottom:6px;"></div>', unsafe_allow_html=True)

# ── 1. Cards ─────────────────────────────────────────────────────────────
btc_p, btc_v                       = dash.get_latest('BTC-USD')
btc_ret, btc_vol, btc_max, btc_min = dash.get_stats('BTC-USD', days)
eth_p, eth_v                       = dash.get_latest('ETH-USD')
eth_ret, eth_vol, eth_max, eth_min = dash.get_stats('ETH-USD', days)

def r_cls(v):  return 'up' if v >= 0 else 'down'
def r_sign(v): return '+' if v >= 0 else ''

st.markdown(f"""
<div class="cripto-grid">
    <div class="cripto-card btc">
        <div class="cripto-symbol" style="color:#f7931a;">BTC</div>
        <div class="cripto-name">Bitcoin</div>
        <div class="cripto-price">$ {btc_p:,.2f}</div>
        {change_span(btc_v, size=13)}
        <div class="cripto-stats">
            <div class="cripto-stat">
                <div class="cripto-stat-lbl">retorno {period_lbl}</div>
                <div class="cripto-stat-val {r_cls(btc_ret)}">{r_sign(btc_ret)}{btc_ret}%</div>
            </div>
            <div class="cripto-stat">
                <div class="cripto-stat-lbl">volatilidade</div>
                <div class="cripto-stat-val" style="color:#6a7890;">{btc_vol}%</div>
            </div>
            <div class="cripto-stat">
                <div class="cripto-stat-lbl">máxima</div>
                <div class="cripto-stat-val" style="color:#d0d8f0;">$ {btc_max:,.0f}</div>
            </div>
            <div class="cripto-stat">
                <div class="cripto-stat-lbl">mínima</div>
                <div class="cripto-stat-val" style="color:#d0d8f0;">$ {btc_min:,.0f}</div>
            </div>
        </div>
        <div class="badge-desc">armazenamento de valor · emissão limitada a 21 milhões</div>
    </div>
    <div class="cripto-card eth">
        <div class="cripto-symbol" style="color:#7b8ef7;">ETH</div>
        <div class="cripto-name">Ethereum</div>
        <div class="cripto-price">$ {eth_p:,.2f}</div>
        {change_span(eth_v, size=13)}
        <div class="cripto-stats">
            <div class="cripto-stat">
                <div class="cripto-stat-lbl">retorno {period_lbl}</div>
                <div class="cripto-stat-val {r_cls(eth_ret)}">{r_sign(eth_ret)}{eth_ret}%</div>
            </div>
            <div class="cripto-stat">
                <div class="cripto-stat-lbl">volatilidade</div>
                <div class="cripto-stat-val" style="color:#6a7890;">{eth_vol}%</div>
            </div>
            <div class="cripto-stat">
                <div class="cripto-stat-lbl">máxima</div>
                <div class="cripto-stat-val" style="color:#d0d8f0;">$ {eth_max:,.0f}</div>
            </div>
            <div class="cripto-stat">
                <div class="cripto-stat-lbl">mínima</div>
                <div class="cripto-stat-val" style="color:#d0d8f0;">$ {eth_min:,.0f}</div>
            </div>
        </div>
        <div class="badge-desc">plataforma de contratos inteligentes e aplicações descentralizadas</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 2. Gráfico comparativo ───────────────────────────────────────────────
st.markdown(sec_header('Desempenho Comparativo', f'base 100 · {period_lbl}', '#f7931a'), unsafe_allow_html=True)

btc_hist = dash.get_history('BTC-USD', days)
eth_hist = dash.get_history('ETH-USD', days)

if not btc_hist.empty and not eth_hist.empty:
    btc_hist['ativo'] = 'Bitcoin (BTC)'
    eth_hist['ativo'] = 'Ethereum (ETH)'
    combined = pd.concat([btc_hist, eth_hist])
    combined['base_100'] = combined.groupby('ativo')['price'].transform(
        lambda x: (x / x.iloc[0]) * 100)
    fig = px.line(combined, x='date', y='base_100', color='ativo',
                  template='plotly_dark',
                  color_discrete_map={'Bitcoin (BTC)': '#f7931a', 'Ethereum (ETH)': '#7b8ef7'},
                  labels={'base_100': 'retorno (%)', 'date': '', 'ativo': ''})
    fig.update_traces(
        line_width=2,
        hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>Retorno: %{y:.1f}%<extra></extra>',
    )
    st.plotly_chart(plotly_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

st.markdown('<hr class="divider"/>', unsafe_allow_html=True)

# ── 3. Preço histórico lado a lado ───────────────────────────────────────
st.markdown(sec_header('Preço Histórico'), unsafe_allow_html=True)

col_a, col_b = st.columns(2, gap='medium')

for col, sym, name, color, fill in [
    (col_a, 'BTC-USD', 'Bitcoin',  '#f7931a', 'rgba(247,147,26,0.07)'),
    (col_b, 'ETH-USD', 'Ethereum', '#7b8ef7', 'rgba(123,142,247,0.07)'),
]:
    hist = dash.get_history(sym, days)
    with col:
        st.markdown(
            f'<div style="font-size:12px;font-weight:600;color:#6a7890;margin-bottom:8px;">{name}</div>',
            unsafe_allow_html=True,
        )
        if not hist.empty:
            fig = px.area(hist, x='date', y='price', template='plotly_dark',
                          labels={'price': 'USD', 'date': ''})
            fig.update_traces(
                line_color=color, line_width=1.5, fillcolor=fill,
                hovertemplate='<b>%{x}</b><br>$ %{y:,.2f}<extra></extra>',
            )
            st.plotly_chart(plotly_layout(fig, margin=(0, 0, 0, 0)),
                            use_container_width=True, config=PLOTLY_CONFIG)