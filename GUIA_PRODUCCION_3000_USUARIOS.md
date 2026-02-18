# 🚀 Guía de Producción para 3000 Usuarios

## 📋 Resumen Ejecutivo

Esta guía explica paso a paso cómo preparar la plataforma Educando para soportar **3000 usuarios simultáneos** sin caídas ni problemas de rendimiento.

**Costo Estimado:** $40-150 USD/mes (vs $0-7 actual)  
**Tiempo de Implementación:** 2-4 horas  
**Nivel Técnico:** Intermedio

---

## ⚠️ Limitaciones Actuales

### Configuración Actual:
```
❌ Backend: 1 worker (Uvicorn) → 200-500 usuarios máx
❌ MongoDB: M0 (512MB gratis) → 500 conexiones máx
❌ Rate Limiting: En memoria → Se pierde al reiniciar
❌ Sin escalamiento horizontal
❌ Sin CDN para archivos estáticos
```

**Resultado:** La plataforma puede caerse con más de 500 usuarios simultáneos.

---

## ✅ Arquitectura Recomendada para 3000 Usuarios

```
┌─────────────────────────────────────────────┐
│ CDN (Cloudflare) - OPCIONAL                │
│ • Cache de archivos estáticos              │
│ • Protección DDoS                          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│ Load Balancer (Render automático)          │
└──────────────────┬──────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼──┐      ┌───▼──┐      ┌───▼──┐
│ API  │      │ API  │      │ API  │
│ #1   │      │ #2   │  ... │ #N   │
│(8 w) │      │(8 w) │      │(8 w) │
└───┬──┘      └───┬──┘      └───┬──┘
    │              │              │
    └──────────────┼──────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│ Redis (Sesiones + Rate Limiting)            │
│ • Compartido entre todas las instancias     │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│ MongoDB Atlas M2+ (Replica Set)             │
│ • 10GB storage                              │
│ • 1000+ conexiones concurrentes             │
│ • Backups automáticos                       │
└─────────────────────────────────────────────┘
```

---

## 📝 Checklist de Implementación

### Fase 1: Base de Datos (CRÍTICO) ⚠️

#### 1.1 Upgrade MongoDB Atlas

```bash
# Paso 1: Ir a MongoDB Atlas Dashboard
https://cloud.mongodb.com/

# Paso 2: Seleccionar tu cluster → Edit Configuration
# Paso 3: Cambiar de M0 (Free) a M2 ($9/mes) o M10 ($57/mes)
```

**Especificaciones Recomendadas:**

| Tier | Storage | RAM | Conexiones | Usuarios | Costo |
|------|---------|-----|------------|----------|-------|
| M0 | 512MB | 0.5GB | 500 | 500 | Gratis |
| M2 | 10GB | 2GB | 1000+ | 1500 | $9/mes |
| M10 | 10GB | 2GB | 3000+ | 3000+ | $57/mes |

**Para 3000 usuarios:** Usar M10 o superior

#### 1.2 Configurar Índices en MongoDB

```javascript
// Conectar a MongoDB Atlas con mongo shell o Compass
use WebApp

// Índices para optimizar consultas frecuentes
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "cedula": 1 }, { unique: true })
db.users.createIndex({ "role": 1 })
db.users.createIndex({ "email": 1, "password_hash": 1 })

db.courses.createIndex({ "code": 1 }, { unique: true })
db.courses.createIndex({ "teacher_id": 1 })

db.grades.createIndex({ "student_id": 1, "course_id": 1 })
db.grades.createIndex({ "course_id": 1 })

db.modules.createIndex({ "number": 1, "course_id": 1 })

// Verificar índices creados
db.users.getIndexes()
db.courses.getIndexes()
```

**Explicación:** Los índices aceleran las búsquedas en un 10-100x.

#### 1.3 Configurar Connection Pooling

Editar `backend/server.py`:

```python
# Línea ~50 - Aumentar pool de conexiones
client = AsyncIOMotorClient(
    mongo_url, 
    serverSelectionTimeoutMS=5000,
    maxPoolSize=200,  # Aumentar de 50 a 200
    minPoolSize=10,
    maxIdleTimeMS=45000
)
```

---

### Fase 2: Backend Multi-Worker (CRÍTICO) ⚠️

#### 2.1 Instalar Gunicorn

Editar `backend/requirements.txt`:

```txt
# Agregar al final:
gunicorn==21.2.0
```

#### 2.2 Configurar Multi-Worker

Crear archivo `backend/gunicorn_config.py`:

