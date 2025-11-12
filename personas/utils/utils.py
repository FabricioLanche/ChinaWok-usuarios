import boto3
import os
from datetime import datetime

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_TOKENS = os.getenv("TABLE_TOKENS", "ChinaWok-Tokens")
TABLE_USUARIOS = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
tabla_tokens = dynamodb.Table(TABLE_TOKENS)
tabla_usuarios = dynamodb.Table(TABLE_USUARIOS)


def validar_token(token):
    """
    Valida un token y retorna información del usuario.
    
    Returns:
        dict: {"statusCode": int, "body": dict}
    """
    if not token:
        return {"statusCode": 400, "body": {"message": "token es obligatorio"}}

    # Buscar token
    resp = tabla_tokens.get_item(Key={"token": token})
    if "Item" not in resp:
        return {"statusCode": 403, "body": {"message": "Token no existe"}}

    token_item = resp["Item"]
    expira = datetime.strptime(token_item["expira"], "%Y-%m-%d %H:%M:%S")
    if expira < datetime.now():
        return {"statusCode": 403, "body": {"message": "Token expirado"}}

    # Buscar usuario asociado
    correo = token_item["correo_usuario"]
    resp_user = tabla_usuarios.get_item(Key={"correo": correo})
    if "Item" not in resp_user:
        return {"statusCode": 403, "body": {"message": "Usuario no encontrado"}}

    user = resp_user["Item"]

    # Respuesta con role incluido
    return {
        "statusCode": 200,
        "body": {
            "message": "Token válido",
            "correo": correo,
            "role": user.get("role", "Cliente")
        }
    }
