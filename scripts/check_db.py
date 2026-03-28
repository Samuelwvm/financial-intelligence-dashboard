import sqlite3
from pathlib import Path
import sys

# Ajusta o caminho para encontrar o banco na pasta data/
root = Path(__file__).parent.parent
db_path = root / "data" / "finance.db"

def check_health():
    if not db_path.exists():
        print(f"❌ Erro: Banco de dados não encontrado em {db_path}")
        return

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    print("="*40)
    print("🔍 RELATÓRIO DE SAÚDE DO BANCO")
    print("="*40)

    # 1. Contagem Geral
    cursor.execute("SELECT count(*) FROM assets_history")
    print(f"📈 Total de registros de preços: {cursor.fetchone()[0]}")

    # 2. Verificar Ativos Novos
    print("\n✅ Verificando novos ativos:")
    novos = ('ITUB4.SA', 'PETR4.SA', 'VALE3.SA', 'BPAC11.SA', 'ABEV3.SA', 'WEGE3.SA', 'BBDC4.SA',  'BBAS3.SA',  'SANB11.SA', 'JBSS32.SA', 'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'TSLA', 'META', 'NU', 'AMD', '2222.SR', 'CL=F', 'GC=F', '^BVSP', '^GSPC', '^DJI', 'USDBRL=X', 'EURBRL=X', 'BTC-USD', 'ETH-USD')
    for sym in novos:
        cursor.execute("SELECT symbol, name FROM assets_metadata WHERE symbol = ?", (sym,))
        row = cursor.fetchone()
        if row:
            cursor.execute("SELECT count(*) FROM assets_history WHERE symbol = ?", (sym,))
            count = cursor.fetchone()[0]
            print(f"   - {row[0]} ({row[1]}): {count} registros encontrados.")
        else:
            print(f"   - {sym}: ⚠️ NÃO CADASTRADO NO BANCO.")

    # 3. Teste de Duplicidade (A prova de fogo)
    cursor.execute("""
        SELECT date, symbol, COUNT(*) 
        FROM assets_history 
        GROUP BY date, symbol 
        HAVING COUNT(*) > 1
    """)
    dups = cursor.fetchall()
    if not dups:
        print("\n✨ Sucesso: Nenhuma duplicata encontrada!")
    else:
        print(f"\n⚠️ Alerta: Encontradas {len(dups)} entradas duplicadas!")

    conn.close()

if __name__ == "__main__":
    check_health()