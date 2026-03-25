import sqlite3
import sys
from pathlib import Path

# Ajuste de path para o db_manager
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
        conn = self.db.get_connection()
        conn.execute(query)
        conn.commit()
        conn.close()

    def normalize_names(self):
        """Exemplo de limpeza: garante que símbolos estejam em maiúsculas."""
        print("🧹 Normalizando símbolos...")
        conn = self.db.get_connection()
        conn.execute("UPDATE assets_history SET symbol = UPPER(symbol)")
        conn.commit()
        conn.close()

    # O "MÉTRICA MESTRE" QUE ESTAVA FALTANDO:
    def run_all_cleaners(self):
        """Executa toda a sequência de limpeza."""
        self.remove_duplicates()
        self.normalize_names()
        print("✨ Limpeza concluída!")