import streamlit as st
from auth import check_session, logout
from pages import login, dashboard, helpdesk
from teste_firebase import teste_firebase

# Configuração da página
st.set_page_config(page_title="Shopfarma - Gestão", layout="wide")

# Verifica se o usuário já está logado
user_data = check_session()

if not user_data:
    login.show()
else:
    dashboard.show()

    # Gerenciar as páginas disponíveis
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    menu = {
        "dashboard": dashboard.show,
        "helpdesk": helpdesk.show
    }

    if st.session_state.current_page in menu:
        menu[st.session_state.current_page]()

teste_firebase()