import os

# Número de workers para manejar carga concurrente.
# Fórmula recomendada: (2 × CPU cores) + 1
# Solo el worker 0 ejecuta el APScheduler para evitar race conditions.
workers = int(os.environ.get("WORKERS", 4))

# Counter for assigning sequential worker IDs
_worker_counter = 0

def post_fork(server, worker):
    """Assign a sequential WORKER_ID to each forked worker.

    Gunicorn does NOT set WORKER_ID automatically. Without this hook,
    os.environ.get("WORKER_ID") returns None in ALL workers, causing
    ALL of them to start the APScheduler (duplicating cron jobs).

    post_fork is called sequentially by the master process, so the
    global counter increment is safe (no concurrent access).
    """
    global _worker_counter
    os.environ["WORKER_ID"] = str(_worker_counter)
    _worker_counter += 1

# Clase de worker: uvicorn para FastAPI async
worker_class = "uvicorn.workers.UvicornWorker"

# Bind al puerto configurado
bind = f"0.0.0.0:{os.environ.get('PORT', '8001')}"

# Timeouts — aumentado a 300s para cierre de módulos (operación larga con 3000 estudiantes)
timeout = 300
graceful_timeout = 60
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Preload app para ahorrar memoria (shared memory entre workers)
preload_app = True

# Reiniciar workers periódicamente para evitar memory leaks
max_requests = 2000
max_requests_jitter = 100

# Worker connections para el worker único (asyncio maneja miles de conexiones concurrentes)
worker_connections = 2000

# Usar memoria compartida para heartbeat en contenedores (evita I/O en disco)
worker_tmp_dir = "/dev/shm"
