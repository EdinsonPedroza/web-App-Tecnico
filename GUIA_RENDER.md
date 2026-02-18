# 🚀 Guía Completa de Despliegue en Render.com

## 🎯 ¿Por qué Render.com?

Railway no funcionó, así que configuramos tu aplicación para **Render.com**, una plataforma confiable y fácil de usar.

### Ventajas de Render:
- ✅ **Muy fácil de usar** - Similar a Railway pero más estable
- ✅ **SSL/HTTPS automático** - Tu sitio será seguro desde el inicio
- ✅ **Deploy automático desde GitHub** - Cada vez que hagas push, se actualiza
- ✅ **Plan gratuito disponible** - Puedes empezar sin pagar
- ✅ **Infraestructura como código** - Todo configurado en `render.yaml`
- ✅ **Soporte excelente** - Documentación clara y comunidad activa

**Tiempo total**: 15-20 minutos  
**Costo**: Desde $0 (gratuito con limitaciones) hasta ~$14/mes (recomendado)

---

## 📋 Requisitos Previos

1. ✅ Cuenta de GitHub (ya la tienes)
2. ✅ Tu código en GitHub (ya está en `EdinsonPedroza/web-App-Tecnico`)
3. ✅ Una tarjeta de débito/crédito (solo para planes pagos, NO para el gratuito)

---

## 🚀 PASO 1: Crear Cuenta en Render

### 1.1 Ir a Render.com

1. **Abre tu navegador** y ve a: https://render.com
2. **Haz clic en "Get Started"** (en la esquina superior derecha)
3. **Selecciona "Sign up with GitHub"**

### 1.2 Autorizar Render

1. **GitHub te pedirá autorización** - Haz clic en "Authorize Render"
2. **Verifica tu email** si Render te lo pide
3. **¡Listo!** Ya tienes tu cuenta creada

---

## 🏗️ PASO 2: Conectar tu Repositorio

### 2.1 Conectar GitHub

1. **En el dashboard de Render**, haz clic en tu foto de perfil (arriba a la derecha)
2. **Selecciona "Account Settings"**
3. **Ve a la sección "GitHub"**
4. **Haz clic en "Connect Account"** si no está conectado
5. **Autoriza el acceso** a tus repositorios

### 2.2 Dar Acceso al Repositorio

1. **Haz clic en "Configure"** junto a tu cuenta de GitHub
2. **Selecciona "Only select repositories"**
3. **Busca y selecciona**: `EdinsonPedroza/web-App-Tecnico`
4. **Haz clic en "Save"**

---

## 🎨 PASO 3: Desplegar con Blueprint (Método Automático)

Render puede leer el archivo `render.yaml` y crear todos los servicios automáticamente.

### 3.1 Crear Blueprint

1. **Ve al Dashboard de Render**: https://dashboard.render.com/
2. **Haz clic en "New +"** (arriba a la derecha)
3. **Selecciona "Blueprint"**
4. **Conecta tu repositorio**: `EdinsonPedroza/web-App-Tecnico`
5. **Render detectará automáticamente** el archivo `render.yaml`
6. **Haz clic en "Apply"**

### 3.2 Render Creará Automáticamente:

- 🔧 **Backend API** (`educando-backend`)
- 🎨 **Frontend** (`educando-frontend`)

⚠️ **Importante**: MongoDB no se crea automáticamente. Lo configuraremos en el siguiente paso.

### 3.3 Esperar el Despliegue Inicial

1. **Render comenzará a construir** los servicios
2. **Verás el progreso** en tiempo real (logs)
3. **Por ahora los servicios fallarán** porque falta MongoDB
4. **No te preocupes**, lo arreglaremos en el siguiente paso

---

## 🗄️ PASO 4: Configurar MongoDB

Tienes 2 opciones para la base de datos. **Recomendamos la Opción 1** (más fácil):

### Opción 1: MongoDB Atlas (Recomendado - Gratis) ✅

