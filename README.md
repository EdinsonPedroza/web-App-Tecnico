# Educando - Web App Técnico

Aplicación web full-stack para gestión educativa con React (frontend), FastAPI (backend), MongoDB Atlas y AWS S3.

✅ **Desplegada y funcionando en producción en Render** para la Corporación Social Educando.

---

## 🚀 Stack Tecnológico

### Frontend
- **React** con JavaScript
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

### Infraestructura
- **MongoDB Atlas Flex** — base de datos (BD: `WebApp`)
- **AWS S3** — almacenamiento de archivos subidos por los usuarios
- **Render** — plataforma de despliegue

---

## 📋 Requisitos Previos

- Docker Desktop instalado y corriendo
- Git

---

## 🛠️ Configuración de Desarrollo (Hot-Reload)

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

### 4. Detener el entorno
```bash
docker compose -f docker-compose.dev.yml down
```

---

## 🚢 Despliegue en Producción

Para el despliegue completo en Render con MongoDB Atlas y AWS S3, sigue la guía paso a paso:

📋 **[DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md)** — Lista de verificación de despliegue en Render

### Credenciales de usuarios semilla

Las credenciales se configuran al hacer el primer deploy con `CREATE_SEED_USERS=true`. Ver los logs del backend para obtenerlas.

> ⚠️ Cambia `CREATE_SEED_USERS` a `false` después del primer deploy.

### Producción para 3000 usuarios

La configuración actual en Render Starter soporta ~200-500 usuarios simultáneos. Para escalar a 3000 usuarios simultáneos se recomienda:

- **MongoDB Atlas:** Upgrade a M10 (3000+ conexiones)
- **Backend:** Múltiples instancias con más workers (actualizar plan de Render)
- **Dominio custom:** Configurar registros CNAME en `corporacioneducando.com`

---

## 📁 Estructura del Proyecto

```
web-App-Tecnico/
├── frontend/                 # Aplicación React (JavaScript)
│   ├── src/                 # Código fuente
│   ├── public/              # Archivos públicos
│   ├── Dockerfile           # Dockerfile de producción (build + nginx)
│   ├── Dockerfile.dev       # Dockerfile de desarrollo (yarn start)
│   └── package.json
├── backend/                  # API FastAPI (Python)
│   ├── server.py            # Aplicación principal
│   ├── Dockerfile           # Dockerfile de producción
│   ├── Dockerfile.dev       # Dockerfile de desarrollo (uvicorn --reload)
│   └── requirements.txt
├── docker-compose.yml        # Configuración de producción local
├── docker-compose.dev.yml    # Configuración de desarrollo (hot-reload)
├── render.yaml               # Configuración de servicios en Render
├── DEPLOY_CHECKLIST.md       # Guía de despliegue en producción
├── ANALISIS_TECNICO.md       # Análisis técnico del proyecto
└── SECURITY.md               # Política de seguridad
```

---

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

# Backend
docker exec -it educando_backend bash
docker exec -it educando_backend pip install nueva-dependencia
```

### Limpiar volúmenes y contenedores
```bash
docker compose -f docker-compose.dev.yml down -v
```

---

## 🐛 Solución de Problemas

### El frontend no se actualiza al hacer cambios

**Problema**: Los cambios en el código no se reflejan en el navegador.

**Solución**:
1. Verifica que estés usando `docker-compose.dev.yml` y no `docker-compose.yml`
2. Reconstruye los contenedores:
   ```bash
   docker compose -f docker-compose.dev.yml down
   docker compose -f docker-compose.dev.yml up --build
   ```

### El backend no se actualiza al hacer cambios

**Problema**: Los cambios en el código Python no se reflejan.

**Solución**:
1. Verifica que el backend esté usando `Dockerfile.dev` con el flag `--reload`
2. Revisa los logs: `docker compose -f docker-compose.dev.yml logs -f backend`

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

### Los datos de MongoDB se pierden al reiniciar

**Problema**: Los datos de MongoDB se pierden al detener los contenedores.

**Solución**: Los datos persisten en el volumen `mongodb_data`. Para limpiar:
```bash
docker compose -f docker-compose.dev.yml down -v  # ⚠️ Esto borrará los datos
```

### Problemas con autenticación o credenciales

**❌ Problema**: Las credenciales no funcionan, no puedo iniciar sesión.

**Causa más común en Render**: MongoDB no está conectado.

Pasos esenciales:
1. ✅ Crear cuenta en MongoDB Atlas: https://www.mongodb.com/cloud/atlas/register
2. ✅ Crear cluster y usuario de base de datos
3. ✅ Configurar `MONGO_URL` en Render → educando-backend → Environment
4. ✅ Re-desplegar el backend
5. ✅ Verificar en los logs: "MongoDB connection successful"

> ⚠️ **Admins y Editores** usan la pestaña "PROFESOR", NO "ESTUDIANTE"

---

## 📚 Documentación Adicional

- [Documentación de React](https://react.dev/)
- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [SECURITY.md](SECURITY.md) — Política de seguridad del proyecto

---

¡Feliz desarrollo! 🎉
