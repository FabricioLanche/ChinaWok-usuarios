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
    
    # 🔒 Verificar permisos ANTES de consultar
    es_admin = verificar_rol(usuario_autenticado, ["Admin"])
    es_gerente = verificar_rol(usuario_autenticado, ["Gerente"])
    es_mismo_usuario = usuario_autenticado["correo"] == correo_solicitado
    
    # Admin ve a todos
    if es_admin:
        pass  # Continúa
    # Gerente ve Clientes y a sí mismo
    elif es_gerente:
        if not es_mismo_usuario:
            # Necesitamos verificar que el usuario solicitado sea Cliente
            # Primero obtenemos el usuario
            try:
                resp_temp = usuarios_table.get_item(Key={"correo": correo_solicitado})
                if "Item" not in resp_temp:
                    return {
                        "statusCode": 404,
                        "body": json.dumps({"message": "Usuario no encontrado"})
                    }
                role_solicitado = resp_temp["Item"].get("role", "Cliente")
                if role_solicitado != "Cliente":
                    return {
                        "statusCode": 403,
                        "body": json.dumps({"message": "Gerente solo puede ver información de Clientes"})
                    }
            except Exception as e:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"message": f"Error al verificar usuario: {str(e)}"})
                }
    # Cliente solo ve su propia información
    elif not es_mismo_usuario:
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "Solo puedes ver tu propia información"})
        }

    # Obtener información del usuario
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
