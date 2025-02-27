import streamlit as st
from auth import check_session, logout
import app_pages.dashboard as dashboard
import app_pages.login as login
import app_pages.helpdesk as helpdesk

# 🔹 Verifica se há usuário logado
if "user" not in st.session_state or not st.session_state["user"]:
    login.show()  # Exibe a tela de login
    st.stop()  # Impede o carregamento do restante da página

# 🔹 Somente exibe a sidebar SE o usuário estiver logado
st.sidebar.image('images/logo_shopfarma_sem_fundo.png', width=150)
user_data = st.session_state["user"]
st.sidebar.markdown(f"👤 **Usuário:** {user_data.get('nome', 'Desconhecido')} ({user_data.get('cargo', 'Sem cargo')})")

# Menus dinâmicos baseados no cargo
menu = {
    "Dashboard": dashboard.show,
    "Helpdesk": helpdesk.show,
    "Sair": logout
}
escolha = st.sidebar.selectbox("📌 Opções", list(menu.keys()))

# Chama a função correspondente ao menu escolhido
menu[escolha]()
