# Recomendaciones de Despliegue para 3000 Usuarios

Este documento proporciona recomendaciones específicas para desplegar la aplicación web "Educando" para soportar hasta 3000 usuarios.

## 📊 Análisis de Capacidad

### Usuarios Concurrentes
Con 3000 usuarios registrados, estimamos que:
- **Usuarios activos diarios**: ~1500-2000 (50-66%)
- **Usuarios concurrentes (pico)**: ~300-500 (10-17% del total)
- **Tráfico promedio**: ~150-200 usuarios conectados simultáneamente

### Recursos Necesarios

#### Opción 1: VPS/Servidor Dedicado (RECOMENDADO)

Para soportar 3000 usuarios de manera confiable, recomendamos:

**Especificaciones Mínimas:**
- **CPU**: 4 vCores (mínimo 2 vCores)
- **RAM**: 8GB (mínimo 4GB)
- **Disco**: 100GB SSD
- **Ancho de banda**: 3-5TB/mes
- **Sistema Operativo**: Ubuntu 22.04 LTS o Ubuntu 24.04 LTS

**Costo Estimado:**
- **Hetzner**: €20-30/mes (~$22-33 USD)
- **DigitalOcean**: $48/mes
- **Vultr**: $48/mes
- **Contabo**: €15-20/mes (~$16-22 USD)

**Proveedor Recomendado: Hetzner**
- Mejor relación precio/rendimiento
- Excelente infraestructura europea
- Soporte técnico confiable
- Opción: CPX31 (4 vCPU, 8GB RAM, 160GB SSD) - €20/mes

#### Configuración del Servidor

```bash
# 1. Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y

# 2. Configurar límites del sistema para MongoDB
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
sysctl -p

# 3. Configurar firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

#### Optimizaciones de Producción

**1. Docker Compose para Producción**

Crear un archivo `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7
    container_name: educando_mongodb
    restart: always
    environment:
      - MONGO_INITDB_DATABASE=educando_db
    volumes:
      - mongodb_data:/data/db
    # Aumentar recursos para MongoDB
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 3G
        reservations:
          cpus: '1'
          memory: 2G
    command: mongod --wiredTigerCacheSizeGB 2

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: educando_backend
    restart: always
    depends_on:
      - mongodb
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=educando_db
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./backend/uploads:/app/uploads
    # Aumentar recursos para backend
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    # Escalar backend (2 instancias)
    scale: 2

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: educando_frontend
    restart: always
    depends_on:
      - backend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
    # Recursos para frontend
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

volumes:
  mongodb_data:
```

**2. Optimizaciones de MongoDB**

```bash
# Conectarse a MongoDB
docker exec -it educando_mongodb mongosh

# Dentro de mongosh, crear índices para mejor rendimiento
use educando_db

// Índices para usuarios
db.users.createIndex({ "email": 1 }, { unique: true, sparse: true })
db.users.createIndex({ "cedula": 1 }, { unique: true, sparse: true })
db.users.createIndex({ "role": 1 })
db.users.createIndex({ "active": 1 })
db.users.createIndex({ "program_id": 1 })

// Índices para cursos
db.courses.createIndex({ "program_id": 1 })
db.courses.createIndex({ "subject_id": 1 })
db.courses.createIndex({ "teacher_id": 1 })
db.courses.createIndex({ "active": 1 })

// Índices para materias
db.subjects.createIndex({ "program_id": 1 })
db.subjects.createIndex({ "module_number": 1 })

// Índices para actividades
db.activities.createIndex({ "course_id": 1 })
db.activities.createIndex({ "due_date": 1 })

// Índices para calificaciones
db.grades.createIndex({ "student_id": 1, "course_id": 1 })
db.grades.createIndex({ "activity_id": 1 })

// Índices para videos
db.videos.createIndex({ "course_id": 1 })

