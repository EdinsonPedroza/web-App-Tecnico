# ✅ SOLUCIÓN: "Las Credenciales No Sirven"

## 📌 RESPUESTA DIRECTA A TU PROBLEMA

**Tu pregunta**: "POR FAVOR YA NO SÉ QUÉ HACER, LAS CREDENCIALES NO SIRVEN. DENTRO DE MONGO QUE DEBO PODER VER"

---

## 🎯 RESPUESTA RÁPIDA (Lee esto primero)

### 1. ¿Por qué NO funcionan las credenciales?

**Causa #1 (90% de los casos)**: MongoDB NO está conectado en Render

**Síntoma**: Las credenciales dan error "Usuario o contraseña incorrectos" incluso con las credenciales correctas.

**Solución**: Conectar MongoDB Atlas a Render (15 minutos)
- **Lee**: [INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md) para hacerlo paso a paso

---

### 2. ¿Qué DEBES poder ver dentro de MongoDB?

Cuando MongoDB está correctamente conectado, debes ver:

```
Base de datos: educando_db
│
├── Colección: users (7 documentos)
│   ├── 1 Editor: carlos.mendez@educando.com
│   ├── 2 Admins: laura.torres@... y roberto.ramirez@...
│   ├── 2 Profesores: diana.silva@... y miguel.castro@...
│   └── 2 Estudiantes: cédulas 1001234567 y 1002345678
│
├── Colección: programs (1 documento)
│   └── Administración de Empresas
│
├── Colección: subjects (6 documentos)
│   └── (6 materias del programa)
│
└── Colección: courses (4 documentos)
    └── (4 cursos activos)
```

**Guía visual completa**: [QUE_VER_EN_MONGO.md](QUE_VER_EN_MONGO.md)

---

## 🚀 SOLUCIÓN EN 3 PASOS

### PASO 1: Verificar si MongoDB está conectado (30 segundos)

1. Ve a: https://dashboard.render.com
2. Selecciona tu servicio: `educando-backend`
3. Haz clic en la pestaña: **Logs**
4. Busca (Ctrl+F o Cmd+F): `"MongoDB connection successful"`

**¿Lo encontraste?**

✅ **SÍ** → MongoDB está conectado
- Tu problema es otro. Ve al **PASO 2**

❌ **NO** → MongoDB NO está conectado
- **Este es tu problema principal**
- Continúa con **PASO 1A** (abajo)

---

### PASO 1A: Conectar MongoDB (Si NO está conectado)

**Tiempo**: 15-20 minutos
**Costo**: $0 (gratuito con MongoDB Atlas)

**Guía paso a paso**: [INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md) - Sección A

**Resumen rápido**:

1. **Crear cuenta en MongoDB Atlas**:
   ```
   → https://www.mongodb.com/cloud/atlas/register
   → Crear cuenta gratis (usa Google/GitHub)
   ```

2. **Crear cluster gratuito**:
   ```
   → Build a Database
   → M0 FREE (512MB gratis)
   → Esperar 2-3 minutos
   ```

3. **Crear usuario de base de datos**:
   ```
   → Database Access → Add New Database User
   → Usuario: educando_user
   → Contraseña: [Genera una segura y GUÁRDALA]
   → Privilegios: Read and write to any database
   ```

4. **Permitir acceso desde cualquier IP**:
   ```
   → Network Access → Add IP Address
   → Allow Access from Anywhere (0.0.0.0/0)
   ```

5. **Obtener connection string**:
   ```
   → Database → Connect → Connect your application
   → Copiar connection string
   → Reemplazar <password> con tu contraseña real
   → Agregar /educando_db antes del ?
   
   Ejemplo correcto:
   mongodb+srv://educando_user:MiPass123@cluster.mongodb.net/educando_db?retryWrites=true
   ```

6. **Configurar en Render**:
   ```
   → Render Dashboard → educando-backend → Environment
   → Agregar variable: MONGO_URL = [tu connection string]
   → Save Changes
   → Manual Deploy → Deploy latest commit
   → Esperar 2-3 minutos
   ```

