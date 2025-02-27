import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
from schemas import USER_SCHEMA, TICKET_SCHEMA, validate_schema

# 🔹 Carregar credenciais do Firebase do Streamlit Secrets
firebase_secrets = {
    "type": st.secrets["FIREBASE"]["type"],
    "project_id": st.secrets["FIREBASE"]["project_id"],
    "private_key_id": st.secrets["FIREBASE"]["private_key_id"],
    "private_key": st.secrets["FIREBASE"]["private_key"].replace('\\n', '\n'),  
    "client_email": st.secrets["FIREBASE"]["client_email"],
    "client_id": st.secrets["FIREBASE"]["client_id"],
    "auth_uri": st.secrets["FIREBASE"]["auth_uri"],
    "token_uri": st.secrets["FIREBASE"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["FIREBASE"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["FIREBASE"]["client_x509_cert_url"],
    "universe_domain": st.secrets["FIREBASE"]["universe_domain"],
}

# 🔹 Inicializar Firebase apenas se ainda não estiver inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_secrets)
    firebase_admin.initialize_app(cred)

# 🔹 Conectar ao Firestore
db = firestore.client()

# -------------------------- [ USUÁRIOS ] --------------------------

def create_user(nome, email, senha, cargo, loja, whatsapp):
    """Cadastra um novo usuário no Firestore"""
    user_data = {
        "nome": nome,
        "email": email,
        "senha": senha,  # 🔹 Melhorar segurança depois
        "cargo": cargo,
        "loja": loja,
        "whatsapp": whatsapp,
        "aprovado": False
    }
    
    if not validate_schema(user_data, USER_SCHEMA):
        raise ValueError("Os dados do usuário não correspondem ao esquema definido.")

    doc_ref = db.collection("usuarios").document(email)
    doc_ref.set(user_data)
    return True

def get_user(email, senha):
    """Busca um usuário no Firestore com base no e-mail e senha."""
    db = firestore.client()
    users_ref = db.collection("usuarios")

    # 🔹 Busca o usuário pelo e-mail
    query = users_ref.where("email", "==", email).stream()
    for doc in query:
        user = doc.to_dict()
        
        # 🔹 Verifica a senha antes de retornar os dados
        if "senha" in user and user["senha"] == senha:
            return user  # ✅ Retorna os dados do usuário se a senha estiver correta
    
    return None  # ❌ Retorna None se o usuário não for encontrado ou a senha estiver errada



def get_pending_users():
    """Retorna usuários pendentes de aprovação"""
    users = db.collection("usuarios").where("aprovado", "==", False).stream()
    return [user.to_dict() for user in users]

def approve_user(email):
    """Aprova um usuário se ele existir"""
    user_ref = db.collection("usuarios").document(email)
    if user_ref.get().exists:
        user_ref.update({"aprovado": True})
        return True
    return False

# -------------------------- [ HELP DESK ] --------------------------

def create_ticket(usuario_id, titulo, descricao, categoria, urgencia="Média"):
    """Cria um novo chamado no Firestore"""
    ticket_data = {
        "titulo": titulo,
        "descricao": descricao,
        "categoria": categoria,
        "urgencia": urgencia,
        "status": "Aberto",
        "usuario_id": usuario_id
    }
    
    if not validate_schema(ticket_data, TICKET_SCHEMA):
        raise ValueError("Os dados do chamado não correspondem ao esquema definido.")

    doc_ref = db.collection("chamados").document()
    doc_ref.set(ticket_data)

def get_user_tickets(usuario_id):
    """Retorna os chamados de um usuário"""
    tickets = db.collection("chamados").where("usuario_id", "==", usuario_id).stream()
    return [{"id": ticket.id, **ticket.to_dict()} for ticket in tickets]

def update_ticket_status(ticket_id, new_status):
    """Atualiza o status de um chamado"""
    ticket_ref = db.collection("chamados").document(ticket_id)
    ticket_ref.update({"status": new_status})
