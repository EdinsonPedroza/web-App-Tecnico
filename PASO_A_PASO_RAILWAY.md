# 🚂 Paso a Paso: Subir a Railway (10 Minutos)

> 📌 **Tu estado actual (como en tu captura):** ya tienes `MongoDB` y un servicio `web-App-Tecnico`.
>
> Para que funcione esta app en Railway, debes dejar **3 servicios** en el mismo proyecto:
> 1) `MongoDB` (base de datos), 2) `backend` (FastAPI), 3) `frontend` (React).
>
> El servicio único `web-App-Tecnico` (raíz del repo) **no sirve para producción** en este proyecto porque solo muestra un mensaje y no levanta la app completa.

## La Forma MÁS FÁCIL - Sin Servidor, Sin Complicaciones

Railway es una plataforma que hace todo por ti. Solo necesitas:
- Una cuenta de GitHub (ya la tienes ✅)
- 10 minutos de tu tiempo
- Tarjeta de crédito/débito (para plan de pago, $10-20/mes según uso)

---

## 📍 PASO 1: Crear Cuenta en Railway

### 1.1 Ve a Railway
```
🌐 https://railway.app
```

### 1.2 Haz Clic en "Start a New Project"

### 1.3 Inicia Sesión con GitHub
- Verás un botón que dice **"Login with GitHub"**
- Haz clic en él
- Autoriza a Railway a acceder a tu cuenta de GitHub
- ✅ Listo, ya tienes cuenta

---

## 📍 PASO 2: Crear tu Proyecto

### 2.1 Click en "New Project"
En el dashboard de Railway, verás un botón grande que dice **"New Project"**.

### 2.2 Selecciona "Deploy from GitHub repo"
Railway te mostrará varias opciones. Elige **"Deploy from GitHub repo"**.

### 2.3 Conecta tu Repositorio
1. Busca: **"web-App-Tecnico"** o **"EdinsonPedroza/web-App-Tecnico"**
2. Si no aparece:
   - Haz clic en **"Configure GitHub App"**
   - Selecciona tu repositorio
   - Autoriza el acceso

### 2.4 Configuración correcta para este repositorio (Monorepo)
Este repo se despliega como **monorepo**:
- ⚙️ Un servicio con **Root Directory = `backend`**
- 🎨 Un servicio con **Root Directory = `frontend`**
- 🗄️ MongoDB como base de datos

Si te aparece un servicio raíz `web-App-Tecnico`, puedes conservarlo solo de referencia, pero lo recomendable es **eliminarlo** para evitar confusión.

---

## 📍 PASO 3: Configurar MongoDB

Tienes dos opciones: usar MongoDB Atlas (gratis, recomendado) o MongoDB de Railway.

### Opción A: Usar MongoDB Atlas (GRATIS - Recomendado) ⭐

MongoDB Atlas es la opción más confiable y tiene un plan gratuito permanente (512 MB).

#### 3A.1 — Crear Cuenta en MongoDB Atlas

1. Abre tu navegador y ve a:
   ```
   🌐 https://www.mongodb.com/cloud/atlas/register
   ```
2. Haz clic en **"Try Free"** (Probar Gratis)
3. Llena el formulario:
   - **Email:** tu correo
   - **First Name:** tu nombre
   - **Last Name:** tu apellido
   - **Password:** crea una contraseña segura
4. Haz clic en **"Create your Atlas account"**
5. Verifica tu email (te llega un correo, haz clic en el enlace)
6. ✅ ¡Cuenta creada!

#### 3A.2 — Crear un Cluster (Base de Datos)

Después de registrarte, Atlas te guía para crear tu primer cluster:

1. Selecciona **"M0 FREE"** (el plan gratuito)
   - Dice: **"Free forever"** — No te cobra nada
