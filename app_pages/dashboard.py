import streamlit as st
from database import get_user_tickets  # Para listar chamados do Helpdesk

def show():
    st.title("📊 Dashboard - Gestão Interna")

    # Verifica se o usuário está logado
    if "user" not in st.session_state:
        st.error("⚠️ Você precisa estar logado para acessar o sistema.")
        st.stop()

    user = st.session_state["user"]

    # Exibir informações básicas do usuário
    st.markdown(f"👤 **Usuário:** {user.get('nome', 'Não informado')}")
    st.markdown(f"📍 **Cargo:** {user.get('cargo', 'Não informado')}")
    st.markdown(f"🏬 **Loja:** {user.get('loja', 'Não informado')}")
    st.markdown("---")

    """
    # 📌 📊 Exibir cards diferentes por cargo 📊 📌
    cols1, cols2, cols3 = st.columns(3)

    if user["cargo"] == "Diretor de Operações (COO)":
        st.subheader("📊 Indicadores da Rede")
        with cols1:
            st.metric("Vendas Totais", "R$ 1.250.000", "+15%")
        with cols2:
            st.metric("Clientes Atendidos", "8.500", "+5%")
        with cols3:
            st.metric("Chamados em Aberto", "3", "-10%")

    elif user["cargo"] == "Gerente de Loja":
        st.subheader("📊 Indicadores da Loja")
        st.metric("Faturamento do Mês", "R$ 120.000", "+8%")
        st.metric("Clientes Atendidos", "900", "+3%")
        st.metric("Estoque Baixo", "5 produtos", "🚨")

    elif user["cargo"] == "Atendente":
        st.subheader("📊 Minhas Metas")
        st.metric("Vendas Realizadas", "75", "+10%")
        st.metric("Clientes Atendidos", "320", "+6%")

    else:
        st.info("⚠️ Nenhum dashboard disponível para este cargo.")
    

    st.markdown("---")
    """
    
    # 🆘 Helpdesk
    st.subheader("🆘 Meus Chamados")
    chamados = get_user_tickets(user["email"])

    if not chamados:
        st.info("Nenhum chamado aberto.")
    else:
        for chamado in chamados:
            with st.expander(f"📌 {chamado['titulo']} ({chamado['status']})"):
                st.write(f"**Descrição:** {chamado['descricao']}")
                #st.write(f"📅 **Data:** {chamado['data']}")

    # 📩 Botão para abrir novo chamado
    if st.button("📩 Abrir Novo Chamado no Helpdesk"):
        st.session_state.current_page = "helpdesk"
