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
cd .aws/
pico credentials
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

# ChinaWok Usuarios API

API de gestión de usuarios con JWT y control de acceso por roles.

## Roles disponibles

- **Cliente**: Usuario estándar, puede modificar su propio perfil
- **Gerente**: Acceso a funciones de gestión (a definir)
- **Admin**: Control total del sistema

## Endpoints

### Públicos (sin autenticación)
- `POST /usuario/crear` - Crear nuevo usuario
- `POST /usuario/login` - Iniciar sesión y obtener JWT

### Protegidos (requieren JWT)
- `GET /usuario/listar` - Listar usuarios
- `POST /usuario/buscar` - Buscar usuario por correo
- `PUT /usuario/modificar` - Modificar usuario
- `DELETE /usuario/eliminar` - Eliminar usuario (solo Admin)

## Configuración

1. Copiar `.env.example` a `.env` y configurar:
   ```bash
   cp .env.example .env
   ```

2. Editar `.env` con tus valores:
   ```env
   AWS_ACCOUNT_ID=your_account_id
   JWT_SECRET=your_secret_key
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Desplegar:
   ```bash
   serverless deploy
   ```

## Uso con Postman

1. Importar `ChinaWok-Usuarios.postman_collection.json`
2. Configurar variable `base_url` con tu API Gateway URL
3. Ejecutar carpeta "1. Crear Usuarios"
4. Cambiar roles manualmente en DynamoDB:
   - `admin@chinawok.pe` → role: "Admin"
   - `gerente@chinawok.pe` → role: "Gerente"
5. Ejecutar carpeta "2. Login" para obtener tokens
6. Probar endpoints con diferentes roles

## Permisos por rol

### Cliente
- ✅ Ver su propio perfil
- ✅ Modificar su propio perfil
- ✅ Agregar información bancaria
- ❌ Cambiar su rol
- ❌ Modificar otros usuarios
- ❌ Eliminar usuarios

### Gerente
- ✅ Todos los permisos de Cliente
- ❌ Cambiar roles
- ❌ Eliminar usuarios

### Admin
- ✅ Control total
- ✅ Modificar cualquier usuario
- ✅ Cambiar roles
- ✅ Eliminar usuarios

## Estructura del JWT

```json
{
  "correo": "usuario@chinawok.pe",
  "role": "Cliente",
  "nombre": "Juan Pérez",
  "iat": 1234567890,
  "exp": 1234654290
}
```

## Esquema de Usuario

```json
{
  "nombre": "string",
  "correo": "email",
  "contrasena": "string (min 6)",
  "role": "Cliente | Gerente | Admin",
  "informacion_bancaria": {
    "numero_tarjeta": "13-19 dígitos",
    "cvv": "3-4 dígitos",
    "fecha_vencimiento": "MM/YY",
    "direccion_delivery": "string"
  },
  "historial_pedidos": []
}
```
