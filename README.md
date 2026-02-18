# Educando - Web App Técnico

Aplicación web full-stack para gestión educativa con React (frontend), FastAPI (backend) y MongoDB.

## 🎉 BASE DE DATOS CONFIGURADA

✅ **La aplicación ya está conectada a MongoDB Atlas (Cluster0 → Base de datos: webApp)**

📖 **Inicio Rápido:** [INICIO_RAPIDO_WEBAPP.md](INICIO_RAPIDO_WEBAPP.md) - ¡Empieza aquí en 5 minutos!  
📚 **Guía Completa:** [CONFIGURACION_MONGODB.md](CONFIGURACION_MONGODB.md) - Todos los detalles

**⚡ Acción requerida:** Configura Network Access en MongoDB Atlas para permitir conexiones ([ver guía](INICIO_RAPIDO_WEBAPP.md#1-configurar-acceso-en-mongodb-atlas-importante))

---

## 🆘 ¿LAS CREDENCIALES NO FUNCIONAN?

### 🚨 Si estás frustrado porque no puedes iniciar sesión:

**LEE PRIMERO:** [🚀 INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md) ⭐ **EMPIEZA AQUÍ** (Diagnóstico en 30 segundos)

**Causa más común:** MongoDB NO está conectado en Render.

### 📚 Guías Completas para Resolver el Problema:

1. **[🚀 INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md)** ⭐ **EMPIEZA AQUÍ** - Diagnóstico rápido en 30 segundos
2. **[🔍 QUE_VER_EN_MONGO.md](QUE_VER_EN_MONGO.md)** - Guía visual: Qué DEBE verse dentro de MongoDB
3. **[📖 RENDER_MONGODB_SETUP.md](RENDER_MONGODB_SETUP.md)** - Configurar MongoDB Atlas paso a paso
4. **[📋 USUARIOS_Y_CONTRASEÑAS.txt](USUARIOS_Y_CONTRASEÑAS.txt)** - Lista completa de credenciales
5. **[📝 TARJETA_REFERENCIA_MONGODB.md](TARJETA_REFERENCIA_MONGODB.md)** - Referencia rápida

### ✅ Credenciales de Prueba (para después de configurar MongoDB):

| Rol | Pestaña | Usuario | Contraseña |
|-----|---------|---------|------------|
| Admin | PROFESOR | laura.torres@educando.com | Admin2026*LT |
| Profesor | PROFESOR | diana.silva@educando.com | Profe2026*DS |
| Estudiante | ESTUDIANTE | 1001234567 | Estud2026*SM |

⚠️ **RECUERDA:** Admins y Editores usan la pestaña "PROFESOR", NO "ESTUDIANTE"

---

## 🌐 ¿Quieres Subir Esto a la Web?

### 🎯 Despliegue en Render.com (Recomendado) ⭐

**La forma más fácil de llevar tu aplicación a producción**

1. **📖 Lee:** [RENDER_MONGODB_SETUP.md](RENDER_MONGODB_SETUP.md) - Guía paso a paso
2. **🚀 Ve a:** https://render.com
3. **⏱️ Tiempo:** 15-30 minutos
4. **💰 Costo:** Desde $0 (gratuito para desarrollo)
5. **🎉 Resultado:** Tu app online con HTTPS automático

### 📚 Guías de Despliegue Disponibles:

- **[RENDER_MONGODB_SETUP.md](RENDER_MONGODB_SETUP.md)** - Configurar MongoDB Atlas y Render paso a paso
- **[DESPLIEGUE.md](DESPLIEGUE.md)** - Guía técnica completa de despliegue
- **[GUIA_PRODUCCION_3000_USUARIOS.md](GUIA_PRODUCCION_3000_USUARIOS.md)** - Escalamiento para producción (3000+ usuarios)

**¿Primera vez desplegando?** → Comienza con RENDER_MONGODB_SETUP.md  
**¿Necesitas soportar muchos usuarios?** → Lee GUIA_PRODUCCION_3000_USUARIOS.md  
**¿Quieres entender todo el proceso?** → Lee DESPLIEGUE.md

---

## 🏭 ¿Necesitas la Plataforma para 3000 Usuarios?

### 🚀 GUÍA DE PRODUCCIÓN COMPLETA

**¿La plataforma se va a caer con muchos usuarios? ¿Qué servidor necesito? ¿Cuánto cuesta?**

📖 **Lee la Guía Completa:** [GUIA_PRODUCCION_3000_USUARIOS.md](GUIA_PRODUCCION_3000_USUARIOS.md)

Esta guía incluye:
- ✅ Todo lo que necesitas para soportar 3000 usuarios simultáneos
- ✅ Configuración paso a paso del servidor y base de datos
- ✅ Costos estimados ($30-310/mes según escala)
- ✅ Arquitectura recomendada con escalamiento horizontal
- ✅ Monitoreo y troubleshooting
- ✅ Checklist completo de implementación

**Resumen Rápido:**
- **MongoDB:** Upgrade a M10 ($57/mes) - 3000+ conexiones
- **Backend:** 4-8 instancias con múltiples workers ($28/mes)
- **Redis:** Para sesiones distribuidas ($15/mes)
- **CDN:** Cloudflare (gratis) para archivos estáticos
- **Monitoreo:** New Relic o DataDog (opcional, $15/mes)

**Configuración Actual:** Soporta ~200-500 usuarios simultáneos (gratis)  
**Configuración 3000 usuarios:** ~$107/mes (M10 + 4 backends + Redis)

---

## 🚀 Stack Tecnológico

### Frontend
- **React 19** con TypeScript
- **React Router v7** para navegación
- **TailwindCSS** para estilos
- **Radix UI** para componentes
- **React Hook Form + Zod** para formularios y validación
- **Axios** para peticiones HTTP

### Backend
- **FastAPI** (Python 3.11)
- **MongoDB** con Motor (async)
- **JWT** para autenticación
- **Uvicorn** como servidor ASGI

### Base de Datos
- **MongoDB 7**

## 📋 Requisitos Previos

- Docker Desktop instalado y corriendo
- Git

## 🛠️ Configuración de Desarrollo (Hot-Reload)

Para desarrollar con recarga automática cuando edites el código:

### 1. Clonar el repositorio
```bash
git clone https://github.com/EdinsonPedroza/web-App-Tecnico.git
cd web-App-Tecnico
```

### 2. Iniciar el entorno de desarrollo
```bash
docker compose -f docker-compose.dev.yml up --build
```

> **Nota**: Si tienes Docker Compose v1, usa `docker-compose` (con guión) en lugar de `docker compose` (con espacio).

Esto iniciará:
- **Frontend** en http://localhost:3000 (con hot-reload)
- **Backend** en http://localhost:8001 (con hot-reload)
- **MongoDB** en puerto 27017 (interno)

### 3. Verificar que funciona

Abre tu navegador en http://localhost:3000 y deberías ver la aplicación.

Para probar el hot-reload:
1. Edita cualquier archivo en `frontend/src` (por ejemplo, un componente)
2. Guarda el archivo
3. El navegador se recargará automáticamente con los cambios

Para el backend:
1. Edita cualquier archivo en `backend` (por ejemplo, `server.py`)
2. Guarda el archivo
3. Uvicorn detectará el cambio y reiniciará el servidor automáticamente

### 4. Detener el entorno
```bash
# Presiona Ctrl+C en la terminal donde corre docker compose
# O en otra terminal:
docker compose -f docker-compose.dev.yml down
```

> **Nota**: Si tienes Docker Compose v1, usa `docker-compose` (con guión) en lugar de `docker compose` (con espacio).

## 🚢 Despliegue en Producción

Para compilar y ejecutar la versión optimizada de producción:

```bash
docker compose up --build
```

Esto iniciará:
- **Frontend** en http://localhost:80 (build estático servido por nginx)
- **Backend** en puerto interno
- **MongoDB** en puerto 27017 (interno)

Para detener:
```bash
docker compose down
```

## 📁 Estructura del Proyecto

```
web-App-Tecnico/
├── frontend/                 # Aplicación React
│   ├── src/                 # Código fuente
│   ├── public/              # Archivos públicos
│   ├── Dockerfile           # Dockerfile de producción (build + nginx)
│   ├── Dockerfile.dev       # Dockerfile de desarrollo (yarn start)
│   └── package.json
├── backend/                  # API FastAPI
│   ├── server.py            # Aplicación principal
│   ├── Dockerfile           # Dockerfile de producción
│   ├── Dockerfile.dev       # Dockerfile de desarrollo (uvicorn --reload)
│   └── requirements.txt
├── docker-compose.yml        # Configuración de producción
└── docker-compose.dev.yml    # Configuración de desarrollo (hot-reload)
```

## 🔧 Comandos Útiles

### Ver logs de un servicio específico
```bash
docker compose -f docker-compose.dev.yml logs -f frontend
docker compose -f docker-compose.dev.yml logs -f backend
```

### Reconstruir un servicio específico
```bash
docker compose -f docker-compose.dev.yml up --build frontend
docker compose -f docker-compose.dev.yml up --build backend
```

### Ejecutar comandos dentro de un contenedor
```bash
# Frontend
docker exec -it educando_frontend sh
docker exec -it educando_frontend yarn add nueva-dependencia

# Backend
docker exec -it educando_backend bash
docker exec -it educando_backend pip install nueva-dependencia
```

### Limpiar volúmenes y contenedores
```bash
docker compose -f docker-compose.dev.yml down -v
```

## 🐛 Solución de Problemas

### El frontend no se actualiza al hacer cambios

**Problema**: Los cambios en el código no se reflejan en el navegador.

**Solución**: 
1. Verifica que estés usando `docker-compose.dev.yml` y no `docker-compose.yml`
2. Asegúrate de que los volúmenes estén montados correctamente:
   ```bash
   docker compose -f docker-compose.dev.yml down
   docker compose -f docker-compose.dev.yml up --build
   ```

### El backend no se actualiza al hacer cambios

**Problema**: Los cambios en el código Python no se reflejan.

**Solución**: 
1. Verifica que el backend esté usando `Dockerfile.dev` con el flag `--reload`
2. Revisa los logs: `docker compose -f docker-compose.dev.yml logs -f backend`
3. Si hay errores de sintaxis, corrígelos y uvicorn se reiniciará automáticamente

### Error: "Cannot connect to the Docker daemon"

**Solución**: Asegúrate de que Docker Desktop esté ejecutándose.

### Error: "Port already in use"

**Problema**: Los puertos 3000, 8001 u 80 ya están siendo usados.

**Solución**: 
1. Detén los contenedores: `docker compose -f docker-compose.dev.yml down`
2. O cambia los puertos en `docker-compose.dev.yml`:
   ```yaml
   ports:
     - "3001:3000"  # Usa 3001 en lugar de 3000
   ```

### Los cambios no se guardan después de reiniciar

**Problema**: Los datos de MongoDB se pierden al detener los contenedores.

**Solución**: Los datos persisten en el volumen `mongodb_data`. Para limpiar:
```bash
docker compose -f docker-compose.dev.yml down -v  # ⚠️ Esto borrará los datos
```

### Problemas con autenticación o credenciales

**❌ Problema**: Las credenciales no funcionan, no puedo iniciar sesión.

**🎯 Solución Rápida**: Lee [INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md) para diagnóstico en 30 segundos.

**📖 Solución Completa**:

1. **Diagnóstico rápido:** [INICIO_RAPIDO_MONGO.md](INICIO_RAPIDO_MONGO.md) - Identifica el problema en 30 seg
2. **Ver qué hay en MongoDB:** [QUE_VER_EN_MONGO.md](QUE_VER_EN_MONGO.md) - Guía visual completa
3. **Configurar MongoDB:** [RENDER_MONGODB_SETUP.md](RENDER_MONGODB_SETUP.md) - Setup paso a paso
4. **Credenciales de prueba:** [USUARIOS_Y_CONTRASEÑAS.txt](USUARIOS_Y_CONTRASEÑAS.txt) - Lista completa

**Causa más común en Render**: MongoDB no está conectado

Pasos esenciales:
1. ✅ Crear cuenta en MongoDB Atlas (gratis): https://www.mongodb.com/cloud/atlas/register
2. ✅ Crear cluster M0 (512MB gratis) y usuario de base de datos
3. ✅ Configurar `MONGO_URL` en Render → educando-backend → Environment
4. ✅ Re-desplegar el backend
5. ✅ Verificar logs: "MongoDB connection successful" y "Credenciales creadas para 7 usuarios"
6. ✅ Probar login con credenciales de USUARIOS_Y_CONTRASEÑAS.txt

## 🔧 Verificar Conexión a MongoDB

Si tienes problemas conectándote a MongoDB (especialmente en producción), usa el script de verificación:

```bash
# Opción 1: Pasar la connection string directamente
python backend/verify_mongodb.py "mongodb+srv://user:pass@cluster.mongodb.net/educando_db"

# Opción 2: Configurar MONGO_URL en backend/.env y ejecutar
python backend/verify_mongodb.py
```

El script verificará:
- ✅ Que la connection string sea válida
- ✅ Que puedas conectarte a MongoDB
- ✅ Que los usuarios estén creados correctamente
- ✅ El estado de las colecciones y documentos

**Requisitos:**
```bash
pip install motor python-dotenv
```

## 📚 Documentación Adicional

- [Documentación de React](https://react.dev/)
- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de Docker Compose](https://docs.docker.com/compose/)

## 📝 Notas

- **Desarrollo**: Usa `docker-compose.dev.yml` para hot-reload
- **Producción**: Usa `docker-compose.yml` para build optimizado
- Los cambios en `package.json` o `requirements.txt` requieren reconstruir: `docker compose -f docker-compose.dev.yml up --build`

---

¡Feliz desarrollo! 🎉
