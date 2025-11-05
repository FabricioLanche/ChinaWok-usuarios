# API CRUD de Usuarios – ChinaWok (AWS Lambda + DynamoDB)

Este proyecto implementa un CRUD completo de usuarios utilizando AWS Lambda, API Gateway y DynamoDB, gestionado mediante el framework Serverless. Incluye autenticación con tokens temporales, control de roles (Cliente / Admin) y endpoints protegidos.

Se utiliza Python 3.12, AWS Lambda, AWS API Gateway, AWS DynamoDB y Serverless Framework. También se incluye una colección de Postman para pruebas.

```
La estructura del proyecto es:
crud-usuarios/
├── crear_usuario.py
├── login.py
├── listar_usuarios.py
├── buscar_usuario.py
├── modificar_usuario.py
├── eliminar_usuario.py
├── validar_token.py
├── requirements.txt
└── serverless.yml
```

Para desplegar el proyecto con Serverless:
```
1️⃣ Instala dependencias:
npm install -g serverless
pip install -r requirements.txt
2️⃣ Configura credenciales AWS:
aws configure
3️⃣ Despliega:
serverless deploy
```
Esto creará automáticamente los endpoints en API Gateway.

Los endpoints principales son:

| Función | Método | Endpoint | Requiere Token | Rol permitido |
|----------|---------|-----------|----------------|----------------|
| Crear usuario | POST | /usuario/crear | No | Público |
| Login | POST | /usuario/login | No | Público |
| Listar usuarios | GET | /usuario/listar | Sí | Admin |
| Buscar usuario | POST | /usuario/buscar | Sí | Admin |
| Modificar usuario | PUT | /usuario/modificar | Sí | Cliente/Admin |
| Eliminar usuario | DELETE | /usuario/eliminar | Sí | Admin |
| Validar token | POST | /usuario/validartoken | Sí | Todos |

Cada usuario se define con el siguiente esquema JSON:
```
{
  "nombre": "string",
  "correo": "string",
  "contrasena": "string",
  "role": "Cliente | Admin",
  "informacion_bancaria": {
    "numero_tarjeta": "string",
    "cvv": "string",
    "fecha_vencimiento": "string",
    "direccion_facturacion": "string"
  }
}
```
Al crear un usuario, el role se establece automáticamente como "Cliente". Solo los administradores pueden listar, buscar o eliminar usuarios. Los clientes pueden modificar sus datos personales o su información bancaria.

El login genera un token único (uuid4) con duración de 60 minutos. Los tokens se almacenan en la tabla ChinaWok-Tokens. Todas las funciones protegidas verifican el token a través de la Lambda Validar_Token_Acceso_ChinaWok. El token también incluye información del usuario como correo y rol, lo cual permite al frontend determinar el nivel de acceso.

Postman Collection: importar “Chinawok - Usuarios con Token Admin.postman_collection.json”. Incluye login de Cliente y Admin (guardan automáticamente {{token}} y {{token_admin}}) y requests con Authorization: Bearer {{token_admin}}.
```
Roles y seguridad:
- Cliente: puede modificar su información y tarjeta.
- Admin: puede listar, buscar y eliminar usuarios, además de cambiar roles.
- Para crear un Admin: 
  1. Crear el usuario como “Cliente”.
  2. Modificarlo a “Admin” desde una cuenta admin.
  3. O agregarlo manualmente en DynamoDB con “role”: “Admin”.
```
Ejemplo creación usuario:
```
POST /usuario/crear
{
  "nombre": "Usuario Prueba",
  "correo": "cliente@chinawok.pe",
  "contrasena": "Cliente123!"
}
```
Ejemplo actualización de tarjeta:
```
PUT /usuario/modificar
{
  "correo": "cliente@chinawok.pe",
  "informacion_bancaria": {
    "numero_tarjeta": "4111111111111111",
    "cvv": "123",
    "fecha_vencimiento": "12/25",
    "direccion_facturacion": "Lima, Perú"
  }
}
```
