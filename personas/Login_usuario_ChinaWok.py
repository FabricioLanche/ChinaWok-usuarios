import json
import boto3
import os
from utils.utils import generar_token

TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource("dynamodb")
usuarios_table = dynamodb.Table(TABLE_USUARIOS_NAME)


def lambda_handler(event, context):
    body = {}
    if isinstance(event, dict) and "body" in event:
        raw_body = event.get("body")
        if isinstance(raw_body, str):
            if raw_body:
                body = json.loads(raw_body)
            else:
                body = {}
        elif isinstance(raw_body, dict):
            body = raw_body
        else:
            body = {}
    elif isinstance(event, dict):
        body = event
    elif isinstance(event, str):
        body = json.loads(event)

    correo = body.get("correo")
    contrasena = body.get("contrasena")

    if not correo or not contrasena:
        return {
            "statusCode": 400,
            "body": {"message": "correo y contrasena son obligatorios"}
        }

    # Buscar usuario
    resp = usuarios_table.get_item(Key={"correo": correo})
    if "Item" not in resp:
        return {
            "statusCode": 401,
            "body": {"message": "Credenciales inválidas"}
        }

    usuario = resp["Item"]

    # Verificar contraseña (en producción usar bcrypt)
    if usuario.get("contrasena") != contrasena:
        return {
            "statusCode": 401,
            "body": {"message": "Credenciales inválidas"}
        }

    # Generar JWT
    token = generar_token(
        correo=usuario["correo"],
        role=usuario.get("role", "Cliente"),
        nombre=usuario.get("nombre", "")
    )

    return {
        "statusCode": 200,
        "body": {
            "message": "Login exitoso",
            "token": token,
            "usuario": {
                "correo": usuario["correo"],
                "nombre": usuario["nombre"],
                "role": usuario.get("role", "Cliente")
            }
        }
    }
