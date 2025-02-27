import streamlit as st

def show():
    # 🔹 Inicializa session_state["current_page"] se não existir
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "dashboard"  # Define o valor padrão

    st.title("📊 Dashboard Principal")

    # 🔹 Exibir informações do usuário logado
    if "user" in st.session_state and st.session_state["user"]:
        user_data = st.session_state["user"]
        st.markdown(f"👤 **Usuário:** {user_data.get('nome', 'Desconhecido')} ({user_data.get('cargo', 'Sem cargo')})")
    else:
        st.error("⚠️ Usuário não autenticado. Faça login novamente.")
        st.stop()

    # 🔹 Criar botões para navegação entre as páginas
    col1, col2, col3 = st.columns(3)

    with col1:
        estoque_btn = st.button("📦 Gestão de Estoque", key="btn_estoque")
    with col2:
        colaboradores_btn = st.button("👥 Gestão de Colaboradores", key="btn_colaboradores")
    with col3:
        helpdesk_btn = st.button("🛠️ Helpdesk", key="btn_helpdesk")

    # 🔹 Atualiza a página com base na escolha do botão
    if estoque_btn:
        st.session_state["current_page"] = "estoque"
    elif colaboradores_btn:
        st.session_state["current_page"] = "colaboradores"
    elif helpdesk_btn:
        st.session_state["current_page"] = "helpdesk"

    # 🔹 Exibir conteúdos das páginas selecionadas dinamicamente
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
    if st.sidebar.button("🔄 Logout", key="logout"):
        st.session_state.clear()
        st.experimental_rerun()