```python
# Configuración de Gunicorn para producción
import os
import multiprocessing

# Número de workers: 2-4 x CPU cores
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2))
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
keepalive = 120

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Bind
bind = f"0.0.0.0:{os.environ.get('PORT', '8001')}"

# Timeout
timeout = 120
graceful_timeout = 30

# Preload app
preload_app = True
```

#### 2.3 Actualizar Dockerfile del Backend

Editar `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear directorio para uploads
RUN mkdir -p uploads

# Usar Gunicorn en lugar de Uvicorn directo
CMD ["gunicorn", "-c", "gunicorn_config.py", "server:app"]
```

---

### Fase 3: Rate Limiting Distribuido con Redis (RECOMENDADO)

#### 3.1 Agregar Redis a render.yaml

Editar `render.yaml` y agregar antes de los servicios:

```yaml
services:
  # Redis para sesiones y rate limiting
  - type: redis
    name: educando-redis
    region: oregon
    plan: starter
    maxmemoryPolicy: allkeys-lru
    ipAllowList: []  # Solo acceso desde otros servicios de Render

  # Backend API Service (modificar)
  - type: web
    name: educando-backend
    env: docker
    region: oregon
    plan: standard  # ← Cambiar de 'starter' a 'standard'
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    envVars:
      - key: MONGO_URL
        sync: false
      - key: REDIS_URL
        fromService:
          type: redis
          name: educando-redis
          property: connectionString
      - key: GUNICORN_WORKERS
        value: "8"
      # ... resto de variables
```

#### 3.2 Instalar Redis en Backend

Editar `backend/requirements.txt`:

```txt
redis==5.0.1
aioredis==2.0.1
```

#### 3.3 Implementar Rate Limiting con Redis

Editar `backend/server.py` (líneas ~67-72):

```python
import redis.asyncio as redis

# Redis para rate limiting distribuido
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    logger.info("Redis conectado para rate limiting distribuido")
else:
    redis_client = None
    logger.warning("Redis no configurado - usando rate limiting en memoria")

# Función de rate limiting
async def check_rate_limit(ip: str) -> bool:
    """Verifica si una IP ha excedido el límite de intentos"""
    if redis_client:
        # Rate limiting con Redis (distribuido)
        key = f"login_attempts:{ip}"
        attempts = await redis_client.get(key)
        if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
            return False
        return True
    else:
        # Fallback a memoria (actual)
        now = datetime.now(timezone.utc).timestamp()
        attempts = [t for t in login_attempts[ip] if now - t < LOGIN_ATTEMPT_WINDOW]
        return len(attempts) < MAX_LOGIN_ATTEMPTS

async def record_login_attempt(ip: str):
    """Registra un intento de login"""
    if redis_client:
        key = f"login_attempts:{ip}"
        await redis_client.incr(key)
        await redis_client.expire(key, LOGIN_ATTEMPT_WINDOW)
    else:
        login_attempts[ip].append(datetime.now(timezone.utc).timestamp())
```

---

### Fase 4: Escalamiento Horizontal en Render

#### 4.1 Actualizar render.yaml

```yaml
services:
  - type: web
    name: educando-backend
    env: docker
    region: oregon
    plan: standard  # Plan Standard permite múltiples instancias
    numInstances: 4  # ← 4 instancias del backend
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    # ... resto de configuración
```

**Explicación:** Render distribuirá automáticamente el tráfico entre las 4 instancias.

#### 4.2 Verificar Load Balancing

Una vez desplegado:

```bash
# Verificar que todas las instancias estén activas
curl https://educando-backend.onrender.com/health
# Repetir varias veces, debería rotar entre instancias
```

---

### Fase 5: CDN y Optimización Frontend (OPCIONAL)

#### 5.1 Configurar Cloudflare (Gratis)

```bash
# Paso 1: Crear cuenta en Cloudflare
https://dash.cloudflare.com/sign-up

# Paso 2: Agregar tu dominio
# Paso 3: Cambiar nameservers en tu proveedor de dominio

# Paso 4: Activar en Cloudflare:
- SSL/TLS: Full (strict)
- Caching: Standard
- Auto Minify: JS, CSS, HTML
- Brotli compression: ON
```

#### 5.2 Configurar CORS para CDN

Editar `backend/server.py`:

```python
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
if CORS_ORIGINS == '*':
    origins = ['*']
else:
    origins = CORS_ORIGINS.split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Configurar en Render → Frontend:

```yaml
envVars:
  - key: REACT_APP_BACKEND_URL
    value: "https://tudominio.com/api"  # Tu dominio con Cloudflare