7. **Verificar que funcionó**:
   ```
   → Logs → Buscar:
     ✅ "MongoDB connection successful"
     ✅ "Datos iniciales creados exitosamente"
     ✅ "Credenciales creadas para 7 usuarios"
   ```

**¿Todos esos mensajes aparecieron?** ¡Perfecto! Ahora prueba el login en **PASO 3**.

---

### PASO 2: Verificar credenciales (Si MongoDB SÍ está conectado)

Si viste "MongoDB connection successful" pero el login no funciona:

#### 2A. Verifica que usas el ROL correcto

**ESTUDIANTES**:
```
✅ Pestaña: ESTUDIANTE (no Profesor)
✅ Usuario: Solo el número de cédula (ej: 1001234567)
✅ Sin puntos, sin guiones, sin espacios
```

**PROFESORES / ADMINS / EDITORES**:
```
✅ Pestaña: PROFESOR (no Estudiante)
✅ Usuario: Email completo (ej: laura.torres@educando.com)
✅ Sin espacios antes o después
```

⚠️ **MUY IMPORTANTE**: Los ADMINS y EDITORES también usan la pestaña "PROFESOR"

#### 2B. Verifica la contraseña exacta

Las contraseñas distinguen entre MAYÚSCULAS y minúsculas.

**Abre**: [USUARIOS_Y_CONTRASEÑAS.txt](USUARIOS_Y_CONTRASEÑAS.txt)

**Prueba con estos usuarios**:

| Rol | Pestaña | Usuario | Contraseña |
|-----|---------|---------|------------|
| Admin | PROFESOR | laura.torres@educando.com | Admin2026*LT |
| Profesor | PROFESOR | diana.silva@educando.com | Profe2026*DS |
| Estudiante | ESTUDIANTE | 1001234567 | Estud2026*SM |

⚠️ **Copia y pega** la contraseña exactamente como está escrita.

#### 2C. Verifica que los usuarios se crearon

En los logs de Render, busca:
```
"Credenciales creadas para 7 usuarios"
```

**❌ No lo viste**: Los usuarios no se crearon
```
→ Manual Deploy → Deploy latest commit
→ Esperar 2-3 minutos
→ Revisar logs nuevamente
```

**✅ Sí lo viste**: Los usuarios existen, el problema es otro (continúa a 2D)

#### 2D. Verifica el frontend y backend

1. **Verifica que el frontend apunte al backend correcto**:
   ```
   Render → educando-frontend → Environment
   → Busca: REACT_APP_BACKEND_URL
   → Debe ser: https://educando-backend.onrender.com (o tu URL de backend)
   ```

2. **Verifica que el backend responda**:
   ```
   Abre en tu navegador:
   https://TU-BACKEND-URL.onrender.com/api/health
   
   Debe devolver:
   {"status": "healthy"}
   ```

3. **Revisa la consola del navegador**:
   ```
   → Abre tu aplicación
   → Presiona F12
   → Pestaña: Console
   → Intenta hacer login
   → ¿Ves errores? Cópialos y busca solución
   ```

---

### PASO 3: Probar el login

Una vez que MongoDB esté conectado y los usuarios creados:

1. **Ve a tu aplicación** en el navegador
2. **Selecciona la pestaña correcta**:
   - Para estudiantes: ESTUDIANTE
   - Para otros: PROFESOR
3. **Ingresa las credenciales de prueba**:
   ```
   Admin:
   - Pestaña: PROFESOR
   - Email: laura.torres@educando.com
   - Contraseña: Admin2026*LT
   ```
4. **Haz clic en "Ingresar"**

✅ **¿Funcionó?** ¡Perfecto! Ya puedes usar la aplicación.

❌ **¿No funcionó?** Lee la **Sección de Problemas Comunes** abajo.

---

## 🔍 CÓMO VER QUÉ HAY DENTRO DE MONGODB

Hay 4 formas de ver los datos en MongoDB:

