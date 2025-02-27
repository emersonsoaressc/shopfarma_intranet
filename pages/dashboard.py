import streamlit as st
from database import get_pending_users, approve_user, update_user

def show():
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
                user_email = user["email"]

                with st.expander(f"📌 {user['nome']} ({user['email']})"):
                    st.write(f"📍 **Cargo:** {user['cargo']}")
                    st.write(f"🏬 **Loja:** {user['loja']}")
                    st.write(f"📞 **WhatsApp:** {user['whatsapp']}")

                    # Inicializa o estado de edição para cada usuário
                    if f"edit_mode_{user_email}" not in st.session_state:
                        st.session_state[f"edit_mode_{user_email}"] = False

                    # Botão para ativar o modo de edição
                    if st.button(f"✏️ Editar {user_email}", key=f"edit_btn_{user_email}"):
                        st.session_state[f"edit_mode_{user_email}"] = not st.session_state[f"edit_mode_{user_email}"]
                        st.experimental_rerun()

                    # Se o modo de edição estiver ativado, mostrar o formulário
                    if st.session_state[f"edit_mode_{user_email}"]:
                        st.subheader("✏️ Editar Usuário")
                        novo_nome = st.text_input("Nome", value=user["nome"], key=f"nome_{user_email}")
                        novo_cargo = st.text_input("Cargo", value=user["cargo"], key=f"cargo_{user_email}")
                        nova_loja = st.text_input("Loja", value=user["loja"], key=f"loja_{user_email}")
                        novo_whatsapp = st.text_input("WhatsApp", value=user["whatsapp"], key=f"whatsapp_{user_email}")

                        if st.button("💾 Salvar Alterações", key=f"save_{user_email}"):
                            update_user(user_email, novo_nome, novo_cargo, nova_loja, novo_whatsapp)
                            st.success(f"✅ Informações de {novo_nome} atualizadas com sucesso!")
                            st.session_state[f"edit_mode_{user_email}"] = False  # Fecha o formulário após salvar
                            st.experimental_rerun()

                    # 🔹 Botão para aprovar o usuário
                    if st.button(f"✅ Aprovar {user['email']}", key=f"approve_{user_email}"):
                        approve_user(user["email"])
                        st.success(f"✅ Usuário {user['nome']} aprovado com sucesso!")
                        st.experimental_rerun()  # Atualiza a página após aprovação
    else:
        st.warning("🔒 Apenas o Diretor de Operações (COO) pode aprovar cadastros.")