```

---

## 💰 Costos Mensuales Estimados

### Configuración Mínima (1500 usuarios)

| Servicio | Tier | Costo |
|----------|------|-------|
| MongoDB Atlas | M2 | $9/mes |
| Render Backend | Standard (2 inst) | $14/mes |
| Render Frontend | Free | $0 |
| Redis | Starter | $7/mes |
| **TOTAL** | | **$30/mes** |

### Configuración Recomendada (3000 usuarios)

| Servicio | Tier | Costo |
|----------|------|-------|
| MongoDB Atlas | M10 | $57/mes |
| Render Backend | Standard (4 inst) | $28/mes |
| Render Frontend | Starter | $7/mes |
| Redis | Standard | $15/mes |
| Cloudflare CDN | Free | $0 |
| **TOTAL** | | **$107/mes** |

### Configuración Profesional (5000+ usuarios)

| Servicio | Tier | Costo |
|----------|------|-------|
| MongoDB Atlas | M20 | $150/mes |
| Render Backend | Pro (8 inst) | $80/mes |
| Render Frontend | Starter | $7/mes |
| Redis | Pro | $40/mes |
| Cloudflare Pro | | $20/mes |
| Monitoring (DataDog) | | $15/mes |
| **TOTAL** | | **$312/mes** |

---

## 🔍 Monitoreo y Observabilidad

### 6.1 Health Checks

Ya implementados en `backend/server.py`:

```python
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
```

Configurar en Render → Backend → Health Check Path: `/api/health`

### 6.2 Logs Centralizados

```bash
# Ver logs en tiempo real desde Render Dashboard
Render → educando-backend → Logs

# Buscar errores:
- "error"
- "exception"
- "failed"
- "timeout"
```

### 6.3 Monitoreo de MongoDB (Recomendado)

MongoDB Atlas incluye monitoreo gratuito:

```bash
# Atlas Dashboard → Metrics
- Conexiones activas
- Operaciones por segundo
- Uso de CPU
- Uso de memoria
- Latencia de queries
```

**Alertas Recomendadas:**
- Conexiones > 80% del límite
- Uso de disco > 80%
- Latencia > 100ms
- CPU > 90%

### 6.4 Herramientas de Monitoreo Profesional (OPCIONAL)

#### New Relic (Recomendado)

```bash
# 1. Crear cuenta: https://newrelic.com/signup
# 2. Instalar agent en backend/requirements.txt
newrelic==9.4.0

# 3. Configurar en Render
NEW_RELIC_LICENSE_KEY=tu_license_key
NEW_RELIC_APP_NAME=educando-backend

# 4. Modificar CMD en Dockerfile
CMD ["newrelic-admin", "run-program", "gunicorn", "-c", "gunicorn_config.py", "server:app"]
```

#### Alternativas:
- **DataDog:** $15/mes por host
- **Sentry:** Para tracking de errores (gratis hasta 5k eventos/mes)
- **Prometheus + Grafana:** Self-hosted (gratis pero requiere VPS)

---

## ⚡ Optimizaciones Adicionales

### 7.1 Compresión Gzip/Brotli

Ya configurado en `frontend/nginx.conf`:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### 7.2 Caching de Assets Estáticos

Editar `frontend/nginx.conf`:

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 7.3 Lazy Loading de Imágenes

En componentes React:

```jsx
<img 
  src={imageUrl} 
  loading="lazy"  // ← Agregar
  alt="descripción" 
/>
```

### 7.4 Code Splitting en React

Ya configurado con React 19:

```javascript
// Importar componentes con lazy loading
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./components/Dashboard'));

function App() {
  return (
    <Suspense fallback={<div>Cargando...</div>}>
      <Dashboard />
    </Suspense>
  );
}
```

---

## 🧪 Testing de Carga

### 8.1 Herramientas Recomendadas

#### Apache Bench (Simple)

```bash
# Instalar
apt-get install apache2-utils  # Ubuntu/Debian
brew install ab  # macOS

# Test: 1000 requests, 100 concurrentes
ab -n 1000 -c 100 https://tudominio.com/api/health

# Resultados a verificar:
# - Requests per second > 100
# - Time per request < 100ms
# - Failed requests: 0
```

#### K6 (Recomendado)

```bash
# Instalar k6
brew install k6  # macOS
# O descargar: https://k6.io/docs/get-started/installation/