### Opción 1: MongoDB Compass (MÁS FÁCIL - Interfaz Gráfica)

**Ventajas**: Visual, fácil de usar, no necesitas saber comandos

**Pasos**:
1. Descarga: https://www.mongodb.com/try/download/compass
2. Instala en tu computadora
3. Abre MongoDB Compass
4. Pega tu connection string de MongoDB Atlas
5. Haz clic en "Connect"
6. En el panel izquierdo: `educando_db` → `users`
7. Verás los 7 usuarios con todos sus datos

**Guía visual completa**: [QUE_VER_EN_MONGO.md](QUE_VER_EN_MONGO.md)

---

### Opción 2: MongoDB Atlas Web (SIN INSTALAR NADA)

**Ventajas**: No necesitas instalar nada, funciona en el navegador

**Pasos**:
1. Ve a: https://cloud.mongodb.com
2. Inicia sesión con tu cuenta de MongoDB Atlas
3. Selecciona tu cluster
4. Haz clic en "Browse Collections"
5. Selecciona `educando_db` → `users`
6. Verás los 7 usuarios listados

---

### Opción 3: Script Automático (PARA PROGRAMADORES)

**Ventajas**: Automatizado, da diagnóstico de problemas

**Pasos**:
```bash
cd backend
pip install motor python-dotenv
python verify_mongodb.py "mongodb+srv://user:pass@cluster.net/educando_db"
```

**Salida esperada**:
```
✅ ¡Conexión exitosa a MongoDB!
✅ ¡Perfecto! Los 7 usuarios iniciales están presentes.

📋 Lista de usuarios:
   [✓] Laura Torres             | admin        | laura.torres@educando.com
   [✓] Roberto Ramirez          | admin        | roberto.ramirez@educando.com
   [✓] Carlos Mendez            | editor       | carlos.mendez@educando.com
   [✓] Diana Silva              | profesor     | diana.silva@educando.com
   [✓] Miguel Castro            | profesor     | miguel.castro@educando.com
   [✓] Sofía Morales            | estudiante   | 1001234567
   [✓] Andrés Lopez             | estudiante   | 1002345678
```

---

### Opción 4: mongosh (Línea de Comandos)

**Ventajas**: Acceso directo, para usuarios avanzados

**Pasos**:
```bash
# Instalar mongosh
brew install mongosh  # macOS
# O descargar desde: https://www.mongodb.com/try/download/shell

# Conectar
mongosh "mongodb+srv://user:pass@cluster.net/educando_db"

# Ver usuarios
db.users.find({}, {password_hash: 0}).pretty()

# Contar usuarios (debe ser 7)
db.users.countDocuments()

# Salir
exit
```

---

## 🆘 PROBLEMAS COMUNES Y SOLUCIONES

### Problema 1: "ServerSelectionTimeoutError"

**Causa**: No puede conectarse a MongoDB

**Soluciones**:
1. Verifica que el cluster de Atlas esté activo (no en pausa)
2. En Atlas → Network Access: Permite 0.0.0.0/0
3. Espera 2-3 minutos si acabas de crear el cluster
4. Verifica que la connection string sea correcta

---

### Problema 2: "Authentication failed"

**Causa**: Usuario o contraseña incorrectos en la connection string

**Soluciones**:
1. Verifica que reemplazaste `<password>` con tu contraseña real
2. Si tu contraseña tiene caracteres especiales (@, :, /), crea un nuevo usuario con contraseña simple
3. Ejemplo de connection string correcta:
   ```
   mongodb+srv://user:Pass123@cluster.mongodb.net/educando_db?retryWrites=true
   ```

---

### Problema 3: "Credenciales incorrectas" en el login

**Causa**: Varios posibles

**Diagnóstico**:
1. ¿MongoDB está conectado? → Logs deben decir "MongoDB connection successful"
2. ¿Usuarios existen? → Logs deben decir "Credenciales creadas para 7 usuarios"
3. ¿Usas el rol correcto? → Estudiantes: ESTUDIANTE, Otros: PROFESOR
4. ¿Contraseña correcta? → Copia de USUARIOS_Y_CONTRASEÑAS.txt

