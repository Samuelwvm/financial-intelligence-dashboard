"""
src/database/queries.py — Central de queries cacheadas.

Todas as páginas importam daqui. Nenhuma página define
sua própria query ou seu próprio @st.cache_data para dados do banco.

Uso nas páginas:
    from src.database.queries import get_latest, get_stats, get_history, ...
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database.db_manager import DatabaseManager


# ─── QUERIES GENÉRICAS (usadas em múltiplas páginas) ───────────────────────

@st.cache_data(ttl=3600)
def get_latest(symbol: str) -> tuple[float, float]:
    """Retorna (price, variation) do registro mais recente do ativo."""
    db = DatabaseManager()
    with db.get_connection() as conn:
        df = pd.read_sql(
            "SELECT price, variation FROM assets_history "
            "WHERE symbol = ? ORDER BY date DESC LIMIT 1",
            conn, params=(symbol,))
    if df.empty:
        return 0.0, 0.0
    return float(df['price'].iloc[0]), float(df['variation'].iloc[0])


@st.cache_data(ttl=3600)
def get_stats(symbol: str, days: int = 30) -> tuple[float, float]:
    """
    Retorna (retorno_percentual, volatilidade_anualizada) para o período.
    
    Quando days=2, busca os 2 últimos registros disponíveis no banco,
    funcionando como proxy de variação diária. Essa abordagem é intencional
    
    — garante que o cálculo funcione mesmo em feriados e fins de semana,
    onde o dia atual pode não ter dado disponível ainda.
    """
    db = DatabaseManager()
    query_days = 2 if days <= 2 else days
    with db.get_connection() as conn:
        df = pd.read_sql(
            "SELECT price FROM assets_history WHERE symbol = ? "
            "ORDER BY date DESC LIMIT ?",
            conn, params=(symbol, query_days))
    if len(df) < 2:
        return 0.0, 0.0
    ret = ((df['price'].iloc[0] / df['price'].iloc[-1]) - 1) * 100
    vol = df['price'].pct_change().std() * np.sqrt(252) * 100
    if pd.isna(vol):
        vol = 0.0
    return round(ret, 1), round(vol, 1)


@st.cache_data(ttl=3600)
def get_ohlc_stats(symbol: str, days: int = 30) -> tuple[float, float, float, float]:
    """
    Versão estendida de get_stats. Retorna (retorno, volatilidade, máxima, mínima).
    Usada pela página de Cripto para exibir high/low do período.
    """
    db = DatabaseManager()
    with db.get_connection() as conn:
        df = pd.read_sql(
            "SELECT price FROM assets_history WHERE symbol = ? "
            "ORDER BY date DESC LIMIT ?",
            conn, params=(symbol, days))
    if len(df) < 2:
        return 0.0, 0.0, 0.0, 0.0
    ret = ((df['price'].iloc[0] / df['price'].iloc[-1]) - 1) * 100
    vol = df['price'].pct_change().std() * np.sqrt(252) * 100
    if pd.isna(vol):
        vol = 0.0
    return round(ret, 1), round(vol, 1), round(df['price'].max(), 2), round(df['price'].min(), 2)


@st.cache_data(ttl=3600)
def get_history(symbol: str, days: int = 30) -> pd.DataFrame:
    """
    Retorna o histórico de preços (date, price) do ativo para o período.
    Quando days=2 (hoje), expande para 7 dias para ter dados suficientes no gráfico.
    """
    db = DatabaseManager()
    chart_days = 7 if days <= 2 else days
    with db.get_connection() as conn:
        df = pd.read_sql(
            "SELECT date, price FROM assets_history "
            "WHERE symbol = ? AND date >= date('now', ?) "
            "ORDER BY date",
            conn, params=(symbol, f'-{chart_days} days'))
    return df


@st.cache_data(ttl=3600)
def get_portfolio_history(symbols: tuple, days: int = 30) -> pd.DataFrame:
    """
    Retorna histórico de múltiplos ativos para o gráfico de desempenho relativo.
    Recebe tuple (não list) para ser hashável pelo cache do Streamlit.
    """
    if not symbols:
        return pd.DataFrame()
    db = DatabaseManager()
    placeholders = ','.join(['?'] * len(symbols))
    with db.get_connection() as conn:
        df = pd.read_sql(
            f"SELECT date, symbol, price FROM assets_history "
            f"WHERE symbol IN ({placeholders}) AND date >= date('now','-{days} days') "
            "ORDER BY date",
            conn, params=list(symbols))
    return df


# ─── QUERIES DE METADADOS (listas de ativos por categoria) ─────────────────

@st.cache_data(ttl=3600)
def get_elite_assets() -> pd.DataFrame:
    """Lista ordenada dos ativos exibidos na Home."""
    elite = [
        'ITUB4.SA', 'PETR4.SA', 'VALE3.SA', 'BPAC11.SA',
        'ABEV3.SA', 'WEGE3.SA', 'BBDC4.SA', 'BBAS3.SA', 'SANB11.SA', 'JBSS32.SA',
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'TSLA', 'META', 'NU',
        '2222.SR', 'AMD', 'BTC-USD', 'ETH-USD',
    ]
    db = DatabaseManager()
    placeholders = ','.join(['?'] * len(elite))
    with db.get_connection() as conn:
        df = pd.read_sql(
            f"SELECT symbol, name FROM assets_metadata WHERE symbol IN ({placeholders})",
            conn, params=elite)
    df['_order'] = df['symbol'].map({s: i for i, s in enumerate(elite)})
    return df.sort_values('_order').drop(columns='_order').reset_index(drop=True)


@st.cache_data(ttl=3600)
def get_br_stocks() -> pd.DataFrame:
    """Lista de ações brasileiras (categoria 'Ação BR')."""
    db = DatabaseManager()
    with db.get_connection() as conn:
        df = pd.read_sql(
            "SELECT symbol, name FROM assets_metadata "
            "WHERE category = 'Ação BR' ORDER BY name",
            conn)
    return df


@st.cache_data(ttl=3600)
def get_us_stocks() -> pd.DataFrame:
    """Lista de ações americanas e internacionais."""
    db = DatabaseManager()
    with db.get_connection() as conn:
        df = pd.read_sql(
            "SELECT symbol, name FROM assets_metadata "
            "WHERE category IN ('Ação EUA', 'Ação Mundo') ORDER BY name",
            conn)
    return df


@st.cache_data(ttl=3600)
def get_commodities_indices() -> pd.DataFrame:
    """Lista de commodities e índices globais."""
    db = DatabaseManager()
    with db.get_connection() as conn:
        df = pd.read_sql(
            "SELECT symbol, name, category FROM assets_metadata "
            "WHERE category IN ('Commodity', 'Índice') ORDER BY category, name",
            conn)
    return df


# ─── QUERY MACROECONÔMICA ──────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_macro_detail() -> dict:
    """
    Retorna SELIC, CDI e IPCA formatados para os cards de Economia Brasil.
    Notas de cálculo:
    - SELIC (série BCB 11): retorna taxa diária efetiva → anualizada por juros compostos (base 252)
    - SELIC Meta (série BCB 432): já retorna taxa anual → usado direto
    - CDI  (série BCB 4389): já retorna taxa anual → usado direto
    - IPCA Mensal (série BCB 433): retorna variação mensal
    - IPCA 12M (série BCB 13522): retorna acumulado oficial 12 meses direto da fonte
    """
    db = DatabaseManager()
    with db.get_connection() as conn:
        #Busca a Selic Meta oficial
        df_meta = pd.read_sql(
            "SELECT price FROM assets_history WHERE symbol = 'SELIC_META' "
            "ORDER BY date DESC LIMIT 1", conn)
        
        # Mantém a query da SELIC (Over) para o cálculo da taxa diária.
        df_selic = pd.read_sql(
            "SELECT price FROM assets_history WHERE symbol = 'SELIC' "
            "ORDER BY date DESC LIMIT 1", conn)
            
        df_cdi = pd.read_sql(
            "SELECT price FROM assets_history WHERE symbol = 'CDI' "
            "ORDER BY date DESC LIMIT 1", conn)
            
        df_ipca = pd.read_sql(
            "SELECT price FROM assets_history WHERE symbol = 'IPCA' "
            "ORDER BY date DESC LIMIT 1", conn)
            
        df_ipca_12m = pd.read_sql(
            "SELECT price FROM assets_history WHERE symbol = 'IPCA12M' "
            "ORDER BY date DESC LIMIT 1", conn)

    # Lógica da selic_annual:
    # Em vez de calcular, usamos o valor direto da selic Meta
    selic_annual = float(df_meta['price'].iloc[0]) if not df_meta.empty else 0.0
    
    # Mantemos o cálculo da taxa diária usando a SELIC Over (série 11)
    selic_daily = float(df_selic['price'].iloc[0]) if not df_selic.empty else 0.0

    cdi_annual = round(float(df_cdi['price'].iloc[0]), 2) if not df_cdi.empty else 0.0
    ipca_monthly = round(float(df_ipca['price'].iloc[0]), 2) if not df_ipca.empty else 0.0
    ipca_12m = round(float(df_ipca_12m['price'].iloc[0]), 2) if not df_ipca_12m.empty else 0.0

    return {
        'selic_annual': selic_annual,
        'selic_daily':  round(selic_daily, 4),
        'cdi_annual':   cdi_annual,
        'ipca_monthly': ipca_monthly,
        'ipca_12m':     ipca_12m,
    }