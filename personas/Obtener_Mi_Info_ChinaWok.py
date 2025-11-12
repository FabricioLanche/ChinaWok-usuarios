import json
import boto3
import os
from personas.utils.utils import verificar_rol

TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource("dynamodb")
usuarios_table = dynamodb.Table(TABLE_USUARIOS_NAME)


def lambda_handler(event, context):
    # Obtener usuario autenticado
    authorizer = event.get("requestContext", {}).get("authorizer", {})
    usuario_autenticado = {
        "correo": authorizer.get("correo"),
        "role": authorizer.get("role")
    }
    
    # Obtener correo del query parameter o body
    correo_solicitado = None
    
    # Intentar desde queryStringParameters (GET)
    if event.get("queryStringParameters"):
        correo_solicitado = event["queryStringParameters"].get("correo")
    
    # Si no, intentar desde body (POST)
    if not correo_solicitado:
        body = {}
        if isinstance(event, dict) and "body" in event:
            raw_body = event.get("body")
            if isinstance(raw_body, str) and raw_body:
                body = json.loads(raw_body)
            elif isinstance(raw_body, dict):
                body = raw_body
        correo_solicitado = body.get("correo")
    
    # Si no se proporciona correo, retornar info del usuario autenticado
    if not correo_solicitado:
        correo_solicitado = usuario_autenticado["correo"]
    
    # 🔒 Verificar permisos
    es_admin = verificar_rol(usuario_autenticado, ["Admin"])
    es_gerente = verificar_rol(usuario_autenticado, ["Gerente"])
    es_mismo_usuario = usuario_autenticado["correo"] == correo_solicitado
    
    # Admin ve todo, Gerente ve todos los usuarios, Cliente solo ve su info
    if not (es_admin or es_gerente or es_mismo_usuario):
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "No tienes permiso para ver esta información"})
        }

    try:
        resp = usuarios_table.get_item(Key={"correo": correo_solicitado})
        
        if "Item" not in resp:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "Usuario no encontrado"})
            }
        
        usuario = resp["Item"]
        
        # Remover contraseña de la respuesta
        if "contrasena" in usuario:
            del usuario["contrasena"]
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Usuario encontrado",
                "usuario": usuario
            }, default=str)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error al buscar usuario: {str(e)}"})
        }