MongoDB Atlas es el servicio en la nube de MongoDB, tiene un tier gratuito generoso.

#### 4.1 Crear Cuenta en MongoDB Atlas

1. **Ve a**: https://www.mongodb.com/cloud/atlas/register
2. **Crea una cuenta** (puedes usar Google o email)
3. **Selecciona el plan gratuito** (M0 Sandbox - Free forever)

#### 4.2 Crear un Cluster

1. **MongoDB te preguntará**: "¿Qué tipo de aplicación vas a construir?"
   - Selecciona cualquier opción (no importa)
2. **Selecciona el plan "M0 FREE"**
3. **Elige un proveedor y región**:
   - Provider: AWS
   - Region: Oregon (us-west-2) - Mismo que Render
4. **Nombre del cluster**: `educando-cluster` (o el que prefieras)
5. **Haz clic en "Create"**

#### 4.3 Configurar Acceso a la Base de Datos

1. **Crear un usuario de base de datos**:
   - Username: `educando_admin`
   - Password: Genera una contraseña segura (guárdala, la necesitarás)
   - Haz clic en "Create User"

2. **Configurar acceso desde cualquier IP**:
   - En "Where would you like to connect from?"
   - Haz clic en "Add IP Address"
   - Haz clic en "Allow Access from Anywhere"
   - IP: `0.0.0.0/0` (permitir todas las IPs)
   - Haz clic en "Add Entry"

3. **Haz clic en "Finish and Close"**

#### 4.4 Obtener la URL de Conexión

1. **En el dashboard de MongoDB Atlas**, haz clic en "Connect"
2. **Selecciona "Connect your application"**
3. **Copia la connection string**, se verá así:
   ```
   mongodb+srv://educando_admin:<password>@educando-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. **Reemplaza `<password>`** con la contraseña que creaste en el paso 4.3
5. **Guarda esta URL**, la necesitarás en el siguiente paso

#### 4.5 Configurar en Render

1. **Ve al Dashboard de Render**: https://dashboard.render.com
2. **Haz clic en el servicio "educando-backend"**
3. **Ve a "Environment"** en el menú izquierdo
4. **Busca la variable `MONGO_URL`**
5. **Pega la URL de MongoDB Atlas** que copiaste (con la contraseña reemplazada)
6. **Haz clic en "Save Changes"**
7. **Render desplegará automáticamente** el backend con la nueva configuración

### Opción 2: Private Service en Render (Más Complejo)

Si prefieres tener MongoDB dentro de Render:

1. **Ve al Dashboard de Render**
2. **Haz clic en "New +"** → "Private Service"
3. **Conecta tu repositorio**
4. **Configuración**:
   - Name: `educando-mongodb`
   - Environment: `Docker`
   - Dockerfile Path: `mongodb.Dockerfile`
   - Plan: `Standard` ($7/mes - Disk incluido)
5. **Agrega un disco persistente**:
   - Haz clic en "Add Disk"
   - Mount Path: `/data/db`
   - Size: 10 GB
6. **Haz clic en "Create Private Service"**
7. **Una vez que esté "Live"**, ve a "Connect"
8. **Copia la "Internal Connection String"**, algo como:
   ```
   mongodb://educando-mongodb:27017
   ```
9. **Configura en el backend**:
   - Ve al servicio "educando-backend"
   - Ve a "Environment"
   - Edita `MONGO_URL` con la URL interna de MongoDB
   - Guarda los cambios

---

## ⚙️ PASO 5: Verificar Variables de Entorno

El archivo `render.yaml` ya tiene la mayoría de variables configuradas. Verifica que todo esté correcto:

### 5.1 Backend

1. **Haz clic en el servicio "educando-backend"**
2. **Ve a "Environment"** en el menú izquierdo
3. **Verifica que existan estas variables**:
   ```
   MONGO_URL=<La URL de MongoDB Atlas o Private Service que configuraste>
   DB_NAME=educando_db
   JWT_SECRET=<Render lo genera automáticamente>
   PORT=10000
   ```

### 5.2 Frontend

1. **Haz clic en el servicio "educando-frontend"**
2. **Ve a "Environment"**
3. **Verifica que exista**:
   ```
   REACT_APP_BACKEND_URL=<URL del backend, Render lo configura automáticamente>
   ```
   
   Nota: El puerto para el frontend lo maneja automáticamente Render/nginx, no necesitas configurarlo.

Si `REACT_APP_BACKEND_URL` no existe o está vacía:
1. Ve al servicio "educando-backend"
2. Copia su URL pública (ej: `https://educando-backend.onrender.com`)
3. Vuelve al frontend → "Environment"
4. Agrega `REACT_APP_BACKEND_URL` con el valor de la URL del backend
5. Guarda los cambios

