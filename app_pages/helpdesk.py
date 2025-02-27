import streamlit as st
from database import get_user_tickets, update_ticket_status, get_pending_tickets, get_all_tickets
from auth import check_session
import app_pages.open_ticket as open_ticket  # Importa o novo arquivo para abertura de chamados

def show():
    """Exibe a página do Helpdesk"""
    user_data = check_session()

    if not user_data:
        st.warning("⚠️ Você precisa estar logado.")
        return

    st.title("🛠️ Helpdesk - Gestão de Chamados")

    # 🔹 Meus Chamados
    st.subheader("📌 Meus Chamados")
    tickets = get_user_tickets(user_data["email"])

    if tickets:
        for ticket in tickets:
            with st.expander(f"{ticket['titulo']} - {ticket['status']}"):
                st.write(f"**Descrição:** {ticket['descricao']}")
                st.write(f"**Categoria:** {ticket['categoria']}")
                st.write(f"**Urgência:** {ticket['urgencia']}")
                st.write(f"**Centro de Custo:** {ticket['loja']}")
                st.write(f"**Histórico:**")

                for event in ticket["historico"]:
                    st.write(f"- {event['acao']} ({event['responsavel']} - {event['data_hora']})")

    else:
        st.info("Nenhum chamado encontrado.")

    # 🔹 Aprovação de Chamados (Somente COO)
    if user_data["cargo"] == "Diretor de Operações (COO)":
        st.subheader("📝 Aprovação de Chamados")

        chamados_pendentes = get_pending_tickets("Pendente")

        if not chamados_pendentes:
            st.success("✅ Nenhum chamado pendente no momento.")
        else:
            for chamado in chamados_pendentes:
                with st.expander(f"📌 {chamado['titulo']} ({chamado['categoria']}) - {chamado['loja']}"):
                    st.write(f"**Descrição:** {chamado['descricao']}")
                    st.write(f"**Aberto por:** {chamado['usuario']} em {chamado['data_abertura']}")
                    
                    # 🔹 Selecionar responsáveis
                    st.subheader("👥 Definir Responsáveis")
                    responsavel_financeiro = st.selectbox("📑 Analista Financeiro", ["Nenhum", "Maria Silva", "Carlos Mendes"])
                    responsavel_outro = st.text_input("🔧 Outro Responsável (TI, Técnico, etc.)")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Aprovar Chamado {chamado['id']}", key=f"approve_{chamado['id']}"):
                            update_ticket_status(
                                chamado["id"], "Aprovado pelo COO", user_data["email"], 
                                responsavel_financeiro, "Emerson Soares", responsavel_outro
                            )
                            st.success(f"✅ Chamado {chamado['id']} aprovado e responsáveis definidos!")
                            st.experimental_rerun()

                    with col2:
                        if st.button(f"❌ Rejeitar Chamado {chamado['id']}", key=f"reject_{chamado['id']}"):
                            update_ticket_status(chamado["id"], "Rejeitado", user_data["email"])
                            st.warning(f"❌ Chamado {chamado['id']} rejeitado.")
                            st.experimental_rerun()

    # 🔹 Botão para abrir chamado
    st.subheader("➕ Novo Chamado")
    if st.button("📌 Abrir Chamado"):
        st.session_state["abrir_chamado"] = True  # Ativa o formulário
    
    # 🔹 Exibir formulário somente se o botão for pressionado
    if st.session_state.get("abrir_chamado", False):
        open_ticket.show()  # Chama a função do novo arquivo open_ticket.py


    if st.button("🔍 Listar Todos os Chamados"):
        chamados = get_all_tickets()
        for chamado in chamados:
            st.write(f"{chamado['titulo']} - {chamado['status']}")