2. **Provider:** Selecciona **AWS** (Amazon Web Services)
3. **Region:** Selecciona la más cercana a ti, por ejemplo:
   - Si estás en Colombia: `us-east-1 (Virginia)` o `sa-east-1 (São Paulo)`
   - Si estás en México: `us-east-1 (Virginia)` o `us-west-2 (Oregon)`
   - Si estás en España: `eu-west-1 (Ireland)`
4. **Cluster Name:** Déjalo como está o ponle `EducandoCluster`
5. Haz clic en **"Create Deployment"** (o "Create Cluster")
6. ⏳ Espera 1-3 minutos mientras se crea
7. ✅ ¡Cluster listo!

#### 3A.3 — Crear un Usuario de Base de Datos

Atlas te pedirá crear un usuario para conectarte a la base de datos:

1. **Authentication Method:** Selecciona **"Username and Password"**
2. **Username:** escribe un nombre de usuario, por ejemplo:
   ```
   educando_user
   ```
3. **Password:** haz clic en **"Autogenerate Secure Password"**
   - ⚠️ **MUY IMPORTANTE:** Copia esta contraseña y guárdala en un lugar seguro (bloc de notas, etc.)
   - La vas a necesitar en el paso siguiente
   - Ejemplo de contraseña generada: `aB3xK9mPqR2wZ7n`
4. Haz clic en **"Create Database User"**
5. ✅ ¡Usuario creado!

> ⚠️ **NOTA:** Si la contraseña tiene caracteres especiales como `@`, `#`, `%`, `!`, etc., debes codificarlos en la URL (por ejemplo `@` se escribe como `%40`). Para evitar complicaciones, lo más fácil es generar una contraseña que solo tenga letras y números.

#### 3A.4 — Permitir Conexiones desde Cualquier IP (Whitelist)

Esto es **OBLIGATORIO** para que Railway pueda conectarse a tu base de datos:

1. En el menú izquierdo de Atlas, haz clic en **"Network Access"**
   - Si no lo ves, busca en **"Security"** → **"Network Access"**
2. Haz clic en el botón **"+ Add IP Address"** (verde)
3. Haz clic en **"ALLOW ACCESS FROM ANYWHERE"**
   - Esto pone automáticamente: `0.0.0.0/0`
   - Significa: cualquier servidor puede conectarse (necesario para Railway)
4. En el campo **"Comment"** (opcional) escribe: `Railway deployment`
5. Haz clic en **"Confirm"**
6. ⏳ Espera 1 minuto a que se active
7. ✅ ¡IP configurada!

> 💡 **¿Es seguro?** Sí, porque tu base de datos sigue protegida por el usuario y contraseña que creaste en el paso anterior. Solo quien tenga las credenciales puede acceder.

#### 3A.5 — Obtener la URL de Conexión (Connection String)

1. En el menú izquierdo de Atlas, haz clic en **"Database"** (o "Clusters")
2. Encuentra tu cluster y haz clic en **"Connect"**
3. Selecciona **"Drivers"** (o "Connect your application")
4. En **"Driver"** selecciona: **Python** versión **3.12 or later**
5. Verás una URL como esta:
   ```
   mongodb+srv://educando_user:<password>@educandocluster.abc123.mongodb.net/?retryWrites=true&w=majority&appName=EducandoCluster
   ```
6. **Copia esa URL completa**
7. Ahora **reemplaza `<password>`** con la contraseña real que guardaste en el paso 3A.3
   - Por ejemplo, si tu contraseña es `aB3xK9mPqR2wZ7n`, la URL queda:
   ```
   mongodb+srv://educando_user:aB3xK9mPqR2wZ7n@educandocluster.abc123.mongodb.net/?retryWrites=true&w=majority&appName=EducandoCluster
   ```
8. **Agrega el nombre de la base de datos** antes del `?`:
   ```
   mongodb+srv://educando_user:aB3xK9mPqR2wZ7n@educandocluster.abc123.mongodb.net/educando_db?retryWrites=true&w=majority&appName=EducandoCluster
   ```
9. ✅ **¡Esta es tu MONGO_URL!** Guárdala, la usarás en el Paso 4.

