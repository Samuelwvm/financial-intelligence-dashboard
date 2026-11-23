# app/Home.py
# Página principal — base para navegação entre as seções, com logo e configuração de layout. 

import streamlit as st
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from src._ui import CSS

st.set_page_config(page_title="Easy Finance", page_icon="assets/wallet_logo.png", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

#Logo da sidebar e navegação
st.logo("assets/wallet_logo.png", icon_image="assets/wallet_logo.png")

pg = st.navigation([
    st.Page("views/01_Home.py",    title="Home",    default=True),
    st.Page("views/02_Brasil.py",  title="Brasil"),
    st.Page("views/03_Mundo.py",   title="Mundo"),
    st.Page("views/04_Cripto.py",  title="Cripto"),
    st.Page("views/05_Entenda.py", title="Entenda"),
])

pg.run()