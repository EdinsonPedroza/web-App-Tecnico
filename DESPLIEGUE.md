# Guía de Despliegue - Escuela Virtual Educando

Esta guía te explica cómo subir tu aplicación a internet.

## Opción 1: Servidor VPS (Recomendado)

### Proveedores económicos:
- **DigitalOcean** - Desde $6/mes
- **Vultr** - Desde $6/mes
- **Hetzner** - Desde $4/mes
- **Linode** - Desde $5/mes

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
Desde tu computadora local:
```bash
scp -r /ruta/a/tu/proyecto root@TU_IP:/root/educando
```

O clona desde GitHub si lo tienes ahí.

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

#### 8. ¡Listo!
Visita `http://TU_IP_DEL_SERVIDOR` en tu navegador.

---

## Opción 2: Railway (Más fácil, gratis para empezar)

### Pasos:

1. Ve a [railway.app](https://railway.app)
2. Crea una cuenta con GitHub
3. Haz clic en "New Project"
4. Selecciona "Deploy from GitHub repo"
5. Conecta tu repositorio
6. Railway detectará el docker-compose.yml automáticamente
7. Configura las variables de entorno en el dashboard
8. ¡Listo! Te dará una URL automática

---

## Opción 3: Render (También fácil)

### Pasos:

1. Ve a [render.com](https://render.com)
2. Crea una cuenta
3. Crea 3 servicios:
   - **MongoDB**: Selecciona "New" > "MongoDB"
   - **Backend**: "New" > "Web Service" > Tu repo > Selecciona carpeta `/backend`
   - **Frontend**: "New" > "Static Site" > Tu repo > Selecciona carpeta `/frontend`
4. Configura las variables de entorno
5. ¡Listo!

---

## Configurar un Dominio Personalizado

### Comprar dominio:
- **Namecheap** - Desde $8/año
- **Google Domains** - Desde $12/año
- **GoDaddy** - Desde $10/año

### Configurar DNS:
1. Ve a tu proveedor de dominio
2. Busca "DNS" o "Nameservers"
3. Agrega un registro tipo A:
   - Nombre: `@` o tu dominio
   - Valor: La IP de tu servidor
4. Espera 5-30 minutos

### Agregar HTTPS (SSL) gratuito:
```bash
# En tu servidor
apt install certbot python3-certbot-nginx -y
certbot --nginx -d tudominio.com
```

---

## Crear los Datos Iniciales

Después de desplegar, necesitas crear el primer usuario admin:

```bash
# Conectarte al contenedor del backend
docker exec -it educando_backend bash

# Ejecutar el script de seed
python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import hashlib
import os

async def seed():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ.get('DB_NAME', 'educando_db')]
    
    # Crear admin
    admin = await db.users.find_one({'email': 'admin@educando.com'})
    if not admin:
        await db.users.insert_one({
            'id': 'user-admin',
            'name': 'Administrador',
            'email': 'admin@educando.com',
            'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
            'role': 'admin',
            'active': True
        })
        print('Admin creado: admin@educando.com / admin123')
    else:
        print('Admin ya existe')

asyncio.run(seed())
"
```

---

## Comandos Útiles

```bash
# Ver logs
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Detener todo
docker-compose down

# Actualizar después de cambios
docker-compose up -d --build

# Ver estado de contenedores
docker-compose ps

# Entrar al contenedor del backend
docker exec -it educando_backend bash

# Backup de la base de datos
docker exec educando_mongodb mongodump --out /backup
docker cp educando_mongodb:/backup ./backup
```

---

## Solución de Problemas

### La página no carga
```bash
# Verificar que los contenedores estén corriendo
docker-compose ps

# Ver logs de errores
docker-compose logs frontend
docker-compose logs backend
```

### Error de conexión a MongoDB
```bash
# Verificar que MongoDB esté corriendo
docker-compose logs mongodb
```

### Los archivos no se suben
- Verificar que el volumen `uploads_data` esté montado
- Verificar permisos de la carpeta uploads

---

## Costos Estimados

| Servicio | Costo Mensual |
|----------|---------------|
| VPS básico | $5-10 |
| Dominio | $1 (anual $8-12) |
| SSL | Gratis (Let's Encrypt) |
| **Total** | **~$6-11/mes** |

---

## Soporte

Si tienes problemas:
1. Revisa los logs: `docker-compose logs -f`
2. Verifica las variables de entorno
3. Asegúrate de que los puertos no estén ocupados

¡Tu escuela virtual está lista para recibir estudiantes!
