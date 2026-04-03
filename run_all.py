import sys
from pathlib import Path
import time

# Garante que o Python encontre a pasta 'src'
sys.path.append(str(Path(__file__).parent))

from src.collectors.yf_collector import YFCollector
from src.collectors.bcb_collector import BCBCollector
from src.processing.cleaners import DataCleaner
from src.processing.analytics import FinancialAnalytics
from src.database.db_manager import DatabaseManager

def run_daily_update():
    start_time = time.time()
    print("🔔 [INÍCIO] Iniciando atualização diária unificada...")

    db = DatabaseManager()

    # Sua lista de ativos para atualização rápida
    elite_assets = [
        'ITUB4.SA', 'PETR4.SA', 'VALE3.SA', 'BPAC11.SA', 'ABEV3.SA',
        'WEGE3.SA', 'BBDC4.SA', 'BBAS3.SA', 'SANB11.SA', 'AAPL',
        'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'TSLA', 'META', 'NU',
        'CL=F', 'GC=F', '^BVSP', '^GSPC', 'USDBRL=X', 'EURBRL=X',
        'BTC-USD', 'ETH-USD'
    ]

    try:
        # 1. Instanciando as classes
        yf       = YFCollector()
        bcb      = BCBCollector()
        cleaner  = DataCleaner()
        analytics = FinancialAnalytics()

        # --- FASE 1: COLETA ---
        print("\n--- [Fase 1/3] Coletando novos dados ---")

        for ticker in elite_assets:
            yf.fetch_and_save(ticker, period="1d")

        for ind in bcb.indicators:
            bcb.fetch_bcb_data(ind['id'], ind['symbol'], days_back=5)

        # --- FASE 2: LIMPEZA ---
        print("\n--- [Fase 2/3] Padronizando e Limpando dados ---")
        cleaner.run_all_cleaners()

        # --- FASE 3: ANALYTICS ---
        print("\n--- [Fase 3/3] Calculando métricas e scores ---")
        analytics.refresh_analytics()

        duration = round(time.time() - start_time, 2)
        details  = f"{len(elite_assets)} ativos atualizados em {duration}s"

        db.log_update(status="Sucesso", details=details)
        print(f"\n✨ [SUCESSO] {details}")

    except Exception as e:
        duration = round(time.time() - start_time, 2)
        details  = f"Erro após {duration}s: {str(e)}"

        db.log_update(status="Erro", details=details)
        print(f"\n❌ [ERRO] {details}")

        # Re-lança a exceção para o GitHub Action marcar o job como falho
        raise

if __name__ == "__main__":
    run_daily_update()