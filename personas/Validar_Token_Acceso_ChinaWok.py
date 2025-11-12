import boto3
import os
from datetime import datetime
from utils.utils import validar_token

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_TOKENS = os.getenv("TABLE_TOKENS", "ChinaWok-Tokens")
TABLE_USUARIOS = os.getenv("TABLE_USUARIOS", "ChinaWok-Usuarios")

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
tabla_tokens = dynamodb.Table(TABLE_TOKENS)
tabla_usuarios = dynamodb.Table(TABLE_USUARIOS)

def lambda_handler(event, context):
    token = event.get("token")
    return validar_token(token)
