import streamlit as st

def show():
    # 🔹 Garantir que "current_page" existe no session_state
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "dashboard"  # Página inicial padrão

    st.title("📊 Dashboard Principal")

    # 🔹 Exibir informações do usuário logado
    if "user" in st.session_state:
        user_data = st.session_state["user"]
        st.markdown(f"👤 **Usuário:** {user_data['nome']} ({user_data['cargo']})")

    # 🔹 Layout dos cards principais
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📦 Gestão de Estoque"):
            st.session_state["current_page"] = "estoque"
            st.experimental_rerun()

    with col2:
        if st.button("👥 Gestão de Colaboradores"):
            st.session_state["current_page"] = "colaboradores"
            st.experimental_rerun()

    with col3:
        if st.button("🛠️ Helpdesk"):
            st.session_state["current_page"] = "helpdesk"
            st.experimental_rerun()

    # 🔹 Controle de navegação entre as páginas
    if st.session_state["current_page"] == "estoque":
        st.subheader("📦 Gestão de Estoque")
        st.write("Aqui ficará a funcionalidade de gestão de estoque.")

    elif st.session_state["current_page"] == "colaboradores":
        st.subheader("👥 Gestão de Colaboradores")
        st.write("Aqui ficará a funcionalidade de gestão de colaboradores.")

    elif st.session_state["current_page"] == "helpdesk":
        st.subheader("🛠️ Helpdesk")
        st.write("Aqui ficará o sistema de suporte interno.")

    # 🔹 Menu lateral para logout
    st.sidebar.title("📌 Opções")
    if st.sidebar.button("🔄 Logout"):
        st.session_state.clear()
        st.experimental_rerun()
