# 🔍 QUÉ DEBES VER DENTRO DE MONGODB - Guía Visual Completa

## 📌 RESPUESTA DIRECTA A TU PREGUNTA

**"¿Qué debo poder ver dentro de MongoDB?"**

Debes ver **EXACTAMENTE** esto:

```
Base de datos: educando_db
│
├── Colección: users (7 documentos)
│   ├── 1 Editor
│   ├── 2 Administradores
│   ├── 2 Profesores
│   └── 2 Estudiantes
│
├── Colección: programs (1 documento)
│   └── Administración de Empresas
│
├── Colección: subjects (6 documentos)
│   ├── Introducción a la Administración
│   ├── Contabilidad Básica
│   ├── Matemáticas Financieras
│   ├── Principios de Marketing
│   ├── Gestión de Recursos Humanos
│   └── Economía Empresarial
│
└── Colección: courses (4 documentos)
    ├── Introducción a la Administración - Febrero 2026 - Grupo A
    ├── Contabilidad Básica - Febrero 2026 - Grupo A
    ├── Matemáticas Financieras - Febrero 2026 - Grupo B
    └── Principios de Marketing - Febrero 2026 - Grupo B
```

---

## 🚀 CÓMO VER TUS DATOS EN MONGODB

### Método 1: MongoDB Compass (RECOMENDADO - Interfaz Gráfica)

#### Paso 1: Descargar e Instalar MongoDB Compass

1. Ve a: https://www.mongodb.com/try/download/compass
2. Descarga la versión para tu sistema operativo:
   - **Windows:** `.msi` o `.exe`
   - **macOS:** `.dmg`
   - **Linux:** `.deb` o `.rpm`
3. Instala siguiendo el asistente (siguiente, siguiente, instalar)

#### Paso 2: Conectar a tu Base de Datos

1. Abre MongoDB Compass
2. En la ventana principal verás: **"New Connection"**
3. Pega tu **connection string** de MongoDB Atlas:
   ```
   mongodb+srv://educando_user:TuPassword123@cluster.mongodb.net/educando_db?retryWrites=true&w=majority
   ```
4. Haz clic en **"Connect"**

#### Paso 3: Navegar a tus Datos

1. **Panel Izquierdo:** Verás una lista de bases de datos
2. Busca y haz clic en **`educando_db`**
3. Verás las colecciones:
   ```
   ├── users
   ├── programs
   ├── subjects
   └── courses
   ```

#### Paso 4: Ver los Usuarios (Colección `users`)

1. Haz clic en la colección **`users`**
2. Verás **7 documentos** en la lista
3. Cada usuario se ve así:

**Ejemplo - Administrador:**
```json
{
  "_id": "675b1c2d8e9a1b3c4d5e6f7a",
  "id": "user-admin-1",
  "name": "Laura Torres",
  "email": "laura.torres@educando.com",
  "cedula": null,
  "password_hash": "$2b$12$abcdefghijklmnopqrstuvwxyz1234567890...",
  "role": "admin",
  "active": true,
  "phone": "3002223344",
  "program_id": null,
  "program_ids": [],
  "subject_ids": [],
  "module": null,
  "grupo": null
}
```

**Ejemplo - Estudiante:**
```json
{
  "_id": "675b1c2d8e9a1b3c4d5e6f7b",
  "id": "user-student-1",
  "name": "Sofía Morales",
  "email": "sofia.morales@educando.com",
  "cedula": "1001234567",
  "password_hash": "$2b$12$abcdefghijklmnopqrstuvwxyz1234567890...",
  "role": "estudiante",
  "active": true,
  "phone": "3006667788",
  "program_id": "prog-admon-empresas",
  "program_ids": ["prog-admon-empresas"],
  "subject_ids": [],
  "module": 1,
  "grupo": "Febrero 2026"
}
```

#### Paso 5: Verificar Otros Datos

**Colección `programs` (1 documento):**
```json
{
  "_id": "675b1c2d8e9a1b3c4d5e6f7c",
  "id": "prog-admon-empresas",
  "name": "Administración de Empresas",
  "description": "Programa de formación en administración de empresas",
  "duration_modules": 6,
  "active": true
}
```

