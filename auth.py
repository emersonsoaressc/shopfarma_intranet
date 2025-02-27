import streamlit as st
from database import get_user

def check_session():
    """Verifica se o usuário está autenticado"""
    return st.session_state.get("user")

def login():
    """Realiza o login do usuário"""
    email = st.text_input("E-mail para Login")
    senha = st.text_input("Senha para Login", type="password")

    if st.button("Entrar"):
        user = get_user(email, senha)
        if user:
            st.session_state["user"] = user
            st.experimental_rerun()
        else:
            st.error("⚠️ Usuário não encontrado ou ainda não aprovado.")

def logout():
    """Realiza o logout do usuário"""
    if st.button("🔒 Logout"):
        st.session_state["user"] = None
        st.experimental_rerun()
