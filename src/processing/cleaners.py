import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database.db_manager import DatabaseManager


class DataCleaner:
    def __init__(self):
        self.db = DatabaseManager()

    def remove_duplicates(self):
        """Remove registros duplicados (mesmo dia e mesmo símbolo)."""
        print("🧹 Removendo duplicatas...")
        query = """
        DELETE FROM assets_history
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM assets_history
            GROUP BY date, symbol
        )
        """
        with self.db.get_connection() as conn:
            conn.execute(query)

    def normalize_names(self):
        """Garante que todos os símbolos estejam em maiúsculas."""
        print("🧹 Normalizando símbolos...")
        with self.db.get_connection() as conn:
            conn.execute("UPDATE assets_history SET symbol = UPPER(symbol)")

    def run_all_cleaners(self):
        """Executa toda a sequência de limpeza em ordem."""
        self.remove_duplicates()
        self.normalize_names()
        print("✨ Limpeza concluída!")