---

### Problema 4: No veo datos en MongoDB

**Causa**: Los datos no se crearon

**Solución**:
1. Render → educando-backend → Manual Deploy → Deploy latest commit
2. Espera 2-3 minutos
3. Verifica logs: "Credenciales creadas para 7 usuarios"
4. Si aún no aparecen, elimina la base de datos y vuelve a desplegar

---

### Problema 5: El frontend no conecta con el backend

**Causa**: Variable de entorno incorrecta

**Solución**:
1. Render → educando-frontend → Environment
2. Verifica: `REACT_APP_BACKEND_URL`
3. Debe ser: `https://educando-backend.onrender.com` (o tu URL)
4. Si cambiaste algo: Re-despliega el frontend

---

## 📚 DOCUMENTACIÓN COMPLETA

Si necesitas más información, consulta:

### Para Solucionar Problemas Rápido:
- **[INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md)** ⭐ - Diagnóstico en 30 segundos
- **[INDICE_MONGODB.md](INDICE_MONGODB.md)** - Índice de toda la documentación

### Para Entender Qué Ver en MongoDB:
- **[QUE_VER_EN_MONGO.md](QUE_VER_EN_MONGO.md)** ⭐ - Guía visual completa

### Para Configurar MongoDB desde Cero:
- **[RENDER_MONGODB_SETUP.md](RENDER_MONGODB_SETUP.md)** - Paso a paso completo

### Para Ver Credenciales:
- **[USUARIOS_Y_CONTRASEÑAS.txt](USUARIOS_Y_CONTRASEÑAS.txt)** - Lista completa

### Referencias Rápidas:
- **[TARJETA_REFERENCIA_MONGODB.md](TARJETA_REFERENCIA_MONGODB.md)** - Comandos y resumen

---

## ✅ CHECKLIST FINAL

Marca cada item cuando lo completes:

### MongoDB Atlas
- [ ] Creé cuenta en MongoDB Atlas
- [ ] Creé cluster M0 (gratuito)
- [ ] Creé usuario de base de datos
- [ ] Permití acceso desde 0.0.0.0/0
- [ ] Copié connection string
- [ ] Reemplacé `<password>` con contraseña real
- [ ] Agregué `/educando_db` antes del `?`

### Render
- [ ] Configuré variable `MONGO_URL` en backend
- [ ] Guardé los cambios
- [ ] Re-desplegué el backend
- [ ] Esperé 2-3 minutos

### Verificación
- [ ] Revisé logs del backend
- [ ] Vi mensaje: "MongoDB connection successful"
- [ ] Vi mensaje: "Credenciales creadas para 7 usuarios"
- [ ] Probé login con: laura.torres@educando.com
- [ ] Login funcionó correctamente ✅

---

## 💡 RESUMEN EJECUTIVO

**Tu problema**: "Las credenciales no sirven"

**Causa principal**: MongoDB NO está conectado en Render (90% de los casos)

**Solución**: Conectar MongoDB Atlas (gratis) a Render

**Tiempo**: 15-20 minutos

**Qué debes ver en MongoDB**: 
- 7 usuarios en colección `users`
- 1 programa, 6 materias, 4 cursos

**Credenciales de prueba**:
- Admin: laura.torres@educando.com / Admin2026*LT
- Estudiante: 1001234567 / Estud2026*SM

**Documentación clave**:
- Diagnóstico: INICIO_RAPIDO_MONGO.md
- Qué ver: QUE_VER_EN_MONGO.md
- Setup: RENDER_MONGODB_SETUP.md
- Credenciales: USUARIOS_Y_CONTRASEÑAS.txt

---

*Esta solución responde directamente a: "POR FAVOR YA NO SÉ QUÉ HACER, LAS CREDENCIALES NO SIRVEN. DENTRO DE MONGO QUE DEBO PODER VER"*

*Última actualización: 2026-02-18*