---

## 🌐 PASO 6: Obtener tu URL Pública

### 6.1 Encontrar la URL del Frontend

1. **Ve al Dashboard de Render**
2. **Haz clic en el servicio "educando-frontend"**
3. **En la parte superior verás la URL pública**, algo como:
   ```
   https://educando-frontend.onrender.com
   ```
4. **Copia esta URL** y ábrela en tu navegador

### 6.2 Primer Acceso

**Credenciales iniciales del administrador:**
- Email: `admin@educando.com`
- Contraseña: `admin123`

⚠️ **MUY IMPORTANTE**: Cambia esta contraseña inmediatamente después de tu primer inicio de sesión.

---

## 🎯 PASO 7: Configurar Dominio Personalizado (Opcional)

Si tienes un dominio propio (ej: `www.mieducando.com`):

### 7.1 En Render

1. **Ve al servicio "educando-frontend"**
2. **Haz clic en "Settings"** en el menú izquierdo
3. **Busca "Custom Domains"**
4. **Haz clic en "Add Custom Domain"**
5. **Ingresa tu dominio**: `www.mieducando.com`
6. **Render te dará instrucciones de DNS**

### 7.2 En tu Proveedor de Dominio

1. **Ve a tu proveedor de dominios** (GoDaddy, Namecheap, etc.)
2. **Busca la configuración de DNS**
3. **Agrega un registro CNAME**:
   - **Host**: `www`
   - **Value**: La URL que te dio Render (ej: `educando-frontend.onrender.com`)
4. **Guarda los cambios**
5. **Espera 10-30 minutos** para que se propague

---

## 💰 Planes y Costos

### Opción 1: Plan Gratuito (Para Probar)

**Costo**: $0/mes
**Incluye**:
- ✅ 750 horas/mes gratis para servicios web
- ⚠️ Los servicios se "duermen" después de 15 min de inactividad
- ⚠️ Pueden tardar 30 segundos en "despertar"
- ⚠️ No incluye base de datos MongoDB persistente

**Ideal para**: Pruebas, demos, proyectos personales

⚠️ **Nota sobre MongoDB**: El plan gratuito de Render no incluye bases de datos. Usa MongoDB Atlas (también gratis) como se explica en el PASO 4.

### Opción 2: Plan Starter (Recomendado)

**Costo**: ~$7/mes (Backend + Frontend en Starter)
**MongoDB**: Gratis con MongoDB Atlas M0, o $7/mes con Private Service en Render
**Total**: $7-14/mes

**Incluye**:
- ✅ Servicios siempre activos (no se duermen)
- ✅ SSL/HTTPS automático
- ✅ Deploy automático desde GitHub
- ✅ Logs completos
- ✅ Mejor rendimiento

**Ideal para**: Producción, aplicación real con usuarios

### Opción 3: Plan Standard

**Costo**: ~$25/mes (Backend + Frontend en Standard)
**MongoDB**: Gratis con MongoDB Atlas M0/M2, o incluido si usas Private Service

**Incluye**:
- ✅ Todo lo del plan Starter
- ✅ Más recursos de CPU y RAM
- ✅ Mejor rendimiento

