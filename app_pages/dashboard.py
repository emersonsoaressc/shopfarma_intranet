import streamlit as st
from database import get_user_tickets, get_pending_users, approve_user  # Para listar chamados do Helpdesk

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
    
    # 🔹 Exibir Aprovação de Usuários (Apenas para COO)
    if user["cargo"] == "Diretor de Operações (COO)":
        st.subheader("📝 Aprovação de Usuários")
        usuarios_pendentes = get_pending_users()

        if not usuarios_pendentes:
            st.success("✅ Nenhum usuário pendente no momento.")
        else:
            for usuario in usuarios_pendentes:
                with st.expander(f"📌 {usuario['nome']} ({usuario['email']})"):
                    st.write(f"📍 **Cargo:** {usuario['cargo']}")
                    st.write(f"🏬 **Loja:** {usuario['loja'] or 'Não definido'}")
                    st.write(f"📞 **WhatsApp:** {usuario['whatsapp']}")

                    if st.button(f"✅ Aprovar {usuario['nome']}", key=f"approve_{usuario['email']}"):
                        approve_user(usuario["email"])
                        st.success(f"✅ Usuário {usuario['nome']} aprovado com sucesso!")
                        st.experimental_rerun()  # Atualiza a página após aprovação

    st.markdown("---")
    