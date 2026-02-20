# 👥 Credenciales de Usuarios del Sistema

**Fecha de Creación:** 19 de Febrero 2026  
**Versión:** 2.0

## 🔐 Usuarios por Defecto

Los usuarios se crean automáticamente llamando al endpoint `/api/admin/reset-users` o ejecutando el script `scripts/reset_users.sh`.

### 📋 Lista de Usuarios

#### 1️⃣ Administradores (2)

**Admin Principal**
- 🔑 **Email:** `admin@educando.com`
- 🔒 **Contraseña:** `Admin2026`
- 👤 **Nombre:** Admin Principal
- 📱 **Teléfono:** 3001234567
- 🚪 **Login:** Usar pestaña "ADMINISTRADOR" en la página de login

**Admin Secundario**
- 🔑 **Email:** `admin2@educando.com`
- 🔒 **Contraseña:** `Admin2026`
- 👤 **Nombre:** Admin Secundario
- 📱 **Teléfono:** 3001234568
- 🚪 **Login:** Usar pestaña "ADMINISTRADOR" en la página de login

---

#### 2️⃣ Editor (1)

**Editor Principal**
- 🔑 **Email:** `editor@educando.com`
- 🔒 **Contraseña:** `Editor2026`
- 👤 **Nombre:** Editor Principal
- 📱 **Teléfono:** 3002222222
- ⚠️ **IMPORTANTE:** El editor inicia sesión usando la pestaña "PROFESOR"

---

#### 3️⃣ Profesores (2)

**Profesor 1**
- 🔑 **Email:** `profesor@educando.com`
- 🔒 **Contraseña:** `Profe2026`
- 👤 **Nombre:** María García
- 📱 **Teléfono:** 3007654321
- 🚪 **Login:** Usar pestaña "PROFESOR" en la página de login

**Profesor 2**
- 🔑 **Email:** `profesor2@educando.com`
- 🔒 **Contraseña:** `Profe2026`
- 👤 **Nombre:** Carlos Rodríguez
- 📱 **Teléfono:** 3009876543
- 🚪 **Login:** Usar pestaña "PROFESOR" en la página de login

---

#### 4️⃣ Estudiantes (2)

**Estudiante 1**
- 🔑 **Cédula:** `1001`
- 🔒 **Contraseña:** `1001`
- 👤 **Nombre:** Juan Martínez
- 📱 **Teléfono:** 3101234567
- 🚪 **Login:** Usar pestaña "ESTUDIANTE" con la cédula

**Estudiante 2**
- 🔑 **Cédula:** `1002`
- 🔒 **Contraseña:** `1002`
- 👤 **Nombre:** Ana Hernández
- 📱 **Teléfono:** 3207654321
- 🚪 **Login:** Usar pestaña "ESTUDIANTE" con la cédula

---

## 🔧 Cómo Reiniciar Usuarios

### Opción 1: Script (Recomendado)
```bash
cd scripts
chmod +x reset_users.sh
./reset_users.sh
```

### Opción 2: Llamada directa a la API
```bash
curl -X POST "http://localhost:8000/api/admin/reset-users?confirm_token=RESET_ALL_USERS_CONFIRM"
```

### Opción 3: Desde Python
```python
import requests
response = requests.post(
    'http://localhost:8000/api/admin/reset-users',
    params={'confirm_token': 'RESET_ALL_USERS_CONFIRM'}
)
print(response.json())
```

### Desactivar en Producción
Para desactivar este endpoint en producción, agrega esta variable de entorno:
```bash
ALLOW_USER_RESET=false
```

---

## ⚠️ NOTAS IMPORTANTES

1. **Formato de Login:**
   - **Admin:** Usa email (admin@educando.com)
   - **Editor:** Usa email EN LA PESTAÑA DE PROFESOR (editor@educando.com)
   - **Profesor:** Usa email (profesor@educando.com)
   - **Estudiante:** Usa cédula sin puntos ni guiones (1001)

2. **Seguridad:**
   - ⚠️ **CAMBIAR CONTRASEÑAS** en producción
   - Este archivo NO debe estar en el repositorio público
   - Las contraseñas por defecto son solo para desarrollo/pruebas

3. **Endpoint de Reset:**
   - ⚠️ **PELIGRO:** `/api/admin/reset-users` elimina TODOS los usuarios
   - Requiere token de confirmación: `confirm_token=RESET_ALL_USERS_CONFIRM`
   - Puede ser desactivado en producción con `ALLOW_USER_RESET=false`
   - Solo usar en desarrollo/testing

4. **Persistencia:**
   - Los usuarios creados por el endpoint de reset NO se sobreescriben automáticamente
   - Solo se recrean si llamas explícitamente al endpoint `/api/admin/reset-users`

---

## 📞 Soporte

Si tienes problemas para iniciar sesión:
1. Verifica que estés usando la pestaña correcta de login
2. Verifica el formato correcto (email para profesores/admin, cédula para estudiantes)
3. Las contraseñas son case-sensitive
4. Si persiste el problema, ejecuta el script de reset de usuarios
