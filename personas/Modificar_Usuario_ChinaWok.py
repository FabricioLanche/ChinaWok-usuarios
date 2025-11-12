import boto3
import os
import json
from utils.utils import validar_token

TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource("dynamodb")
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
        return {"statusCode": 401, "body": {"message": "Falta token"}}

    resp_val = validar_token(token)
    if resp_val.get("statusCode") == 403:
        return {"statusCode": 403, "body": {"message": "Forbidden - Acceso No Autorizado"}}

    correo = body.get("correo")
    if not correo:
        path_params = event.get("pathParameters") or {}
        correo = path_params.get("correo")

    if not correo:
        return {"statusCode": 400, "body": {"message": "correo es obligatorio"}}

    new_info_bancaria = body.get("informacion_bancaria")
    new_nombre = body.get("nombre")
    new_contrasena = body.get("contrasena")

    update_parts = []
    expr_values = {}

    if new_info_bancaria:
        update_parts.append("informacion_bancaria = :info")
        expr_values[":info"] = new_info_bancaria
    if new_nombre:
        update_parts.append("nombre = :nombre")
        expr_values[":nombre"] = new_nombre
    if new_contrasena:
        update_parts.append("contrasena = :contrasena")
        expr_values[":contrasena"] = new_contrasena

    if not update_parts:
        return {"statusCode": 400, "body": {"message": "No hay campos a actualizar"}}

    update_expr = "SET " + ", ".join(update_parts)

    resp = usuarios_table.update_item(
        Key={"correo": correo},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ReturnValues="ALL_NEW"
    )

    user = resp.get("Attributes", {})
    user.pop("contrasena", None)

    return {
        "statusCode": 200,
        "body": user
    }
