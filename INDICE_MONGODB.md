# 📚 ÍNDICE: Documentación de MongoDB y Credenciales

## 🆘 ¿Estás frustrado porque las credenciales no funcionan?

### 🚀 EMPIEZA AQUÍ (Si estás desesperado):

**[INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md)** ⭐
- ⏱️ Tiempo: 30 segundos para diagnóstico
- 🎯 Identifica rápidamente si MongoDB está conectado
- ✅ Solución paso a paso dependiendo del problema
- 📋 Checklist simple para verificar configuración

---

## 📖 GUÍAS PRINCIPALES

### Para Resolver Problemas con Credenciales

| Guía | Cuándo Usarla | Tiempo |
|------|---------------|--------|
| **[INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md)** ⭐ | Cuando las credenciales no funcionan y no sabes por qué | 30 seg diagnóstico + 15 min solución |
| **[QUE_VER_EN_MONGO.md](QUE_VER_EN_MONGO.md)** | Cuando quieres ver qué DEBE haber en tu base de datos | 5-10 min lectura |
| **[RENDER_MONGODB_SETUP.md](RENDER_MONGODB_SETUP.md)** | Cuando necesitas configurar MongoDB desde cero | 15-20 min |
| **[RESUMEN_USUARIOS_Y_MONGODB.md](RESUMEN_USUARIOS_Y_MONGODB.md)** | Para entender el sistema completo | 10 min lectura |

### Referencias Rápidas

| Documento | Contenido | Formato |
|-----------|-----------|---------|
| **[TARJETA_REFERENCIA_MONGODB.md](TARJETA_REFERENCIA_MONGODB.md)** | Comandos y pasos resumidos | Referencia de 1 página |
| **[USUARIOS_Y_CONTRASEÑAS.txt](USUARIOS_Y_CONTRASEÑAS.txt)** | Lista completa de credenciales | Lista con tabla |
| **[SOLUCION_COMPLETA.md](SOLUCION_COMPLETA.md)** | Solución detallada y completa | Guía extensa |

---

## 🎯 ELIGE TU CAMINO

### Camino 1: "¡Solo quiero que funcione!" (Frustración Alta 😤)

```
1. Lee: INICIO_RAPIDO_MONGO.md (30 segundos)
   └─ Te dice exactamente qué hacer

2. Si MongoDB NO está conectado:
   └─ Sigue: Sección A del INICIO_RAPIDO_MONGO.md
      └─ Configura MongoDB Atlas (15 minutos)
      
3. Si MongoDB SÍ está conectado:
   └─ Sigue: Sección B del INICIO_RAPIDO_MONGO.md
      └─ Verifica credenciales y rol (2 minutos)

4. Prueba login con:
   └─ USUARIOS_Y_CONTRASEÑAS.txt
```

### Camino 2: "Quiero entender qué hay en MongoDB" (Curiosidad 🔍)

```
1. Lee: QUE_VER_EN_MONGO.md
   └─ Guía visual completa con ejemplos
   
2. Descarga: MongoDB Compass
   └─ https://www.mongodb.com/try/download/compass
   
3. Conecta y explora:
   └─ Verás las 4 colecciones
   └─ 7 usuarios con todos sus campos
   └─ Estructura completa de datos
```

### Camino 3: "Necesito configurar todo desde cero" (Setup Completo 🛠️)

```
1. Lee: RENDER_MONGODB_SETUP.md
   └─ Guía paso a paso de 400+ líneas
   
2. Sigue todos los pasos:
   ├─ Crear cuenta en MongoDB Atlas
   ├─ Crear cluster gratuito
   ├─ Configurar usuario y red
   ├─ Obtener connection string
   └─ Configurar en Render
   
3. Verifica con: verify_mongodb.py
   └─ Script automático de verificación
```

### Camino 4: "Solo necesito las credenciales" (Rápido ⚡)

```
1. Abre: USUARIOS_Y_CONTRASEÑAS.txt
   └─ Lista completa de 7 usuarios
   
2. Usa estas credenciales de prueba:
   ├─ Admin: laura.torres@educando.com / Admin2026*LT
   ├─ Profesor: diana.silva@educando.com / Profe2026*DS
   └─ Estudiante: 1001234567 / Estud2026*SM
   
3. RECUERDA:
   ├─ Estudiantes → Pestaña ESTUDIANTE + cédula
   └─ Otros roles → Pestaña PROFESOR + email
```

