import json
import boto3
import os

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_USUARIOS_NAME = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
usuarios_table = dynamodb.Table(TABLE_USUARIOS_NAME)


def lambda_handler(event, context):

    body = {}

    if isinstance(event, dict) and "body" in event:
        raw_body = event.get("body")
        if isinstance(raw_body, str):
            body = json.loads(raw_body) if raw_body else {}
        elif isinstance(raw_body, dict):
            body = raw_body
        else:
            body = {}
    elif isinstance(event, dict):
        body = event
    elif isinstance(event, str):
        body = json.loads(event)
    else:
        body = {}

    correo = body.get("correo")

    if not correo:
        path_params = event.get("pathParameters") or {}
        correo = path_params.get("correo")

    if not correo:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "correo es obligatorio"})
        }

    new_nombre = body.get("nombre")
    new_contrasena = body.get("contrasena")
    new_role = body.get("role")
    new_info_bancaria = body.get("informacion_bancaria")

    update_parts = []
    expr_values = {}
    expr_names = {}  

    if new_nombre:
        update_parts.append("nombre = :nombre")
        expr_values[":nombre"] = new_nombre

    if new_contrasena:
        update_parts.append("contrasena = :contrasena")
        expr_values[":contrasena"] = new_contrasena

    if new_role:
 
        update_parts.append("#role_attr = :role")
        expr_values[":role"] = new_role
        expr_names["#role_attr"] = "role"

    if new_info_bancaria is not None:
        update_parts.append("informacion_bancaria = :info")
        expr_values[":info"] = new_info_bancaria

    if not update_parts:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "No hay campos a actualizar"})
        }

    update_expr = "SET " + ", ".join(update_parts)

    params = {
        "Key": {"correo": correo},
        "UpdateExpression": update_expr,
        "ExpressionAttributeValues": expr_values,
        "ReturnValues": "ALL_NEW"
    }

    if expr_names:
        params["ExpressionAttributeNames"] = expr_names

    resp = usuarios_table.update_item(**params)

    updated = resp.get("Attributes", {})
    updated.pop("contrasena", None)  

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Usuario actualizado",
            "user": updated
        })
    }
