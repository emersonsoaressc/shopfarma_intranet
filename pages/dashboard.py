import streamlit as st
from database import get_pending_users, approve_user, update_user

def show():
    # 🔹 Evita que o conteúdo seja renderizado mais de uma vez
    if "dashboard_loaded" in st.session_state:
        return
    st.session_state["dashboard_loaded"] = True

    # 🔹 Título principal do dashboard
    st.title("📊 Dashboard - Gestão de Usuários")

    # 🔹 Exibir informações do usuário logado
    if "user" in st.session_state and st.session_state["user"]:
        user_data = st.session_state["user"]
        st.markdown(f"👤 **Usuário:** {user_data.get('nome', 'Desconhecido')} ({user_data.get('cargo', 'Sem cargo')})")
    else:
        st.error("⚠️ Usuário não autenticado. Faça login novamente.")
        st.stop()

    # 🔹 Somente o COO pode aprovar usuários
    if user_data.get("cargo") == "Diretor de Operações (COO)":
        st.subheader("📝 Aprovação de Usuários")

        # Buscar usuários pendentes
        pending_users = get_pending_users()

        if not pending_users:
            st.success("✅ Nenhum usuário pendente para aprovação no momento.")
        else:
            for user in pending_users:
                with st.expander(f"📌 {user['nome']} ({user['email']})"):
                    st.write(f"📍 **Cargo:** {user['cargo']}")
                    st.write(f"🏬 **Loja:** {user['loja']}")
                    st.write(f"📞 **WhatsApp:** {user['whatsapp']}")

                    # 🔹 Botão de edição (ícone ✏️)
                    edit_key = f"edit_{user['email']}"
                    if st.button("✏️ Editar", key=edit_key):
                        st.session_state[f"edit_{user['email']}"] = True

                    # 🔹 Se o botão de editar foi pressionado, exibir formulário de edição
                    if st.session_state.get(f"edit_{user['email']}", False):
                        st.subheader("✏️ Editar Usuário")
                        novo_nome = st.text_input("Nome", value=user["nome"], key=f"nome_{user['email']}")
                        novo_cargo = st.text_input("Cargo", value=user["cargo"], key=f"cargo_{user['email']}")
                        nova_loja = st.text_input("Loja", value=user["loja"], key=f"loja_{user['email']}")
                        novo_whatsapp = st.text_input("WhatsApp", value=user["whatsapp"], key=f"whatsapp_{user['email']}")

                        if st.button("💾 Salvar Alterações", key=f"save_{user['email']}"):
                            update_user(user["email"], novo_nome, novo_cargo, nova_loja, novo_whatsapp)
                            st.success(f"✅ Informações de {novo_nome} atualizadas com sucesso!")
                            st.session_state[f"edit_{user['email']}"] = False  # Fecha o formulário de edição
                            st.experimental_rerun()

                    # 🔹 Botão para aprovar o usuário
                    approve_key = f"approve_{user['email']}"
                    if st.button(f"✅ Aprovar {user['email']}", key=approve_key):
                        approve_user(user["email"])
                        st.success(f"✅ Usuário {user['nome']} aprovado com sucesso!")
                        st.experimental_rerun()  # Atualiza a página após aprovação
    else:
        st.warning("🔒 Apenas o Diretor de Operações (COO) pode aprovar cadastros.")