# Crear script de test
cat > load_test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Subir a 100 usuarios
    { duration: '5m', target: 100 },   // Mantener 100 usuarios
    { duration: '2m', target: 1000 },  // Subir a 1000 usuarios
    { duration: '5m', target: 1000 },  // Mantener 1000 usuarios
    { duration: '2m', target: 3000 },  // Subir a 3000 usuarios
    { duration: '10m', target: 3000 }, // Mantener 3000 usuarios
    { duration: '2m', target: 0 },     // Bajar a 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% de requests < 500ms
    http_req_failed: ['rate<0.01'],   // < 1% de errores
  },
};

export default function () {
  const res = http.get('https://tudominio.com/api/health');
  check(res, {
    'status 200': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
EOF

# Ejecutar test
k6 run load_test.js
```

### 8.2 Métricas Objetivo

| Métrica | Objetivo | Aceptable | Crítico |
|---------|----------|-----------|---------|
| Response Time (p95) | < 200ms | < 500ms | > 1000ms |
| Throughput | > 500 req/s | > 200 req/s | < 100 req/s |
| Error Rate | < 0.1% | < 1% | > 5% |
| Availability | 99.9% | 99% | < 99% |
| CPU Usage | < 60% | < 80% | > 90% |
| Memory Usage | < 70% | < 85% | > 95% |

---

## 🚨 Troubleshooting

### Problema: Backend se cae con muchos usuarios

**Causa:** Workers insuficientes

**Solución:**
```yaml
# render.yaml - Aumentar workers
envVars:
  - key: GUNICORN_WORKERS
    value: "16"  # Aumentar de 8 a 16
```

### Problema: MongoDB conexiones agotadas

**Causa:** Pool de conexiones insuficiente

**Solución:**
```python
# backend/server.py
client = AsyncIOMotorClient(
    mongo_url,
    maxPoolSize=500,  # Aumentar
    minPoolSize=50
)
```

### Problema: Rate limiting no funciona entre instancias

**Causa:** Rate limiting en memoria

**Solución:** Implementar Redis (ver Fase 3)

### Problema: Latencia alta en consultas

**Causa:** Falta de índices en MongoDB

**Solución:** Crear índices (ver Fase 1.2)

---

## ✅ Checklist Final

### Antes del Lanzamiento

- [ ] MongoDB actualizado a M10+
- [ ] Índices creados en todas las colecciones
- [ ] Backend con Gunicorn (8+ workers)
- [ ] Redis configurado para rate limiting
- [ ] 4+ instancias del backend en Render
- [ ] Health checks configurados
- [ ] Monitoreo activo (logs, métricas)
- [ ] CDN configurado (Cloudflare)
- [ ] Tests de carga completados exitosamente
- [ ] Plan de respaldo y recuperación
- [ ] Documentación actualizada

### Durante el Lanzamiento

- [ ] Monitorear logs en tiempo real
- [ ] Verificar métricas de MongoDB Atlas
- [ ] Revisar health checks cada 5 minutos
- [ ] Tener plan de rollback listo

### Después del Lanzamiento

- [ ] Revisar logs diariamente (primera semana)
- [ ] Configurar alertas automáticas
- [ ] Optimizar queries lentas
- [ ] Ajustar capacidad según uso real

---

## 📞 Soporte y Recursos

### Documentación Oficial
- [Render.com Scaling Guide](https://render.com/docs/scaling)
- [MongoDB Performance Best Practices](https://www.mongodb.com/docs/manual/administration/production-notes/)
- [FastAPI Performance](https://fastapi.tiangolo.com/deployment/server-workers/)

### Contacto de Soporte
- Render Support: support@render.com
- MongoDB Atlas Support: Desde el dashboard

---

## 🎯 Resumen de Acciones Inmediatas

### 🔴 CRÍTICO (Hacer AHORA)

1. **Upgrade MongoDB:** M0 → M10 ($57/mes)
2. **Crear índices:** En todas las colecciones
3. **Configurar Gunicorn:** Multi-worker en backend
4. **Actualizar render.yaml:** Plan Standard + 4 instancias

### 🟡 IMPORTANTE (Hacer en 1 semana)

5. **Configurar Redis:** Para rate limiting distribuido
6. **Implementar monitoring:** New Relic o DataDog
7. **Tests de carga:** Con K6 (3000 usuarios)
8. **CDN:** Configurar Cloudflare

### 🟢 OPCIONAL (Hacer en 1 mes)

9. **Optimizar queries:** Analizar slow queries
10. **Caching avanzado:** Redis para datos frecuentes
11. **Auto-scaling:** Configurar en Render
12. **Disaster recovery:** Backups y plan de recuperación

---

**¡La plataforma estará lista para 3000 usuarios simultáneos! 🚀**
