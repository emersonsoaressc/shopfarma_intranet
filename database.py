import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
import os

# 🔹 Verifique se o arquivo existe antes de carregar as credenciais
FIREBASE_CREDENTIALS_PATH = "firebase_config.json"

if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
    raise FileNotFoundError("❌ Arquivo 'firebase_config.json' não encontrado. Certifique-se de que ele está no diretório correto.")

# 🔹 Inicializar o Firebase apenas se ainda não foi inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

# 🔹 Conectar ao Firestore
db = firestore.client()


# 🔹 Verifica se o Firebase já foi inicializado antes de chamar initialize_app()
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)

# 🔹 Conectar ao Firestore
db = firestore.client()


# -------------------------- [ FUNÇÃO AUXILIAR - HASH DE SENHA ] --------------------------
def hash_password(password):
    """Retorna o hash SHA-256 da senha para armazená-la de forma segura."""
    return hashlib.sha256(password.encode()).hexdigest()


# -------------------------- [ USUÁRIOS ] --------------------------
def create_default_coo():
    """Cria um usuário padrão COO no Firebase se ainda não existir"""
    users_ref = db.collection("usuarios").document("emerson.soares.sc@gmail.com")
    if not users_ref.get().exists:
        users_ref.set({
            "nome": "Emerson Gustavo da Silva Soares",
            "email": "emerson.soares.sc@gmail.com",
            "senha": hash_password("admin123"),  # 🔹 Senha criptografada
            "cargo": "Diretor de Operações (COO)",
            "loja": None,
            "whatsapp": "+5548984876012",
            "aprovado": True  # COO já está aprovado por padrão
        })


def create_user(nome, email, senha, cargo, loja, whatsapp):
    """Cadastra um novo usuário no Firestore"""
    doc_ref = db.collection("usuarios").document(email)
    if doc_ref.get().exists:
        return False  # Usuário já existe

    doc_ref.set({
        "nome": nome,
        "email": email,
        "senha": hash_password(senha),  # 🔹 Senha criptografada
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
        if user_data["senha"] == hash_password(senha) and user_data["aprovado"]:
            return user_data
    return None


def get_pending_users():
    """Retorna usuários que precisam ser aprovados"""
    users = db.collection("usuarios").where("aprovado", "==", False).stream()
    return [{"email": user.id, **user.to_dict()} for user in users]


def approve_user(email):
    """Aprova um usuário no sistema"""
    user_ref = db.collection("usuarios").document(email)
    if user_ref.get().exists:
        user_ref.update({"aprovado": True})


# -------------------------- [ HELP DESK ] --------------------------
def create_ticket(usuario_email, titulo, descricao, categoria, urgencia="Média"):
    """Cria um novo chamado no Firestore"""
    doc_ref = db.collection("chamados").document()
    doc_ref.set({
        "usuario_email": usuario_email,
        "titulo": titulo,
        "descricao": descricao,
        "categoria": categoria,
        "urgencia": urgencia,
        "status": "Aberto",
        "data_abertura": firestore.SERVER_TIMESTAMP
    })


def get_user_tickets(usuario_email):
    """Retorna os chamados de um usuário"""
    tickets = db.collection("chamados").where("usuario_email", "==", usuario_email).stream()
    return [{"id": ticket.id, **ticket.to_dict()} for ticket in tickets]


def update_ticket_status(ticket_id, new_status):
    """Atualiza o status de um chamado"""
    ticket_ref = db.collection("chamados").document(ticket_id)
    if ticket_ref.get().exists:
        ticket_ref.update({"status": new_status})
