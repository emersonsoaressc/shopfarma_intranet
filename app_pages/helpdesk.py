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
            with st.expander(f"📌 {chamado['loja']} - {chamado['titulo']} - {chamado['status']}"):
                st.write(f"**Descrição:** {ticket['descricao']}")
                st.write(f"**Categoria:** {ticket['categoria']}")
                st.write(f"**Urgência:** {ticket['urgencia']}")
                st.write(f"**Centro de Custo:** {ticket['loja']}")
                st.write(f"**Histórico:**")

                for event in ticket["historico"]:
                    st.write(f"- {event['acao']} ({event['responsavel']} - {event['data_hora']})")

    else:
        st.info("Nenhum chamado encontrado.")

 # 🔹 Se usuário for COO, exibe a seção de aprovação
    if user_data["cargo"] == "Diretor de Operações (COO)":
        st.subheader("📝 Aprovação de Chamados")
        chamados_pendentes = get_pending_tickets()

        if chamados_pendentes:
            for chamado in chamados_pendentes:
                with st.expander(f"📌 {chamado['loja']} - {chamado['titulo']} - {chamado['status']}"):
                    st.write(f"**Descrição:** {chamado['descricao']}")
                    st.write(f"**Categoria:** {chamado['categoria']}")
                    st.write(f"**Urgência:** {chamado['urgencia']}")
                    st.write(f"**Centro de Custo:** {chamado['loja']}")

                    # Exibir histórico do chamado
                    st.write("**Histórico:**")
                    for event in chamado["historico"]:
                        st.write(f"- {event['acao']} ({event['responsavel']} - {event['data_hora']})")

                    # Aprovação do COO
                    if st.button(f"✅ Aprovar {chamado['titulo']}", key=f"approve_{chamado['id']}"):
                        update_ticket_status(chamado["id"], "Aprovado pelo COO", user_data["email"])
                        st.success(f"✅ Chamado {chamado['titulo']} aprovado!")
                        st.experimental_rerun()
        else:
            st.success("✅ Nenhum chamado pendente no momento.")
            
            
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
