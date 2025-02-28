from datetime import datetime



USER_SCHEMA = {
    "nome": str,
    "email": str,
    "senha": str,  # 🔹 Idealmente, armazenada de forma segura (hash)
    "cargo": str,
    "loja": str,  # Pode ser string ou None
    "whatsapp": str,
    "aprovado": bool
}

TICKET_SCHEMA = {
    "titulo": str,
    "descricao": str,
    "categoria": str,
    "urgencia": str,
    "status": str,
    "usuario_id": str
}

def validate_schema(data, schema):
    """
    Valida um dicionário com base no esquema fornecido.
    :param data: Dicionário com os dados a serem validados.
    :param schema: Esquema a ser seguido.
    :return: True se válido, False se inválido.
    """
    for key, expected_type in schema.items():
        if key not in data:
            return False  # Faltando um campo obrigatório
        if not isinstance(data[key], expected_type):
            if isinstance(expected_type, tuple):  # Permite múltiplos tipos (ex: str ou None)
                if not any(isinstance(data[key], t) for t in expected_type):
                    return False
            else:
                return False
    return True




def novo_chamado(titulo, descricao, loja, usuario):
    """Retorna um dicionário com a estrutura de um chamado."""
    return {
        "titulo": titulo,
        "descricao": descricao,
        "loja": loja,
        "status": "Aberto",
        "historico": [
            {"status": "Aberto", "usuario": usuario, "data_hora": datetime.now().isoformat()}
        ],
        "necessita_orcamento": False,
        "orcamentos": [],
        "nota_fiscal": None,
        "boleto": None,
        "usuario_abriu": usuario,
        "data_abertura": datetime.now().isoformat(),
        "responsavel_atual": "COO"
    }
