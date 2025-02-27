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
            for idx, user in enumerate(pending_users):
                user_email = user["email"]

                # Criar uma chave única para cada usuário
                unique_key = f"{user_email}_{idx}"

                with st.expander(f"📌 {user['nome']} ({user['email']})", expanded=False):
                    st.write(f"📍 **Cargo:** {user['cargo']}")
                    st.write(f"🏬 **Loja:** {user['loja']}")
                    st.write(f"📞 **WhatsApp:** {user['whatsapp']}")

                    # Inicializa o estado de edição para cada usuário
                    if f"edit_mode_{unique_key}" not in st.session_state:
                        st.session_state[f"edit_mode_{unique_key}"] = False

                    # Botão para ativar o modo de edição
                    if st.button(f"✏️ Editar", key=f"edit_btn_{unique_key}"):
                        st.session_state[f"edit_mode_{unique_key}"] = not st.session_state[f"edit_mode_{unique_key}"]
                        st.experimental_rerun()

                    # Se o modo de edição estiver ativado, mostrar o formulário
                    if st.session_state[f"edit_mode_{unique_key}"]:
                        st.subheader("✏️ Editar Usuário")
                        novo_nome = st.text_input("Nome", value=user["nome"], key=f"nome_{unique_key}")
                        novo_cargo = st.text_input("Cargo", value=user["cargo"], key=f"cargo_{unique_key}")
                        nova_loja = st.text_input("Loja", value=user["loja"], key=f"loja_{unique_key}")
                        novo_whatsapp = st.text_input("WhatsApp", value=user["whatsapp"], key=f"whatsapp_{unique_key}")

                        if st.button("💾 Salvar Alterações", key=f"save_{unique_key}"):
                            update_user(user_email, novo_nome, novo_cargo, nova_loja, novo_whatsapp)
                            st.success(f"✅ Informações de {novo_nome} atualizadas com sucesso!")
                            st.session_state[f"edit_mode_{unique_key}"] = False  # Fecha o formulário após salvar
                            st.experimental_rerun()

                    # 🔹 Botão para aprovar o usuário
                    if st.button(f"✅ Aprovar", key=f"approve_{unique_key}"):
                        approve_user(user["email"])
                        st.success(f"✅ Usuário {user['nome']} aprovado com sucesso!")
                        st.experimental_rerun()  # Atualiza a página após aprovação
    else:
        st.warning("🔒 Apenas o Diretor de Operações (COO) pode aprovar cadastros.")
