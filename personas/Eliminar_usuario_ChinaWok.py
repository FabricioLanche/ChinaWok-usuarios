import json
import boto3
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
usuarios_table = dynamodb.Table(TABLE_USUARIOS_NAME)


def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    correo = path_params.get("correo")

    if not correo and "correo" in event:
        correo = event["correo"]

    if not correo:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "correo es obligatorio"})
        }

    # opcional: verificar primero si existe
    resp = usuarios_table.get_item(Key={"correo": correo})
    if "Item" not in resp:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Usuario no encontrado"})
        }

    usuarios_table.delete_item(Key={"correo": correo})

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Usuario eliminado"})
    }
