# Guía de Despliegue - Escuela Virtual Educando

Esta guía te explica cómo subir tu aplicación a internet de forma profesional y optimizada.

## 📦 Estado de Optimización

✅ **La aplicación ya está optimizada para producción:**
- Frontend usa build optimizado de React con minificación
- Nginx sirve archivos estáticos comprimidos
- Backend usa FastAPI (uno de los frameworks más rápidos)
- MongoDB con índices eficientes
- Multi-stage Docker builds (reduce tamaño de imágenes)
- Tamaño total del proyecto: ~7.4MB (sin node_modules)

**No se requieren optimizaciones adicionales antes del despliegue.**

## Opción 1: Servidor VPS (Recomendado para Control Total)

**Ideal para:** Instituciones que quieren control total, mejor rendimiento y precios predecibles.

### Proveedores económicos:
- **DigitalOcean** - Desde $6/mes (https://www.digitalocean.com/)
- **Vultr** - Desde $6/mes (https://www.vultr.com/)
- **Hetzner** - Desde $4/mes (https://www.hetzner.com/) - Mejor precio/rendimiento
- **Linode (Akamai)** - Desde $5/mes (https://www.linode.com/)
- **Contabo** - Desde $4/mes (https://contabo.com/) - Muy económico

### Requisitos mínimos del servidor:
- **CPU:** 1 vCore
- **RAM:** 2GB (mínimo 1GB, pero 2GB es recomendado)
- **Disco:** 25GB SSD
- **Sistema:** Ubuntu 22.04 LTS o Ubuntu 24.04 LTS
- **Ancho de banda:** 1TB/mes (suficiente para ~500-1000 usuarios activos)

### Pasos de instalación:

#### 1. Crear un servidor
- Elige Ubuntu 22.04 LTS
- Mínimo 1GB RAM, 25GB disco
- Anota la IP del servidor

#### 2. Conectarte al servidor
```bash
ssh root@TU_IP_DEL_SERVIDOR
```

#### 3. Instalar Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

#### 4. Instalar Docker Compose
```bash
apt install docker-compose -y
```

#### 5. Subir tu código

**Opción A - Desde GitHub (Recomendado):**
```bash
cd /root
git clone https://github.com/EdinsonPedroza/web-App-Tecnico.git educando
cd educando
```

**Opción B - Desde tu computadora local:**
```bash
# En tu computadora (no en el servidor)
cd /ruta/donde/esta/tu/proyecto
tar czf educando.tar.gz --exclude=node_modules --exclude=.git .
scp educando.tar.gz root@TU_IP:/root/

# Luego en el servidor
cd /root
mkdir educando
cd educando
tar xzf ../educando.tar.gz
rm ../educando.tar.gz  # Limpia el archivo comprimido
```

#### 6. Configurar variables de entorno
```bash
cd /root/educando
cp .env.example .env
nano .env
```

Configura:
```
DOMAIN_URL=http://TU_IP_DEL_SERVIDOR
JWT_SECRET=una_clave_muy_segura_y_larga_12345
```

#### 7. Iniciar la aplicación
```bash
docker-compose up -d --build
```

**Nota:** El primer build tomará 5-10 minutos. Los siguientes serán más rápidos.

#### 8. Verificar que todo funciona
```bash
# Ver el estado de los contenedores
docker-compose ps

# Ver los logs
docker-compose logs -f

# Verificar que el frontend responde
curl http://localhost

# Verificar que el backend responde
curl http://localhost/api/health || curl http://localhost:8001/health
```

#### 9. ¡Listo!
Visita `http://TU_IP_DEL_SERVIDOR` en tu navegador.

**Credenciales iniciales:**
Consulta el archivo `USUARIOS_Y_CONTRASEÑAS.txt` para las credenciales completas del sistema.

Ejemplo de credenciales de administrador:
- Email: `laura.torres@educando.com`
- Contraseña: Ver USUARIOS_Y_CONTRASEÑAS.txt

⚠️ **IMPORTANTE:** En producción, cambia todas las contraseñas inmediatamente después del primer acceso.

---

## Opción 2: Railway (Más fácil, sin necesidad de servidor)

**Ideal para:** Desarrollo rápido, pruebas o instituciones pequeñas que no quieren administrar servidores.

### Ventajas:
- ✅ Deploy automático desde GitHub
- ✅ Configuración en minutos
- ✅ Plan gratuito disponible (limitado)
- ✅ SSL incluido
- ⚠️ Puede ser más caro a largo plazo ($5-20/mes según uso)

### Pasos:

1. **Prepara tu repositorio en GitHub**
   - Tu código debe estar en GitHub
   - Asegúrate de tener el `docker-compose.yml` en la raíz

2. **Crea cuenta en Railway**
   - Ve a [railway.app](https://railway.app)
   - Crea una cuenta con GitHub
   - Verifica tu correo

3. **Crea un nuevo proyecto**
   - Haz clic en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Autoriza a Railway a acceder a tu repositorio
   - Selecciona el repositorio `web-App-Tecnico`

4. **Railway detectará automáticamente:**
   - El `docker-compose.yml`
   - Los servicios (frontend, backend, mongodb)
   - Las variables de entorno necesarias

5. **Configura las variables de entorno**
   - En el dashboard de Railway, ve a cada servicio
   - Backend necesita:
     ```
     MONGO_URL=mongodb://mongodb:27017
     DB_NAME=educando_db
     JWT_SECRET=tu_clave_secreta_aqui_muy_larga_y_segura
     ```
   - Frontend automáticamente detecta el backend

6. **Deploy automático**
   - Railway construirá y desplegará automáticamente
   - Te dará URLs automáticas para cada servicio
   - Ejemplo: `https://tu-app.up.railway.app`

7. **¡Listo!**
   - Visita la URL que te dio Railway
   - Usa las credenciales del archivo USUARIOS_Y_CONTRASEÑAS.txt (por ejemplo: laura.torres@educando.com)

**Costos estimados en Railway:**
- Plan gratuito: $5 de crédito gratis/mes (suficiente para pruebas)
- Plan de pago: ~$10-20/mes según uso

---

## Opción 3: Render (También fácil y confiable)

**Ideal para:** Similar a Railway, pero con mejor plan gratuito para bases de datos.

### Ventajas:
- ✅ Plan gratuito más generoso
- ✅ SSL incluido
- ✅ Deploy automático
- ⚠️ Los servicios gratuitos "duermen" después de inactividad

### Pasos:

1. **Crea cuenta en Render**
   - Ve a [render.com](https://render.com)
   - Crea una cuenta con GitHub

2. **Crea 3 servicios separados:**

   **a) MongoDB:**
   - Click en "New +" > "MongoDB"
   - Nombre: `educando-db`
   - Plan: Free (256MB) o Starter ($7/mes)
   - Copia la "Internal Connection String"

   **b) Backend:**
   - Click en "New +" > "Web Service"
   - Conecta tu repositorio
   - Configuración:
     - Name: `educando-backend`
     - Root Directory: `backend`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn server:app --host 0.0.0.0 --port 8001`
     - Plan: Free o Starter ($7/mes)
   - Variables de entorno:
     ```
     MONGO_URL=<la connection string de MongoDB>
     DB_NAME=educando_db
     JWT_SECRET=tu_clave_secreta_muy_larga
     ```

   **c) Frontend:**
   - Click en "New +" > "Static Site"
   - Conecta tu repositorio
   - Configuración:
     - Name: `educando-frontend`
     - Root Directory: `frontend`
     - Build Command: `yarn install && yarn build`
     - Publish Directory: `build`
     - Plan: Free
   - Variables de entorno:
     ```
     REACT_APP_BACKEND_URL=<URL del backend>
     ```

3. **¡Listo!**
   - Render construirá y desplegará todo automáticamente
   - Visita la URL del frontend
   - Usa las credenciales iniciales

**Costos estimados en Render:**
- Plan gratuito: $0 (con limitaciones)
- Plan básico: ~$7-14/mes (más confiable)

---

## 📊 Comparación de Opciones

| Característica | VPS (Opción 1) | Railway (Opción 2) | Render (Opción 3) |
|----------------|----------------|-------------------|-------------------|
| **Dificultad** | Media | Fácil | Fácil |
| **Costo mensual** | $4-10 | $10-20 | $0-14 |
| **Control total** | ✅ Sí | ❌ No | ❌ No |
| **Mantenimiento** | Tú lo haces | Automático | Automático |
| **Escalabilidad** | Manual | Automática | Automática |
| **SSL/HTTPS** | Manual (gratis) | ✅ Incluido | ✅ Incluido |
| **Plan gratuito** | ❌ No | ⚠️ $5 crédito | ✅ Limitado |
| **Ideal para** | Producción seria | Pruebas/Desarrollo | Inicio/Pruebas |

### Recomendación:
- **¿Primera vez?** → Railway o Render (más fácil)
- **¿Uso en producción?** → VPS (mejor costo/beneficio a largo plazo)
- **¿Solo para probar?** → Render (plan gratuito)

---

## Configurar un Dominio Personalizado (Opcional pero Recomendado)

### ¿Por qué usar un dominio propio?
- Más profesional (`educando.com` vs `123.45.67.89`)
- Facilita recordar la dirección
- Permite agregar HTTPS fácilmente

### Comprar dominio:
- **Namecheap** - Desde $8/año (https://www.namecheap.com/) - Recomendado
- **Porkbun** - Desde $7/año (https://porkbun.com/) - Más barato
- **Google Domains** - Desde $12/año (https://domains.google/)
- **GoDaddy** - Desde $10/año (https://www.godaddy.com/)

### Configurar DNS (Para VPS):

1. **Obtén la IP de tu servidor**
   ```bash
   # Si estás dentro del servidor
   curl ifconfig.me
   ```

2. **Ve a tu proveedor de dominio**
   - Busca la sección "DNS Management" o "DNS Settings"

3. **Agrega un registro tipo A:**
   ```
   Tipo: A
   Nombre: @ (o vacío, o tu dominio)
   Valor: LA_IP_DE_TU_SERVIDOR
   TTL: 3600 (o automático)
   ```

4. **Opcional - Agrega www:**
   ```
   Tipo: CNAME
   Nombre: www
   Valor: tudominio.com
   TTL: 3600
   ```

5. **Espera la propagación**
   - Normalmente toma 5-30 minutos
   - Puede tomar hasta 24 horas
   - Verifica en: https://dnschecker.org/

### Configurar DNS (Para Railway/Render):

1. En el dashboard de Railway/Render:
   - Ve a Settings > Domains
   - Haz clic en "Add Custom Domain"
   - Ingresa tu dominio

2. Te darán instrucciones específicas con valores CNAME

3. Agrega el CNAME en tu proveedor de dominios

4. Railway/Render configurará SSL automáticamente

### Agregar HTTPS (SSL) gratuito con Let's Encrypt (Solo para VPS):

**¿Por qué HTTPS?**
- Seguridad: Los datos viajan encriptados
- Confianza: Los navegadores muestran el candado verde
- SEO: Google favorece sitios HTTPS
- Obligatorio: Para usar ciertas APIs del navegador

**Pasos:**

1. **Instala Certbot:**
   ```bash
   apt update
   apt install certbot python3-certbot-nginx -y
   ```

2. **Actualiza nginx.conf para usar tu dominio:**
   ```bash
   cd /root/educando/frontend
   nano nginx.conf
   ```
   
   Cambia `server_name localhost;` por:
   ```nginx
   server_name tudominio.com www.tudominio.com;
   ```

3. **Reconstruye el contenedor:**
   ```bash
   cd /root/educando
   docker-compose down
   docker-compose up -d --build
   ```

4. **Obtén el certificado SSL:**
   ```bash
   # Instala nginx temporalmente en el servidor (no en Docker)
   apt install nginx -y
   
   # Detén el contenedor frontend temporalmente
   docker stop educando_frontend
   
   # Obtén el certificado
   certbot --nginx -d tudominio.com -d www.tudominio.com
   
   # Sigue las instrucciones en pantalla:
   # - Ingresa tu email
   # - Acepta los términos
   # - Elige redireccionar HTTP a HTTPS (opción 2)
   
   # Copia los certificados al proyecto
   mkdir -p /root/educando/ssl
   cp /etc/letsencrypt/live/tudominio.com/fullchain.pem /root/educando/ssl/
   cp /etc/letsencrypt/live/tudominio.com/privkey.pem /root/educando/ssl/
   
   # Detén nginx del servidor
   systemctl stop nginx
   systemctl disable nginx
   
   # Reinicia el contenedor frontend
   docker start educando_frontend
   ```

5. **Actualiza nginx.conf para SSL:**
   ```nginx
   server {
       listen 80;
       server_name tudominio.com www.tudominio.com;
       return 301 https://$server_name$request_uri;
   }
   
   server {
       listen 443 ssl;
       server_name tudominio.com www.tudominio.com;
       
       ssl_certificate /etc/nginx/ssl/fullchain.pem;
       ssl_certificate_key /etc/nginx/ssl/privkey.pem;
       
       root /usr/share/nginx/html;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://backend:8001;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_cache_bypass $http_upgrade;
           client_max_body_size 50M;
       }
   }
   ```

6. **Actualiza docker-compose.yml:**
   ```yaml
   frontend:
     build:
       context: ./frontend
     container_name: educando_frontend
     restart: always
     depends_on:
       - backend
     ports:
       - "80:80"
       - "443:443"
     volumes:
       - ./ssl:/etc/nginx/ssl:ro
   ```

7. **Reconstruye y reinicia:**
   ```bash
   docker-compose up -d --build
   ```

8. **Configura renovación automática:**
   ```bash
   # El certificado expira cada 90 días
   # Configura cron para renovarlo automáticamente
   crontab -e
   
   # Agrega esta línea:
   0 3 * * * certbot renew --quiet && cp /etc/letsencrypt/live/tudominio.com/fullchain.pem /root/educando/ssl/ && cp /etc/letsencrypt/live/tudominio.com/privkey.pem /root/educando/ssl/ && docker restart educando_frontend
   ```

9. **¡Listo!**
   - Visita `https://tudominio.com`
   - Deberías ver el candado verde

**Nota:** Railway y Render configuran SSL automáticamente, no necesitas hacer esto.

---

## 🔒 Crear los Datos Iniciales y Seguridad

### El sistema crea automáticamente:
Cuando inicias la aplicación por primera vez, se crean automáticamente:
- ✅ Usuario admin
- ✅ Programas de estudio
- ✅ Materias
- ✅ Cursos de ejemplo

**Credenciales iniciales del administrador:**

Consulta el archivo `USUARIOS_Y_CONTRASEÑAS.txt` en la raíz del proyecto para todas las credenciales.

Ejemplo de credenciales de administrador:
- Email: `laura.torres@educando.com`
- Contraseña: Ver USUARIOS_Y_CONTRASEÑAS.txt

### ⚠️ IMPORTANTE - Cambiar credenciales de admin:

**Después del primer deploy, DEBES:**

1. **Inicia sesión como admin**
   - Ve a tu sitio web
   - Inicia sesión con las credenciales del archivo USUARIOS_Y_CONTRASEÑAS.txt

2. **Cambia la contraseña inmediatamente**
   - Ve a tu perfil o configuración
   - Cambia la contraseña a una segura
   - Usa al menos 12 caracteres
   - Incluye mayúsculas, minúsculas, números y símbolos
   - Ejemplo: `Educ@nd0*2025!Segur0`

3. **Opcional - Cambia el email del admin:**
   ```bash
   # Conéctate al contenedor del backend
   docker exec -it educando_backend bash
   
   # Abre Python
   python3
   
   # Ejecuta este código:
   import asyncio
   from motor.motor_asyncio import AsyncIOMotorClient
   from passlib.context import CryptContext
   import os
   
   pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
   
   async def update_admin():
       client = AsyncIOMotorClient(os.environ['MONGO_URL'])
       db = client[os.environ.get('DB_NAME', 'educando_db')]
       
       # Actualiza email y contraseña
       new_email = "tuemail@tudominio.com"
       new_password = "TuContraseñaSuperSegura123!"
       password_hash = pwd_context.hash(new_password)
       
       result = await db.users.update_one(
           {"role": "admin"},
           {"$set": {
               "email": new_email,
               "password_hash": password_hash
           }}
       )
       print(f"Admin actualizado: {result.modified_count} documento(s)")
       print(f"Nuevo email: {new_email}")
       print("Usa la nueva contraseña para iniciar sesión")
   
   asyncio.run(update_admin())
   exit()
   
   # Sal del contenedor
   exit
   ```

### Crear usuarios adicionales:

**Desde la interfaz web (Recomendado):**
1. Inicia sesión como admin
2. Ve a la sección correspondiente (Profesores, Estudiantes, etc.)
3. Haz clic en "Nuevo" y llena el formulario

**Desde la línea de comandos:**
```bash
# Solo si necesitas crear usuarios mediante scripts
docker exec -it educando_backend python3 create_user_script.py
```

---

## 🛠️ Comandos Útiles para Administración

### Gestión de contenedores:

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f mongodb

# Ver estado de contenedores
docker-compose ps

# Reiniciar todos los servicios
docker-compose restart

# Reiniciar un servicio específico
docker-compose restart backend

# Detener todo
docker-compose down

# Detener y eliminar volúmenes (⚠️ BORRA LA BASE DE DATOS)
docker-compose down -v

# Actualizar después de cambios en el código
git pull  # Si usas GitHub
docker-compose up -d --build

# Ver uso de recursos
docker stats
```

### Entrar a los contenedores:

```bash
# Entrar al contenedor del backend
docker exec -it educando_backend bash

# Entrar al contenedor del frontend
docker exec -it educando_frontend sh

# Entrar a MongoDB
docker exec -it educando_mongodb mongosh
```

### Backup de la base de datos:

```bash
# Crear backup
docker exec educando_mongodb mongodump --out /backup
docker cp educando_mongodb:/backup ./backup_$(date +%Y%m%d)

# Restaurar backup
docker cp ./backup_20240115 educando_mongodb:/backup
docker exec educando_mongodb mongorestore /backup
```

### Backup automático (cron):

```bash
# Edita el crontab
crontab -e

# Agrega esta línea para backup diario a las 3 AM
0 3 * * * docker exec educando_mongodb mongodump --out /backup && docker cp educando_mongodb:/backup /root/backups/backup_$(date +\%Y\%m\%d)

# Agrega esta línea para limpiar backups antiguos (más de 30 días)
0 4 * * * find /root/backups -name "backup_*" -type d -mtime +30 -exec rm -rf {} \;
```

### Monitoreo:

```bash
# Ver logs de errores
docker-compose logs --tail=100 | grep -i error

# Ver uso de disco
df -h

# Ver uso de memoria
free -h

# Ver procesos de Docker
docker ps
```

---

## 🐛 Solución de Problemas Comunes

### La página no carga

**Síntomas:** No puedes acceder a `http://TU_IP`

**Soluciones:**
```bash
# 1. Verifica que los contenedores estén corriendo
docker-compose ps
# Deberían aparecer 3 contenedores: frontend, backend, mongodb

# 2. Verifica los logs
docker-compose logs frontend
docker-compose logs backend

# 3. Verifica el puerto 80
netstat -tulpn | grep :80
# O en sistemas sin netstat:
ss -tulpn | grep :80

# 4. Verifica el firewall (en Ubuntu/Debian)
ufw status
# Si está activo, permite el puerto 80:
ufw allow 80/tcp
ufw allow 443/tcp

# 5. Reinicia todo
docker-compose down
docker-compose up -d --build
```

### Error de conexión a MongoDB

**Síntomas:** Backend muestra errores de conexión a la base de datos

**Soluciones:**
```bash
# 1. Verifica que MongoDB esté corriendo
docker-compose logs mongodb

# 2. Verifica la conexión desde el backend
docker exec -it educando_backend bash
ping mongodb

# 3. Reinicia MongoDB
docker-compose restart mongodb

# 4. Si nada funciona, elimina y recrea los volúmenes
docker-compose down -v
docker-compose up -d --build
# ⚠️ Esto eliminará todos los datos, úsalo solo si tienes backup
```

### Los archivos no se suben

**Síntomas:** No se pueden subir videos, actividades o archivos

**Soluciones:**
```bash
# 1. Verifica que el volumen de uploads exista
docker volume ls | grep uploads

# 2. Verifica permisos
docker exec -it educando_backend ls -la /app/uploads
docker exec -it educando_backend chmod 777 /app/uploads

# 3. Verifica el tamaño máximo en nginx
# Ya está configurado para 50MB, pero puedes aumentarlo
nano /root/educando/frontend/nginx.conf
# Busca: client_max_body_size 50M;
# Cambia a: client_max_body_size 100M;
docker-compose restart frontend
```

### Error "port already in use"

**Síntomas:** El puerto 80 o 8001 ya está siendo usado

**Soluciones:**
```bash
# 1. Ver qué está usando el puerto
lsof -i :80
# O:
netstat -tulpn | grep :80

# 2. Detener el proceso
kill -9 PID_DEL_PROCESO

# 3. O cambia el puerto en docker-compose.yml
nano docker-compose.yml
# Cambia:
ports:
  - "8080:80"  # Usa puerto 8080 en lugar de 80
```

### El sitio es muy lento

**Síntomas:** La aplicación tarda mucho en cargar

**Soluciones:**
```bash
# 1. Verifica recursos del servidor
htop
# O:
top

# 2. Verifica el uso de Docker
docker stats

# 3. Aumenta memoria del servidor (en tu proveedor VPS)
# O:
# 4. Optimiza MongoDB agregando índices
docker exec -it educando_mongodb mongosh
use educando_db
db.users.createIndex({"email": 1})
db.courses.createIndex({"program_id": 1})
exit
```

### No puedo iniciar sesión como admin

**Síntomas:** Las credenciales de admin no funcionan

**Soluciones:**
```bash
# 1. Verifica que exista el usuario admin
docker exec -it educando_mongodb mongosh
use educando_db
db.users.findOne({role: "admin"})
exit

# 2. Si no existe, el startup del backend lo creará
docker-compose restart backend
docker-compose logs -f backend
# Espera a que veas "Application startup complete"

# 3. Si las credenciales fueron cambiadas, resetéalas
# Ver sección "Crear los Datos Iniciales y Seguridad"
```

### Error después de actualizar el código

**Síntomas:** Después de hacer `git pull`, algo no funciona

**Soluciones:**
```bash
# 1. Reconstruye completamente
docker-compose down
docker-compose up -d --build

# 2. Si aún hay problemas, elimina imágenes antiguas
docker-compose down
docker image prune -a
docker-compose up -d --build

# 3. Verifica que no haya cambios en requirements.txt o package.json
docker-compose logs backend
docker-compose logs frontend
```

### Certificado SSL expirado

**Síntomas:** Navegador muestra "certificado no válido"

**Soluciones:**
```bash
# Los certificados Let's Encrypt expiran cada 90 días
# 1. Renueva el certificado
certbot renew

# 2. Copia los nuevos certificados
cp /etc/letsencrypt/live/tudominio.com/fullchain.pem /root/educando/ssl/
cp /etc/letsencrypt/live/tudominio.com/privkey.pem /root/educando/ssl/

# 3. Reinicia el frontend
docker-compose restart frontend
```

---

## 💰 Costos Estimados Detallados

### Opción 1: VPS (Control Total)

| Componente | Proveedor | Costo Mensual | Costo Anual |
|------------|-----------|---------------|-------------|
| Servidor VPS 2GB | Hetzner/Contabo | $4-5 | $48-60 |
| Dominio | Namecheap | ~$0.70 | $8-10 |
| SSL | Let's Encrypt | Gratis | Gratis |
| Backup (opcional) | Proveedor VPS | $1-2 | $12-24 |
| **Total** | | **$6-8/mes** | **$68-94/año** |

**Capacidad estimada:**
- 500-1000 usuarios activos simultáneos
- 50-100GB de archivos subidos
- Suficiente para una institución pequeña-mediana

### Opción 2: Railway

| Componente | Costo |
|------------|-------|
| Plan Hobby | $5 crédito gratis/mes |
| Uso típico | $10-20/mes |
| SSL | Incluido |
| Dominio custom | Incluido |

### Opción 3: Render

| Componente | Plan Gratuito | Plan Pagado |
|------------|---------------|-------------|
| Frontend | Gratis | $0 |
| Backend | Gratis* | $7/mes |
| MongoDB | Gratis (256MB) | $7/mes |
| SSL | Incluido | Incluido |
| **Total** | **Gratis** | **$14/mes** |

*El plan gratuito "duerme" después de inactividad

### ¿Cuál elegir según tu presupuesto?

- **$0/mes:** Render (plan gratuito) - Solo para pruebas o uso muy ligero
- **$6-8/mes:** VPS - Mejor opción calidad/precio para producción
- **$10-20/mes:** Railway - Si quieres facilidad y no te importa pagar más
- **$14/mes:** Render pagado - Balance entre facilidad y costo

---

## 📱 Acceso desde Dispositivos Móviles

La aplicación es **responsive** y funciona perfectamente en:
- 📱 Smartphones (iOS y Android)
- 📱 Tablets
- 💻 Laptops
- 🖥️ Computadores de escritorio

**No necesitas crear una app móvil**, simplemente:
1. Los usuarios abren su navegador (Chrome, Safari, Firefox, etc.)
2. Ingresan a `https://tudominio.com`
3. Inician sesión
4. ¡Listo!

**Agregar a pantalla de inicio (opcional):**
Los usuarios pueden agregar un ícono en su teléfono:
- **Android:** Chrome > Menú > "Agregar a pantalla de inicio"
- **iOS:** Safari > Compartir > "Agregar a inicio"

---

## 🔐 Mejores Prácticas de Seguridad

### 1. Contraseñas seguras
- ✅ Usa contraseñas de al menos 12 caracteres
- ✅ Incluye mayúsculas, minúsculas, números y símbolos
- ✅ Cambia la contraseña del admin inmediatamente
- ✅ No reutilices contraseñas

### 2. Actualizaciones regulares
```bash
# Actualiza el sistema operativo (Ubuntu)
apt update && apt upgrade -y

# Actualiza Docker
apt install docker-ce docker-ce-cli -y

# Actualiza la aplicación
cd /root/educando
git pull
docker-compose up -d --build
```

### 3. Firewall configurado
```bash
# Instala UFW si no está instalado
apt install ufw -y

# Reglas básicas
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 4. Backups regulares
- Configura backups automáticos (ver sección de comandos útiles)
- Guarda copias fuera del servidor (Google Drive, Dropbox, etc.)
- Prueba restaurar un backup periódicamente

### 5. Monitoreo
```bash
# Instala un monitor simple
apt install htop iotop -y

# Verifica regularmente
htop
docker stats
```

### 6. Variables de entorno seguras
- ✅ Cambia `JWT_SECRET` por algo único y largo
- ✅ No compartas tu archivo `.env`
- ✅ No subas `.env` a GitHub

### 7. Limita acceso SSH
```bash
# Edita la configuración SSH
nano /etc/ssh/sshd_config

# Cambia:
PermitRootLogin no
PasswordAuthentication no
# (Usa llaves SSH en su lugar)

# Reinicia SSH
systemctl restart sshd
```

---

## 📞 Soporte y Recursos Adicionales

### Si tienes problemas:

1. **Revisa esta guía primero**
   - La mayoría de problemas comunes están documentados

2. **Revisa los logs**
   ```bash
   docker-compose logs -f
   ```

3. **Verifica las variables de entorno**
   ```bash
   cat .env
   ```

4. **Asegúrate de que los puertos no estén ocupados**
   ```bash
   netstat -tulpn | grep -E ':(80|443|8001|27017)'
   ```

5. **Busca en la documentación oficial**
   - Docker: https://docs.docker.com/
   - FastAPI: https://fastapi.tiangolo.com/
   - MongoDB: https://docs.mongodb.com/

### Recursos útiles:

- **Tutorial de Docker:** https://www.docker.com/101-tutorial
- **Tutorial de Docker Compose:** https://docs.docker.com/compose/gettingstarted/
- **Guía de UFW (Firewall):** https://www.digitalocean.com/community/tutorials/ufw-essentials-common-firewall-rules-and-commands
- **Let's Encrypt:** https://letsencrypt.org/getting-started/
- **MongoDB University (cursos gratis):** https://university.mongodb.com/

### Comunidades de ayuda:

- **Stack Overflow:** https://stackoverflow.com/
- **Reddit r/docker:** https://reddit.com/r/docker
- **Reddit r/selfhosted:** https://reddit.com/r/selfhosted
- **Discord de FastAPI:** https://discord.gg/fastapi

---

## ✅ Checklist de Despliegue

Usa esta lista para asegurarte de que todo esté configurado correctamente:

### Antes del despliegue:
- [ ] El código está en GitHub o lo tienes respaldado
- [ ] Has elegido un proveedor (VPS, Railway o Render)
- [ ] Tienes un dominio (opcional pero recomendado)
- [ ] Has leído esta guía completa

### Durante el despliegue:
- [ ] Servidor creado (si usas VPS)
- [ ] Docker y Docker Compose instalados
- [ ] Código subido al servidor
- [ ] Variables de entorno configuradas (`.env`)
- [ ] Aplicación corriendo (`docker-compose ps`)
- [ ] Frontend accesible desde el navegador
- [ ] Backend respondiendo (`/api/health`)

### Después del despliegue:
- [ ] Has cambiado la contraseña del admin
- [ ] Has configurado el dominio (si lo tienes)
- [ ] Has configurado HTTPS/SSL
- [ ] Firewall configurado (puertos 80, 443, SSH)
- [ ] Backups configurados
- [ ] Has creado al menos 1 usuario de prueba
- [ ] Has probado todas las funcionalidades principales

### Opcional pero recomendado:
- [ ] Configurar monitoreo (htop, docker stats)
- [ ] Configurar renovación automática de SSL
- [ ] Documentar credenciales en un lugar seguro
- [ ] Probar la aplicación desde dispositivos móviles
- [ ] Configurar un email de recuperación
- [ ] Informar a los usuarios sobre la URL

---

## 🎉 ¡Tu Escuela Virtual Está Lista!

Felicidades por completar el despliegue. Tu plataforma educativa está ahora disponible en internet y lista para recibir estudiantes y profesores.

### Próximos pasos recomendados:

1. **Crea usuarios de prueba**
   - Al menos 1 profesor
   - Al menos 1 estudiante
   - Prueba el flujo completo

2. **Capacita a los usuarios**
   - Muéstrales cómo iniciar sesión
   - Explícales las funcionalidades
   - Proporciona la URL del sitio

3. **Monitorea el uso**
   - Revisa los logs regularmente
   - Verifica que no haya errores
   - Pregunta feedback a los usuarios

4. **Mantén actualizado**
   - Actualiza el sistema operativo mensualmente
   - Actualiza Docker cuando haya nuevas versiones
   - Actualiza la aplicación cuando haya mejoras

---

**¿Preguntas? ¿Problemas?**

Recuerda revisar:
1. Esta guía
2. Los logs: `docker-compose logs -f`
3. La sección de solución de problemas
4. Las comunidades de ayuda mencionadas arriba

¡Éxito con tu plataforma educativa! 🚀📚
