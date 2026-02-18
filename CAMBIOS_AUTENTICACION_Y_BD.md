# 🔐 Cambios en Autenticación y Base de Datos

## 📋 Resumen de Cambios

Este documento describe los cambios realizados para resolver los problemas de autenticación y actualizar el nombre de la base de datos.

---

## 🎯 Problemas Resueltos

### 1. ✅ Soporte para Contraseñas en Texto Plano

**Problema:** Las contraseñas encriptadas con bcrypt estaban causando problemas de inicio de sesión con datos existentes que usan texto plano.

**Solución:** Se modificó el sistema de autenticación para soportar **múltiples formatos de contraseña** simultáneamente:

- ✅ **Texto plano** (para compatibilidad con datos existentes)
- ✅ **Bcrypt** (formato seguro con hash)
- ✅ **SHA256** (formato legacy)

**Orden de verificación:**
1. Primero intenta comparación directa (texto plano)
2. Si falla, intenta verificación bcrypt
3. Si falla, intenta verificación SHA256

### 2. ✅ Actualización de Nombre de Base de Datos

**Problema:** La base de datos anterior era `educando_db`, pero ahora es `WebApp`.

**Solución:** Se actualizaron todos los archivos de configuración:

- ✅ `backend/.env` → `DB_NAME="WebApp"`
- ✅ `backend/.env.example` → `DB_NAME=WebApp`
- ✅ `.env.example` → `DB_NAME=WebApp`
- ✅ `backend/verify_mongodb.py` → Default: `'WebApp'`

### 3. ✅ Configuración de Modo de Almacenamiento de Contraseñas

**Nueva Variable de Entorno:** `PASSWORD_STORAGE_MODE`

**Opciones:**
- `plain` = Almacena contraseñas en texto plano (configuración actual)
- `bcrypt` = Hashea contraseñas con bcrypt (más seguro)

**Configuración Actual:** `PASSWORD_STORAGE_MODE="plain"`

---

## 📝 Archivos Modificados

### 1. `backend/server.py`

#### Cambios en `hash_password()`:
```python
def hash_password(password: str) -> str:
    """Store password based on PASSWORD_STORAGE_MODE (plain or bcrypt)"""
    if PASSWORD_STORAGE_MODE == 'plain':
        # Store password as plain text (for backwards compatibility with existing data)
        return password
    else:
        # Hash password using bcrypt
        return pwd_context.hash(password)
```

