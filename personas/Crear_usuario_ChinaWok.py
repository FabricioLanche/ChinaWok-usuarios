import json
import boto3
import os
from datetime import datetime, timezone

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
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

    nombre = body.get("nombre")
    correo = body.get("correo")
    contrasena = body.get("contrasena")
    role = body.get("role", "Cliente")
    informacion_bancaria = body.get("informacion_bancaria")

    if not nombre or not correo or not contrasena:
        return {
            "statusCode": 400,
            "body": {"message": "nombre, correo y contrasena son obligatorios"}
        }

    resp = usuarios_table.get_item(Key={"correo": correo})
    if "Item" in resp:
        return {
            "statusCode": 409,
            "body": {"message": "Usuario ya existe"}
        }

    # 🚨 Verificar si ya existe un admin en la tabla
    scan = usuarios_table.scan()
    hay_admin = any(u.get("role") == "Admin" for u in scan.get("Items", []))

    # Si ya hay admin, forzar a Cliente
    if hay_admin and role == "Admin":
        role = "Cliente"

    item = {
        "nombre": nombre,
        "correo": correo,
        "contrasena": contrasena,
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    if informacion_bancaria:
        item["informacion_bancaria"] = informacion_bancaria

    usuarios_table.put_item(Item=item)

    return {
        "statusCode": 201,
        "body": {
            "message": "Usuario creado correctamente",
            "role_asignado": role
        }
    }
