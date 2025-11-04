import json
import boto3
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
usuarios_table = dynamodb.Table(TABLE_USUARIOS_NAME)



def lambda_handler(event, context):
    resp = usuarios_table.scan()
    items = resp.get("Items", [])

    for u in items:
        u.pop("contrasena", None)

    return {
        "statusCode": 200,
        "body": items
    }
