import sqlite3
from contextlib import contextmanager
from pathlib import Path


class DatabaseManager:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.db_path = self.project_root / "data" / "finance.db"
        self.schema_path = Path(__file__).parent / "schema.sql"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self):
        """
        Context manager que garante commit em caso de sucesso
        e rollback + fechamento em qualquer situação.

        Uso:
            with db.get_connection() as conn:
                pd.read_sql(..., conn)
                conn.execute(...)
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_db(self):
        """Lê o arquivo .sql e cria as tabelas iniciais."""
        with open(self.schema_path, 'r') as f:
            schema_sql = f.read()

        with self.get_connection() as conn:
            conn.executescript(schema_sql)

        print(f"✅ Banco de dados inicializado em: {self.db_path}")


if __name__ == "__main__":
    db = DatabaseManager()
    db.initialize_db()