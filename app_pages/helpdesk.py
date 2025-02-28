import streamlit as st
from database import get_user_tickets, update_ticket_status, get_pending_tickets, get_all_tickets, get_aproved_users, get_assigned_tickets, anexar_orcamento
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
            with st.expander(f"{ticket['loja']} - {ticket['titulo']} - {ticket['status']}"):
                st.write(f"**Descrição:** {ticket['descricao']}")
                st.write(f"**Categoria:** {ticket['categoria']}")
                st.write(f"**Urgência:** {ticket['urgencia']}")
                st.write(f"**Centro de Custo:** {ticket['loja']}")
                st.write(f"**Histórico:**")
                for event in ticket["historico"]:
                    st.write(f"- {event['acao']} ({event['responsavel']} - {event['data_hora']})")
                st.write(f"**Aguardando por:** {ticket['responsaveis']['Proximo']}")

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

                    # Buscar usuários aprovados para designação
                    usuarios_aprovados = get_aproved_users()
                    opcoes_usuarios = {u["email"]: u["nome"] for u in usuarios_aprovados}

                    responsavel = st.selectbox(
                        "👤 Escolha o responsável a ser designado pelo chamado:",
                        options=list(opcoes_usuarios.keys()),
                        format_func=lambda x: opcoes_usuarios[x]
                    )

                    if st.button(f"✅ Aprovar e Designar Responsável ({chamado['titulo']})"):
                        update_ticket_status(chamado["id"], "Aprovado pelo COO", user_data["email"], responsavel)
                        st.success(f"✅ Chamado aprovado e atribuído a {opcoes_usuarios[responsavel]}")
                        st.rerun()
        else:
            st.success("✅ Nenhum chamado pendente no momento.")


    st.title("🛠️ Helpdesk - Meus Chamados Atribuídos")

    chamados_atribuidos = get_assigned_tickets(user_data["email"])

    if not chamados_atribuidos:
        st.info("📌 Nenhum chamado atribuído a você no momento.")
    else:
        for chamado in chamados_atribuidos:
            with st.expander(f"{chamado['titulo']} - {chamado['status']}"):

                st.write(f"📍 **Loja:** {chamado['loja']}")
                st.write(f"📂 **Categoria:** {chamado['categoria']}")
                st.write(f"📜 **Descrição:** {chamado['descricao']}")
                st.write(f"🚀 **Urgência:** {chamado['urgencia']}")

                # Exibir histórico do chamado
                st.write("📜 **Histórico:**")
                for evento in chamado["historico"]:
                    st.write(f"- {evento['acao']} ({evento['responsavel']} - {evento['data_hora']})")
                    if "parecer" in evento:
                        st.write(f"💬 **Parecer:** {evento['parecer']}")

                # 🔹 Se for o Analista Financeiro, permitir anexar orçamentos e parecer
                if user_data["cargo"] == "Assistente Financeiro":
                    st.subheader("📑 Anexar Orçamentos e Parecer")

                    parecer = st.text_area("💬 Escreva seu parecer sobre o orçamento")
                    orcamento_file = st.file_uploader("📂 Faça o upload do PDF do orçamento", type=["pdf"])

                    enviar_para = st.radio("📤 Enviar orçamento para:", ["COO", "CEO"], horizontal=True)

                    if st.button("📤 Enviar Orçamento"):
                        if orcamento_file and parecer:
                            anexar_orcamento(chamado["id"], user_data["email"], orcamento_file, parecer, enviar_para)
                            st.success(f"✅ Orçamento anexado e enviado para {enviar_para} com sucesso!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Você precisa anexar um PDF e escrever um parecer antes de enviar.")

            
            
            
            
            
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
