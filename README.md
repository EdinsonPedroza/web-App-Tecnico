# Educando - Web App Técnico

Aplicación web full-stack para gestión educativa con React (frontend), FastAPI (backend) y MongoDB.

## 🌐 ¿Quieres Subir Esto a la Web?

**¡Perfecto! Tenemos guías súper fáciles para ti:**

- **📱 [GUÍA RÁPIDA - La Forma MÁS FÁCIL](GUIA_RAPIDA_DESPLIEGUE.md)** ⭐ Empieza aquí
- **🚂 [Paso a Paso con Railway](PASO_A_PASO_RAILWAY.md)** - 10 minutos, sin servidor
- **📋 [Tarjeta de Referencia Rápida](REFERENCIA_RAPIDA.md)** - Para imprimir
- **📚 [Guía Completa de Despliegue](DESPLIEGUE.md)** - Todas las opciones detalladas
- **🚀 [Recomendaciones para 3000+ Usuarios](DEPLOYMENT_RECOMMENDATIONS.md)** - Escalamiento

**Tiempo estimado:** 10-30 minutos  
**Costo estimado:** $5-20/mes  
**Dificultad:** Fácil 😊

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
