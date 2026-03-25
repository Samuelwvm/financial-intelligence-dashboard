import yfinance as yf
import pandas as pd
import sys
from pathlib import Path

# Importação robusta do nosso DatabaseManager
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database.db_manager import DatabaseManager

class YFCollector:
    def __init__(self):
        self.db = DatabaseManager()

    def sync_metadata(self, asset_list):
        """Garante que todas as empresas da sua lista estejam cadastradas no banco."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        for asset in asset_list:
            cursor.execute('''
                INSERT OR IGNORE INTO assets_metadata (symbol, name, category, sector)
                VALUES (?, ?, ?, ?)
            ''', (asset['symbol'], asset['name'], asset['category'], asset['sector']))
        
        conn.commit()
        conn.close()
        print(f"✅ Metadados sincronizados ({len(asset_list)} ativos verificados).")

    def fetch_and_save(self, symbol: str, period: str = "1d"):
        """
        Busca dados no Yahoo Finance e salva na tabela de histórico.
        period="1y" para carga histórica.
        period="1d" para atualização diária rápida.
        """
        try:
            ticker = yf.Ticker(symbol)
            # O yfinance aceita períodos como '1d', '5d', '1mo', '1y', 'max'
            df = ticker.history(period=period)
            
            if df.empty:
                print(f"⚠️ Nenhum dado encontrado para {symbol}")
                return

            # Limpeza e formatação
            df.index = df.index.strftime('%Y-%m-%d')
            df = df.reset_index()
            
            conn = self.db.get_connection()
            cursor = conn.cursor()

            for _, row in df.iterrows():
                # 'Close' é o preço de fechamento
                cursor.execute('''
                    INSERT OR IGNORE INTO assets_history (date, symbol, price, variation)
                    VALUES (?, ?, ?, ?)
                ''', (row['Date'], symbol, row['Close'], 0.0))
            
            conn.commit()
            conn.close()
            print(f"✔️ {symbol} atualizado (Período: {period}).")
            
        except Exception as e:
            print(f"❌ Erro ao coletar {symbol}: {e}")

if __name__ == "__main__":
    collector = YFCollector()
    
    # --- SUA LISTA DE ELITE CONSOLIDADA ---
    elite_assets = [
        # BRASIL
        {'symbol': 'ITUB4.SA', 'name': 'Itaú Unibanco', 'category': 'Ação BR', 'sector': 'Financeiro'},
        {'symbol': 'PETR4.SA', 'name': 'Petrobras', 'category': 'Ação BR', 'sector': 'Energia'},
        {'symbol': 'VALE3.SA', 'name': 'Vale', 'category': 'Ação BR', 'sector': 'Mineração'},
        {'symbol': 'BPAC11.SA', 'name': 'BTG Pactual', 'category': 'Ação BR', 'sector': 'Financeiro'},
        {'symbol': 'ABEV3.SA', 'name': 'Ambev', 'category': 'Ação BR', 'sector': 'Consumo'},
        {'symbol': 'WEGE3.SA', 'name': 'WEG', 'category': 'Ação BR', 'sector': 'Industrial'},
        {'symbol': 'BBDC4.SA', 'name': 'Bradesco', 'category': 'Ação BR', 'sector': 'Financeiro'},
        {'symbol': 'BBAS3.SA', 'name': 'Banco do Brasil', 'category': 'Ação BR', 'sector': 'Financeiro'},
        {'symbol': 'SANB11.SA', 'name': 'Santander BR', 'category': 'Ação BR', 'sector': 'Financeiro'},
        
        # EUA
        {'symbol': 'AAPL', 'name': 'Apple', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'GOOGL', 'name': 'Alphabet (Google)', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'MSFT', 'name': 'Microsoft', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'AMZN', 'name': 'Amazon', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'NVDA', 'name': 'NVIDIA', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'TSLA', 'name': 'Tesla', 'category': 'Ação EUA', 'sector': 'Automotivo'},
        {'symbol': 'META', 'name': 'Meta', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'NU', 'name': 'Nubank', 'category': 'Ação EUA', 'sector': 'Financeiro'},
        
        # COMMODITIES & ÍNDICES
        {'symbol': 'CL=F', 'name': 'Petróleo Brent', 'category': 'Commodity', 'sector': 'Energia'},
        {'symbol': 'GC=F', 'name': 'Ouro', 'category': 'Commodity', 'sector': 'Segurança'},
        {'symbol': '^BVSP', 'name': 'Ibovespa', 'category': 'Índice', 'sector': 'Brasil'},
        {'symbol': '^GSPC', 'name': 'S&P 500', 'category': 'Índice', 'sector': 'EUA'},
        {'symbol': '^DJI',  'name': 'Dow Jones', 'category': 'Índice', 'sector': 'EUA'},
        
        # MOEDAS & CRIPTO
        {'symbol': 'USDBRL=X', 'name': 'Dólar/Real', 'category': 'Moeda', 'sector': 'Câmbio'},
        {'symbol': 'EURBRL=X', 'name': 'Euro/Real', 'category': 'Moeda', 'sector': 'Câmbio'},
        {'symbol': 'BTC-USD', 'name': 'Bitcoin', 'category': 'Cripto', 'sector': 'Tecnologia'},
        {'symbol': 'ETH-USD', 'name': 'Ethereum', 'category': 'Cripto', 'sector': 'Tecnologia'}
    ]
    
    print("🚀 Executando carga padrão (1 ano para teste inicial)...")
    collector.sync_metadata(elite_assets)
    
    for asset in elite_assets:
        collector.fetch_and_save(asset['symbol'], period="1y")
        
    print("🏁 Sincronização finalizada!")