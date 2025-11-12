import json
import boto3
import os

TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource("dynamodb")
usuarios_table = dynamodb.Table(TABLE_USUARIOS_NAME)


def lambda_handler(event, context):
    try:
        response = usuarios_table.scan()
        usuarios = response.get("Items", [])
        
        # Remover contraseñas de la respuesta
        for usuario in usuarios:
            if "contrasena" in usuario:
                del usuario["contrasena"]
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Usuarios obtenidos correctamente",
                "usuarios": usuarios
            }, default=str)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error al listar usuarios: {str(e)}"})
        }