---

## 🔧 HERRAMIENTAS Y SCRIPTS

### Script de Verificación Automática

**Archivo**: `backend/verify_mongodb.py`

**Uso**:
```bash
pip install motor python-dotenv
python backend/verify_mongodb.py "mongodb+srv://user:pass@cluster.net/educando_db"
```

**Qué hace**:
- ✅ Verifica conexión a MongoDB
- ✅ Lista todas las colecciones
- ✅ Cuenta documentos en cada colección
- ✅ Muestra los 7 usuarios (sin contraseñas)
- ✅ Da diagnóstico de problemas comunes

### MongoDB Compass (GUI)

**Descarga**: https://www.mongodb.com/try/download/compass

**Ventajas**:
- 🖼️ Interfaz gráfica fácil de usar
- 📊 Visualiza datos en formato JSON
- 🔍 Busca y filtra documentos
- ✏️ Edita documentos directamente
- 🌐 Conecta a MongoDB Atlas o local

### MongoDB Atlas Web Interface

**URL**: https://cloud.mongodb.com

**Ventajas**:
- 🌐 No necesitas instalar nada
- ☁️ Acceso desde cualquier navegador
- 📊 Browse Collections directamente
- 🔒 Gestión de usuarios y red

---

## 📊 ESTRUCTURA DE DATOS ESPERADA

### En MongoDB debes ver:

```
Base de datos: educando_db
├── users (7 documentos)
│   ├── 1 Editor
│   ├── 2 Administradores
│   ├── 2 Profesores
│   └── 2 Estudiantes
│
├── programs (1 documento)
│   └── Administración de Empresas
│
├── subjects (6 documentos)
│   ├── Introducción a la Administración
│   ├── Contabilidad Básica
│   ├── Matemáticas Financieras
│   ├── Principios de Marketing
│   ├── Gestión de Recursos Humanos
│   └── Economía Empresarial
│
└── courses (4 documentos)
    └── (Cursos asignados a profesores y estudiantes)
```

**Detalles completos**: Ver [QUE_VER_EN_MONGO.md](QUE_VER_EN_MONGO.md)

---

## ⚡ SOLUCIÓN DE PROBLEMAS COMUNES

| Problema | Documento a Leer | Solución Rápida |
|----------|------------------|-----------------|
| "Credenciales incorrectas" | INICIO_RAPIDO_MONGO.md | Verifica que MongoDB esté conectado en logs |
| "No veo usuarios en MongoDB" | QUE_VER_EN_MONGO.md → Caso 2 | Re-despliega el backend |
| "ServerSelectionTimeoutError" | RENDER_MONGODB_SETUP.md | Permite 0.0.0.0/0 en Network Access |
| "Authentication failed" | TARJETA_REFERENCIA_MONGODB.md | Verifica contraseña en connection string |
| "No sé qué pestaña usar" | USUARIOS_Y_CONTRASEÑAS.txt | Estudiantes: ESTUDIANTE, Otros: PROFESOR |

---

## 🎓 CREDENCIALES DE PRUEBA

### Administrador

```
Pestaña: PROFESOR
Email: laura.torres@educando.com
Contraseña: Admin2026*LT
```

### Profesor

```
Pestaña: PROFESOR
Email: diana.silva@educando.com
Contraseña: Profe2026*DS
```

### Estudiante

```
Pestaña: ESTUDIANTE
Cédula: 1001234567
Contraseña: Estud2026*SM
```

⚠️ **Lista completa**: [USUARIOS_Y_CONTRASEÑAS.txt](USUARIOS_Y_CONTRASEÑAS.txt)

---

## 🔍 GUÍA DE VERIFICACIÓN PASO A PASO

### 1. Verificar MongoDB en Render (30 segundos)

```
1. Ve a: https://dashboard.render.com
2. Servicio: educando-backend
3. Pestaña: Logs
4. Buscar: "MongoDB connection successful"
```

**✅ Lo viste**: MongoDB conectado → Continúa a paso 2

**❌ No lo viste**: MongoDB NO conectado → Lee [INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md)

### 2. Verificar Usuarios Creados (30 segundos)

```
En los mismos logs, buscar:
"Credenciales creadas para 7 usuarios"
```

**✅ Lo viste**: Usuarios creados → Continúa a paso 3

