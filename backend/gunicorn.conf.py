import os

# Número de workers: configurable via env var, default 2
workers = int(os.environ.get("WORKERS", 2))

# Clase de worker: uvicorn para FastAPI async
worker_class = "uvicorn.workers.UvicornWorker"

# Bind al puerto configurado
bind = f"0.0.0.0:{os.environ.get('PORT', '8001')}"

# Timeouts
timeout = 120
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
