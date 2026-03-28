import sqlite3
from pathlib import Path

# Localiza o banco
db_path = Path(__file__).parent.parent / "data" / "finance.db"

def reset_database():
    if not db_path.exists():
        print(f"❌ Banco não encontrado em: {db_path}")
        return

    print(f"⚠️ Atenção: Iniciando limpeza completa do banco {db_path.name}...")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # 1. Limpa todo o histórico de preços
        cursor.execute("DELETE FROM assets_history")
        hist_rows = cursor.rowcount
        
        # 2. Limpa todos os metadados (empresas cadastradas)
        cursor.execute("DELETE FROM assets_metadata")
        meta_rows = cursor.rowcount

        # Precisamos salvar as deleções ANTES de rodar o VACUUM
        conn.commit()
        print(f"✅ Dados deletados com sucesso!")

    except Exception as e:
        print(f"❌ Erro durante a limpeza: {e}")
        conn.rollback()
        return
    finally:
        conn.close()

    # 3. Agora sim, rodamos o VACUUM com uma conexão limpa e fora de transação
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("VACUUM")
        conn.close()
        print(f"🧹 Arquivo do banco otimizado (VACUUM concluído).")
    except:
        pass # Se o vacuum falhar por algum motivo externo, os dados já foram limpos

    print(f"\n--- Resumo ---")
    print(f"   - {hist_rows} registros de histórico removidos.")
    print(f"   - {meta_rows} ativos removidos dos metadados.")
    print(f"🚀 O banco está pronto para uma nova carga limpa!")

if __name__ == "__main__":
    confirma = input("Isso apagará TODOS os dados para uma nova carga. Confirmar? (s/n): ")
    if confirma.lower() == 's':
        reset_database()
    else:
        print("Operação cancelada.")