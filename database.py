import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import datetime
import hashlib
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
    """Cria um novo usuário no Firestore com senha hash."""
    users_ref = db.collection("usuarios").document(email)

    if users_ref.get().exists:
        return False  # Usuário já existe

    hashed_password = hashlib.sha256(senha.encode()).hexdigest()
    user_data = {
        "nome": nome,
        "email": email,
        "senha": hashed_password,
        "cargo": cargo,
        "loja": loja,
        "whatsapp": whatsapp,
        "status": "Pendente"  # O usuário começa com status pendente até ser aprovado pelo COO
    }

    if not validate_schema(user_data, USER_SCHEMA):
        raise ValueError("Os dados do usuário não correspondem ao esquema definido.")

    users_ref.set(user_data)
    return True

def get_user(email, senha):
    """Busca um usuário no Firestore com base no e-mail e senha."""
    users_ref = db.collection("usuarios")
    query = users_ref.where(filter=("email", "==", email)).stream()  # ✅ Correção do WARNING

    for doc in query:
        user = doc.to_dict()
        hashed_input_password = hashlib.sha256(senha.encode()).hexdigest()
        if "senha" in user and user["senha"] == hashed_input_password:
            return user
    return None

def approve_user(email):
    """Aprova um usuário alterando seu status no Firestore."""
    user_ref = db.collection("usuarios").document(email)
    if user_ref.get().exists:
        user_ref.update({"status": "Aprovado"})
        return True
    return False

def get_pending_users():
    """Retorna todos os usuários pendentes de aprovação."""
    users = db.collection("usuarios").where(filter=("status", "==", "Pendente")).stream()
    return [{"id": user.id, **user.to_dict()} for user in users]

# -------------------------- [ HELP DESK ] --------------------------

def create_ticket(usuario_id, titulo, descricao, categoria, urgencia="Média", loja="Matriz"):
    """Cria um novo chamado no Firestore."""
    ticket_data = {
        "titulo": titulo,
        "descricao": descricao,
        "categoria": categoria,
        "urgencia": urgencia,
        "status": "Aberto",
        "usuario_id": usuario_id,
        "loja": loja,
        "historico": [
            {
                "acao": "Chamado aberto",
                "responsavel": usuario_id,
                "data_hora": datetime.datetime.utcnow().isoformat()
            }
        ],
        "anexos": {
            "orcamentos": [],
            "nota_fiscal": "",
            "boleto": ""
        },
        "responsaveis": {
            "COO": "",
            "Financeiro": "",
            "CEO": "",
        }
    }

    if not validate_schema(ticket_data, TICKET_SCHEMA):
        raise ValueError("Os dados do chamado não correspondem ao esquema definido.")

    doc_ref = db.collection("chamados").document()
    doc_ref.set(ticket_data)

def get_user_tickets(usuario_id):
    """Retorna os chamados de um usuário."""
    tickets = db.collection("chamados").where(filter=("usuario_id", "==", usuario_id)).stream()  # ✅ Correção do WARNING
    return [{"id": ticket.id, **ticket.to_dict()} for ticket in tickets]

def update_ticket_status(ticket_id, new_status, usuario_id, responsaveis=None):
    """Atualiza o status de um chamado e registra no histórico."""
    ticket_ref = db.collection("chamados").document(ticket_id)
    ticket = ticket_ref.get()

    if ticket.exists:
        ticket_data = ticket.to_dict()
        ticket_data["status"] = new_status
        ticket_data["historico"].append({
            "acao": f"Status atualizado para {new_status}",
            "responsavel": usuario_id,
            "data_hora": datetime.datetime.utcnow().isoformat()
        })

        if responsaveis:
            ticket_data["responsaveis"].update(responsaveis)

        ticket_ref.update(ticket_data)

def upload_file(ticket_id, file_type, file_url, usuario_id):
    """Faz o upload de arquivos (orçamentos, notas fiscais, boletos) e atualiza o chamado."""
    ticket_ref = db.collection("chamados").document(ticket_id)
    ticket = ticket_ref.get()

    if ticket.exists:
        ticket_data = ticket.to_dict()
        if file_type == "orcamento":
            ticket_data["anexos"]["orcamentos"].append(file_url)
        elif file_type == "nota_fiscal":
            ticket_data["anexos"]["nota_fiscal"] = file_url
        elif file_type == "boleto":
            ticket_data["anexos"]["boleto"] = file_url

        ticket_data["historico"].append({
            "acao": f"Arquivo {file_type} anexado",
            "responsavel": usuario_id,
            "data_hora": datetime.datetime.utcnow().isoformat()
        })

        ticket_ref.update(ticket_data)

def get_pending_tickets():
    """Retorna todos os chamados que ainda não foram finalizados."""
    tickets = db.collection("chamados").where(filter=("status", "!=", "Chamado finalizado")).stream()  # ✅ Correção do WARNING
    return [{"id": ticket.id, **ticket.to_dict()} for ticket in tickets]
