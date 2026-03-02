# Frontend — Educando

Aplicación React (JavaScript) para la plataforma educativa Educando.

## Tecnologías

- **React** con JavaScript (Create React App + CRACO)
- **React Router v7** para navegación
- **TailwindCSS** para estilos
- **Radix UI** para componentes de UI accesibles
- **React Hook Form + Zod** para formularios y validación
- **Axios** para peticiones HTTP al backend

## Desarrollo

```bash
# Desde la raíz del proyecto con hot-reload:
docker compose -f docker-compose.dev.yml up --build frontend
```

El frontend queda disponible en http://localhost:3000.

## Estructura de carpetas

```
frontend/
├── public/          # Archivos estáticos públicos
├── src/
│   ├── components/  # Componentes reutilizables de UI
│   ├── pages/       # Vistas/páginas de la aplicación
│   ├── hooks/       # Custom hooks
│   ├── lib/         # Utilidades y configuración de Axios
│   └── App.js       # Componente raíz y configuración de rutas
├── Dockerfile        # Imagen de producción (build + nginx)
├── Dockerfile.dev    # Imagen de desarrollo (yarn start)
└── package.json
```

## Build de producción

El build de producción se genera automáticamente al hacer deploy en Render.
Para generarlo localmente:

```bash
docker compose up --build frontend
```
