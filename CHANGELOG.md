# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y el proyecto utiliza [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.0.0] — Lanzamiento inicial

### Añadido

- Plataforma educativa completa con cuatro roles de usuario: **editor**, **admin**, **profesor** y **estudiante**.
- Gestión de **programas**, **módulos**, **materias** y **actividades**.
- Sistema de **calificaciones** con soporte para recuperación, promociones y egresados.
- **Cierre automático de módulos** según reglas académicas configurables.
- Almacenamiento de archivos en **AWS S3** (PDFs, recursos de actividades).
- Autenticación segura con **JWT** y contraseñas hasheadas con bcrypt.
- API REST con **FastAPI** (Python 3.11) y base de datos **MongoDB Atlas Flex**.
- Frontend **React** (JavaScript) con TailwindCSS y Radix UI.
- Despliegue en **Render** con pipeline automático desde GitHub.
- Más de 350 pruebas automatizadas en el backend.
