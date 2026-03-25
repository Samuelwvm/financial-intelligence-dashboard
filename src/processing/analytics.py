import pandas as pd
import sys
from pathlib import Path

# Ajuste de path para o db_manager
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database.db_manager import DatabaseManager

class FinancialAnalytics:
    def __init__(self):
        self.db = DatabaseManager()

    def calculate_variations(self):
        """Calcula a variação percentual entre o preço atual e o anterior."""
        print("📊 Calculando variações de mercado...")
        
        conn = self.db.get_connection()
        # Pegamos os dados ordenados por símbolo e data
        df = pd.read_sql_query("SELECT * FROM assets_history ORDER BY symbol, date", conn)
        
        if df.empty:
            conn.close()
            return

        # Calcula a variação percentual agrupada por símbolo
        df['variation'] = df.groupby('symbol')['price'].pct_change() * 100
        df['variation'] = df['variation'].fillna(0) # O primeiro dia de cada ativo fica 0

        # Atualiza o banco de dados com as novas variações
        cursor = conn.cursor()
        for _, row in df.iterrows():
            cursor.execute('''
                UPDATE assets_history 
                SET variation = ? 
                WHERE date = ? AND symbol = ?
            ''', (row['variation'], row['date'], row['symbol']))
        
        conn.commit()
        conn.close()

    def generate_scores(self):
        """Exemplo: Cria um 'score' simples baseado na performance recente."""
        print("📊 Gerando pontuações de tendência...")
        # Aqui você pode criar lógicas mais complexas no futuro
        pass

    # O "MÉTRICA MESTRE" QUE O RUN_ALL CHAMA:
    def refresh_analytics(self):
        """Executa toda a inteligência de dados em sequência."""
        self.calculate_variations()
        self.generate_scores()
        print("✨ Analytics atualizado com sucesso!")