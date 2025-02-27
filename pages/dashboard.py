import streamlit as st
from database import get_pending_users, approve_user

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

                    # 🔹 Criando um identificador único para cada botão
                    approve_key = f"approve_{user['email']}"

                    if st.button(f"✅ Aprovar {user['email']}", key=approve_key):
                        approve_user(user["email"])
                        st.success(f"✅ Usuário {user['nome']} aprovado com sucesso!")
                        st.experimental_rerun()  # Atualiza a página após aprovação
    else:
        st.warning("🔒 Apenas o Diretor de Operações (COO) pode aprovar cadastros.")
