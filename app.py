import streamlit as st
from auth import check_session
import pages.dashboard as dashboard
import pages.login as login

# Verifica se o usuário está autenticado
user_data = check_session()

if user_data:
    st.session_state["user"] = user_data
    dashboard.show()  # Carrega o dashboard após login
else:
    login.show()  # Mostra a tela de login

