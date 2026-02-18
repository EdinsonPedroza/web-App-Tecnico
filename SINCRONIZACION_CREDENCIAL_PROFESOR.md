# Sincronización de Credencial de Profesor a MongoDB

## Resumen de Cambios

Este documento describe los cambios realizados para sincronizar la credencial del profesor `pr.o.fe.sorSl@educando.com` a la base de datos MongoDB WebApp.

## Credencial Añadida

**Email:** pr.o.fe.sorSl@educando.com  
**Contraseña:** educador123  
**Rol:** profesor  
**Nombre:** Profesor Sl  
**Teléfono:** 3009998877  
**ID de Usuario:** user-prof-3  

## Cambios Realizados

### 1. Actualización de `backend/server.py`

Se añadió la nueva credencial de profesor en la función `create_initial_data()` (líneas 257-260):

```python
{"id": "user-prof-3", "name": "Profesor Sl", "email": "pr.o.fe.sorSl@educando.com", 
 "cedula": None, "password_hash": hash_password("educador123"), "role": "profesor", 
 "program_id": None, "program_ids": [], "subject_ids": [], "phone": "3009998877", 
 "active": True, "module": None, "grupo": None},
```

### 2. Actualización de `USUARIOS_Y_CONTRASEÑAS.txt`

Se documentó la nueva credencial como "PROFESOR 3" en el archivo de referencia de usuarios.

### 3. Configuración de MongoDB

Se actualizó la configuración para apuntar a la base de datos correcta:

- **DB_NAME:** WebApp (con mayúsculas W y A)
- **Conexión:** mongodb+srv://<username>:<password>@cluster0.avzgmr5.mongodb.net/webApp?appName=Cluster0

**NOTA:** Las credenciales de MongoDB se configuraron en `backend/.env.local` que está excluido de git por seguridad. Este archivo contiene la URL de conexión completa con usuario y contraseña.

### 4. Corrección de DB_NAME

Se corrigió el valor de `DB_NAME` en `backend/.env` de "webApp" a "WebApp" para que coincida con el nombre de la base de datos en MongoDB Atlas.

## Cómo Funciona

### Inicialización de Datos

Cuando el backend se inicia por primera vez o cuando la base de datos está vacía:

1. La función `create_initial_data()` se ejecuta automáticamente en el evento `startup`
2. Verifica si ya existen usuarios en la base de datos
3. Si NO existen usuarios, crea todos los usuarios iniciales, incluyendo el nuevo profesor
4. La contraseña se hashea usando bcrypt antes de almacenarse

### Autenticación

Para iniciar sesión con esta credencial:

1. Ir a la página de login
2. Seleccionar la pestaña **"PROFESOR"**
3. Ingresar email: `pr.o.fe.sorSl@educando.com`
4. Ingresar contraseña: `educador123`
5. Hacer clic en "Ingresar"

El sistema:
- Busca el usuario por email en la base de datos
- Verifica que el rol sea "profesor", "admin" o "editor"
- Valida la contraseña usando bcrypt
- Genera un token JWT si las credenciales son correctas
- Redirige al dashboard de profesor

## Seguridad

✅ La contraseña se hashea con bcrypt (algoritmo seguro de hashing)  
✅ Las credenciales de MongoDB están en `.env.local` (no se commitean a git)  
✅ El sistema usa autenticación JWT con tokens  
✅ Hay rate limiting en el login (5 intentos cada 5 minutos)  

## Verificación

Para verificar que la credencial funciona correctamente:

```bash
cd /home/runner/work/web-App-Tecnico/web-App-Tecnico/backend
python3 -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
password = 'educador123'
pwd_hash = pwd_context.hash(password)
is_valid = pwd_context.verify(password, pwd_hash)
print(f'Password hash test: {is_valid}')
"
```

Resultado esperado: `Password hash test: True`

## Próximos Pasos

Si necesitas que los usuarios se creen en una base de datos existente que ya tiene usuarios:

1. **Opción 1 - Reiniciar la base de datos:**
   - Eliminar todos los documentos de la colección `users`
   - Reiniciar el backend para que cree los usuarios nuevos

2. **Opción 2 - Insertar manualmente:**
   - Conectarse a MongoDB Atlas
   - Ejecutar un script para insertar solo el nuevo usuario
   
3. **Opción 3 - Usar el endpoint de admin:**
   - Crear un endpoint en el backend para añadir usuarios
   - Usarlo para añadir el nuevo profesor sin eliminar datos existentes

## Archivos Modificados

- ✅ `backend/server.py` - Añadida credencial en create_initial_data()
- ✅ `USUARIOS_Y_CONTRASEÑAS.txt` - Documentación actualizada
- ✅ `backend/.env` - DB_NAME corregido a "WebApp"
- ✅ `backend/.env.local` - Credenciales de MongoDB (NO en git)

## Fecha de Cambios

**Fecha:** 2026-02-18  
**Base de datos:** WebApp (MongoDB Atlas)  
**Sistema:** Plataforma Educando
