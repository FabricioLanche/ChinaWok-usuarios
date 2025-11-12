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
    
    # Obtener correo del query parameter
    correo_solicitado = None
    
    if event.get("queryStringParameters"):
        correo_solicitado = event["queryStringParameters"].get("correo")
    
    # Si no se proporciona correo, retornar info del usuario autenticado
    if not correo_solicitado:
        correo_solicitado = usuario_autenticado["correo"]
    
    # Obtener información del usuario solicitado
    try:
        resp = usuarios_table.get_item(Key={"correo": correo_solicitado})
        
        if "Item" not in resp:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "Usuario no encontrado"})
            }
        
        usuario_solicitado = resp["Item"]
        role_solicitado = usuario_solicitado.get("role", "Cliente")
        
        # 🔒 Verificar permisos
        es_admin = verificar_rol(usuario_autenticado, ["Admin"])
        es_gerente = verificar_rol(usuario_autenticado, ["Gerente"])
        es_mismo_usuario = usuario_autenticado["correo"] == correo_solicitado
        
        # Admin ve a todos
        if es_admin:
            pass
        # Gerente solo ve a Clientes (y a sí mismo)
        elif es_gerente:
            if not (role_solicitado == "Cliente" or es_mismo_usuario):
                return {
                    "statusCode": 403,
                    "body": json.dumps({"message": "Gerente solo puede ver información de Clientes"})
                }
        # Cliente solo ve su propia información
        elif not es_mismo_usuario:
            return {
                "statusCode": 403,
                "body": json.dumps({"message": "Solo puedes ver tu propia información"})
            }
        
        # Remover contraseña de la respuesta
        if "contrasena" in usuario_solicitado:
            del usuario_solicitado["contrasena"]
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Usuario encontrado",
                "usuario": usuario_solicitado
            }, default=str)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error al buscar usuario: {str(e)}"})
        }
