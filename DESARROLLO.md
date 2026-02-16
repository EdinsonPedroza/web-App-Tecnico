# 🚀 Guía Rápida - Desarrollo con Hot-Reload

## Problema Original

Cuando ejecutabas `docker-compose up --build`, la aplicación se compilaba pero no tenías hot-reload (recarga automática al editar código).

## ✅ Solución

Ahora hay **DOS** configuraciones de Docker:

### 1️⃣ Desarrollo (con hot-reload) ⭐ **USA ESTA**
```bash
docker-compose -f docker-compose.dev.yml up --build
```
- ✅ Frontend en http://localhost:3000 - SE ACTUALIZA AUTOMÁTICAMENTE
- ✅ Backend en http://localhost:8001 - SE ACTUALIZA AUTOMÁTICAMENTE
- ✅ Cambios en tiempo real sin reconstruir

### 2️⃣ Producción (sin hot-reload)
```bash
docker-compose up --build
```
- Frontend en http://localhost:80 (versión compilada con nginx)
- Para despliegue final, no para desarrollo

## 📝 Cómo Usar

### Paso 1: Iniciar desarrollo
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Paso 2: Editar código
1. Abre `frontend/src/App.js` o cualquier archivo
2. Haz un cambio
3. Guarda el archivo (Ctrl+S)
4. 🎉 **El navegador se recarga automáticamente**

### Paso 3: Ver cambios en el backend
1. Edita `backend/server.py`
2. Guarda
3. Uvicorn detecta el cambio y reinicia el servidor
4. Revisa los logs: `docker-compose -f docker-compose.dev.yml logs -f backend`

### Paso 4: Detener
```bash
# En la terminal donde está corriendo:
Ctrl+C

# O en otra terminal:
docker-compose -f docker-compose.dev.yml down
```

## 🔍 ¿Qué cambió?

### Antes (docker-compose.yml)
- ❌ Frontend: compilaba build y servía con nginx (sin hot-reload)
- ❌ Backend: sin flag --reload

### Ahora (docker-compose.dev.yml)
- ✅ Frontend: usa `yarn start` (servidor de desarrollo con hot-reload)
- ✅ Backend: usa `uvicorn --reload` (reinicio automático)
- ✅ Volúmenes montados: tus archivos locales se reflejan en el contenedor

## 💡 Consejos

- **Siempre usa `-f docker-compose.dev.yml`** para desarrollo
- Si cambias `package.json` o `requirements.txt`, reconstruye:
  ```bash
  docker-compose -f docker-compose.dev.yml up --build
  ```
- Para ver logs de un servicio:
  ```bash
  docker-compose -f docker-compose.dev.yml logs -f frontend
  docker-compose -f docker-compose.dev.yml logs -f backend
  ```

## 🐛 Si algo no funciona

1. Detén todo: `docker-compose -f docker-compose.dev.yml down`
2. Reconstruye: `docker-compose -f docker-compose.dev.yml up --build`
3. Revisa los logs para ver errores

---

**¡Listo! Ahora puedes editar código y verlo en tiempo real.** 🎉
