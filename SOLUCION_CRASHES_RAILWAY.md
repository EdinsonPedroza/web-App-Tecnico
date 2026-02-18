# 🔧 Solución: Backend se Cae en Railway

## ❌ Problemas Identificados y Solucionados

### 1. **CRÍTICO: MONGO_URL no configurado en Railway**
**Síntoma:** Backend crashea inmediatamente al iniciar
**Causa:** La variable de entorno `MONGO_URL` no está configurada en Railway, o está configurada como `mongodb://localhost:27017` que no funciona en Railway.

**✅ Solución:**
```bash
# En Railway, configura MONGO_URL con la URL real de tu MongoDB:
MONGO_URL=mongodb+srv://usuario:password@cluster.mongodb.net/educando_db
# O si usas MongoDB de Railway:
MONGO_URL=mongodb://mongo:CONTRASEÑA@monorail.proxy.rlwy.net:PORT
```

### 2. **CRÍTICO: Sin manejo de errores en startup**
**Síntoma:** Crashes silenciosos sin logs descriptivos
**Causa:** La función `startup_event()` no tenía try/catch, causando crashes sin información.

**✅ Solución:** Agregado manejo de errores con logs detallados:
```python
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting application initialization...")
        await db.command('ping')  # Test MongoDB connection
        logger.info("MongoDB connection successful")
        await create_initial_data()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise RuntimeError(f"Application startup failed: {e}") from e
```

### 3. **Sin manejador global de excepciones**
**Síntoma:** Errores inesperados causan crashes
**Causa:** No había un manejador global para capturar excepciones no esperadas.

**✅ Solución:** Agregado exception handler:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )
```

### 4. **Problema con CORS_ORIGINS**
**Síntoma:** CORS puede fallar si la variable no tiene comas
**Causa:** `split(',')` en un string sin comas genera array de caracteres individuales.

**✅ Solución:** Verificar si hay comas antes de hacer split:
```python
allow_origins=os.environ.get('CORS_ORIGINS', '*').split(',') if ',' in os.environ.get('CORS_ORIGINS', '*') else [os.environ.get('CORS_ORIGINS', '*')]
```

### 5. **Falta endpoint de health check**
**Síntoma:** Difícil diagnosticar problemas de conexión a base de datos
**Causa:** No había un endpoint simple para verificar el estado de la aplicación.

**✅ Solución:** Agregado `/api/health`:
```python
@api_router.get("/health")
async def health_check():
    try:
        await db.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )
```

## 📋 Checklist para Desplegar en Railway

### Paso 1: Configurar Variables de Entorno en Railway

Ve a tu servicio Backend en Railway → Settings → Variables y agrega:

```bash
# OBLIGATORIO - Sin esto, el backend crashea
MONGO_URL=mongodb+srv://usuario:password@tu-cluster.mongodb.net/educando_db

# Opcionales (tienen valores por defecto)
DB_NAME=educando_db
JWT_SECRET=tu_clave_secreta_super_segura_aqui_cambiar_en_produccion
CORS_ORIGINS=https://tu-frontend.railway.app
```

### Paso 2: Verificar Logs en Railway

Después de desplegar, ve a:
1. Railway Dashboard → Tu Servicio Backend → **Logs**
2. Busca estos mensajes:

✅ **Inicio Exitoso:**
```
INFO - Connecting to MongoDB at: cluster.mongodb.net/educando_db
INFO - MongoDB client initialized for database: educando_db
INFO - Starting application initialization...
INFO - MongoDB connection successful
INFO - Application startup completed successfully
```

❌ **Si falla:**
```
ERROR - Failed to initialize MongoDB client: ...
ERROR - Startup failed: ...
```

### Paso 3: Probar el Health Check

Una vez desplegado, prueba el endpoint:

```bash
curl https://tu-backend.railway.app/api/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-18T01:00:00.000Z"
}
```

**Si falla:**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "error message here"
}
```

### Paso 4: Verificar la Aplicación Principal

```bash
curl https://tu-backend.railway.app/api/
```

**Respuesta esperada:**
```json
{
  "message": "Corporación Social Educando API"
}
```

## 🐛 Troubleshooting

### El backend sigue cayendo

1. **Verifica los logs en Railway:**
   ```
   Railway Dashboard → Backend Service → Logs tab
   ```

2. **Busca el mensaje de error específico:**
   - Si dice "MONGO_URL": Configura la variable en Railway
   - Si dice "timeout": Tu MongoDB puede estar bloqueando la conexión (verifica IP whitelist)
   - Si dice "authentication failed": Verifica usuario/contraseña de MongoDB

3. **Verifica el health check:**
   ```bash
   curl https://tu-backend.railway.app/api/health
   ```

### MongoDB no se conecta

1. **Si usas MongoDB Atlas:**
   - Ve a Network Access en Atlas
   - Agrega IP `0.0.0.0/0` para permitir Railway
   - Verifica que el usuario/contraseña sea correcto

2. **Si usas MongoDB de Railway:**
   - Railway proporciona la URL automáticamente
   - Copia exactamente la variable `MONGO_URL` que Railway te da
   - No cambies nada en la URL

### Error 502 Bad Gateway

1. El backend está crasheando
2. Revisa los logs en Railway
3. Verifica que todas las variables de entorno estén configuradas
4. Prueba el health check

### Error de CORS

Si el frontend no puede conectarse al backend:
```bash
# En Railway, configura:
CORS_ORIGINS=https://tu-frontend.railway.app

# O para permitir múltiples dominios:
CORS_ORIGINS=https://tu-frontend.railway.app,https://tu-dominio.com
```

## 📊 Monitoreo

### Endpoints para Monitoreo

1. **Health Check:** `GET /api/health`
   - Verifica estado de la aplicación y base de datos

2. **API Root:** `GET /api/`
   - Verifica que la API esté respondiendo

3. **Logs de Railway:**
   - Railway Dashboard → Logs
   - Filtra por ERROR o WARNING

## 🎯 Resultado Esperado

Después de aplicar estos cambios:

✅ Backend inicia correctamente incluso si hay problemas temporales
✅ Logs detallados para diagnosticar cualquier problema
✅ Health check endpoint para monitoreo
✅ Manejo robusto de errores sin crashes silenciosos
✅ Valores por defecto seguros para desarrollo local

## 📝 Notas Adicionales

- El archivo `backend/.env` ya no tiene `MONGO_URL` hardcodeado a localhost
- Usa `MONGO_URL` de Railway para producción
- Para desarrollo local, puedes crear un `.env.local` con `MONGO_URL=mongodb://localhost:27017`
- Los logs ahora son mucho más verbosos para facilitar debugging

## ✅ Verificación Final

Cuando todo funcione correctamente, deberías ver:

1. ✅ Backend desplegado sin crashes
2. ✅ Logs que muestran "Application startup completed successfully"
3. ✅ `/api/health` retorna `{"status": "healthy"}`
4. ✅ Frontend puede conectarse al backend
5. ✅ Puedes hacer login y usar la aplicación

---

**¿Necesitas ayuda?** Revisa los logs en Railway y busca el mensaje de error específico.
