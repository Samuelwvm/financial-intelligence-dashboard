import streamlit as st
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))
from src._ui import CSS, sec_header

st.set_page_config(page_title="Entenda - Radar Financeiro", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

st.markdown("""
<style>
.termo-badge {
    font-size: 9px !important;
    font-weight: 700 !important;
    letter-spacing: .8px;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 4px;
    border: 0.5px solid;
    white-space: nowrap;
    display: inline-block;
    margin-bottom: 12px;
}
.termo-body {
    font-size: 14px !important;
    line-height: 1.8;
    color: #7080a0 !important;
    margin-bottom: 10px;
}
.termo-body strong {
    color: #b0b8d8 !important;
    font-weight: 600 !important;
}
.termo-exemplo {
    background: #0f1118;
    border-left: 2px solid #2a3050;
    border-radius: 0 6px 6px 0;
    padding: 10px 14px;
    font-size: 13px !important;
    color: #6a7890 !important;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)

CATS = {
    'Mercado':    ('#0d2e1a', '#1a4a2a', '#4caf7d'),
    'Risco':      ('#2e0d0d', '#4a1a1a', '#e05a5a'),
    'Renda Fixa': ('#0d1929', '#1a2a40', '#7eb8f7'),
    'Cambio':     ('#1e1e0d', '#3a3a1a', '#e0b84c'),
    'Cripto':     ('#1e120d', '#3a2a1a', '#f7931a'),
    'Indicadores':('#150d29', '#2a1a4a', '#a07ef7'),
}

GLOSSARIO = [
    {'termo':'Acao','cat':'Mercado',
     'def':'Uma <strong>acao</strong> e um pedaco de uma empresa. Quando voce compra uma acao da Petrobras, voce se torna socio de uma fracao dela e tem direito a uma parte dos lucros (dividendos) e valorizacao do negocio.',
     'ex':'Se a Petrobras sobe 10% e voce tem R$ 1.000 investidos, seu patrimonio vai para R$ 1.100.'},
    {'termo':'Ibovespa (IBOV)','cat':'Mercado',
     'def':'O <strong>Ibovespa</strong> e o principal indice da bolsa brasileira (B3). Ele reune as acoes mais negociadas do pais e funciona como um termometro da economia. Quando o Ibovespa sobe, em geral as empresas do Brasil estao indo bem.',
     'ex':'Ibovespa em 130.000 pontos vs 120.000 = crescimento de ~8% no periodo.'},
    {'termo':'S&P 500','cat':'Mercado',
     'def':'O <strong>S&P 500</strong> e o principal indice dos EUA, composto pelas 500 maiores empresas americanas - Apple, Microsoft, Google, Amazon e mais. E o maior termometro da economia global.',
     'ex':'Uma queda de 5% no S&P 500 costuma puxar a bolsa brasileira para baixo tambem.'},
    {'termo':'Dow Jones','cat':'Mercado',
     'def':'O <strong>Dow Jones</strong> e o indice mais antigo dos EUA, composto pelas 30 maiores e mais tradicionais empresas americanas. E mais conservador que o S&P 500 e reflete a velha economia americana.',
     'ex':'Boeing, Coca-Cola, Goldman Sachs e Apple fazem parte do Dow Jones.'},
    {'termo':'Dividendo','cat':'Mercado',
     'def':'<strong>Dividendos</strong> sao a parte do lucro que a empresa distribui para seus acionistas. Funciona como um rendimento passivo - voce recebe periodicamente sem precisar vender a acao.',
     'ex':'Investiu R$ 10.000 com dividend yield de 8% ao ano, recebe ~R$ 800/ano.'},
    {'termo':'Liquidez','cat':'Mercado',
     'def':'<strong>Liquidez</strong> e a facilidade de comprar ou vender um ativo rapidamente sem perder valor. Acoes de grandes empresas tem alta liquidez. Imoveis tem baixa liquidez.',
     'ex':'Uma acao com volume de R$ 500 milhoes/dia tem altissima liquidez.'},
    {'termo':'Volatilidade','cat':'Risco',
     'def':'<strong>Volatilidade</strong> mede o quanto o preco de um ativo oscila ao longo do tempo. Alta volatilidade = sobe e desce muito. Baixa volatilidade = mais estavel. Calculamos como o desvio padrao dos retornos diarios, anualizado.',
     'ex':'Bitcoin pode ter volatilidade de 80% ao ano. Tesouro Selic tem volatilidade proxima de zero.'},
    {'termo':'Retorno','cat':'Risco',
     'def':'<strong>Retorno</strong> e o quanto um investimento cresceu (ou caiu) em um periodo. O retorno nos cards e sempre referente ao periodo selecionado.',
     'ex':'Comprou a R$ 50 e vendeu a R$ 60 - retorno de 20%.'},
    {'termo':'Risco vs Retorno','cat':'Risco',
     'def':'Na renda variavel, <strong>maior risco geralmente vem com maior potencial de retorno</strong>. O grafico de Risco vs Retorno do dashboard mostra exatamente essa relacao para cada ativo da sua carteira.',
     'ex':'Bitcoin: alto risco, alto retorno historico. Tesouro Selic: baixo risco, retorno menor.'},
    {'termo':'Diversificacao','cat':'Risco',
     'def':'<strong>Diversificar</strong> e nao colocar todos os ovos na mesma cesta. Misturar acoes brasileiras, americanas, cripto e renda fixa reduz o risco total da carteira.',
     'ex':'Carteira 100% em uma empresa vs carteira com 20 ativos: o risco cai drasticamente.'},
    {'termo':'Selic','cat':'Renda Fixa',
     'def':'A <strong>Selic</strong> e a taxa basica de juros do Brasil, definida pelo Banco Central a cada 45 dias. Ela influencia tudo: rendimento da poupanca, custo do credito e o comportamento da bolsa. Selic alta = renda fixa mais atrativa.',
     'ex':'Selic a 13,75% ao ano = quem investe no Tesouro Selic ganha ~13,75% com baixissimo risco.'},
    {'termo':'CDI','cat':'Renda Fixa',
     'def':'O <strong>CDI</strong> (Certificado de Deposito Interbancario) e a taxa que os bancos cobram entre si. Na pratica, anda colado a Selic e e usado como referencia para quase toda a renda fixa brasileira.',
     'ex':'Um CDB que rende 110% do CDI e melhor que um que rende 90% do CDI.'},
    {'termo':'IPCA','cat':'Renda Fixa',
     'def':'O <strong>IPCA</strong> e o indice oficial de inflacao do Brasil. Um investimento bom e aquele que rende <strong>acima do IPCA</strong> - senao, seu dinheiro perde poder de compra mesmo rendendo.',
     'ex':'IPCA a 5% ao ano e seu investimento rendeu 4% - voce perdeu 1% de poder de compra.'},
    {'termo':'Cambio','cat':'Cambio',
     'def':'<strong>Cambio</strong> e a taxa de conversao entre duas moedas. Dolar a R$ 5,20 significa que voce precisa de R$ 5,20 para comprar US$ 1,00. O cambio sobe e desce conforme a economia, juros e fluxo de capital.',
     'ex':'Dolar subindo = importados ficam mais caros, exportacoes brasileiras ficam mais competitivas.'},
    {'termo':'Dolar Comercial','cat':'Cambio',
     'def':'O <strong>dolar comercial</strong> e a taxa usada em transacoes financeiras e comerciais - importacoes, exportacoes, remessas ao exterior. E diferente do dolar turismo (que inclui spread do banco).',
     'ex':'Dolar comercial: R$ 5,20. Dolar turismo: R$ 5,60 (o banco cobra a diferenca).'},
    {'termo':'Bitcoin (BTC)','cat':'Cripto',
     'def':'O <strong>Bitcoin</strong> e a primeira e maior criptomoeda do mundo, criada em 2009. Funciona numa rede descentralizada (blockchain) e tem emissao limitada a 21 milhoes de unidades. E chamado de ouro digital.',
     'ex':'Em 2020 o BTC valia ~US$ 10.000. Em 2021 chegou a US$ 69.000. Alta volatilidade.'},
    {'termo':'Ethereum (ETH)','cat':'Cripto',
     'def':'O <strong>Ethereum</strong> e a segunda maior criptomoeda e a principal plataforma para contratos inteligentes e aplicacoes descentralizadas (DeFi, NFTs).',
     'ex':'Criar um NFT ou usar um aplicativo DeFi consome ETH como taxa.'},
    {'termo':'Blockchain','cat':'Cripto',
     'def':'<strong>Blockchain</strong> e a tecnologia por tras das criptomoedas. E um banco de dados distribuido - registros copiados em milhares de computadores, tornando as transacoes praticamente impossiveis de falsificar.',
     'ex':'Uma transacao de Bitcoin fica registrada permanentemente em todos os nos da rede.'},
    {'termo':'P/L (Preco/Lucro)','cat':'Indicadores',
     'def':'O <strong>P/L</strong> indica quantos anos de lucro voce pagaria pela empresa ao preco atual. P/L muito alto pode indicar acao cara; P/L baixo pode ser uma pechincha - ou uma armadilha.',
     'ex':'Empresa com P/L 8 vs concorrente com P/L 25 = a primeira esta mais barata pelo lucro.'},
    {'termo':'Dividend Yield','cat':'Indicadores',
     'def':'O <strong>Dividend Yield</strong> mostra quanto a empresa paga em dividendos em relacao ao preco da acao, em porcentagem ao ano. E o rendimento passivo do acionista.',
     'ex':'Acao a R$ 20 que paga R$ 2/ano em dividendos - Dividend Yield de 10% ao ano.'},
    {'termo':'Market Cap (Valor de Mercado)','cat':'Indicadores',
     'def':'O <strong>Market Cap</strong> e o valor total de uma empresa na bolsa: preco da acao x numero de acoes. Serve para comparar o tamanho relativo das empresas.',
     'ex':'Acao a R$ 50 x 1 bilhao de acoes = Market Cap de R$ 50 bilhoes.'},
]

# Render
st.markdown(
    '<div class="pg-title">Entenda o Mercado</div>'
    '<div class="pg-subtitle">Glossario interativo - clique em qualquer termo para expandir</div>',
    unsafe_allow_html=True,
)

busca = st.text_input('_', placeholder='Buscar termo... ex: volatilidade, selic, bitcoin',
                      label_visibility='collapsed')

cat_sel = st.radio('_', ['Todos'] + list(CATS.keys()),
                   horizontal=True, label_visibility='collapsed')

st.markdown('<hr class="divider" style="margin-top:10px;"/>', unsafe_allow_html=True)

filtrado = GLOSSARIO
if cat_sel != 'Todos':
    filtrado = [t for t in filtrado if t['cat'] == cat_sel]
if busca:
    q = busca.lower()
    filtrado = [t for t in filtrado if q in t['termo'].lower() or q in t['def'].lower()]

if not filtrado:
    st.info('Nenhum termo encontrado.')
else:
    st.markdown(
        f'<div style="font-size:11px;color:#3a3f55;margin-bottom:14px;">'
        f'{len(filtrado)} termo{"s" if len(filtrado)!=1 else ""} encontrado{"s" if len(filtrado)!=1 else ""}'
        f'</div>', unsafe_allow_html=True,
    )
    for item in filtrado:
        cat = item['cat']
        bg, border, txt = CATS.get(cat, ('#1a1a2a', '#2a2a3a', '#8090b0'))
        with st.expander(item['termo']):
            st.markdown(
                f'<span class="termo-badge" style="background:{bg};border-color:{border};color:{txt};">{cat}</span>'
                f'<div class="termo-body">{item["def"]}</div>'
                f'<div class="termo-exemplo">{item["ex"]}</div>',
                unsafe_allow_html=True,
            )