**Colección `subjects` (6 documentos):**
```json
{
  "_id": "675b1c2d8e9a1b3c4d5e6f7d",
  "id": "subj-intro-admin",
  "name": "Introducción a la Administración",
  "code": "ADMIN101",
  "credits": 3,
  "module": 1,
  "program_id": "prog-admon-empresas",
  "description": "Fundamentos de la administración empresarial",
  "active": true
}
```

**Colección `courses` (4 documentos):**
```json
{
  "_id": "675b1c2d8e9a1b3c4d5e6f7e",
  "id": "course-1",
  "name": "Introducción a la Administración - Febrero 2026 - Grupo A",
  "subject_id": "subj-intro-admin",
  "program_id": "prog-admon-empresas",
  "teacher_id": "user-teacher-1",
  "grupo": "Febrero 2026",
  "module": 1,
  "schedule": "Lunes y Miércoles 8:00-10:00",
  "classroom": "Aula 101",
  "max_students": 30,
  "enrolled_students": 2,
  "student_ids": ["user-student-1", "user-student-2"],
  "start_date": "2026-02-01T00:00:00Z",
  "end_date": "2026-06-30T00:00:00Z",
  "active": true
}
```

---

### Método 2: MongoDB Atlas Web Interface (Sin Instalar Nada)

#### Paso 1: Iniciar Sesión en MongoDB Atlas

1. Ve a: https://cloud.mongodb.com
2. Inicia sesión con tu cuenta de MongoDB Atlas

#### Paso 2: Navegar a tu Cluster

1. En el dashboard principal, verás tu cluster (ej: `educando-cluster`)
2. Haz clic en **"Browse Collections"**

#### Paso 3: Ver las Colecciones

1. En el panel izquierdo, selecciona **`educando_db`**
2. Verás las 4 colecciones:
   - `users`
   - `programs`
   - `subjects`
   - `courses`

#### Paso 4: Inspeccionar Documentos

1. Haz clic en cualquier colección (ej: `users`)
2. Verás todos los documentos en formato JSON
3. Puedes navegar entre páginas si hay muchos documentos
4. Puedes buscar documentos específicos usando el filtro:
   ```json
   {"email": "laura.torres@educando.com"}
   ```

---

### Método 3: Usando mongosh (Línea de Comandos)

Si prefieres la línea de comandos:

#### Instalar mongosh

**Ubuntu/Debian:**
```bash
wget -qO- https://www.mongodb.org/static/pgp/server-7.0.asc | sudo tee /etc/apt/trusted.gpg.d/server-7.0.asc
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-mongosh
```

**macOS:**
```bash
brew install mongosh
```

**Windows:**
Descargar desde: https://www.mongodb.com/try/download/shell

#### Conectar y Ver Datos

```bash
# Conectar (reemplaza con tu connection string)
mongosh "mongodb+srv://educando_user:TuPassword@cluster.mongodb.net/educando_db"

# Una vez conectado, ejecuta estos comandos:

# Ver todas las colecciones
show collections

# Contar usuarios (debe ser 7)
db.users.countDocuments()

# Ver todos los usuarios (sin contraseñas)
db.users.find({}, {password_hash: 0}).pretty()

# Ver un usuario específico por email
db.users.findOne({email: "laura.torres@educando.com"}, {password_hash: 0})

# Ver un estudiante por cédula
db.users.findOne({cedula: "1001234567"}, {password_hash: 0})

# Ver todos los programas
db.programs.find().pretty()

# Ver todas las materias
db.subjects.find().pretty()

# Ver todos los cursos
db.courses.find().pretty()

# Estadísticas generales
db.users.countDocuments()      // Debe ser: 7
db.programs.countDocuments()   // Debe ser: 1
db.subjects.countDocuments()   // Debe ser: 6
db.courses.countDocuments()    // Debe ser: 4

# Salir
exit
```

---

### Método 4: Script de Verificación Automático

Usa el script incluido en el repositorio:

```bash
# Desde el directorio del proyecto
cd backend

# Instalar dependencias
pip install motor python-dotenv

# Ejecutar verificación
python verify_mongodb.py "mongodb+srv://usuario:password@cluster.mongodb.net/educando_db"
```

