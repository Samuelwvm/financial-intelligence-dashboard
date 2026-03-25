import pandas as pd
import requests
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Mantendo sua estrutura de importação robusta
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database.db_manager import DatabaseManager

class BCBCollector:
    def __init__(self):
        self.db = DatabaseManager()
        self.indicators = [
            {'id': 11, 'name': 'Selic', 'symbol': 'SELIC', 'category': 'Macro'},
            {'id': 433, 'name': 'IPCA (Inflação)', 'symbol': 'IPCA', 'category': 'Macro'},
            {'id': 4389, 'name': 'CDI', 'symbol': 'CDI', 'category': 'Macro'}
        ]

    def sync_metadata(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        for ind in self.indicators:
            cursor.execute('''
                INSERT OR IGNORE INTO assets_metadata (symbol, name, category, sector)
                VALUES (?, ?, ?, ?)
            ''', (ind['symbol'], ind['name'], ind['category'], 'Economia BR'))
        conn.commit()
        conn.close()

    def fetch_bcb_data(self, code, symbol, days_back=365):
        """
        Coleta dados do BCB. 
        days_back=365 para carga histórica.
        days_back=5 para atualização diária segura.
        """
        try:
            end_date = datetime.now().strftime('%d/%m/%Y')
            # O start_date agora é calculado com base no parâmetro days_back
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%d/%m/%Y')
            
            url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial={start_date}&dataFinal={end_date}"
            
            response = requests.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"⚠️ Erro na API do BCB para {symbol}: Status {response.status_code}")
                return

            data = response.json()

            if not isinstance(data, list):
                print(f"⚠️ Formato inesperado para {symbol}")
                return

            conn = self.db.get_connection()
            cursor = conn.cursor()

            for item in data:
                d = item['data'].split('/')
                iso_date = f"{d[2]}-{d[1]}-{d[0]}"
                
                valor_raw = item['valor']
                valor = float(valor_raw.replace(',', '.')) if isinstance(valor_raw, str) else float(valor_raw)
                
                cursor.execute('''
                    INSERT OR IGNORE INTO assets_history (date, symbol, price, variation)
                    VALUES (?, ?, ?, ?)
                ''', (iso_date, symbol, valor, 0.0))
            
            conn.commit()
            conn.close()
            print(f"✔️ {symbol} (BCB) sincronizado para os últimos {days_back} dias!")
            
        except Exception as e:
            print(f"❌ Erro crítico ao coletar {symbol}: {e}")

if __name__ == "__main__":
    collector = BCBCollector()
    collector.sync_metadata()
    print("🚀 Executando coleta padrão (365 dias)...")
    for ind in collector.indicators:
        collector.fetch_bcb_data(ind['id'], ind['symbol'], days_back=365)