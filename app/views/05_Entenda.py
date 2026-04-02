# views /05_Entenda.py
# Página de glossário interativo — termos financeiros explicados de forma simples e visual.

import streamlit as st
from pathlib import Path
import sys

#root = Path(__file__).parent.parent.parent
#sys.path.append(str(root))

from src._ui import sec_header, page_footer

st.markdown("""
<style>
.termo-badge {
    font-size: 11px !important;
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
    font-size: 16px !important;
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
    font-size: 15px !important;
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
    {'termo':'Ação','cat':'Mercado',
     'def':'Uma <strong>ação</strong> é um pedaço de uma empresa. Quando voce compra uma ação da Petrobras, voce se torna socio de uma fração dela e tem direito a uma parte dos lucros (dividendos) e da valorização do negocio.',
     'ex':'Se a Petrobras sobe 10% e você tem R\$1.000 investidos, seu patrimônio vai para R\$1.100.'},

    {'termo':'Ibovespa (IBOV)','cat':'Mercado',
     'def':'O <strong>Ibovespa</strong> e o principal índice da bolsa brasileira (B3). Ele reune as ações mais negociadas do país e funciona como um termometro da economia. Quando o Ibovespa sobe, em geral as empresas do Brasil estao indo bem.',
     'ex':'Ibovespa em 130.000 pontos vs 120.000 = crescimento de ~8% no periodo.'},

    {'termo':'S&P 500','cat':'Mercado',
     'def':'O <strong>S&P 500</strong> e o principal índice dos EUA, composto pelas 500 maiores empresas americanas - Apple, Microsoft, Google, Amazon e mais. É o maior termometro da economia global.',
     'ex':'Uma queda de 5% no S&P 500 costuma puxar a bolsa brasileira para baixo tambem.'},

    {'termo':'Dow Jones','cat':'Mercado',
     'def':'O <strong>Dow Jones</strong> é o índice mais antigo dos EUA, composto pelas 30 maiores e mais tradicionais empresas americanas. É mais conservador que o S&P 500 e reflete a velha economia americana.',
     'ex':'Boeing, Coca-Cola, Goldman Sachs e Apple fazem parte do Dow Jones.'},

    {'termo':'Dividendo','cat':'Mercado',
     'def':'<strong>Dividendos</strong> são a parte do lucro que a empresa distribui para seus acionistas. Funciona como um rendimento passivo - você recebe periodicamente sem precisar vender a ação.',
     'ex':'Investiu 10.000 reais com $ Dividend yield (Rendimento de dividendos) $ de 8% ao ano, recebe ~R$ 800/ano.'},

    {'termo':'Liquidez','cat':'Mercado',
     'def':'<strong>Liquidez</strong> é a facilidade de comprar ou vender um ativo rapidamente sem perder valor. Ações de grandes empresas tem alta liquidez. Imoveis tem baixa liquidez.',
     'ex':'Uma ação com volume de R$ 500 milhoes/dia tem altissima liquidez.'},

    {'termo':'Volatilidade','cat':'Risco',
     'def':'<strong>Volatilidade</strong> mede o quanto o preço de um ativo oscila ao longo do tempo. Alta volatilidade = sobe e desce muito. Baixa volatilidade = mais estavel. Calculamos como o desvio padrão dos retornos diarios, anualizado.',
     'ex':'Bitcoin pode ter volatilidade de 80% ao ano. Tesouro Selic tem volatilidade próxima de zero.'},

    {'termo':'Retorno','cat':'Risco',
     'def':'<strong>Retorno</strong> é o quanto um investimento cresceu (ou caiu) em um período. O retorno nos cards e sempre referente ao período selecionado.',
     'ex':'Comprou a R\$50 e vendeu a R\$60 - retorno de 20%.'},

    {'termo':'Risco vs Retorno','cat':'Risco',
     'def':'Na renda variável, <strong>maior risco geralmente vem com maior potencial de retorno</strong>. O gráfico de Risco vs Retorno do dashboard mostra exatamente essa relação para cada ativo da sua carteira.',
     'ex':'Bitcoin: alto risco, alto retorno histórico. Tesouro Selic: baixo risco, retorno menor.'},

    {'termo':'Diversificação','cat':'Risco',
     'def':'<strong>Diversificar</strong> é não colocar todos os ovos na mesma cesta. Misturar ações brasileiras, americanas, cripto e renda fixa reduz o risco total da carteira.',
     'ex':'Carteira 100% em uma empresa X carteira com 20 ativos: o risco cai drasticamente.'},

    {'termo':'Selic','cat':'Renda Fixa',
     'def':'A <strong>Selic</strong> é a taxa basica de juros do Brasil, definida pelo Banco Central a cada 45 dias. Ela influencia tudo: rendimento da poupança, custo do crédito e o comportamento da bolsa. Selic alta = renda fixa mais atrativa.',
     'ex':'Selic a 13,75% ao ano = quem investe no Tesouro Selic ganha ~13,75% com baixissimo risco.'},

    {'termo':'CDB','cat':'Renda Fixa',
     'def':'O <strong>CDB</strong> (Certificado de Depósito Bancário) é um título de renda fixa emitido pelos bancos para captar dinheiro. Você empresta dinheiro para o banco e recebe juros em troca. O rendimento pode ser pré-fixado, pós-fixado (geralmente atrelado ao CDI) ou indexado à inflação.',
     'ex':'Empresta 10.000 reais por 1 ano em um CDB que rende 110% do CDI - ao final do ano recebe o valor investido + os juros. 110% do CDI - isso significa que se o CDI for 10% ao ano, seu rendimento será de 11% ao ano. Se o CDI subir para 12%, seu rendimento sobe para 13,2%. CDBs pós-fixados acompanham as variações do CDI. CDBs pré-fixados tem a taxa definida no momento da aplicação, então não são afetados por mudanças no CDI.'},

    {'termo':'CDI','cat':'Renda Fixa',
     'def':'O <strong>CDI</strong> (Certificado de Deposito Interbancário) é a taxa que os bancos cobram entre si. Na pratica, anda colado a Selic e é usado como referência para quase toda a renda fixa brasileira.',
     'ex':'Um CDB que rende 110% do CDI é melhor que um que rende 90% do CDI. Se a Selic subir, o CDI sobe junto, e seu rendimento acompanha. CDI é a taxa mais comum para investimentos de renda fixa pós-fixados.'},

    {'termo':'IPCA','cat':'Renda Fixa',
     'def':'O <strong>IPCA</strong> é o indice oficial de inflação do Brasil. Um investimento bom é aquele que rende <strong>acima do IPCA</strong> - caso contrário, seu dinheiro perde poder de compra mesmo rendendo. Investimentos indexados ao IPCA garantem que seu dinheiro acompanhe a inflação, preservando o poder de compra.',
     'ex':'IPCA a 5% ao ano e seu investimento rendeu 4% - voce perdeu 1% de poder de compra.'},

    {'termo':'Tesouro Direto','cat':'Renda Fixa',
     'def':'O <strong>Tesouro Direto</strong> é um programa do governo brasileiro que permite pessoas físicas comprarem títulos públicos pela internet. É uma forma segura e acessível de investir em renda fixa, com opções pré-fixadas, pós-fixadas e indexadas à inflação.',
     'ex':'Tesouro IPCA+ 2035: título do Tesouro Direto que paga IPCA + uma taxa fixa, garantindo rendimento real acima da inflação.'},

    {'termo':'Spread','cat':'Câmbio',
     'def':'O <strong>spread</strong> é a diferença entre o preço que o banco paga para pegar dinheiro emprestado (de você) e o preço que ele cobra para emprestar esse mesmo dinheiro (para outros).',
     'ex':'O banco toma R$ 1.000 de você pagando 10% de juros e empresta para o seu vizinho cobrando 40%; esses 30% de diferença são o spread, a margem de lucro do banco.'},

    {'termo':'Câmbio','cat':'Câmbio',
     'def':'<strong>Câmbio</strong> é a taxa de conversão entre duas moedas. Dólar a R\$ 5,20 significa que voce precisa de R\$ 5,20 para comprar US$ 1,00. O cambio sobe e desce conforme a economia, juros e fluxo de capital.',
     'ex':'Dólar subindo = importados ficam mais caros, exportações brasileiras ficam mais competitivas.'},

    {'termo':'Dólar Comercial','cat':'Câmbio',
     'def':'O <strong>dólar comercial</strong> é a taxa usada em transações financeiras e comerciais - importações, exportações, remessas ao exterior. É diferente do dólar turismo (que inclui spread do banco).',
     'ex':'Dólar comercial: R\$ 5,20. Dólar turismo: R\$ 5,60 (o banco cobra a diferenca).'},

    {'termo':'Bitcoin (BTC)','cat':'Cripto',
     'def':'O <strong>Bitcoin</strong> é a primeira e maior criptomoeda do mundo, criada em 2009. Funciona numa rede descentralizada (blockchain) e tem emissão limitada a 21 milhoes de unidades. É chamado de ouro digital.',
     'ex':'Em 2020 o BTC valia ~US\$ 10.000. Em 2021 chegou a US\$ 69.000. Alta volatilidade.'},

    {'termo':'Ethereum (ETH)','cat':'Cripto',
     'def':'O <strong>Ethereum</strong> é a segunda maior criptomoeda, é a principal plataforma para contratos inteligentes e aplicações descentralizadas (DeFi, NFTs).',
     'ex':'Criar um NFT ou usar um aplicativo DeFi consome ETH como taxa.'},

    {'termo':'Blockchain','cat':'Cripto',
     'def':'<strong>Blockchain</strong> é a tecnologia por trás das criptomoedas. É um banco de dados distribuído - registros copiados em milhares de computadores, tornando as transacoes praticamente impossiveis de falsificar.',
     'ex':'Uma transação de Bitcoin fica registrada permanentemente em todos os nós da rede.'},

    {'termo':'P/L (Preço/Lucro)','cat':'Indicadores',
     'def':'O <strong>P/L</strong> indica quantos anos de lucro você pagaria pela empresa ao preço atual. P/L muito alto pode indicar ação cara; P/L baixo pode ser uma pechincha - ou uma armadilha.',
     'ex':'Ação a R\$ 50 com lucro por ação de R\$ 5 tem P/L de 10 - você pagaria 10 anos de lucro para comprar essa ação. O P/L de 10 significa que você leva 10 anos para recuperar o dinheiro que investiu através do lucro da empresa. Comparar o P/L de uma empresa com seus pares e com sua própria história ajuda a entender se a ação está cara ou barata.'},

    {'termo':'Dividend Yield','cat':'Indicadores',
     'def':'O <strong>Dividend Yield</strong> mostra quanto a empresa paga em dividendos em relação ao preço da ação, em porcentagem ao ano. É o rendimento passivo do acionista. Resumindo é Rendimento de dividendos, o retorno que o investidor recebe ao comprar uma ação.',
     'ex':'Ação a R/$ 100 que paga R/$ 10/ano em dividendos - Dividend Yield de 10% ao ano. Ou seja, para cada 100 reais investidos, a empresa te devolve 10 reais por ano.'},

    {'termo':'Market Cap (Valor de Mercado)','cat':'Indicadores',
     'def':'O <strong>Market Cap</strong> é o valor total de uma empresa na bolsa: preço da ação x número de ações. Serve para comparar o tamanho relativo das empresas.',
     'ex':'Ação a R\$ 50 x 1 bilhão de ações = Market Cap de R\$ 50 bilhões.'},
]

# ─── RENDER ────────────────────────────────────────────────────────────────

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

st.markdown(page_footer(), unsafe_allow_html=True)