**Ideal para**: Aplicación con muchos usuarios (100+)

---

## 🔧 Solución de Problemas Comunes

### Problema 1: Error "Failed to Build"

**Causa**: Error en la construcción del Docker

**Solución**:
1. Ve al servicio que falló
2. Haz clic en "Logs"
3. Lee el error (generalmente falta una dependencia)
4. Corrige el error en tu código local
5. Haz `git push` - Render desplegará automáticamente

### Problema 2: Frontend no se conecta al Backend

**Causa**: La variable `REACT_APP_BACKEND_URL` no está configurada correctamente

**Solución**:
1. Ve al servicio "educando-backend"
2. Copia la URL completa (ej: `https://educando-backend.onrender.com`)
3. Ve al servicio "educando-frontend"
4. Ve a "Environment"
5. Edita `REACT_APP_BACKEND_URL` y pega la URL del backend
6. **Importante**: Incluye `https://` al inicio
7. Haz clic en "Save Changes"
8. Render desplegará automáticamente con la nueva variable

### Problema 3: Base de Datos no se Conecta

**Causa**: MongoDB no está corriendo o la URL es incorrecta

**Solución**:
1. Ve al servicio "educando-mongodb"
2. Verifica que esté "Live" (activo)
3. Ve a "Connect"
4. Copia la "Internal Connection String"
5. Ve al servicio "educando-backend"
6. Ve a "Environment"
7. Edita `MONGO_URL` y pega la conexión interna
8. Guarda los cambios

### Problema 4: Servicio se Queda en "Deploying"

**Causa**: El build está tomando más tiempo del esperado

**Solución**:
1. Espera 15-20 minutos (la primera vez puede ser lento)
2. Si después de 30 minutos sigue igual:
   - Ve a "Logs"
   - Busca errores
   - Si ves un error, corrígelo en tu código
   - Haz `git push` para reintentar

### Problema 5: Error 502 Bad Gateway

**Causa**: El backend no responde correctamente

**Solución**:
1. Ve al servicio "educando-backend"
2. Ve a "Logs"
3. Busca errores de Python
4. Verifica que la aplicación esté escuchando en el puerto correcto
5. Verifica la variable de entorno `PORT=8001`

---

## 📊 Monitoreo y Mantenimiento

### Ver Logs en Tiempo Real

1. **Ve al Dashboard de Render**
2. **Haz clic en el servicio** que quieres monitorear
3. **Haz clic en "Logs"** en el menú izquierdo
4. **Verás los logs en tiempo real**

### Reiniciar un Servicio

1. **Ve al servicio**
2. **Haz clic en "Manual Deploy"** (arriba a la derecha)
3. **Selecciona "Clear build cache & deploy"**
4. **Espera a que se complete**

### Actualizar tu Aplicación

**Es automático con Render:**
1. Haz cambios en tu código local
2. Ejecuta:
   ```bash
   git add .
   git commit -m "Descripción de los cambios"
   git push
   ```
3. Render detectará el push automáticamente
4. Desplegará los cambios en 5-10 minutos

---

## 📈 Escalar tu Aplicación

Cuando tu aplicación crezca y tengas más usuarios:

### Aumentar Recursos

1. **Ve al servicio** (backend o frontend)
2. **Haz clic en "Settings"**
3. **Busca "Instance Type"**
4. **Selecciona un plan superior**:
   - Starter: $7/mes por servicio
   - Standard: $25/mes por servicio
   - Pro: $85/mes por servicio

### Aumentar Almacenamiento de MongoDB

1. **Ve al servicio "educando-mongodb"**
2. **Haz clic en "Settings"**
3. **Busca "Disk Size"**
4. **Aumenta el tamaño** según necesites:
   - 1GB: Incluido en plan Starter
   - 10GB: Plan Standard
   - Más: Planes superiores

---

## 🔐 Seguridad y Mejores Prácticas

### 1. Cambiar Credenciales por Defecto

