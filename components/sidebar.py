import streamlit as st

def show():
    # Se o usuário não estiver logado, não exibir o sidebar
    if "user" not in st.session_state or not st.session_state["user"]:
        return  

    user = st.session_state["user"]

    with st.sidebar:
        st.image("images/logo_shopfarma_sem_fundo.png", width=200)

        st.markdown(f"### 👤 {user['nome']}")
        st.markdown(f"📍 {user['cargo']}")

        st.divider()

        # Menu de navegação
        menu = {
            "📊 Dashboard": "dashboard",
            "🆘 Helpdesk": "helpdesk"
        }

        if user["cargo"] == "Diretor de Operações (COO)":
            menu["👥 Aprovar Usuários"] = "aprovar_usuarios"
            menu["🏬 Gestão de Colaboradores"] = "colaboradores"

        if user["cargo"] in ["Diretor de Operações (COO)", "Gerente de Loja"]:
            menu["📦 Gestão de Estoque"] = "estoque"

        page = st.radio("📌 Opções", list(menu.keys()), key="menu_sidebar")

        if page:
            st.session_state.current_page = menu[page]

        st.divider()

        if st.button("🔄 Logout", key="logout_sidebar"):
            st.session_state.pop("user", None)
            st.session_state.pop("current_page", None)
            st.experimental_rerun()