El script te mostrará:
```
================================================================================
VERIFICACIÓN DE CONEXIÓN A MONGODB
================================================================================

📡 Intentando conectar a: mongodb+srv://educando_user:***@cluster.mongodb.net

⏳ Probando conexión...
✅ ¡Conexión exitosa a MongoDB!

📊 Información del servidor:
   - Versión MongoDB: 7.0.5
   - Host: cluster.mongodb.net

📁 Bases de datos disponibles:
   - educando_db

📚 Colecciones en 'educando_db':
   - users: 7 documentos
   - programs: 1 documentos
   - subjects: 6 documentos
   - courses: 4 documentos

👥 Usuarios en la colección 'users': 7

✅ ¡Perfecto! Los 7 usuarios iniciales están presentes.

📋 Lista de usuarios:
   [✓] Laura Torres             | admin        | laura.torres@educando.com
   [✓] Roberto Ramirez          | admin        | roberto.ramirez@educando.com
   [✓] Carlos Mendez            | editor       | carlos.mendez@educando.com
   [✓] Diana Silva              | profesor     | diana.silva@educando.com
   [✓] Miguel Castro            | profesor     | miguel.castro@educando.com
   [✓] Sofía Morales            | estudiante   | 1001234567
   [✓] Andrés Lopez             | estudiante   | 1002345678

================================================================================
RESUMEN
================================================================================
✅ La conexión a MongoDB funciona correctamente
✅ Puedes usar esta connection string en Render
```

---

## 📊 LISTA COMPLETA DE LOS 7 USUARIOS

Aquí está la lista EXACTA de usuarios que debes ver en MongoDB:

### 1. Editor (1 usuario)

| Campo | Valor |
|-------|-------|
| id | `user-editor-1` |
| name | Carlos Mendez |
| email | carlos.mendez@educando.com |
| cedula | `null` |
| role | editor |
| active | `true` |
| phone | 3001112233 |
| **Contraseña** | Ver USUARIOS_Y_CONTRASEÑAS.txt |

### 2. Administradores (2 usuarios)

**Admin 1:**
| Campo | Valor |
|-------|-------|
| id | `user-admin-1` |
| name | Laura Torres |
| email | laura.torres@educando.com |
| cedula | `null` |
| role | admin |
| active | `true` |
| phone | 3002223344 |
| **Contraseña** | Ver USUARIOS_Y_CONTRASEÑAS.txt |

**Admin 2:**
| Campo | Valor |
|-------|-------|
| id | `user-admin-2` |
| name | Roberto Ramirez |
| email | roberto.ramirez@educando.com |
| cedula | `null` |
| role | admin |
| active | `true` |
| phone | 3003334455 |
| **Contraseña** | Ver USUARIOS_Y_CONTRASEÑAS.txt |

### 3. Profesores (2 usuarios)

**Profesor 1:**
| Campo | Valor |
|-------|-------|
| id | `user-teacher-1` |
| name | Diana Silva |
| email | diana.silva@educando.com |
| cedula | `null` |
| role | profesor |
| active | `true` |
| phone | 3004445566 |
| subject_ids | `["subj-intro-admin", "subj-marketing"]` |
| **Contraseña** | Ver USUARIOS_Y_CONTRASEÑAS.txt |

**Profesor 2:**
| Campo | Valor |
|-------|-------|
| id | `user-teacher-2` |
| name | Miguel Castro |
| email | miguel.castro@educando.com |
| cedula | `null` |
| role | profesor |
| active | `true` |
| phone | 3005556677 |
| subject_ids | `["subj-contabilidad", "subj-matematicas"]` |
| **Contraseña** | Ver USUARIOS_Y_CONTRASEÑAS.txt |

### 4. Estudiantes (2 usuarios)

**Estudiante 1:**
| Campo | Valor |
|-------|-------|
| id | `user-student-1` |
| name | Sofía Morales |
| email | sofia.morales@educando.com |
| **cedula** | **1001234567** ⬅️ Usar para login |
| role | estudiante |
| active | `true` |
| phone | 3006667788 |
| program_id | prog-admon-empresas |
| module | 1 |
| grupo | Febrero 2026 |
| **Contraseña** | Ver USUARIOS_Y_CONTRASEÑAS.txt |

**Estudiante 2:**
| Campo | Valor |
|-------|-------|
| id | `user-student-2` |
| name | Andrés Lopez |
| email | andres.lopez@educando.com |
| **cedula** | **1002345678** ⬅️ Usar para login |
| role | estudiante |
| active | `true` |
| phone | 3007778899 |
| program_id | prog-admon-empresas |
| module | 1 |
| grupo | Febrero 2026 |
| **Contraseña** | Ver USUARIOS_Y_CONTRASEÑAS.txt |

