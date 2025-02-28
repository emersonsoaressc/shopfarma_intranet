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

    # 🔹 Define um valor padrão para 'loja' caso seja None
    if not loja:
        loja = "100 - Central"

    users_ref = db.collection("usuarios").document(email)

    if users_ref.get().exists:
        return False  # Usuário já existe

    hashed_password = hashlib.sha256(senha.encode()).hexdigest()
    user_data = {
        "nome": nome.strip(),
        "email": email.strip(),
        "senha": hashed_password,
        "cargo": cargo.strip(),
        "loja": loja.strip() if loja else None,  # Loja pode ser string ou None
        "whatsapp": whatsapp.strip(),
        "aprovado": False  # O usuário começa como não aprovado
    }

    # 🔹 Checa se todos os campos obrigatórios estão presentes
    for field in USER_SCHEMA.keys():
        if field not in user_data:
            raise ValueError(f"O campo {field} está ausente.")

    # 🔹 Valida o esquema antes de inserir no Firestore
    if not validate_schema(user_data, USER_SCHEMA):
        raise ValueError("Os dados do usuário não correspondem ao esquema definido.")

    users_ref.set(user_data)
    return True

def get_user(email, senha):
    """Busca um usuário no Firestore com base no e-mail e senha."""
    users_ref = db.collection("usuarios")
    query = users_ref.where("email", "==", email).stream()  # 🔹 CORRIGIDO

    for doc in query:
        user = doc.to_dict()
        hashed_input_password = hashlib.sha256(senha.encode()).hexdigest()
        if "senha" in user and user["senha"] == hashed_input_password:
            return user
    return None

def approve_user(email):
    """Aprova um usuário alterando seu status no Firestore."""
    user_ref = db.collection("usuarios").document(email)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_ref.update({"aprovado": True})  # Atualiza o campo 'aprovado' para True
        return True
    return False


def get_pending_users():
    """Retorna usuários que ainda não foram aprovados."""
    users_ref = db.collection("usuarios")
    query = users_ref.where("aprovado", "==", False).stream()  # Garante que pega apenas os pendentes

    pending_users = []
    for doc in query:
        user_data = doc.to_dict()
        user_data["id"] = doc.id  # Inclui o ID do documento Firestore
        pending_users.append(user_data)

    return pending_users


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
    tickets = db.collection("chamados").where("usuario_id", "==", usuario_id).stream()  # 🔹 CORRIGIDO
    return [{"id": ticket.id, **ticket.to_dict()} for ticket in tickets]

def get_aproved_users():
    """Retorna todos os usuários aprovados no sistema"""
    users_ref = db.collection("usuarios").where("aprovado", "==", True).stream()
    return [{"email": user.id, **user.to_dict()} for user in users_ref]


def update_ticket_status(ticket_id, new_status, usuario_id, responsavel_email=None):
    """Atualiza o status de um chamado e registra no histórico"""
    ticket_ref = db.collection("chamados").document(ticket_id)
    ticket = ticket_ref.get()

    if ticket.exists:
        ticket_data = ticket.to_dict()
        ticket_data["status"] = new_status

        # Adiciona a mudança no histórico do chamado
        ticket_data["historico"].append({
            "acao": f"Status atualizado para {new_status}",
            "responsavel": usuario_id,
            "data_hora": datetime.datetime.utcnow().isoformat()
        })

        # Se um responsável foi designado, atualizar o chamado
        if responsavel_email:
            ticket_data["responsaveis"]["Proximo"] = responsavel_email

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
    """Retorna chamados que estão pendentes de aprovação."""
    try:
        tickets_ref = db.collection("chamados").where("status", "==", "Aberto").stream()
        chamados = [{"id": ticket.id, **ticket.to_dict()} for ticket in tickets_ref]
        
        print(f"📌 CHAMADOS PENDENTES PARA APROVAÇÃO: {chamados}")  # Debug no log

        return chamados
    except Exception as e:
        print(f"⚠️ ERRO AO BUSCAR CHAMADOS PENDENTES: {e}")
        return []  # Retorna lista vazia em caso de erro


def get_all_tickets():
    """Retorna TODOS os chamados (para testar se há dados no Firestore)"""
    tickets_ref = db.collection("chamados").stream()
    chamados = [{"id": ticket.id, **ticket.to_dict()} for ticket in tickets]
    
    print(f"📋 Todos os chamados: {chamados}")  # Debug no terminal
    
    return chamados

def get_assigned_tickets(usuario_email):
    """Retorna os chamados atribuídos ao usuário"""
    tickets = db.collection("chamados").where("responsaveis.Proximo", "==", usuario_email).stream()
    return [{"id": ticket.id, **ticket.to_dict()} for ticket in tickets]

def anexar_orcamento(ticket_id, usuario_email, orcamento_url):
    """Anexa orçamento ao chamado e atualiza o status"""
    ticket_ref = db.collection("chamados").document(ticket_id)
    ticket = ticket_ref.get()

    if ticket.exists:
        ticket_data = ticket.to_dict()
        
        ticket_data["anexos"]["orcamentos"].append(orcamento_url)

        # Atualiza histórico
        ticket_data["historico"].append({
            "acao": "Orçamento anexado",
            "responsavel": usuario_email,
            "data_hora": datetime.datetime.utcnow().isoformat()
        })

        # Se for analista financeiro, avança o chamado para o CEO
        if ticket_data["responsaveis"]["Proximo"] == usuario_email:
            ticket_data["responsaveis"]["Proximo"] = ticket_data["responsaveis"]["CEO"]
            ticket_data["status"] = "Orçamentos apresentados"

        ticket_ref.update(ticket_data)

