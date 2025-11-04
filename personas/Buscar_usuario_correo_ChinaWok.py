import json
import boto3
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
usuarios_table = dynamodb.Table(TABLE_USUARIOS_NAME)


def lambda_handler(event, context):
    # Opción 1: correo viene en pathParameters: /usuarios/{correo}
    path_params = event.get("pathParameters") or {}
    correo = path_params.get("correo")

    # Opción 2 (si quieres simple para pruebas): event["correo"]
    if not correo and "correo" in event:
        correo = event["correo"]

    if not correo:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "correo es obligatorio"})
        }

    resp = usuarios_table.get_item(Key={"correo": correo})

    if "Item" not in resp:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Usuario no encontrado"})
        }

    user = resp["Item"]
    user.pop("contrasena", None)

    return {
        "statusCode": 200,
        "body": user
    }