exit
```

**3. Configuración de Nginx Optimizada**

Actualizar `frontend/nginx.conf`:

```nginx
# Configuración optimizada para 3000 usuarios
worker_processes auto;
worker_rlimit_nofile 8192;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Optimizaciones
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    
    # Compresión
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;
    
    # Cacheo de archivos estáticos
    open_file_cache max=10000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;

    # Límites de rate
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=addr:10m;

    server {
        listen 80;
        server_name tudominio.com www.tudominio.com;
        
        # Límites de conexión
        limit_conn addr 10;
        
        root /usr/share/nginx/html;
        index index.html;

        # Cache de archivos estáticos
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location / {
            try_files $uri $uri/ /index.html;
        }

        # API con rate limiting
        location /api {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://backend:8001;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            
            # Límites de tamaño
            client_max_body_size 50M;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
```

**4. Monitoreo y Logs**

```bash
# Instalar herramientas de monitoreo
apt install htop iotop nethogs -y

# Ver uso de recursos en tiempo real
htop

# Ver estadísticas de Docker
docker stats

# Configurar rotación de logs
cat > /etc/docker/daemon.json <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

systemctl restart docker
```

**5. Backups Automáticos**

```bash
# Crear script de backup
cat > /root/backup_educando.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/root/backups/educando"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de MongoDB
docker exec educando_mongodb mongodump --out /backup/$DATE
docker cp educando_mongodb:/backup/$DATE $BACKUP_DIR/mongo_$DATE

# Backup de archivos subidos
tar czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /root/educando/backend uploads

# Limpiar backups antiguos (más de 7 días)
find $BACKUP_DIR -type d -name "mongo_*" -mtime +7 -exec rm -rf {} \;
find $BACKUP_DIR -type f -name "uploads_*" -mtime +7 -delete

echo "Backup completado: $DATE"
EOF

chmod +x /root/backup_educando.sh

# Configurar cron para backups diarios a las 3 AM
(crontab -l 2>/dev/null; echo "0 3 * * * /root/backup_educando.sh >> /var/log/educando_backup.log 2>&1") | crontab -
```

#### Opción 2: Servicios Cloud Manejados (Más Fácil pero Más Caro)

Si prefieres no administrar servidores:

**Railway**
- Costo estimado: $80-120/mes para 3000 usuarios
- ✅ Fácil de usar, escalado automático
- ❌ Más caro a largo plazo

**Render**
- Frontend: Gratis (static site)
- Backend: $25-40/mes (instancias escalables)
- MongoDB: $25-50/mes (base de datos manejada)
- **Total**: $50-90/mes
- ✅ Balance entre facilidad y costo

**MongoDB Atlas + Heroku/Railway**
- MongoDB Atlas: $57/mes (M10 - 2GB RAM, 10GB storage)
- Heroku: $25-50/mes por instancia backend
- Frontend: Netlify/Vercel gratis
- **Total**: $80-110/mes

#### Opción 3: Solución Híbrida (Recomendado para Instituciones)

**Configuración Ideal:**
- **VPS para Frontend y Backend**: Hetzner CPX31 (€20/mes)
- **MongoDB Atlas para Base de Datos**: M10 ($57/mes)
- **Total**: ~$80/mes

**Ventajas:**
- ✅ Base de datos profesional con backups automáticos
- ✅ Mejor rendimiento y confiabilidad
- ✅ Escalado fácil si crece el número de usuarios
- ✅ Soporte técnico para la base de datos

**Configuración:**

```yaml
# docker-compose.prod-atlas.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: educando_backend
    restart: always
    environment:
      # Usar MongoDB Atlas
      # ⚠️ IMPORTANTE: Reemplazar 'usuario:password' con tus credenciales reales de MongoDB Atlas
      # Nunca commitees estas credenciales al repositorio - usa variables de entorno
      - MONGO_URL=mongodb+srv://usuario:password@cluster.mongodb.net/
      - DB_NAME=educando_db
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - ./backend/uploads:/app/uploads
    scale: 2

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
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

## 🔒 Seguridad para Producción

### 1. SSL/TLS (HTTPS) - OBLIGATORIO

```bash
# Instalar Certbot
apt install certbot python3-certbot-nginx -y

# Obtener certificado SSL
certbot --nginx -d tudominio.com -d www.tudominio.com

# Renovación automática
echo "0 3 * * * certbot renew --quiet" | crontab -
```

### 2. Firewall Configurado

```bash
# Configurar UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 3. Variables de Entorno Seguras

```bash
# Generar JWT_SECRET fuerte
openssl rand -base64 64

# Actualizar .env
JWT_SECRET=<tu_clave_generada_muy_larga_y_segura>
```

### 4. Actualizaciones Regulares

```bash
# Crear script de actualización
cat > /root/update_educando.sh <<'EOF'
#!/bin/bash
cd /root/educando

# Backup antes de actualizar
/root/backup_educando.sh

# Actualizar código
git pull

# Reconstruir contenedores
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build

# Verificar estado
docker compose -f docker-compose.prod.yml ps

echo "Actualización completada: $(date)"
EOF

chmod +x /root/update_educando.sh
```

## 📈 Monitoreo de Rendimiento

### Herramientas Recomendadas

**1. Uptimerobot (Gratis)**
- Monitorea disponibilidad de tu sitio
- Alertas por email/SMS
- https://uptimerobot.com

**2. Grafana + Prometheus (Avanzado)**
```bash
# Para monitoreo detallado de métricas
docker run -d --name=grafana -p 3000:3000 grafana/grafana
docker run -d --name=prometheus -p 9090:9090 prom/prometheus
```

**3. Logs Centralizados**
```bash
# Ver logs de todos los servicios
docker compose logs -f --tail=100

# Buscar errores
docker compose logs | grep -i error

# Logs específicos de un servicio
docker compose logs backend -f
```

## 🚨 Plan de Contingencia

### Si el servidor se cae:

1. **Verificar estado**
   ```bash
   docker compose ps
   docker compose logs
   ```

2. **Reiniciar servicios**
   ```bash
   docker compose restart
   ```

3. **Si no funciona, reconstruir**
   ```bash
   docker compose down
   docker compose up -d --build
   ```

4. **Restaurar desde backup**
   ```bash
   # Restaurar MongoDB
   docker cp /root/backups/educando/mongo_FECHA educando_mongodb:/backup
   docker exec educando_mongodb mongorestore /backup/FECHA
   
   # Restaurar uploads
   tar xzf /root/backups/educando/uploads_FECHA.tar.gz -C /root/educando/backend/
   ```

## 💰 Comparación de Costos Anuales

| Opción | Costo Mensual | Costo Anual | Recomendación |
|--------|---------------|-------------|---------------|
| VPS Solo (Hetzner) | €20 ($22) | $264 | ✅ Mejor precio |
| VPS + MongoDB Atlas | $80 | $960 | ✅ Más confiable |
| Railway | $100 | $1200 | ⚠️ Fácil pero caro |
| Render Completo | $70 | $840 | ✅ Balance |

**Adicionales:**
- Dominio: ~$10/año
- SSL: Gratis (Let's Encrypt)
- Backups externos: $5-10/mes (opcional)

## ✅ Checklist de Despliegue para 3000 Usuarios

### Pre-Despliegue
- [ ] Servidor con al menos 4 vCPU y 8GB RAM contratado
- [ ] Dominio registrado y configurado
- [ ] Backup del código actual
- [ ] Plan de migración documentado

### Durante el Despliegue
- [ ] Docker y Docker Compose instalados
- [ ] Variables de entorno configuradas con valores seguros
- [ ] Índices de MongoDB creados
- [ ] SSL/HTTPS configurado
- [ ] Firewall configurado
- [ ] Nginx optimizado para alto tráfico
- [ ] Backups automáticos configurados

### Post-Despliegue
- [ ] Pruebas de carga realizadas
- [ ] Monitoreo configurado (UptimeRobot mínimo)
- [ ] Credenciales de admin cambiadas
- [ ] Documentación de procedimientos actualizada
- [ ] Plan de contingencia probado
- [ ] Usuarios de prueba creados y verificados

### Mantenimiento Continuo
- [ ] Backups diarios verificados
- [ ] Logs revisados semanalmente
- [ ] Actualizaciones del sistema mensuales
- [ ] Métricas de rendimiento monitoreadas
- [ ] Plan de escalado definido para más usuarios

## 📞 Soporte y Recursos

### Si necesitas ayuda adicional:
- **Hetzner Support**: https://docs.hetzner.com/
- **Docker Documentation**: https://docs.docker.com/
- **MongoDB Atlas Support**: https://www.mongodb.com/docs/atlas/
- **Nginx Optimization**: https://www.nginx.com/blog/tuning-nginx/

## 🎯 Conclusión

Para una institución educativa con 3000 usuarios, recomendamos:

**Opción IDEAL**: VPS Hetzner CPX31 + MongoDB Atlas M10
- **Costo**: ~$80/mes
- **Rendimiento**: Excelente
- **Escalabilidad**: Fácil
- **Confiabilidad**: Alta

**Opción ECONÓMICA**: VPS Hetzner CPX31 con MongoDB local
- **Costo**: ~$22/mes
- **Rendimiento**: Bueno
- **Escalabilidad**: Manual pero posible
- **Confiabilidad**: Buena (con backups diarios)

Ambas opciones soportarán cómodamente a 3000 usuarios con la configuración correcta. La diferencia principal es el nivel de confiabilidad y la facilidad de administración de la base de datos.

---

**¿Preguntas?** Consulta el archivo `DESPLIEGUE.md` para instrucciones detalladas paso a paso.
