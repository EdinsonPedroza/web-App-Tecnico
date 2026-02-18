# Escuela Técnica Virtual - PRD

## Problema Original
El usuario solicitó una aplicación web para una escuela técnica virtual con tres roles: Admin, Profesor y Estudiante.

## Roles y Funcionalidades

### Admin
- Gestiona programas técnicos, materias, cursos, profesores y estudiantes
- Asigna materias a programas específicos
- Asigna estudiantes a cursos
- Login con email y contraseña

### Profesor  
- Selecciona curso a gestionar al iniciar sesión
- Crea actividades con archivos adjuntos y fechas límite
- Gestiona notas en vista tipo hoja de cálculo
- Sube videos de clase (enlaces de YouTube)

### Estudiante
- Login con cédula y contraseña
- Ve actividades: Activas, No Disponibles, Bloqueadas (vencidas)
- Entrega actividades con archivos adjuntos
- Ve notas por materia y promedio general

## Stack Tecnológico
- **Frontend:** React, Vite, Tailwind CSS, shadcn/ui
- **Backend:** Python, FastAPI, Motor (MongoDB async)
- **Base de datos:** MongoDB
- **Autenticación:** JWT

## Arquitectura
```
/app
├── backend/
│   ├── server.py       # API FastAPI
│   ├── uploads/        # Archivos subidos
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/ # Componentes UI
    │   ├── pages/      # Páginas por rol
    │   └── context/    # AuthContext
    └── package.json
```

## Funcionalidades Implementadas

### Fecha: 2026-02-15
- [x] Sistema de autenticación JWT para 3 roles
- [x] Dashboard de Admin con CRUD completo
- [x] Dashboard de Profesor con gestión de cursos
- [x] Dashboard de Estudiante con actividades y notas
- [x] Subida de archivos para actividades (profesor)
- [x] Subida de archivos para entregas (estudiante)
- [x] Selector de programa al crear/editar materias
- [x] Asignación de cursos a estudiantes
- [x] Estados de actividad: Activa, No Disponible, Bloqueada
- [x] Vista tipo hoja de cálculo para notas
- [x] Videos de clase con enlaces de YouTube

## Credenciales de Prueba
**NOTA:** Ver el archivo `USUARIOS_Y_CONTRASEÑAS.txt` en la raíz del proyecto para todas las credenciales actuales.

Las credenciales reales del sistema son:
- **Admin:** laura.torres@educando.com / Admin2026*LT
- **Profesor:** diana.silva@educando.com / Profe2026*DS
- **Estudiante:** Cédula 1001234567 / Estud2026*SM (Ver USUARIOS_Y_CONTRASEÑAS.txt para todas las credenciales)

## Backlog

### P1 - Alta Prioridad
- [ ] Scripts de despliegue (Docker, docker-compose)
- [ ] Documentación de configuración

### P2 - Media Prioridad
- [ ] Notificaciones por email
- [ ] Exportar notas a Excel
- [ ] Recuperación de contraseña

### P3 - Baja Prioridad
- [ ] Dashboard analítico para admin
- [ ] Modo oscuro
- [ ] App móvil
