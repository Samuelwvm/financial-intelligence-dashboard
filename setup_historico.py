import sys
from pathlib import Path

# Garante que o Python encontre a pasta 'src' estando na raiz
sys.path.append(str(Path(__file__).parent))

from src.collectors.yf_collector import YFCollector
from src.collectors.bcb_collector import BCBCollector

def run_initial_setup():
    print("⏳ [INÍCIO] Iniciando carga histórica de 365 dias...")
    
    # 1. Inicializa os Coletores
    yf = YFCollector()
    bcb = BCBCollector()
    
    # 2. Define a Lista de Elite (Sincronização de Metadados)
    elite_assets = [
        # BRASIL
        {'symbol': 'ITUB4.SA', 'name': 'Itaú Unibanco', 'category': 'Ação BR', 'sector': 'Financeiro'},
        {'symbol': 'PETR4.SA', 'name': 'Petrobras', 'category': 'Ação BR', 'sector': 'Energia'},
        {'symbol': 'VALE3.SA', 'name': 'Vale', 'category': 'Ação BR', 'sector': 'Mineração'},
        {'symbol': 'BPAC11.SA', 'name': 'BTG Pactual', 'category': 'Ação BR', 'sector': 'Financeiro'},
        {'symbol': 'ABEV3.SA', 'name': 'Ambev', 'category': 'Ação BR', 'sector': 'Consumo'},
        {'symbol': 'WEGE3.SA', 'name': 'WEG', 'category': 'Ação BR', 'sector': 'Industrial'},
        {'symbol': 'BBDC4.SA', 'name': 'Bradesco', 'category': 'Ação BR', 'sector': 'Financeiro'},
        {'symbol': 'BBAS3.SA', 'name': 'Banco do Brasil', 'category': 'Ação BR', 'sector': 'Financeiro'},
        {'symbol': 'SANB11.SA', 'name': 'Santander BR', 'category': 'Ação BR', 'sector': 'Financeiro'},
        {'symbol': 'JBSS32.SA', 'name': 'JBS', 'category': 'Ação BR', 'sector': 'Alimentos'},
        # EUA
        {'symbol': 'AAPL', 'name': 'Apple', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'GOOGL', 'name': 'Alphabet (Google)', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'MSFT', 'name': 'Microsoft', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'AMZN', 'name': 'Amazon', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'NVDA', 'name': 'NVIDIA', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'TSLA', 'name': 'Tesla', 'category': 'Ação EUA', 'sector': 'Automotivo'},
        {'symbol': 'META', 'name': 'Meta', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': 'NU', 'name': 'Nubank', 'category': 'Ação EUA', 'sector': 'Financeiro'},
        {'symbol': 'AMD', 'name': 'Advanced Micro Devices', 'category': 'Ação EUA', 'sector': 'Tecnologia'},
        {'symbol': '2222.SR', 'name': 'Saudi Aramco', 'category': 'Ação Mundo', 'sector': 'Energia'},
        # COMMODITIES, ÍNDICES, MOEDAS E CRIPTO
        {'symbol': 'CL=F', 'name': 'Petróleo Brent', 'category': 'Commodity', 'sector': 'Energia'},
        {'symbol': 'GC=F', 'name': 'Ouro', 'category': 'Commodity', 'sector': 'Segurança'},
        {'symbol': '^BVSP', 'name': 'Ibovespa', 'category': 'Índice', 'sector': 'Brasil'},
        {'symbol': '^GSPC', 'name': 'S&P 500', 'category': 'Índice', 'sector': 'EUA'},
        {'symbol': '^DJI',  'name': 'Dow Jones', 'category': 'Índice', 'sector': 'EUA'},
        {'symbol': 'USDBRL=X', 'name': 'Dólar/Real', 'category': 'Moeda', 'sector': 'Câmbio'},
        {'symbol': 'EURBRL=X', 'name': 'Euro/Real', 'category': 'Moeda', 'sector': 'Câmbio'},
        {'symbol': 'BTC-USD', 'name': 'Bitcoin', 'category': 'Cripto', 'sector': 'Tecnologia'},
        {'symbol': 'ETH-USD', 'name': 'Ethereum', 'category': 'Cripto', 'sector': 'Tecnologia'}
    ]

    # --- PASSO 1: Sincronizar Metadados (Registrar ativos nas tabelas) ---
    print("\n--- [Fase 1/3] Sincronizando Metadados ---")
    yf.sync_metadata(elite_assets)
    bcb.sync_metadata()

    # --- PASSO 2: Carga do Yahoo Finance (1 Ano) ---
    print("\n--- [Fase 2/3] Coletando Yahoo Finance (1y) ---")
    for asset in elite_assets:
        yf.fetch_and_save(asset['symbol'], period="1y")

    # --- PASSO 3: Carga do Banco Central (365 Dias) ---
    print("\n--- [Fase 3/3] Coletando Banco Central (365d) ---")
    for ind in bcb.indicators:
        bcb.fetch_bcb_data(ind['id'], ind['symbol'], days_back=365)

    print("\n✅ [SUCESSO] O banco 'finance.db' foi populado com sucesso!")

if __name__ == "__main__":
    run_initial_setup()


