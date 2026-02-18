# ✅ Checklist de Despliegue en Render

## 📝 Usa esta lista para verificar cada paso

---

## ANTES DE EMPEZAR

- [ ] Tengo cuenta de GitHub
- [ ] Mi código está en GitHub: `EdinsonPedroza/web-App-Tecnico`
- [ ] Tengo una tarjeta para plan pagado (opcional, solo si NO usas plan gratuito)
- [ ] Tengo 30 minutos disponibles

---

## PASO 1: CONFIGURAR RENDER (5 min)

- [ ] Fui a https://render.com
- [ ] Hice clic en "Get Started"
- [ ] Seleccioné "Sign up with GitHub"
- [ ] Autoricé a Render
- [ ] Verifiqué mi email (si me lo pidieron)
- [ ] Conecté mi cuenta de GitHub
- [ ] Di acceso al repositorio `web-App-Tecnico`

---

## PASO 2: DESPLEGAR CON BLUEPRINT (10 min)

- [ ] En Render Dashboard, hice clic en "New +" → "Blueprint"
- [ ] Seleccioné mi repositorio: `EdinsonPedroza/web-App-Tecnico`
- [ ] Render detectó el archivo `render.yaml` automáticamente
- [ ] Hice clic en "Apply"
- [ ] Esperé 5-10 minutos mientras Render construye
- [ ] Vi que se crearon 2 servicios:
  - [ ] `educando-backend`
  - [ ] `educando-frontend`
- [ ] Los servicios están en "Building" o "Live" (por ahora pueden fallar, es normal)

---

## PASO 3: CONFIGURAR MONGODB (10 min)

### Opción A: MongoDB Atlas (Recomendado - Gratis) ✅

- [ ] Fui a https://www.mongodb.com/cloud/atlas/register
- [ ] Creé una cuenta (usé Google o email)
- [ ] Seleccioné el plan **M0 FREE**
- [ ] Configuré mi cluster:
  - [ ] Provider: AWS
  - [ ] Region: Oregon (us-west-2)
  - [ ] Nombre: `educando-cluster`
- [ ] Hice clic en "Create"
- [ ] Creé un usuario de base de datos:
  - [ ] Username: `educando_admin`
  - [ ] Password: _________________ (guardé esta contraseña)
- [ ] Configuré acceso desde cualquier IP:
  - [ ] Agregué IP: `0.0.0.0/0`
- [ ] Hice clic en "Finish and Close"
- [ ] Obtuve la connection string:
  - [ ] Clic en "Connect"
  - [ ] Seleccioné "Connect your application"
  - [ ] Copié la URL
  - [ ] Reemplacé `<password>` con mi contraseña
  - [ ] Mi URL se ve así: `mongodb+srv://educando_admin:MIPASSWORD@educando-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority`

### Opción B: Private Service en Render ($7/mes)

- [ ] En Render: "New +" → "Private Service"
- [ ] Conecté mi repositorio
- [ ] Configuré:
  - [ ] Name: `educando-mongodb`
  - [ ] Environment: Docker
  - [ ] Dockerfile Path: `mongodb.Dockerfile`
  - [ ] Plan: Standard ($7/mes)
- [ ] Agregué disco:
  - [ ] Mount Path: `/data/db`
  - [ ] Size: 10 GB
- [ ] Esperé a que esté "Live"
- [ ] Copié la "Internal Connection String"

---

## PASO 4: CONFIGURAR VARIABLES EN EL BACKEND (3 min)

- [ ] En Render Dashboard, hice clic en el servicio "educando-backend"
- [ ] Fui a "Environment" en el menú izquierdo
- [ ] Verifiqué/agregué estas variables:
  - [ ] `MONGO_URL` = (pegué la URL de MongoDB Atlas o Private Service)
  - [ ] `DB_NAME` = `educando_db` (debería estar ya)
  - [ ] `JWT_SECRET` = (Render lo generó automáticamente)
  - [ ] `PORT` = `10000` (Render lo configura automáticamente)
- [ ] Hice clic en "Save Changes"
- [ ] Esperé 2-3 minutos para que Render redesplegara

---

## PASO 5: VERIFICAR FRONTEND (2 min)

- [ ] En Render Dashboard, hice clic en el servicio "educando-frontend"
- [ ] Fui a "Environment"
- [ ] Verifiqué que exista:
  - [ ] `REACT_APP_BACKEND_URL` = (URL del backend, debería estar automático)
- [ ] Si `REACT_APP_BACKEND_URL` está vacío:
  - [ ] Fui al servicio "educando-backend"
  - [ ] Copié su URL pública (ej: `https://educando-backend.onrender.com`)
  - [ ] Volví al frontend → Environment
  - [ ] Agregué `REACT_APP_BACKEND_URL` con la URL del backend
  - [ ] Guardé los cambios

Nota: El puerto se configura automáticamente en Render, no necesitas configurarlo manualmente.

---

## PASO 6: VERIFICAR QUE TODO ESTÉ LIVE (5 min)

- [ ] En Render Dashboard, verifiqué que ambos servicios estén "Live":
  - [ ] `educando-backend` → ✅ "Live"
  - [ ] `educando-frontend` → ✅ "Live"
- [ ] Si algún servicio está en "Failed":
  - [ ] Hice clic en el servicio
  - [ ] Revisé los "Logs"
  - [ ] Busqué errores en rojo
  - [ ] Corregí el problema (usualmente es la URL de MongoDB)