#### Cambios en `verify_password()`:
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash, SHA256, or plain text"""
    # First, try plain text comparison (for backwards compatibility with existing data)
    if plain_password == hashed_password:
        return True
    
    try:
        # Try bcrypt (new format)
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, UnknownHashError):
        # Fall back to SHA256 for legacy passwords
        if not hashed_password.startswith(('$2a$', '$2b$', '$2y$')):
            try:
                return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
            except Exception:
                return False
        return False
    except Exception as e:
        logger.error(f"Unexpected error during password verification: {type(e).__name__}")
        return False
```

#### Nueva Configuración:
```python
# Password storage mode: 'plain' for plain text, 'bcrypt' for hashed (default: 'plain' for compatibility)
PASSWORD_STORAGE_MODE = os.environ.get('PASSWORD_STORAGE_MODE', 'plain').lower()
```

### 2. `backend/.env`

```bash
DB_NAME="WebApp"
CORS_ORIGINS="*"

# Password Storage Mode: 'plain' or 'bcrypt'
# 'plain' = Store passwords as plain text (for backwards compatibility)
# 'bcrypt' = Hash passwords with bcrypt (more secure, but incompatible with existing plain text passwords)
PASSWORD_STORAGE_MODE="plain"
```

### 3. `backend/verify_mongodb.py`

```python
# Línea 47: Cambio de default
db_name = 'WebApp'  # default (antes: 'educando_db')
```

---

## 🔍 Cómo Funciona Ahora

### Inicio de Sesión

1. Usuario ingresa email/cédula y contraseña
2. Sistema busca el usuario en la base de datos `WebApp`
3. Sistema compara la contraseña ingresada con `password_hash` del usuario:
   - **Si coinciden como texto plano** → ✅ Login exitoso
   - **Si no coinciden, intenta bcrypt** → ✅ Login exitoso si el hash es válido
   - **Si falla bcrypt, intenta SHA256** → ✅ Login exitoso si el hash es válido
   - **Si todo falla** → ❌ Credenciales incorrectas

### Creación de Nuevos Usuarios

Cuando se crean usuarios con `create_initial_data()`:
- Si `PASSWORD_STORAGE_MODE="plain"` → Contraseña se guarda como texto plano
- Si `PASSWORD_STORAGE_MODE="bcrypt"` → Contraseña se hashea con bcrypt

**Configuración Actual:** Texto plano (`PASSWORD_STORAGE_MODE="plain"`)

---

## 🧪 Pruebas Realizadas

Se verificó que el sistema funciona con todos los formatos:

```
✅ Test 1: Plain Text Password (MODE='plain')
   Password: educador123
   Stored:   educador123
   Verification: True

✅ Test 2: Existing Plain Text in Database
   Password: educador123
   Stored:   educador123
   Verification: True

✅ Test 3: Existing Bcrypt Hash in Database
   Password: Profe2026*DS
   Stored:   $2b$12$h9yGc6e7a4s1YBiNGyzEQOMLFGfz6tZ...
   Verification: True

✅ Test 4: Existing SHA256 Hash in Database
   Password: Admin2026*LT
   Stored:   12c9ee5983c30e043803e6cf0c5d4f8a7f12a853...
   Verification: True

✅ Test 5: Wrong Password (should fail)
   Password: wrongpassword
   Stored:   educador123
   Verification: False ✓
```

---

## 📦 Credencial del Profesor Añadida

En `backend/server.py`, línea 260:

```python
{"id": "user-prof-3", 
 "name": "Profesor Sl", 
 "email": "pr.o.fe.sorSl@educando.com", 
 "cedula": None, 
 "password_hash": hash_password("educador123"),  # Ahora se guarda como "educador123" (texto plano)
 "role": "profesor", 
 "program_id": None, 
 "program_ids": [], 
 "subject_ids": [], 
 "phone": "3009998877", 
 "active": True, 
 "module": None, 
 "grupo": None},
```

Con `PASSWORD_STORAGE_MODE="plain"`, la contraseña se guarda como `"educador123"` (texto plano).

---

## 🚀 Cómo Usar

### Para Iniciar Sesión con el Profesor

1. Ve a la página de login
2. Selecciona la pestaña **"PROFESOR"**
3. Ingresa email: `pr.o.fe.sorSl@educando.com`
4. Ingresa contraseña: `educador123`
5. Haz clic en "Ingresar"

### Para Cambiar el Modo de Almacenamiento

Si en el futuro quieres usar bcrypt (más seguro):

1. Edita `backend/.env`:
   ```bash
   PASSWORD_STORAGE_MODE="bcrypt"
   ```

2. **IMPORTANTE:** Esto solo afecta a nuevos usuarios. Los usuarios existentes con contraseñas en texto plano seguirán funcionando porque `verify_password()` soporta todos los formatos.

---

## ⚠️ Consideraciones de Seguridad

### Texto Plano vs Bcrypt

**Texto Plano (Actual):**
- ✅ Compatible con datos existentes
- ✅ Fácil de debuguear
- ❌ **NO es seguro** - Si alguien accede a la base de datos, puede ver todas las contraseñas
- ❌ No cumple con mejores prácticas de seguridad

**Bcrypt (Recomendado para Producción):**
- ✅ **Muy seguro** - Incluso con acceso a la base de datos, las contraseñas están protegidas
- ✅ Cumple con estándares de seguridad
- ✅ Resistente a ataques de fuerza bruta
- ⚠️ Requiere migración de contraseñas existentes

### Recomendación

Para un sistema en **producción**, se recomienda:

1. **Opción A - Migración Gradual:**
   - Mantener `PASSWORD_STORAGE_MODE="plain"` temporalmente
   - Implementar un endpoint de "cambio de contraseña"
   - Al cambiar contraseña, guardarla con bcrypt
   - Gradualmente, todos los usuarios tendrán bcrypt

2. **Opción B - Migración Masiva:**
   - Forzar a todos los usuarios a resetear su contraseña
   - Cambiar `PASSWORD_STORAGE_MODE="bcrypt"`
   - Todas las nuevas contraseñas se guardan con bcrypt

---

## 📊 Base de Datos WebApp

### Estructura Esperada

```
WebApp (base de datos)
├── users (colección)
│   ├── user-editor-1 (Carlos Mendez)
│   ├── user-admin-1 (Laura Torres)
│   ├── user-admin-2 (Roberto Ramirez)
│   ├── user-prof-1 (Diana Silva)
│   ├── user-prof-2 (Miguel Castro)
│   ├── user-prof-3 (Profesor Sl) ← NUEVO
│   ├── user-est-1 (Sofía Morales)
│   └── user-est-2 (Andrés Lopez)
├── programs (colección)
├── subjects (colección)
├── courses (colección)
└── ... (otras colecciones)
```

### Verificar Base de Datos

Para verificar que la base de datos está correctamente configurada:

```bash
cd backend
python verify_mongodb.py "mongodb+srv://usuario:password@cluster.mongodb.net/WebApp"
```

---

## 🔄 Compatibilidad

El sistema ahora es **completamente compatible** con:

1. ✅ Contraseñas existentes en texto plano (MongoDB existente)
2. ✅ Contraseñas con hash bcrypt (nuevas implementaciones)
3. ✅ Contraseñas con hash SHA256 (legacy)
4. ✅ Mezcla de todos los formatos en la misma base de datos

---

## 📅 Historial de Cambios

**Fecha:** 2026-02-18  
**Base de datos:** WebApp (MongoDB Atlas)  
**Sistema:** Plataforma Educando  
**Modo de contraseñas:** Plain text (compatible con todos los formatos)

---

## 🆘 Solución de Problemas

### Problema: "Credenciales incorrectas" con contraseña correcta

**Causa posible:** La contraseña en la base de datos tiene un formato diferente.

**Solución:** El sistema ahora intenta todos los formatos automáticamente. Si sigue fallando:

1. Verifica que el usuario existe en la base de datos `WebApp`
2. Verifica el campo `password_hash` del usuario
3. Compara directamente con la contraseña ingresada

### Problema: Usuarios no se crean al iniciar

**Causa:** La colección `users` ya tiene datos.

**Solución:** La función `create_initial_data()` solo crea usuarios si la colección está vacía. Para recrear usuarios:

1. Elimina todos los documentos de la colección `users`
2. Reinicia el backend
3. Los usuarios se crearán automáticamente

---

## ✅ Resumen Final

- ✅ Base de datos actualizada a `WebApp`
- ✅ Soporte para contraseñas en texto plano
- ✅ Soporte para contraseñas con bcrypt
- ✅ Soporte para contraseñas con SHA256
- ✅ Credencial del profesor `pr.o.fe.sorSl@educando.com` añadida
- ✅ Configuración flexible con `PASSWORD_STORAGE_MODE`
- ✅ Totalmente compatible con datos existentes

**El sistema está listo para usarse con la base de datos WebApp y contraseñas en cualquier formato.**
