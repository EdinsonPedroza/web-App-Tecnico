# Consideraciones de Producción

Este documento describe los aspectos importantes a considerar al desplegar la aplicación en producción.

## 🔴 Crítico: Almacenamiento de Archivos (Alta Importancia)

### Problema
Los archivos subidos (PDFs de talleres, entregas de estudiantes, etc.) se guardan en el disco local del contenedor (`backend/uploads/`). En plataformas como Render, Railway, o Heroku, este disco es **efímero** y se borra en cada redespliegue o reinicio.

### Impacto
- ❌ Los archivos subidos por profesores y estudiantes **se perderán** al redesplegar
- ❌ Los archivos se perderán al reiniciar el servicio
- ❌ No hay backup automático de los archivos

### Soluciones Recomendadas

#### Opción 1: Cloudinary (Recomendado para empezar)
- ✅ **Plan gratuito**: 25GB de almacenamiento, 25 créditos/mes
- ✅ Fácil de integrar con Python
- ✅ CDN incluido (entrega rápida de archivos)
- 💰 **Costo**: Gratis hasta 25GB, luego desde $89/mes

**Implementación básica:**
```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)

# Al subir archivo:
result = cloudinary.uploader.upload(file, folder="educando/uploads")
file_url = result['secure_url']
```

#### Opción 2: AWS S3
- ✅ Muy escalable
- ✅ Precio por uso (muy económico al inicio)
- ⚠️ Requiere cuenta de AWS y configuración de IAM
- 💰 **Costo**: ~$0.023 por GB/mes + transferencia

#### Opción 3: Render Disk (Persistente)
- ✅ Incluido con plan Starter ($7/mes)
- ⚠️ Requiere upgrade de plan gratuito
- ⚠️ No tiene CDN (puede ser lento en algunas regiones)
- 💰 **Costo**: Incluido con plan Starter ($7/mes)

### Estado Actual
⚠️ La aplicación detecta automáticamente si está en producción (Render, Railway, Heroku) y muestra una advertencia en los logs al iniciar.

---

## 🟡 Importante: Seguridad de Contraseñas

### Configuración Actual
- **Modo por defecto**: `bcrypt` (seguro)
- **Compatibilidad**: El sistema verifica automáticamente contraseñas en formato bcrypt, SHA256, o texto plano

### Recomendaciones
1. ✅ **Producción**: Usar `PASSWORD_STORAGE_MODE=bcrypt`
2. ⚠️ **Compatibilidad**: Si tienes usuarios con contraseñas en texto plano, el sistema las verifica automáticamente
3. 🔄 **Migración**: Al cambiar de `plain` a `bcrypt`, los usuarios existentes pueden:
   - Seguir iniciando sesión (el sistema verifica ambos formatos)
   - Al cambiar su contraseña, se guardará en bcrypt automáticamente

### Configuración en Render/Railway
```bash
# Variables de entorno
PASSWORD_STORAGE_MODE=bcrypt
```

---

## 🟡 Rate Limiting (Limitación de Intentos de Login)

### Comportamiento Actual
- Máximo 5 intentos de login fallidos por IP en 5 minutos
- El contador está en memoria RAM
- **Se resetea** al reiniciar el servidor

### Impacto
- 🟢 Bajo en uso normal (protege contra ataques mientras el servidor esté activo)
- ⚠️ Un atacante podría intentar de nuevo después de reiniciar el servidor
- ⚠️ En deployments con múltiples instancias, cada instancia tiene su propio contador

### Solución Futura (Opcional)
Para protección más robusta en producción con alto tráfico:

```python
# Usar Redis para rate limiting distribuido
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# En check_rate_limit():
key = f"login_attempts:{ip_address}"
attempts = redis_client.get(key)
if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
    return False
redis_client.incr(key)
redis_client.expire(key, LOGIN_ATTEMPT_WINDOW)
```

**Cuándo implementar Redis:**
- Múltiples instancias del backend (load balancing)
- Más de 500 usuarios activos simultáneos
- Ataques frecuentes de fuerza bruta

---

## 🟢 Usuarios Semilla (Seed Users)

