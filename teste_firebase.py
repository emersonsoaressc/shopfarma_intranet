import streamlit as st
from database import create_user, get_user, create_ticket, get_user_tickets


def teste_firebase():
    st.title("Teste do Firebase")

    # Teste de Cadastro de Usuário
    if st.button("Criar Usuário Teste"):
        create_user("Usuário Teste", "teste@email.com", "123456", "Gestor", "001 - Matriz", "+5548999999999")
        st.success("Usuário criado com sucesso!")

    # Teste de Obter Usuário
    if st.button("Buscar Usuário"):
        user = get_user("teste@email.com")
        st.write(user)

    # Teste de Criar Chamado
    if st.button("Criar Chamado"):
        create_ticket("teste@email.com", "Problema no sistema", "Sistema travando ao abrir", "TI", "Alta")
        st.success("Chamado criado!")

    # Teste de Buscar Chamados
    if st.button("Buscar Chamados"):
        tickets = get_user_tickets("teste@email.com")
        st.write(tickets)
