import streamlit as st

def show_sidebar():
    # Ícones no topo
    st.sidebar.image("images/logo_shopfarma_sem_fundo.png", width=200)

    # Seção de Usuário
    if "user" in st.session_state and st.session_state["user"]:
        user_data = st.session_state["user"]
        st.sidebar.markdown(f"👤 **{user_data.get('nome', 'Usuário')}**")
        st.sidebar.markdown(f"📍 {user_data.get('cargo', 'Cargo não informado')}")

        # Botão para acessar perfil
        if st.sidebar.button("⚙️ Meu Perfil", key="meu_perfil"):
            st.session_state.current_page = "perfil"

    st.sidebar.markdown("---")

    # Navegação do sistema
    menu = {
        "📊 Dashboard": "dashboard",
        "📝 Aprovar Usuários": "aprovar_usuarios",
        "👥 Colaboradores": "colaboradores",
        "📦 Estoque": "estoque",
        "🆘 Helpdesk": "helpdesk"
    }

    for label, page in menu.items():
        if st.sidebar.button(label, key=f"menu_{page}"):
            st.session_state.current_page = page

    st.sidebar.markdown("---")

    # Botão de logout
    if st.sidebar.button("🔄 Logout", key="logout"):
        st.session_state.pop("user", None)
        st.experimental_rerun()