---

## 🔍 CAMPOS IMPORTANTES A VERIFICAR

### Campo `password_hash`

Este campo contiene la contraseña encriptada. Se ve así:

```
$2b$12$K8YfJ3ZxLm9QpR5vWnE2K.X7UvY4jH6gT3mP9sA1bN5cD2eF8iG4h
```

**¿Qué significa?**
- `$2b$` → Algoritmo bcrypt
- `12` → Costo computacional (rounds)
- El resto → Hash de la contraseña

⚠️ **IMPORTANTE:** NO puedes "descifrar" este hash para ver la contraseña original. Las contraseñas originales están en `USUARIOS_Y_CONTRASEÑAS.txt`.

### Campo `active`

```json
"active": true
```

- `true` → Usuario puede iniciar sesión
- `false` → Usuario bloqueado/inactivo

### Campo `role`

```json
"role": "admin"  // o "profesor", "editor", "estudiante"
```

Define los permisos del usuario.

### Campos específicos de estudiantes

```json
"cedula": "1001234567",    // Número de identificación (para login)
"program_id": "prog-admon-empresas",
"module": 1,
"grupo": "Febrero 2026"
```

### Campos específicos de profesores

```json
"subject_ids": ["subj-intro-admin", "subj-marketing"]
```

Lista de materias que el profesor puede enseñar.

---

## 🚨 ¿QUÉ HACER SI NO VES LOS DATOS?

### Caso 1: La base de datos `educando_db` no existe

**Causa:** El backend nunca se conectó exitosamente a MongoDB.

**Solución:**
1. Verifica que configuraste `MONGO_URL` en Render
2. Re-despliega el backend
3. Espera 2-3 minutos
4. Verifica los logs del backend

### Caso 2: La base de datos existe pero está vacía

**Causa:** El backend se conectó pero no creó los datos iniciales.

**Solución:**
1. Verifica los logs del backend en Render
2. Busca el mensaje: `"Datos iniciales creados exitosamente"`
3. Si no aparece, revisa errores en los logs
4. Re-despliega el backend si es necesario

### Caso 3: Hay menos de 7 usuarios

**Causa:** Los datos se crearon parcialmente.

**Solución:**
1. Elimina todos los documentos de la colección `users`
2. Re-despliega el backend
3. El backend detectará que no hay usuarios y los creará automáticamente

**Eliminar usuarios en MongoDB Compass:**
```
1. Abre la colección `users`
2. Selecciona todos los documentos (Ctrl+A o Cmd+A)
3. Haz clic en "Delete Selected Documents"
4. Confirma
```

**Eliminar usuarios en mongosh:**
```javascript
db.users.deleteMany({})
```

### Caso 4: Los usuarios existen pero las contraseñas no funcionan

**Causa:** Posible problema con el hash de contraseñas.

**Solución:**
1. Verifica que estás usando la contraseña correcta de `USUARIOS_Y_CONTRASEÑAS.txt`
2. Verifica que estás usando el rol correcto:
   - Estudiantes: Pestaña "ESTUDIANTE" + cédula
   - Otros: Pestaña "PROFESOR" + email
3. Las contraseñas distinguen mayúsculas y minúsculas
4. No debe haber espacios antes o después

### Caso 5: No puedo conectarme a MongoDB desde Compass

**Causa:** Problemas de red o configuración.

**Solución:**
1. Verifica tu connection string (sin espacios, contraseña correcta)
2. En MongoDB Atlas → Network Access:
   - Asegúrate de que 0.0.0.0/0 está permitido
3. Verifica que el cluster no esté en pausa
4. Intenta desde MongoDB Atlas web interface como alternativa

---

## 📸 GUÍA VISUAL: CAPTURAS DE PANTALLA ESPERADAS

### En MongoDB Compass:

**1. Vista de Colecciones:**
```
Debes ver esto en el panel izquierdo:

📦 educando_db
  ├── 📄 users (7)
  ├── 📄 programs (1)
  ├── 📄 subjects (6)
  └── 📄 courses (4)
```

**2. Vista de Documentos (users):**
```
Lista con 7 filas, cada una mostrando:
- _id (ObjectId)
- id (string)
- name (string)
- email o cedula (string)
- role (string)
- ...otros campos
```