> ⚠️ **Errores comunes:**
> - ❌ Dejar `<password>` sin reemplazar — debes poner tu contraseña real
> - ❌ Poner espacios en la URL — no debe tener espacios
> - ❌ Olvidar agregar `/educando_db` — sin esto usa la base de datos por defecto
> - ❌ Usar contraseña con `@` o `#` — estos caracteres rompen la URL

#### 3A.6 — Verificar que Todo Está Bien en Atlas

Antes de continuar, verifica:
- [ ] ¿Creaste el cluster? (debe decir "Active" en verde)
- [ ] ¿Creaste el usuario de base de datos?
- [ ] ¿Guardaste la contraseña?
- [ ] ¿Agregaste `0.0.0.0/0` en Network Access?
- [ ] ¿Copiaste la URL de conexión y reemplazaste `<password>`?

Si todas son ✅, continúa al Paso 4.

---

### Opción B: Usar MongoDB de Railway

Si prefieres no crear una cuenta de Atlas, Railway puede crear un MongoDB por ti:

1. **Click en "+ New"** en tu proyecto de Railway
2. **Selecciona "Database"**
3. **Selecciona "MongoDB"**
4. Railway lo configura automáticamente y te da una `MONGO_URL`
5. Copia esa URL para usarla en el Paso 4
6. ✅ MongoDB listo

> **Nota:** MongoDB de Railway no tiene plan gratuito. Se cobra por uso.

---

## 📍 PASO 4: Crear y Configurar el Backend

### 4.0 Crear servicio Backend (si aún no existe)
1. Click en **+ Create**
2. **GitHub Repo** → selecciona `web-App-Tecnico`
3. Elige **Deploy from monorepo**
4. En **Root Directory** escribe: `backend`
5. Deploy

### 4.1 Haz Click en el Servicio "backend"

### 4.2 Ve a la Pestaña "Variables"

### 4.3 Agrega Estas Variables:

Haz clic en **"+ New Variable"** y agrega cada una:

**Variable 1 (OBLIGATORIA):**
```
Nombre: MONGO_URL
Valor:  <TU_URL_DE_MONGODB_ATLAS_DEL_PASO_3A.5>
```

Ejemplo completo:
```
MONGO_URL=mongodb+srv://educando_user:aB3xK9mPqR2wZ7n@educandocluster.abc123.mongodb.net/educando_db?retryWrites=true&w=majority&appName=EducandoCluster
```

> ⚠️ **SIN esta variable, el backend no podrá conectarse a la base de datos.**

**Variable 2:**
```
Nombre: DB_NAME
Valor:  educando_db
```

**Variable 3:**
```
Nombre: JWT_SECRET
Valor:  [GENERA UNA CLAVE SEGURA AQUÍ]
```

#### ¿Cómo Generar JWT_SECRET?

**Opción 1 - Fácil:**
Ve a: https://randomkeygen.com/
Copia cualquiera de las "CodeIgniter Encryption Keys"

**Opción 2 - Crear tu propia:**
Usa algo como: `mi_escuela_educando_2025_clave_super_secreta_12345678`
(Pero más largo y con caracteres especiales)

### 4.4 Guarda los Cambios
Haz clic en **"Save"** o las variables se guardan automáticamente.

---

## 📍 PASO 5: Crear y Configurar el Frontend

### 5.0 Crear servicio Frontend (si aún no existe)
1. Click en **+ Create**
2. **GitHub Repo** → selecciona `web-App-Tecnico`
3. Elige **Deploy from monorepo**
4. En **Root Directory** escribe: `frontend`
5. Deploy

### 5.1 Haz Click en el Servicio "frontend"

### 5.2 Ve a la Pestaña "Variables"

### 5.3 Agrega Esta Variable:

```
Nombre: REACT_APP_BACKEND_URL
Valor:  https://backend-production-XXXX.up.railway.app
```

**IMPORTANTE**: Necesitas la URL del backend primero.

