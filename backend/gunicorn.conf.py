import os

# Número de workers para manejar carga concurrente.
# Fórmula recomendada: (2 × CPU cores) + 1
# Solo el worker 0 ejecuta el APScheduler para evitar race conditions.
workers = int(os.environ.get("WORKERS", 4))

# Clase de worker: uvicorn para FastAPI async
worker_class = "uvicorn.workers.UvicornWorker"

# Bind al puerto configurado
bind = f"0.0.0.0:{os.environ.get('PORT', '8001')}"

# Timeouts — aumentado a 180s para cierre de módulos (operación larga con 3000 estudiantes)
timeout = 180
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Preload app para ahorrar memoria (shared memory entre workers)
preload_app = True

# Reiniciar workers periódicamente para evitar memory leaks
max_requests = 1000
max_requests_jitter = 50

# Worker connections para el worker único (asyncio maneja miles de conexiones concurrentes)
worker_connections = 1000