**❌ No lo viste**: Re-despliega el backend

### 3. Verificar Connection String (1 minuto)

```
Render → educando-backend → Environment
Buscar: MONGO_URL
Formato correcto:
mongodb+srv://user:password@cluster.net/educando_db?retryWrites=true
                                        ^^^^^^^^^^^ Este debe estar
```

### 4. Probar Login (1 minuto)

```
Aplicación → Pestaña PROFESOR
Email: laura.torres@educando.com
Contraseña: Admin2026*LT (copia y pega)
```

**✅ Funciona**: ¡Todo está bien!

**❌ No funciona**: Lee [INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md) Sección B

---

## 📞 CONTACTO Y AYUDA

### Si sigues teniendo problemas después de leer las guías:

**Comparte esta información**:

1. **Logs del backend** (últimas 50 líneas):
   ```
   Render → educando-backend → Logs → Copiar
   ```

2. **Variables de entorno**:
   ```
   ¿Existe MONGO_URL? (SÍ/NO)
   ¿Qué formato tiene? (Censura la contraseña)
   ```

3. **Qué ves en MongoDB**:
   ```
   Usa MongoDB Compass o Atlas
   ¿Cuántas colecciones ves?
   ¿Cuántos usuarios hay?
   ```

4. **Qué probaste**:
   ```
   ¿Qué guías leíste?
   ¿Qué pasos seguiste?
   ¿En qué paso te atascaste?
   ```

---

## 📝 RESUMEN EJECUTIVO

### El Problema (El usuario reporta):
```
"POR FAVOR YA NO SÉ QUÉ HACER, LAS CREDENCIALES NO SIRVEN. 
DENTRO DE MONGO QUE DEBO PODER VER"
```

### La Respuesta:

**1. ¿Por qué no funcionan las credenciales?**
- Causa más probable: MongoDB NO está conectado en Render
- Solución: [INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md)

**2. ¿Qué debo ver en MongoDB?**
- 4 colecciones: users, programs, subjects, courses
- 7 usuarios: 1 editor, 2 admins, 2 profesores, 2 estudiantes
- Guía visual: [QUE_VER_EN_MONGO.md](QUE_VER_EN_MONGO.md)

**3. ¿Cómo lo arreglo?**
- Configura MongoDB Atlas (gratis)
- Conecta a Render con MONGO_URL
- Verifica logs y prueba login
- Guía completa: [RENDER_MONGODB_SETUP.md](RENDER_MONGODB_SETUP.md)

**4. ¿Cuáles son las credenciales?**
- Ver: [USUARIOS_Y_CONTRASEÑAS.txt](USUARIOS_Y_CONTRASEÑAS.txt)
- Ejemplo: laura.torres@educando.com / Admin2026*LT

---

## 🗂️ TODOS LOS ARCHIVOS DE DOCUMENTACIÓN

### Guías de MongoDB y Credenciales (NUEVO ⭐)

1. **INICIO_RAPIDO_MONGO.md** - Diagnóstico en 30 segundos (NUEVO ⭐)
2. **QUE_VER_EN_MONGO.md** - Guía visual de qué ver en MongoDB (NUEVO ⭐)
3. **INDICE_MONGODB.md** - Este índice (NUEVO ⭐)
4. **RENDER_MONGODB_SETUP.md** - Configuración completa paso a paso
5. **RESUMEN_USUARIOS_Y_MONGODB.md** - Resumen ejecutivo
6. **USUARIOS_Y_CONTRASEÑAS.txt** - Lista de credenciales
7. **TARJETA_REFERENCIA_MONGODB.md** - Referencia rápida
8. **SOLUCION_COMPLETA.md** - Solución detallada

### Guías de Despliegue

9. **INICIO_RAPIDO_RENDER.md** - Deploy en Render (20 min)
10. **GUIA_RENDER.md** - Guía completa de Render
11. **CHECKLIST_RENDER.md** - Lista verificable
12. **DESPLIEGUE.md** - Documentación técnica completa

### Scripts y Herramientas

13. **backend/verify_mongodb.py** - Script de verificación automática
14. **verificar_autenticacion.py** - Verificar autenticación

---

*Última actualización: 2026-02-18*
*Creado para responder: "POR FAVOR YA NO SÉ QUÉ HACER, LAS CREDENCIALES NO SIRVEN. DENTRO DE MONGO QUE DEBO PODER VER"*
