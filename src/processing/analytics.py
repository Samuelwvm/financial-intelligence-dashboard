import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database.db_manager import DatabaseManager


class FinancialAnalytics:
    def __init__(self):
        self.db = DatabaseManager()

    def calculate_variations(self):
        """
        Calcula a variação percentual dia a dia para cada ativo
        e grava o resultado de volta em assets_history.variation.
        """
        print("📊 Calculando variações de mercado...")

        with self.db.get_connection() as conn:
            df = pd.read_sql_query(
                "SELECT rowid, symbol, date, price FROM assets_history "
                "ORDER BY symbol, date",
                conn)

            if df.empty:
                return

            df['variation'] = (
                df.groupby('symbol')['price']
                  .pct_change()
                  .mul(100)
                  .fillna(0)
            )

            cursor = conn.cursor()
            cursor.executemany(
                "UPDATE assets_history SET variation = ? WHERE rowid = ?",
                zip(df['variation'].round(4), df['rowid'])
            )

        print("✅ Variações calculadas.")

    def generate_scores(self):
        """Placeholder para scores e métricas futuras de tendência."""
        print("📊 Gerando pontuações de tendência...")
        pass

    def refresh_analytics(self):
        """Ponto de entrada principal — chamado pelo run_all."""
        self.calculate_variations()
        self.generate_scores()
        print("✨ Analytics atualizado com sucesso!")