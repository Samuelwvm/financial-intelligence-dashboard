import sqlite3
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        # Localiza a pasta data/ na raiz do projeto
        self.project_root = Path(__file__).parent.parent.parent
        self.db_path = self.project_root / "data" / "finance_v2.db"
        self.schema_path = Path(__file__).parent / "schema.sql"
        
        # Garante que a pasta existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def initialize_db(self):
        """Lê o arquivo .sql e cria as tabelas iniciais."""
        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
        print(f"✅ Banco de dados V2 inicializado em: {self.db_path}")

if __name__ == "__main__":
    db = DatabaseManager()
    db.initialize_db()