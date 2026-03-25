import sys
from pathlib import Path
import time

# Garante que o Python encontre a pasta 'src'
sys.path.append(str(Path(__file__).parent))

from src.collectors.yf_collector import YFCollector
from src.collectors.bcb_collector import BCBCollector
from src.processing.cleaners import DataCleaner     # Ajuste conforme o nome da sua classe/função
from src.processing.analytics import FinancialAnalytics # Ajuste conforme o nome da sua classe/função

def run_daily_update():
    start_time = time.time()
    print("🔔 [INÍCIO] Iniciando atualização diária unificada...")

    # 1. Instanciando as classes
    yf = YFCollector()
    bcb = BCBCollector()
    cleaner = DataCleaner()
    analytics = FinancialAnalytics()

    # Sua lista de ativos para atualização rápida
    elite_assets = [
        'ITUB4.SA', 'PETR4.SA', 'VALE3.SA', 'BPAC11.SA', 'ABEV3.SA', 
        'WEGE3.SA', 'BBDC4.SA', 'BBAS3.SA', 'SANB11.SA', 'AAPL', 
        'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'TSLA', 'META', 'NU', 
        'CL=F', 'GC=F', '^BVSP', '^GSPC', 'USDBRL=X', 'EURBRL=X', 
        'BTC-USD', 'ETH-USD'
    ]

    # --- FASE 1: COLETA (O "O QUE ACONTECEU?") ---
    print("\n--- [Fase 1/3] Coletando novos dados ---")
    
    # Coleta Yahoo Finance (Apenas 1 dia para ser ultra rápido)
    for ticker in elite_assets:
        yf.fetch_and_save(ticker, period="1d")

    # Coleta Banco Central (5 dias de margem para cobrir finais de semana/feriados)
    for ind in bcb.indicators:
        bcb.fetch_bcb_data(ind['id'], ind['symbol'], days_back=5)

    # --- FASE 2: LIMPEZA (O "ESTÁ TUDO CERTO?") ---
    print("\n--- [Fase 2/3] Padronizando e Limpando dados ---")
    cleaner.run_all_cleaners() # Chama sua lógica de limpeza do cleaners.py

    # --- FASE 3: INTELIGÊNCIA (O "QUANTO RENDEU?") ---
    print("\n--- [Fase 3/3] Calculando métricas e scores ---")
    analytics.refresh_analytics() # Chama seus cálculos do analytics.py

    end_time = time.time()
    duration = end_time - start_time
    print(f"\n✨ [SUCESSO] Sincronização total finalizada em {duration:.2f}s!")

if __name__ == "__main__":
    run_daily_update()