import streamlit as st
from database import create_user
import auth

def show():
    """Exibe a tela de login e cadastro"""
    st.image('images/logo_shopfarma_sem_fundo.png', width=250)

    if "show_register" not in st.session_state:
        st.session_state.show_register = False

    if not st.session_state.show_register:
        st.title("🔑 Login")
        auth.login()

        if st.button("Cadastre-se"):
            st.session_state.show_register = True
            st.experimental_rerun()
    else:
        st.title("📋 Novo Cadastro")

        nome = st.text_input("Nome Completo")
        email_cadastro = st.text_input("E-mail para Cadastro")
        senha_cadastro = st.text_input("Senha para Cadastro", type="password")
        whatsapp = st.text_input("Número do WhatsApp", placeholder="+5548999999999")

        cargo = st.selectbox("Cargo", [
            "Proprietário (CEO)", "Diretor de Operações (COO)", 
            "Diretor Comercial (CCO)", "Diretor Financeiro (CFO)", 
            "Gestor", "Assistente"
        ])

        loja = st.selectbox("Selecione sua Loja", [
            "001 - Matriz", "004 - Centrinho", "005 - Calil"
        ]) if cargo == "Gestor" else None

        if st.button("Registrar"):
            if nome and email_cadastro and senha_cadastro and whatsapp and cargo:
                create_user(nome, email_cadastro, senha_cadastro, cargo, loja, whatsapp)
                st.success("✅ Cadastro enviado! Aguarde aprovação do COO.")
                st.session_state.show_register = False
                st.experimental_rerun()
            else:
                st.warning("⚠️ Preencha todos os campos antes de cadastrar.")

        if st.button("Voltar ao Login"):
            st.session_state.show_register = False
            st.experimental_rerun()
