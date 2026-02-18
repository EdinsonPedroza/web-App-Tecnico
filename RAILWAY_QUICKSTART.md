# 🚀 Guía Rápida: Configurar Backend en Railway

## ⚡ Variables de Entorno OBLIGATORIAS

### En Railway Dashboard → Backend Service → Variables:

```bash
# ❗ OBLIGATORIO - Sin esto el backend crashea
MONGO_URL=mongodb+srv://usuario:password@cluster.mongodb.net/educando_db

# Opcional (tienen valores por defecto)
DB_NAME=educando_db
JWT_SECRET=tu_clave_secreta_larga_y_segura_cambiar_en_produccion
CORS_ORIGINS=*
```

## 📋 Checklist Rápido

### ✅ Antes de Desplegar:
- [ ] Crear MongoDB en Railway o usar MongoDB Atlas
- [ ] Copiar la URL de conexión de MongoDB
- [ ] Configurar `MONGO_URL` en Railway Backend Service

### ✅ Después de Desplegar:
- [ ] Ver logs: Railway → Backend → Logs tab
- [ ] Buscar: "Application startup completed successfully"
- [ ] Probar: `curl https://tu-backend.railway.app/api/health`
- [ ] Debe retornar: `{"status": "healthy", "database": "connected"}`

## 🔍 Verificación Rápida

### 1. Health Check
```bash
curl https://tu-backend.railway.app/api/health
```

**✅ Respuesta OK:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-18T01:00:00.000Z"
}
```

**❌ Respuesta Error:**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "error message"
}
```

### 2. API Root
```bash
curl https://tu-backend.railway.app/api/
```

**✅ Respuesta OK:**
```json
{
  "message": "Corporación Social Educando API"
}
```

## 🐛 Problemas Comunes

### ❌ Backend crashea al iniciar

**Causa:** `MONGO_URL` no configurado

**Solución:**
1. Railway → Backend Service → Variables
2. Agregar: `MONGO_URL=mongodb+srv://...`
3. Redeploy

### ❌ Error "timeout" en logs

**Causa:** MongoDB no accesible desde Railway

**Solución para MongoDB Atlas:**
1. Atlas → Network Access
2. Add IP Address → Allow Access from Anywhere (`0.0.0.0/0`)
3. Save

**Solución para MongoDB de Railway:**
- La URL debe ser la que Railway proporciona automáticamente
- Copiar exactamente sin cambios

### ❌ Error 502 Bad Gateway

**Causa:** Backend está crasheando

**Solución:**
1. Railway → Backend → Logs
2. Buscar línea con "ERROR"
3. Ver `SOLUCION_CRASHES_RAILWAY.md` para más detalles

### ❌ Frontend no conecta al backend

**Causa:** CORS mal configurado

**Solución:**
```bash
# En Railway Backend Variables:
CORS_ORIGINS=https://tu-frontend.railway.app

# Para múltiples dominios:
CORS_ORIGINS=https://tu-frontend.railway.app,https://tudominio.com
```

## 📊 Logs que Debes Ver

**✅ Inicio Correcto:**
```
INFO - Connecting to MongoDB at: cluster.mongodb.net
INFO - MongoDB client initialized for database: educando_db
INFO - Starting application initialization...
INFO - MongoDB connection successful
INFO - Verificando y creando datos iniciales...
INFO - Application startup completed successfully
```

**❌ Error de Conexión:**
```
ERROR - Failed to initialize MongoDB client: ...
ERROR - Startup failed: ...
```

## 🎯 MongoDB en Railway vs Atlas

### Opción 1: MongoDB de Railway (Más Fácil)
1. Railway → Add Service → Database → MongoDB
2. Railway crea `MONGO_URL` automáticamente
3. Listo ✅

### Opción 2: MongoDB Atlas (Gratuito Permanente)
1. Crear cuenta en [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Crear cluster gratuito (M0)
3. Database Access → Crear usuario
4. Network Access → Add IP → `0.0.0.0/0`
5. Connect → Copiar connection string
6. Railway → Backend → Variables → Agregar `MONGO_URL`

## 💡 Tips Importantes

1. **No uses `localhost` en MONGO_URL** - No funciona en Railway
2. **El puerto `$PORT`** - Railway lo asigna automáticamente
3. **Logs son tu amigo** - Siempre revisa los logs primero
4. **Health check** - Úsalo para verificar que todo funciona
5. **Variables de entorno** - Se aplican después de redeploy

## 📞 ¿Necesitas Ayuda?

1. ✅ Revisa los logs en Railway
2. ✅ Prueba el health check
3. ✅ Lee `SOLUCION_CRASHES_RAILWAY.md` para más detalles
4. ✅ Verifica que todas las variables estén configuradas

---

**Versión:** 1.0  
**Última actualización:** 18 Feb 2026
