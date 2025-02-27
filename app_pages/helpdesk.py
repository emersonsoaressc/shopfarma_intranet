import streamlit as st
from database import create_ticket, get_user_tickets, update_ticket_status, upload_file
from auth import check_session

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
                st.write(f"**Histórico:**")
                for event in ticket["historico"]:
                    st.write(f"- {event['acao']} ({event['responsavel']} - {event['data_hora']})")

                if user_data["cargo"] == "COO":
                    novo_status = st.selectbox(
                        f"Atualizar Status ({ticket['titulo']})",
                        ["Aprovado pelo COO", "Rejeitado", "Orçamentos apresentados", "Aprovado pelo CEO", "Nota fiscal emitida", "Boleto emitido", "Chamado finalizado"],
                        index=0
                    )
                    if st.button(f"✅ Atualizar {ticket['titulo']}", key=f"update_{ticket['id']}"):
                        update_ticket_status(ticket["id"], novo_status, user_data["email"])
                        st.success(f"✅ Status atualizado para {novo_status}")
                        st.experimental_rerun()

    else:
        st.info("Nenhum chamado encontrado.")

    # 🔹 Abrir Novo Chamado
    st.subheader("➕ Abrir Novo Chamado")
    titulo = st.text_input("Título do Chamado")
    descricao = st.text_area("Descrição")
    categoria = st.selectbox("Categoria", ["TI", "Infraestrutura", "Administrativo"])
    urgencia = st.selectbox("Urgência", ["Baixa", "Média", "Alta"])
    loja = st.selectbox("Centro de Custo", ["Matriz", "Filial 1", "Filial 2"])

    if st.button("Criar Chamado"):
        if titulo and descricao:
            create_ticket(user_data["email"], titulo, descricao, categoria, urgencia, loja)
            st.success("✅ Chamado aberto com sucesso!")
            st.experimental_rerun()
        else:
            st.warning("⚠️ Preencha todos os campos antes de criar um chamado.")