### Cambio Implementado ✅
Los usuarios semilla (Carlos Mendez, Laura Torres, etc.) **ya NO se sobrescriben** en cada reinicio.

### Comportamiento Actual
1. En el primer inicio (base de datos vacía):
   - Se crean 8 usuarios semilla con sus contraseñas por defecto

2. En reinicios posteriores:
   - ✅ Los usuarios semilla NO se sobrescriben
   - ✅ Los cambios hechos desde el admin panel son permanentes
   - ✅ Si eliminas un usuario semilla, no se recrea automáticamente

### Usuarios Semilla por Defecto
Ver el archivo `USUARIOS_Y_CONTRASEÑAS.txt` para la lista completa.

---

## 🟢 Token JWT - Expiración

### Configuración Actual
- Duración: 7 días
- Algoritmo: HS256

### ¿Por qué expiran?
Por seguridad. Si un token es robado, solo funciona por 7 días.

### Experiencia del Usuario
- Los usuarios deben volver a iniciar sesión cada 7 días
- Es comportamiento normal y esperado
- No es un bug

### Ajustar Duración (si es necesario)
```python
# En server.py, función create_token():
"exp": datetime.now(timezone.utc) + timedelta(days=30)  # 30 días en vez de 7
```

⚠️ **No recomendado**: Aumentar mucho la duración reduce la seguridad.

---

## 📊 MongoDB Atlas - Límites del Plan Gratuito

### Plan M0 (Gratuito)
- ✅ 512 MB de almacenamiento
- ✅ Compartido (suficiente para desarrollo)
- ⚠️ Máximo 500 conexiones simultáneas

### Cuándo Actualizar
Monitor en MongoDB Atlas → Metrics:
- Si el almacenamiento supera 400 MB (80%)
- Si las conexiones frecuentemente alcanzan el límite
- Si notas lentitud con muchos usuarios

### Plan M2 ($9/mes)
- 2 GB de almacenamiento
- 500 conexiones
- Dedicado (mejor rendimiento)

### Plan M10 ($57/mes)
- 10 GB de almacenamiento
- 3000+ conexiones
- Ideal para 3000+ usuarios simultáneos
- Ver: `GUIA_PRODUCCION_3000_USUARIOS.md`

---

## 🛡️ Checklist de Seguridad para Producción

- [ ] `PASSWORD_STORAGE_MODE=bcrypt` configurado en variables de entorno
- [ ] `JWT_SECRET` cambiado a un valor secreto largo y aleatorio
- [ ] MongoDB Atlas: IP Whitelist configurada correctamente
- [ ] MongoDB Atlas: Usuario de base de datos con contraseña fuerte
- [ ] HTTPS habilitado (Render/Railway lo hacen automáticamente)
- [ ] Variables de entorno configuradas (no hardcodeadas)
- [ ] CORS configurado correctamente (`CORS_ORIGINS` en producción)
- [ ] `DEBUG=false` en producción (o no configurado)
- [ ] Plan de migración de archivos a Cloudinary/S3 definido
- [ ] Monitoreo de espacio en MongoDB Atlas configurado

---

## 🚀 Próximos Pasos Recomendados

### Corto Plazo (1-2 semanas)
1. **Migrar archivos a Cloudinary** (prevenir pérdida de archivos)
2. Configurar alertas en MongoDB Atlas (uso de espacio)
3. Documentar proceso de backup de MongoDB

### Mediano Plazo (1-2 meses)
1. Implementar Redis para rate limiting (si hay múltiples instancias)
2. Agregar monitoreo de logs (Sentry, LogDNA, etc.)
3. Implementar tests automatizados

### Largo Plazo (3-6 meses)
1. Migrar a arquitectura con CDN para frontend
2. Implementar sistema de cache (Redis) para consultas frecuentes
3. Considerar upgrade de MongoDB si el almacenamiento lo requiere

---

## 📞 Soporte

Si tienes dudas sobre alguna de estas consideraciones:
1. Revisa la documentación en `/docs/*.md`
2. Consulta `GUIA_PRODUCCION_3000_USUARIOS.md` para escalamiento
3. Revisa los logs del servidor en Render/Railway Dashboard

**Última actualización**: Febrero 2026
