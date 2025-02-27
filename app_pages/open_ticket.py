import streamlit as st
from database import create_ticket
from auth import check_session

def show():
    """Exibe o formulário para abertura de chamado"""
    user_data = check_session()
    
    if not user_data:
        st.warning("⚠️ Você precisa estar logado.")
        return

    st.subheader("📋 Formulário de Abertura de Chamado")
    
    titulo = st.text_input("Título do Chamado")
    descricao = st.text_area("Descrição")
    categoria = st.selectbox("Categoria", [
        "💻 Computadores e Periféricos",
        "🌐 Internet e Conectividade",
        "🖥️ ERP Trier e Softwares",
        "🏦 Skytef e Pagamentos",
        "🕒 Ponto Biométrico",
        "🍽️ Ifood e Voa Delivery",
        "❄️ Ar Condicionado e Climatização",
        "⚡ Elétrica e Iluminação",
        "🏗️ Obras e Benfeitorias",
        "🚰 Hidráulica e Encanamento",
        "📑 Documentação e Licenças",
        "💲 Pagamentos e Contabilidade",
        "🚛 Fornecedores e Compras"
    ])
    urgencia = st.selectbox("Urgência", ["Baixa", "Média", "Alta"])
    loja = st.selectbox("Centro de Custo", [
        "001 - Matriz", "004 - Centrinho", "005 - Calil", "007 - Rio Vermelho",
        "008 - Vargem Grande", "009 - Canasvieiras", "010 - UPA Norte",
        "011 - Trindade", "012 - Palhoça", "100 - Central"])

    if st.button("✅ Criar Chamado"):
        if titulo and descricao:
            create_ticket(user_data["email"], titulo, descricao, categoria, urgencia, loja)
            st.success("✅ Chamado aberto com sucesso!")
            st.session_state["abrir_chamado"] = False  # Oculta o formulário após a criação
            st.experimental_rerun()
        else:
            st.warning("⚠️ Preencha todos os campos antes de criar um chamado.")
