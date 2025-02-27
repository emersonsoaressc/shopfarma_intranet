import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# 🔹 Inicializa o Firebase apenas uma vez
if not firebase_admin._apps:
    try:
        # 🔹 Pega as credenciais do Streamlit Secrets
        firebase_config = json.loads(st.secrets["FIREBASE"])
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro ao inicializar Firebase: {e}")

# 🔹 Conectar ao Firestore
db = firestore.client()

# -------------------------- [ USUÁRIOS ] --------------------------

def create_default_coo():
    """Cria um usuário padrão COO no Firebase se ainda não existir"""
    users_ref = db.collection("usuarios").document("emerson.soares.sc@gmail.com")
    if not users_ref.get().exists:
        users_ref.set({
            "nome": "Emerson Gustavo da Silva Soares",
            "email": "emerson.soares.sc@gmail.com",
            "senha": "admin123",  # 🔹 Idealmente, criptografar isso depois!
            "cargo": "Diretor de Operações (COO)",
            "loja": None,
            "whatsapp": "+5548984876012",
            "aprovado": True  # COO já está aprovado por padrão
        })

def create_user(nome, email, senha, cargo, loja, whatsapp):
    """Cadastra um novo usuário no Firestore"""
    doc_ref = db.collection("usuarios").document(email)
    doc_ref.set({
        "nome": nome,
        "email": email,
        "senha": senha,  # 🔹 Armazene as senhas de forma segura (hash no futuro)
        "cargo": cargo,
        "loja": loja,
        "whatsapp": whatsapp,
        "aprovado": False  # Usuário precisa ser aprovado pelo COO
    })
    return True

def get_user(email, senha):
    """Retorna um usuário se ele existir e estiver aprovado"""
    doc = db.collection("usuarios").document(email).get()
    if doc.exists:
        user_data = doc.to_dict()
        if user_data["senha"] == senha and user_data["aprovado"]:
            return user_data
    return None

def get_pending_users():
    """Retorna usuários que precisam ser aprovados"""
    users = db.collection("usuarios").where("aprovado", "==", False).stream()
    return [user.to_dict() for user in users]

def approve_user(email):
    """Aprova um usuário no sistema"""
    user_ref = db.collection("usuarios").document(email)
    user_ref.update({"aprovado": True})

# -------------------------- [ HELP DESK ] --------------------------

def create_ticket(usuario_id, titulo, descricao, categoria, urgencia="Média"):
    """Cria um novo chamado no Firestore"""
    doc_ref = db.collection("chamados").document()
    doc_ref.set({
        "titulo": titulo,
        "descricao": descricao,
        "categoria": categoria,
        "urgencia": urgencia,
        "status": "Aberto",
        "usuario_id": usuario_id
    })

def get_user_tickets(usuario_id):
    """Retorna os chamados de um usuário"""
    tickets = db.collection("chamados").where("usuario_id", "==", usuario_id).stream()
    return [{"id": ticket.id, **ticket.to_dict()} for ticket in tickets]

def update_ticket_status(ticket_id, new_status):
    """Atualiza o status de um chamado"""
    ticket_ref = db.collection("chamados").document(ticket_id)
    ticket_ref.update({"status": new_status})
