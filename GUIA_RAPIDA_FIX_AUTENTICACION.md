# GUÍA RÁPIDA: Qué se Arregló y Cómo Probarlo

## 🎯 Problema Resuelto

**Antes:** Solo los usuarios creados desde la página web funcionaban en Docker. Los usuarios semilla (como `pr.o.fe.sorSl@educando.com`) no se creaban.

**Ahora:** Todos los usuarios funcionan - tanto los semilla como los creados desde la web.

## 🔧 Qué Se Cambió

### 1. Usuarios Semilla Ahora Siempre Se Crean

**El problema principal:** El código verificaba si existían usuarios en la base de datos. Si encontraba alguno (aunque fuera creado desde la web), se saltaba la creación de usuarios semilla.

**La solución:** Ahora los usuarios semilla SIEMPRE se crean o actualizan automáticamente cuando el backend inicia.

### 2. Configuración Mejorada

- ✅ **DB_NAME** ahora es `WebApp` en TODOS los ambientes (antes era inconsistente)
- ✅ **Credenciales eliminadas** de docker-compose.yml (más seguro)
- ✅ **PASSWORD_STORAGE_MODE** configurado en todos los ambientes
- ✅ **Variables de entorno** con valores por defecto sensatos

## 🧪 Cómo Probarlo

### Opción 1: Probar con Docker (Local)

```bash
# 1. Levantar los contenedores
cd /ruta/a/web-App-Tecnico
docker-compose up -d

# 2. Ver los logs del backend
docker-compose logs -f backend

# 3. Buscar estos mensajes:
#    ✅ "MongoDB connection successful"
#    ✅ "7 usuarios semilla disponibles"
```

### Opción 2: Probar Login

1. Abre la aplicación en tu navegador: `http://localhost`
2. Selecciona la pestaña **"PROFESOR"**
3. Prueba con un usuario semilla:
   - **Email:** `pr.o.fe.sorSl@educando.com`
   - **Contraseña:** `educador123`
4. Haz clic en **"Ingresar"**
5. **Resultado esperado:** ✅ Login exitoso, acceso al dashboard

### Opción 3: Probar con Usuario Creado desde Web

1. Si antes creaste usuarios desde la interfaz web, también deberían funcionar
2. Inicia sesión con esas credenciales
3. **Resultado esperado:** ✅ Login exitoso

## 📋 Usuarios Semilla Disponibles

Ahora estos usuarios SIEMPRE están disponibles:

### Editores
- **Email:** `carlos.mendez@educando.com`
- **Contraseña:** `Editor2026*CM`
- **Pestaña de login:** PROFESOR

### Administradores
- **Email:** `laura.torres@educando.com` | Contraseña: `Admin2026*LT`
- **Email:** `roberto.ramirez@educando.com` | Contraseña: `Admin2026*RR`
- **Pestaña de login:** PROFESOR

### Profesores
- **Email:** `diana.silva@educando.com` | Contraseña: `Profe2026*DS`
- **Email:** `miguel.castro@educando.com` | Contraseña: `Profe2026*MC`
- **Email:** `pr.o.fe.sorSl@educando.com` | Contraseña: `educador123` ⭐
- **Pestaña de login:** PROFESOR

### Estudiantes
- **Cédula:** `1001234567` | Contraseña: `Estud2026*SM`
- **Cédula:** `1002345678` | Contraseña: `Estud2026*AL`
- **Pestaña de login:** ESTUDIANTE

## 🚀 Para Render

### ¿Qué Necesitas Hacer?

1. **Verificar/Configurar MONGO_URL en Render Dashboard:**
   - Ve a: Render Dashboard → `educando-backend` → Environment
   - Verifica que existe la variable `MONGO_URL`
   - **Debe incluir `/WebApp`** en la URL:
     ```
     mongodb+srv://usuario:password@cluster.mongodb.net/WebApp?retryWrites=true&w=majority
                                                            ^^^^^^
     ```

2. **Verificar las demás variables:**
   - `DB_NAME=WebApp` ✅ (ya actualizado en render.yaml)
   - `PASSWORD_STORAGE_MODE=plain` ✅ (ya actualizado en render.yaml)
   - `JWT_SECRET` debe existir (generado automáticamente)

3. **Hacer re-deploy** (si es necesario):
   - Render debería hacer auto-deploy al hacer push
   - O puedes hacer deploy manual desde el dashboard

4. **Verificar logs en Render:**
   - Ve a: Render Dashboard → `educando-backend` → Logs
   - Busca: `"MongoDB connection successful"`
   - Busca: `"7 usuarios semilla disponibles"`

## ❓ Solución de Problemas

### Problema: "MongoDB connection failed"

**Solución:**
- Verifica que `MONGO_URL` esté correctamente configurado
- Para MongoDB Atlas, verifica que la IP `0.0.0.0/0` esté permitida en Network Access
- Verifica que el usuario y contraseña de MongoDB sean correctos

### Problema: "Credenciales incorrectas" al intentar login

**Solución:**
1. Revisa los logs del backend:
   ```bash
   docker-compose logs -f backend
   ```
2. Busca: `"7 usuarios semilla disponibles"`
3. Si no ves ese mensaje, los usuarios no se crearon
4. Verifica que MongoDB esté conectado

### Problema: Los usuarios semilla aún no existen

**Solución:**
- Reinicia el backend:
  ```bash
  docker-compose restart backend
  docker-compose logs -f backend
  ```
- Los usuarios deberían crearse/actualizarse automáticamente

## 📚 Documentación Completa

Para más detalles, ver:
- `SOLUCION_AUTENTICACION_DOCKER_RENDER.md` - Análisis técnico completo
- `USUARIOS_Y_CONTRASEÑAS.txt` - Lista completa de usuarios y credenciales

## ✅ Checklist de Verificación

- [ ] Docker levanta correctamente (`docker-compose up -d`)
- [ ] Backend se conecta a MongoDB (ver logs)
- [ ] Mensaje "7 usuarios semilla disponibles" aparece en logs
- [ ] Login funciona con `pr.o.fe.sorSl@educando.com` / `educador123`
- [ ] Login funciona con usuarios creados desde web
- [ ] (Render) MONGO_URL configurado correctamente con `/WebApp`
- [ ] (Render) Login funciona en producción

---

**¿Necesitas ayuda?** Revisa `SOLUCION_AUTENTICACION_DOCKER_RENDER.md` para análisis detallado.
