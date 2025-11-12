import json
import boto3
import os
from utils.utils import validar_token

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
usuarios_table = dynamodb.Table(TABLE_USUARIOS_NAME)

def _parse_body(event):
    body = event.get("body", {})
    if isinstance(body, str):
        body = json.loads(body) if body.strip() else {}
    elif not isinstance(body, dict):
        body = {}
    return body

def _get_token(event, body):
    headers = event.get("headers", {}) or {}
    token = headers.get("Authorization") or headers.get("authorization") or body.get("token")
    if not token:
        return None
    if isinstance(token, str) and token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1].strip()
    return token

def lambda_handler(event, context):
    body = _parse_body(event)
    token = _get_token(event, body)

    if not token:
        return {
            "statusCode": 401,
            "body": {"message": "Falta token"}
        }

    resp_val = validar_token(token)

    if resp_val.get("statusCode") == 403:
        return {
            "statusCode": 403,
            "body": {"message": "Forbidden - Acceso No Autorizado"}
        }

    path_params = event.get("pathParameters") or {}
    correo = path_params.get("correo") or body.get("correo") or event.get("correo")

    if not correo:
        return {
            "statusCode": 400,
            "body": {"message": "correo es obligatorio"}
        }

    resp = usuarios_table.get_item(Key={"correo": correo})
    if "Item" not in resp:
        return {
            "statusCode": 404,
            "body": {"message": "Usuario no encontrado"}
        }

    usuarios_table.delete_item(Key={"correo": correo})

    return {
        "statusCode": 200,
        "body": {"message": f"Usuario '{correo}' eliminado correctamente"}
    }