**3. Vista de un Documento Individual:**
```json
{
  "_id": ObjectId("..."),
  "id": "user-admin-1",
  "name": "Laura Torres",
  "email": "laura.torres@educando.com",
  "cedula": null,
  "password_hash": "$2b$12$...",
  "role": "admin",
  "active": true,
  "phone": "3002223344",
  "program_id": null,
  "program_ids": [],
  "subject_ids": [],
  "module": null,
  "grupo": null
}
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

Marca cada item cuando lo verifiques:

### Conexión
- [ ] Me conecté exitosamente a MongoDB (Compass, Atlas o mongosh)
- [ ] Veo la base de datos `educando_db`

### Colecciones
- [ ] Veo la colección `users` con 7 documentos
- [ ] Veo la colección `programs` con 1 documento
- [ ] Veo la colección `subjects` con 6 documentos
- [ ] Veo la colección `courses` con 4 documentos

### Usuarios
- [ ] Veo 1 usuario con role "editor"
- [ ] Veo 2 usuarios con role "admin"
- [ ] Veo 2 usuarios con role "profesor"
- [ ] Veo 2 usuarios con role "estudiante"

### Campos de Usuarios
- [ ] Todos los usuarios tienen `password_hash` (no `null`)
- [ ] Todos los usuarios tienen `active: true`
- [ ] Los profesores/admins/editores tienen `email`
- [ ] Los estudiantes tienen `cedula` (ej: "1001234567")

### Prueba de Login
- [ ] Probé login con admin: laura.torres@educando.com
- [ ] Probé login con estudiante: cédula 1001234567
- [ ] El login funcionó correctamente
- [ ] Veo el dashboard correspondiente al rol

---

## 🎯 RESUMEN EJECUTIVO

**¿Qué debes ver en MongoDB?**
- ✅ Base de datos: `educando_db`
- ✅ Colección `users`: **7 usuarios**
  - 1 Editor
  - 2 Admins
  - 2 Profesores
  - 2 Estudiantes
- ✅ Colección `programs`: 1 programa
- ✅ Colección `subjects`: 6 materias
- ✅ Colección `courses`: 4 cursos

**¿Cómo verificar?**
1. **Método más fácil:** MongoDB Compass (interfaz gráfica)
2. **Método online:** MongoDB Atlas web interface
3. **Método automatizado:** Script `verify_mongodb.py`
4. **Método avanzado:** mongosh (línea de comandos)

**¿Qué hacer si no veo los datos?**
1. Verificar que MongoDB esté conectado en Render
2. Verificar logs del backend: "Datos iniciales creados exitosamente"
3. Si es necesario, eliminar datos y re-desplegar

**Contraseñas:**
Ver archivo `USUARIOS_Y_CONTRASEÑAS.txt` para las contraseñas de prueba.

---

## 📚 ARCHIVOS RELACIONADOS

- **`USUARIOS_Y_CONTRASEÑAS.txt`** → Credenciales completas
- **`RENDER_MONGODB_SETUP.md`** → Cómo configurar MongoDB en Render
- **`RESUMEN_USUARIOS_Y_MONGODB.md`** → Resumen ejecutivo
- **`TARJETA_REFERENCIA_MONGODB.md`** → Referencia rápida
- **`backend/verify_mongodb.py`** → Script de verificación automática
- **`backend/server.py`** (líneas 124-327) → Código que crea los datos

---

## 🆘 NECESITAS MÁS AYUDA?

Si después de seguir esta guía todavía no ves los datos:

1. **Comparte los logs del backend en Render**
   - Render → educando-backend → Logs
   - Copia las últimas 50 líneas

2. **Comparte lo que ves en MongoDB Compass**
   - ¿Ves la base de datos educando_db?
   - ¿Cuántos documentos hay en cada colección?

3. **Ejecuta el script de verificación**
   ```bash
   python backend/verify_mongodb.py "tu_connection_string"
   ```
   - Comparte la salida completa

Con esta información podremos diagnosticar exactamente qué está pasando.

---

*Última actualización: 2026-02-18*
*Guía creada para responder: "POR FAVOR YA NO SÉ QUÉ HACER, LAS CREDENCIALES NO SIRVEN. DENTRO DE MONGO QUE DEBO PODER VER"*