⚠️ **MUY IMPORTANTE**: Después del primer inicio de sesión:
1. Inicia sesión con `admin@educando.com` / `admin123`
2. Ve a tu perfil
3. Cambia la contraseña inmediatamente
4. Usa una contraseña fuerte (12+ caracteres, mayúsculas, minúsculas, números, símbolos)

### 2. Configurar Variables Secretas

Nunca incluyas secretos en el código:
- ✅ `JWT_SECRET`: Render lo genera automáticamente (seguro)
- ✅ `MONGO_URL`: Se configura vía variables de entorno
- ❌ NO incluyas contraseñas en el código fuente

### 3. Habilitar HTTPS

Render lo hace automáticamente, pero verifica:
1. Tu URL debe empezar con `https://`
2. Verás un candado 🔒 en el navegador
3. Si no lo ves, ve a "Settings" → "HTTPS" y verifica que esté habilitado

### 4. Backups de Base de Datos

**Importante para producción:**
1. Ve a "educando-mongodb"
2. Haz clic en "Backups" (si está disponible en tu plan)
3. Configura backups automáticos
4. O manualmente exporta tu base de datos periódicamente

### 5. Limitar Acceso

1. Ve a "educando-backend"
2. Ve a "Settings" → "Environment"
3. Agrega `ALLOWED_ORIGINS` con la URL de tu frontend
4. Esto previene acceso no autorizado a tu API

---

## 📚 Recursos Adicionales

### Documentación Oficial
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/

### Comunidad y Soporte
- **Render Community**: https://community.render.com/
- **Render Status**: https://status.render.com/ (para verificar si hay problemas)
- **Soporte de Render**: support@render.com

### Tutoriales en Video
- YouTube: "How to deploy to Render"
- YouTube: "Render.com tutorial español"

---

## ✅ Checklist Post-Despliegue

Usa este checklist para verificar que todo quedó perfecto:

- [ ] ✅ Los 3 servicios están "Live" en Render
- [ ] ✅ Puedo acceder al frontend en la URL pública
- [ ] ✅ Puedo iniciar sesión con las credenciales por defecto
- [ ] ✅ Cambié la contraseña del administrador
- [ ] ✅ El frontend se conecta correctamente al backend
- [ ] ✅ Puedo crear un usuario de prueba
- [ ] ✅ Puedo subir archivos (si aplica)
- [ ] ✅ La URL usa HTTPS (candado 🔒)
- [ ] ✅ Los logs no muestran errores críticos
- [ ] ✅ Configure backups de la base de datos (recomendado)

---

## 🎉 ¡Felicidades!

Tu aplicación **Educando** ya está desplegada en Render y disponible en internet.

**Próximos pasos:**
1. Comparte la URL con tus usuarios
2. Monitorea los logs regularmente
3. Considera configurar un dominio personalizado
4. Cuando tengas más usuarios, considera escalar a un plan superior

**¿Necesitas ayuda?**
- Revisa la sección de "Solución de Problemas" en esta guía
- Consulta la documentación oficial de Render
- Contacta al soporte de Render

---

## 🔄 Comparación: Railway vs Render

| Característica | Railway | Render |
|----------------|---------|--------|
| **Facilidad de uso** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ |
| **Estabilidad** | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐ |
| **Documentación** | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐ |
| **Precio** | ~$15/mes | ~$14/mes |
| **Plan gratuito** | Limitado | Sí, con limitaciones |
| **HTTPS automático** | ✅ | ✅ |
| **Deploy desde GitHub** | ✅ | ✅ |
| **Soporte** | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐☆ |

**Conclusión**: Render es más estable y tiene mejor documentación, aunque Railway es un poco más fácil de usar.

---

¿Necesitas configurar para otra plataforma? Otras opciones:
- **Vercel** (solo frontend estático)
- **Heroku** (fácil pero más caro)
- **DigitalOcean App Platform** (balance entre precio y facilidad)
- **AWS/GCP/Azure** (más complejo pero más poderoso)