#### ¿Cómo Obtener la URL del Backend?

1. Ve al servicio **"backend"**
2. Ve a **"Settings"** → **"Networking"**
3. Haz clic en **"Generate Domain"**
4. Railway te dará una URL como: `https://backend-production-a1b2.up.railway.app`
5. **Copia esa URL**
6. Vuelve al frontend
7. Pégala en `REACT_APP_BACKEND_URL`

---

## 📍 PASO 6: Generar Dominio para el Frontend

### 6.1 Ve al Servicio "frontend"

### 6.2 Ve a "Settings" → "Networking"

### 6.3 Click en "Generate Domain"

Railway te dará una URL pública como:
```
https://web-app-tecnico-production.up.railway.app
```

✅ ¡Esta es la URL de tu aplicación!

---

## 📍 PASO 7: Esperar el Deploy

### 7.1 Ver los Logs

1. Haz clic en cada servicio (MongoDB, Backend, Frontend)
2. Verás los logs de construcción en tiempo real
3. Espera a ver **"✓ Success"** o **"Deployed"**

### 7.2 Tiempo de Espera

- **MongoDB**: 1-2 minutos
- **Backend**: 5-7 minutos
- **Frontend**: 5-7 minutos

**Total**: ~10-15 minutos la primera vez

### 7.3 Verifica que Todo Esté "Active"

En tu dashboard de Railway deberías ver:
- 🟢 MongoDB: Active
- 🟢 Backend: Active
- 🟢 Frontend: Active

---

## 📍 PASO 8: ¡Visitar tu Aplicación!

### 8.1 Copia la URL del Frontend

La URL que obtuviste en el Paso 6, algo como:
```
https://web-app-tecnico-production.up.railway.app
```

### 8.2 Ábrela en tu Navegador

Pega la URL en tu navegador favorito.

### 8.3 ¡Tu Aplicación Está Viva! 🎉

Deberías ver la página de inicio de "Educando".

---

## 📍 PASO 9: Primer Inicio de Sesión

### 9.1 Haz Clic en "Iniciar Sesión"

### 9.2 Usa las Credenciales Iniciales:

```
Email:      admin@educando.com
Contraseña: admin123
```

### 9.3 ¡Bienvenido!

Ya estás dentro de tu plataforma educativa.

---

## 📍 PASO 10: Cambiar Contraseña (IMPORTANTE)

### ⚠️ MUY IMPORTANTE: Cambia la Contraseña Ahora

1. Ve a tu **Perfil** o **Configuración**
2. Busca **"Cambiar Contraseña"**
3. Ingresa:
   - Contraseña actual: `admin123`
   - Nueva contraseña: `[UNA MUY SEGURA]`
4. **Guarda los cambios**

#### Ejemplo de Contraseña Segura:
```
Educ@nd0-2025!Segur0*Mi$Escuela
```

