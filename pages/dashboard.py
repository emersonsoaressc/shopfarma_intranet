import streamlit as st
from auth import check_session, logout

def show():
    """Exibe a dashboard principal"""
    user_data = check_session()

    if not user_data:
        st.warning("⚠️ Você precisa estar logado.")
        return

    st.image('images/logo_shopfarma_sem_fundo.png', width=250)
    st.markdown(f"### 👤 Bem-vindo, {user_data['nome']} ({user_data['cargo']})")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if user_data["cargo"] in ["COO", "Gestor"]:
            if st.button("🛒 Gestão de Estoque"):
                st.session_state.current_page = "estoque"

    with col2:
        if user_data["cargo"] in ["COO", "Assistente"]:
            if st.button("👥 Gestão de Colaboradores"):
                st.session_state.current_page = "colaboradores"

    with col3:
        if st.button("🛠️ Helpdesk"):
            st.session_state.current_page = "helpdesk"

    with col4:
        logout()

    if st.session_state.current_page == "estoque":
        st.title("📦 Gestão de Estoque")
    elif st.session_state.current_page == "colaboradores":
        st.title("👥 Gestão de Colaboradores")
    elif st.session_state.current_page == "helpdesk":
        st.title("🛠️ Helpdesk")
