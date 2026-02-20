# Documentación Técnica – Web App Técnico

## Procesos Automáticos Programados (Scheduler)

### Hora y Zona Horaria

El proceso automático de **cierre de módulos, promociones y revisión de fechas de recuperación** se ejecuta diariamente a las **02:00 AM hora Colombia** (zona horaria `America/Bogota`, UTC‑5).

| Parámetro         | Valor                                      |
|-------------------|--------------------------------------------|
| Hora de ejecución | 02:00 AM                                   |
| Zona horaria      | `America/Bogota` (Colombia, UTC-5)         |
| Frecuencia        | Una vez por día                            |
| Implementación    | APScheduler `CronTrigger` con `ZoneInfo`   |

La configuración relevante en `backend/server.py`:

```python
from zoneinfo import ZoneInfo
from apscheduler.triggers.cron import CronTrigger

scheduler.add_job(
    check_and_close_modules,
    CronTrigger(hour=2, minute=0, timezone=ZoneInfo("America/Bogota")),
    id='auto_close_modules',
    replace_existing=True
)
```

### Comportamiento Idempotente

El job es **idempotente**: antes de cerrar un módulo, consulta la colección `module_closures` en MongoDB para verificar si ya existe un registro con el mismo `program_id`, `module_number` y `closed_date`. Si el registro existe, **no** vuelve a ejecutar el cierre. Esto garantiza que aunque el proceso se reinicie o el cron dispare varias veces, un módulo nunca se cierra dos veces.

```
module_closures
└── { program_id, module_number, closed_date }  ← clave de idempotencia
```

### Recomendación en Render

Para evitar ejecuciones múltiples en producción:

1. **Usar un único Web Service** (no escalar a múltiples instancias). El scheduler corre en el mismo proceso de la aplicación con APScheduler, que es suficiente para un solo dyno.
2. Si en el futuro se necesita escalar horizontalmente, extraer el job a un **Worker Service** separado en Render (sin `web` routing) para que solo una instancia ejecute el scheduler.
3. El mecanismo idempotente de `module_closures` actúa como segunda línea de defensa incluso si hubiera múltiples instancias.

---

## Panel de Recuperaciones – Identificador de Estudiante

El panel de recuperaciones (`/admin/recoveries`) muestra como **identificador principal** de cada estudiante:

- **Nombre completo** (campo `student_name`)
- **Cédula** (campo `student_cedula`, prefijado con `CC`) cuando está disponible

El ID técnico UUID se muestra en una línea secundaria de menor prominencia para referencia interna.

La API `/api/admin/recovery-panel` devuelve por cada estudiante:

```json
{
  "student_id": "<UUID>",
  "student_name": "Nombre Completo",
  "student_cedula": "1001234567",
  "failed_subjects": [...]
}
```

Si un estudiante no tiene cédula registrada, el campo `student_cedula` es `null` y no se muestra el prefijo `CC`.