Debe tener:
- Al menos 12 caracteres
- Mayúsculas y minúsculas
- Números
- Caracteres especiales (@, #, $, !, *, etc.)

---

## ✅ Verificación Final

### Prueba Estas Funciones:

- [ ] ¿Puedes iniciar sesión?
- [ ] ¿Puedes ver el dashboard?
- [ ] ¿Puedes crear un usuario nuevo?
- [ ] ¿Puedes crear un curso?
- [ ] ¿Funciona en tu celular?
- [ ] ¿Cambiaste la contraseña de admin?

Si todas tienen ✅, **¡FELICIDADES!** Tu aplicación está lista.

---

## 🎨 Personalizar el Dominio (Opcional)

Si quieres usar un dominio personalizado como `www.miescuela.com`:

### 1. Compra un Dominio

En cualquiera de estos sitios:
- **Namecheap**: https://www.namecheap.com (~$8-12/año)
- **GoDaddy**: https://www.godaddy.com (~$10-15/año)
- **Google Domains**: https://domains.google.com (~$12/año)

### 2. Conecta el Dominio a Railway

1. En Railway, ve al servicio **Frontend**
2. Ve a **Settings** → **Networking** → **Custom Domains**
3. Haz clic en **"Add Custom Domain"**
4. Ingresa tu dominio: `miescuela.com`
5. Railway te dará instrucciones de DNS

### 3. Configura DNS en tu Proveedor

En Namecheap, GoDaddy, etc.:

1. Ve a **DNS Management**
2. Agrega un registro **CNAME**:
   ```
   Tipo:  CNAME
   Host:  www (o @)
   Valor: [El que te dio Railway]
   TTL:   Automático
   ```
3. Guarda los cambios

### 4. Espera la Propagación

- Normalmente toma 10-30 minutos
- Puede tomar hasta 24 horas
- Verifica en: https://dnschecker.org/

### 5. ¡Listo!

Ahora puedes acceder a tu app con: `https://www.miescuela.com`

Railway configurará SSL/HTTPS automáticamente. 🔒

---

## 💰 Costos de Railway

### Plan Hobby (Para empezar):

```
Costo Base:    $5/mes (500 horas de ejecución)
Costo Real:    $10-20/mes según uso (promedio ~$15)
```

### ¿Qué Incluye?

- ✅ Hasta 500 horas de ejecución/mes
- ✅ SSL/HTTPS automático
- ✅ Dominios ilimitados
- ✅ Deploy automático desde GitHub
- ✅ Escalamiento automático
- ✅ Backups automáticos

### ¿Es Mucho?

Para una escuela pequeña-mediana (hasta 500 estudiantes):
- **$10-20/mes** (promedio $15) es un precio justo
- Es menos que una licencia de Zoom o Google Workspace
- No necesitas contratar administrador de sistemas

---

## 🆘 Problemas Comunes

### ❌ "Build Failed"

**Solución:**
1. Ve a los logs del servicio que falló
2. Lee el error (suele ser claro)
3. Generalmente es una variable de entorno mal configurada
4. Verifica que `JWT_SECRET`, `MONGO_URL` y `DB_NAME` estén bien

### ❌ "Service Not Found"

**Solución:**
1. Espera 1-2 minutos más
2. Los servicios tardan en iniciarse
3. Refresca la página del navegador

### ❌ No Puedo Iniciar Sesión

**Solución:**
1. Verifica las credenciales:
   - Email: `admin@educando.com` (exacto, con @educando.com)
   - Contraseña: `admin123` (todo minúsculas)
2. Espera 2 minutos después del deploy
3. Revisa los logs del backend

### ❌ Error 502 Bad Gateway

**Solución:**
1. El backend no está respondiendo
2. Ve a los logs del backend
3. Verifica que `MONGO_URL` esté correcta
4. Reinicia el servicio backend en Railway

### ❌ Error "bad auth : authentication failed"

Este error significa que la contraseña o usuario en tu `MONGO_URL` es incorrecto.

**Solución paso a paso:**
1. Ve a **MongoDB Atlas** → **Database Access** (menú izquierdo)
2. Encuentra tu usuario (ej: `educando_user`)
3. Haz clic en **"Edit"** (botón de lápiz)
4. Haz clic en **"Edit Password"**
5. Genera una nueva contraseña **sin caracteres especiales** (solo letras y números)
6. **Copia la nueva contraseña**
7. Haz clic en **"Update User"**
8. Ve a **Railway Dashboard** → **Backend Service** → **Variables**
9. Actualiza `MONGO_URL` reemplazando la contraseña vieja por la nueva
10. Railway re-desplegará automáticamente
11. Espera 2-3 minutos
12. ✅ ¡Listo!

**También verifica:**
- En MongoDB Atlas → **Network Access**: debe tener `0.0.0.0/0`
- La URL no debe tener `<password>` literal — reemplázalo por tu contraseña real
- No uses `mongodb://localhost:27017` en Railway — eso solo funciona en tu computadora

### ❌ La App No Carga

**Solución:**
1. Verifica que los 3 servicios estén "Active"
2. Verifica la URL del frontend
3. Abre las herramientas de desarrollador (F12)
4. Mira si hay errores en la consola

---

## 🔎 Verificación Rápida (Checklist para hacerlo "bien")

Cuando termines, valida en este orden:

1. **Servicios en verde**
   - MongoDB: Online
   - backend: Active/Healthy
   - frontend: Active/Healthy

2. **Dominios generados**
   - Backend con dominio público generado
   - Frontend con dominio público generado

3. **Variables correctas**
   - Backend: `MONGO_URL`, `DB_NAME`, `JWT_SECRET`
   - Frontend: `REACT_APP_BACKEND_URL` (apuntando al dominio del backend)

4. **Pruebas funcionales mínimas**
   - Abre URL frontend en incógnito
   - Inicia sesión
   - Navega al dashboard
   - Cierra sesión e inicia nuevamente

5. **Prueba técnica mínima**
   - Abre en navegador: `https://TU_BACKEND.up.railway.app/docs`
   - Debe cargar Swagger de FastAPI

---

## 📱 Compartir con Usuarios

### ¿Cómo Acceden los Usuarios?

**Es Simple:**

1. **Comparte la URL** de tu aplicación:
   ```
   https://tu-app.up.railway.app
   ```

2. **Los usuarios la abren** en cualquier navegador:
   - 💻 Computadora: Chrome, Firefox, Edge, Safari
   - 📱 Celular: Chrome, Safari, Samsung Internet
   - 📱 Tablet: Cualquier navegador

3. **Inician sesión** con sus credenciales

4. **¡Listo!** Ya pueden usar la plataforma

### No Necesitan:
- ❌ Instalar nada
- ❌ Descargar apps
- ❌ Configurar nada
- ❌ Conocimientos técnicos

### Solo Necesitan:
- ✅ Un dispositivo con internet
- ✅ Un navegador web
- ✅ Sus credenciales de acceso

---

## 🎯 Próximos Pasos

Ahora que tu aplicación está en línea:

### 1. Crea Usuarios de Prueba

- Crea 1-2 profesores
- Crea 1-2 estudiantes
- Prueba que todo funcione

### 2. Capacita a los Usuarios

- Muéstrales cómo iniciar sesión
- Explícales las funcionalidades básicas
- Comparte tutoriales o guías

### 3. Monitorea el Uso

- Revisa los logs de Railway
- Ve cuántos recursos usas
- Ajusta el plan si es necesario

### 4. Haz Backups Regulares

Railway hace backups automáticos, pero puedes:
- Exportar datos periódicamente
- Guardar copias locales
- Documentar cambios importantes

---

## 🎉 ¡FELICIDADES!

Tu plataforma educativa "Educando" está ahora:

- ✅ **Disponible en internet 24/7**
- ✅ **Accesible desde cualquier dispositivo**
- ✅ **Con SSL/HTTPS seguro**
- ✅ **Con deploy automático**
- ✅ **Lista para recibir usuarios**

---

## 📞 Soporte

### Si Necesitas Ayuda:

**Documentación de Railway:**
https://docs.railway.app/

**Discord de Railway:**
https://discord.gg/railway

**Esta Guía Completa:**
Ver archivo `DESPLIEGUE.md` en este repositorio

**Stack Overflow:**
https://stackoverflow.com/questions/tagged/railway

---

## 🚀 ¡Tu Escuela Virtual Ya Está en la Nube!

**URL de tu aplicación:**
```
https://tu-app.up.railway.app
```

**Credenciales admin:**
```
Email:      admin@educando.com
Contraseña: [LA QUE CAMBIASTE]
```

---

**¡Mucho éxito con tu plataforma educativa!** 📚✨🎓

**Tiempo total invertido:** ~15 minutos  
**Complejidad:** ⭐⭐ (Muy fácil)  
**¿Funcionó?** ✅ ¡Sí!  