---

## PASO 7: ACCEDER A MI APLICACIÓN (2 min)

- [ ] Hice clic en el servicio "educando-frontend"
- [ ] Copié la URL pública (algo como: `https://educando-frontend.onrender.com`)
- [ ] Abrí esa URL en mi navegador
- [ ] Vi la página de login de mi aplicación ✅
- [ ] Inicié sesión con:
  - Email: `admin@educando.com`
  - Password: `admin123`
- [ ] ¡Funcionó! 🎉

---

## PASO 8: CAMBIAR CONTRASEÑA POR DEFECTO (2 min)

⚠️ **MUY IMPORTANTE**

- [ ] Después de iniciar sesión, fui a mi perfil
- [ ] Cambié la contraseña por defecto `admin123`
- [ ] Usé una contraseña segura (12+ caracteres, mayúsculas, minúsculas, números, símbolos)
- [ ] Nueva contraseña: _________________ (la guardé en un lugar seguro)

---

## PASO 9: PROBAR FUNCIONALIDADES (5 min)

- [ ] Probé crear un usuario de prueba
- [ ] Probé iniciar sesión con ese usuario
- [ ] Probé navegar por la aplicación
- [ ] Verifiqué que el frontend se conecta al backend correctamente
- [ ] Probé subir un archivo (si aplica)
- [ ] Todo funciona correctamente ✅

---

## PASO 10: CONFIGURACIÓN ADICIONAL (Opcional)

### Si quiero un dominio personalizado:

- [ ] Fui al servicio "educando-frontend" en Render
- [ ] Hice clic en "Settings"
- [ ] Busqué "Custom Domains"
- [ ] Agregué mi dominio (ej: `www.mieducando.com`)
- [ ] Seguí las instrucciones de Render para configurar DNS
- [ ] Esperé 10-30 minutos para propagación de DNS

### Si quiero backups automáticos de MongoDB Atlas:

- [ ] Fui a MongoDB Atlas Dashboard
- [ ] Seleccioné mi cluster
- [ ] Fui a "Backup"
- [ ] Configuré backups automáticos

---

## ✅ VERIFICACIÓN FINAL

### Checklist de Verificación:

- [ ] Puedo acceder a mi aplicación en la URL pública
- [ ] El login funciona
- [ ] Cambié la contraseña por defecto
- [ ] El frontend se conecta al backend
- [ ] Puedo crear usuarios
- [ ] La base de datos guarda información correctamente
- [ ] HTTPS está habilitado (veo el candado 🔒 en el navegador)
- [ ] Los logs no muestran errores críticos

---

## 📊 INFORMACIÓN DE MI DESPLIEGUE

**Anota esta información para referencia futura:**

### URLs:
- Frontend: _________________________________
- Backend: _________________________________

### MongoDB:
- Provider: [ ] MongoDB Atlas  [ ] Render Private Service
- Connection String: _________________________ (guárdalo seguro)

### Credenciales:
- Email admin: `admin@educando.com`
- Nueva contraseña: _________________ (la que creaste)

### Costos:
- Render Backend: $___/mes
- Render Frontend: $___/mes
- MongoDB: $___/mes
- **Total**: $___/mes

---

## 🆘 SI ALGO NO FUNCIONA

### Frontend no carga:
1. [ ] Verifiqué que el servicio esté "Live" en Render
2. [ ] Revisé los logs del frontend
3. [ ] Esperé 30 segundos (servicios gratuitos se "despiertan")

### Backend no responde:
1. [ ] Verifiqué que el servicio esté "Live"
2. [ ] Revisé la variable `MONGO_URL` en Environment
3. [ ] Verifiqué que MongoDB Atlas esté corriendo
4. [ ] Revisé los logs del backend

### No puedo conectarme a MongoDB:
1. [ ] Verifiqué la URL de conexión (sin espacios, con contraseña correcta)
2. [ ] Verifiqué que MongoDB Atlas permita conexiones desde `0.0.0.0/0`
3. [ ] Intenté crear un nuevo usuario en MongoDB Atlas
4. [ ] Verifiqué que el cluster esté "Active"

### Consultar Documentación:
- [ ] Leí [GUIA_RENDER.md](GUIA_RENDER.md) - Guía completa
- [ ] Leí [INICIO_RAPIDO_RENDER.md](INICIO_RAPIDO_RENDER.md) - Guía rápida
- [ ] Consulté https://render.com/docs
- [ ] Busqué en https://community.render.com/

---

## 🎉 ¡COMPLETADO!

**Fecha de despliegue**: _______________

**Tiempo total**: _______ minutos

**¿Todo funcionó?**: [ ] Sí [ ] Más o menos [ ] No

**Notas**:
_______________________________________________
_______________________________________________
_______________________________________________

---

## 📌 PARA IMPRIMIR

Imprime este checklist y márcalo mientras sigues los pasos.
Te ayudará a no olvidar ningún paso importante.

**¡Felicidades por desplegar tu aplicación!** 🎉

---

**¿Necesitas ayuda?**
- Revisa la sección "SI ALGO NO FUNCIONA" arriba
- Lee la documentación completa en [GUIA_RENDER.md](GUIA_RENDER.md)
- Consulta la comparación en [COMPARACION_RAILWAY_VS_RENDER.md](COMPARACION_RAILWAY_VS_RENDER.md)
