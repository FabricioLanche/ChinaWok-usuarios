import boto3
import hashlib
import uuid
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):

    correo = event.get('correo')
    contrasena = event.get('contrasena')

    if not correo or not contrasena:
        return {
            'statusCode': 400,
            'body': 'correo y contrasena son obligatorios'
        }

    hashed_password = hash_password(contrasena)

    dynamodb = boto3.resource('dynamodb')
    tabla_usuarios = dynamodb.Table('ChinaWok-Usuarios')

    response = tabla_usuarios.get_item(Key={'correo': correo})
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': 'Usuario no existe'
        }

    usuario = response['Item']
    hashed_password_bd = hash_password(usuario['contrasena']) 

    if hashed_password != hashed_password_bd:
        return {
            'statusCode': 403,
            'body': 'Password incorrecto'
        }

    token = str(uuid.uuid4())
    fecha_exp = datetime.now() + timedelta(minutes=60)

    tabla_tokens = dynamodb.Table('ChinaWok-Tokens')
    tabla_tokens.put_item(
        Item={
            'token': token,
            'correo_usuario': correo,
            'expira': fecha_exp.strftime('%Y-%m-%d %H:%M:%S')
        }
    )

    return {
        'statusCode': 200,
        'token': token,
        'expira': fecha_exp.strftime('%Y-%m-%d %H:%M:%S'),
        'usuario': {
            'correo': correo,
            'nombre': usuario.get('nombre'),
            'role': usuario.get('role')
        }
    }
