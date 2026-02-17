# 💰 Cotización del Proyecto - Plataforma Educativa "Educando"

> **Fecha:** Febrero 2026  
> **Cliente:** Colegio técnico (amigo emprendedor)  
> **Proyecto:** Sistema de gestión académica web completo  
> **Estado:** Proyecto terminado y listo para despliegue

---

## 📋 Resumen del Proyecto

**Educando** es una plataforma web de gestión académica completa para instituciones de educación técnica en Colombia. Incluye gestión de estudiantes, profesores, administradores y editores con interfaces dedicadas para cada rol.

---

## 🔍 Inventario Técnico del Proyecto

| Elemento | Cantidad | Detalle |
|---|---|---|
| **Líneas de código backend** | ~1,935 | Python (FastAPI + MongoDB) |
| **Líneas de código frontend** | ~8,580 | React 19 + TypeScript |
| **Páginas completas** | 22 | Con lógica, validación y diseño |
| **Componentes UI** | 47 | Reutilizables con Radix UI |
| **Endpoints API** | ~50 | REST API completa con autenticación |
| **Colecciones en BD** | 9 | MongoDB con relaciones |
| **Archivos fuente** | 75+ | Frontend + Backend |
| **Dockerfiles** | 4 | Dev y producción |
| **Documentos/guías** | 30+ | Documentación completa |

---

## 🏗️ Desglose de Funcionalidades

### 1. Sistema de Autenticación y Seguridad
- Login multi-rol (4 roles: estudiante, profesor, admin, editor)
- Autenticación JWT con tokens de 7 días
- Encriptación de contraseñas con Bcrypt
- Rate limiting (5 intentos cada 5 minutos)
- Sanitización de inputs
- Control de acceso basado en roles (RBAC)

### 2. Módulo Estudiante (8 páginas)
- Selector de programa y curso
- Dashboard del estudiante
- Visualización de actividades y entregas
- Sistema de calificaciones
- Acceso a videos de clase
- Envío de trabajos con archivos adjuntos
- Control de fechas límite

### 3. Módulo Profesor (6 páginas)
- Selector de cursos asignados
- Dashboard de curso
- Creación y gestión de actividades
- Sistema de calificación (escala 0-5)
- Gestión de recuperaciones automáticas
- Subida de videos de clase
- Listado de estudiantes

### 4. Módulo Administrador (7 páginas)
- Dashboard con estadísticas del sistema
- Gestión de programas técnicos (CRUD completo)
- Gestión de materias por programa y módulo
- Gestión de profesores (crear, editar, eliminar)
- Gestión de estudiantes (matrícula, promoción, graduación)
- Gestión de cursos/grupos
- Operaciones masivas (módulo 1 para todos)

### 5. Módulo Editor (1 página)
- Creación y gestión de cuentas de administrador

### 6. Sistema de Calificaciones
- Calificación por actividad
- Cálculo automático de nota de recuperación
- Flujo de aprobación/rechazo de recuperaciones
- Habilitación selectiva de recuperaciones

### 7. Gestión de Archivos
- Subida y descarga de archivos
- Videos de clase (enlaces YouTube)
- Adjuntos en actividades y entregas

### 8. Infraestructura y DevOps
- 4 Dockerfiles (frontend/backend × dev/prod)
- 2 Docker Compose (desarrollo y producción)
- Configuración Nginx para producción
- Variables de entorno configurables
- Hot-reload en desarrollo

### 9. Programas Pre-configurados
- Técnico en Asistencia Administrativa (12 meses, 2 módulos, ~8 materias)
- Técnico en Atención a la Primera Infancia (12 meses, 2 módulos, ~8 materias)
- Técnico en Seguridad y Salud en el Trabajo (12 meses, 2 módulos, ~8 materias)

---

## ⏱️ Estimación de Horas de Desarrollo

| Fase | Horas estimadas | Descripción |
|---|---|---|
| Diseño y planificación | 25 h | Arquitectura, BD, wireframes, UX |
| Backend - Servidor y configuración | 10 h | FastAPI, CORS, middleware |
| Backend - Autenticación y seguridad | 25 h | JWT, bcrypt, rate limiting, RBAC |
| Backend - CRUD Usuarios (4 roles) | 20 h | Crear, editar, eliminar, filtrar |
| Backend - Programas y materias | 16 h | CRUD + lógica de módulos |
| Backend - Cursos y grupos | 16 h | Asignación profesores/estudiantes |
| Backend - Actividades | 16 h | CRUD + auto-numeración |
| Backend - Calificaciones | 24 h | Notas + lógica de recuperación |
| Backend - Entregas y archivos | 16 h | Subida, validación, fechas límite |
| Backend - Videos y estadísticas | 10 h | CRUD videos + dashboard stats |
| Frontend - Setup y configuración | 10 h | React, Tailwind, Radix UI, routing |
| Frontend - Auth y contexto | 16 h | Login, AuthContext, protección de rutas |
| Frontend - Módulo Estudiante (8 pág) | 50 h | 8 páginas completas con lógica |
| Frontend - Módulo Profesor (6 pág) | 45 h | 6 páginas + formularios complejos |
| Frontend - Módulo Admin (7 pág) | 50 h | 7 páginas + operaciones CRUD |
| Frontend - Módulo Editor (1 pág) | 8 h | Gestión de administradores |
| Frontend - Componentes compartidos | 35 h | 47 componentes reutilizables |
| Frontend - Validación de formularios | 16 h | React Hook Form + Zod |
| Frontend - Diseño responsivo | 16 h | Adaptación móvil/tablet/desktop |
| Infraestructura Docker | 16 h | Dockerfiles + Compose + Nginx |
| Pruebas y corrección de errores | 25 h | Testing manual y automatizado |
| Documentación | 15 h | 30+ guías y documentos |
| **TOTAL** | **~500 horas** | |

---

## 💵 Valoración del Proyecto

### Tarifas de referencia en Colombia (2025-2026)

| Nivel de desarrollador | Tarifa por hora (COP) | Tarifa por hora (USD) |
|---|---|---|
| Junior freelance | $30,000 - $45,000 | $7 - $11 |
| Mid-level freelance | $50,000 - $80,000 | $12 - $20 |
| Senior freelance | $80,000 - $150,000 | $20 - $37 |
| Agencia/empresa | $150,000 - $300,000 | $37 - $73 |

> **Nota:** Tasa de cambio de referencia: ~$4,100 COP = 1 USD

---

### 📊 Rangos de Precio según Contexto

#### Opción 1: Precio de Mercado (lo que vale realmente)
> Si una empresa o freelancer senior cobra por este trabajo

| Concepto | Cálculo | Total COP | Total USD |
|---|---|---|---|
| 500 horas × $80,000/hora | Tarifa mid-senior | **$40,000,000** | **~$9,750** |

**Rango:** $35,000,000 - $50,000,000 COP ($8,500 - $12,200 USD)

Este es el valor real del proyecto si lo cotizas a una empresa de software o un freelancer experimentado en Colombia.

---

#### Opción 2: Precio Justo (freelancer independiente)
> Precio razonable reconociendo el trabajo hecho, con un descuento de amistad

| Concepto | Cálculo | Total COP | Total USD |
|---|---|---|---|
| 500 horas × $50,000/hora | Tarifa mid-level | **$25,000,000** | **~$6,100** |

**Rango:** $20,000,000 - $28,000,000 COP ($4,900 - $6,800 USD)

---

#### ⭐ Opción 3: Precio Amigo (RECOMENDADO)
> Precio solidario para un amigo que está montando su colegio, pero que reconozca tu trabajo

| Concepto | Cálculo | Total COP | Total USD |
|---|---|---|---|
| 500 horas × $30,000/hora | Tarifa reducida | **$15,000,000** | **~$3,650** |

**Rango recomendado: $12,000,000 - $18,000,000 COP ($2,900 - $4,400 USD)**

### ¿Por qué este rango?

✅ **$12,000,000 COP (~$2,900 USD)** — Precio mínimo que deberías cobrar. Por debajo de esto estarías regalando tu trabajo. Equivale a menos de $24,000/hora, que es menos que un junior.

✅ **$15,000,000 COP (~$3,650 USD)** — El punto ideal. Es un descuento de más del 60% sobre el precio de mercado, pero aún reconoce el esfuerzo de ~500 horas de desarrollo.

✅ **$18,000,000 COP (~$4,400 USD)** — Techo del precio amigo. Sigue siendo menos de la mitad del valor de mercado, pero te compensa mejor.

---

#### Opción 4: Precio Mínimo Absoluto
> Solo si es un amigo MUY cercano y quieres ayudarlo al máximo

| Concepto | Total COP | Total USD |
|---|---|---|
| Mínimo viable | **$8,000,000** | **~$1,950** |

⚠️ **Advertencia:** A este precio estás cobrando ~$16,000 COP/hora (~$4 USD/hora), que está por debajo de cualquier tarifa profesional. Solo recomendado si hay un acuerdo adicional (participación en el negocio, mantenimiento pagado, etc.)

---

## 💡 Esquema de Pago Sugerido

Para facilitar el pago, especialmente si el colegio está empezando:

### Plan de pagos en 3 cuotas (sobre $15,000,000 COP):

| Cuota | Momento | Monto COP | Monto USD |
|---|---|---|---|
| 1ra cuota (40%) | Al entregar el proyecto | $6,000,000 | ~$1,460 |
| 2da cuota (30%) | A los 30 días | $4,500,000 | ~$1,100 |
| 3ra cuota (30%) | A los 60 días | $4,500,000 | ~$1,100 |
| **Total** | | **$15,000,000** | **~$3,660** |

### Plan alternativo en 6 cuotas:

| Cuota | Monto COP/mes |
|---|---|
| 6 cuotas mensuales iguales | $2,500,000/mes |
| **Total** | **$15,000,000** |

---

## 🖥️ Costos Recurrentes (Hosting y Mantenimiento)

El cliente debe saber que además del desarrollo hay costos mensuales:

### Hosting (obligatorio)

| Servicio | Costo mensual | Notas |
|---|---|---|
| **VPS básico** (DigitalOcean/Hetzner) | $40,000 - $80,000 COP ($10-20 USD) | 2GB RAM, suficiente para empezar |
| **VPS recomendado** (Railway/Render) | $80,000 - $160,000 COP ($20-40 USD) | Más fácil de administrar |
| **Dominio .com.co** | ~$50,000 COP/año ($12 USD/año) | educando.com.co o similar |
| **SSL (HTTPS)** | Gratis | Let's Encrypt incluido |

**Costo mensual estimado de hosting: $50,000 - $120,000 COP/mes ($12 - $30 USD)**

### Mantenimiento (recomendado)

| Tipo | Costo mensual sugerido | Incluye |
|---|---|---|
| **Básico** | $300,000 - $500,000 COP | Corrección de bugs, actualizaciones de seguridad |
| **Estándar** | $500,000 - $1,000,000 COP | Básico + pequeñas mejoras + soporte por WhatsApp |
| **Premium** | $1,000,000 - $2,000,000 COP | Estándar + nuevas funcionalidades + soporte prioritario |

---

## 📝 Lo que se Entrega

1. ✅ Código fuente completo (frontend + backend)
2. ✅ Base de datos configurada con datos iniciales
3. ✅ Dockerfiles para despliegue en cualquier servidor
4. ✅ 30+ documentos de guía y documentación
5. ✅ Guías paso a paso de despliegue (Railway, VPS, Docker)
6. ✅ Configuración de entornos (desarrollo y producción)
7. ✅ Capacitación básica del sistema (1-2 sesiones)

---

## 🤝 Recomendaciones Finales

### Lo que yo haría en tu lugar:

1. **Cobra mínimo $12,000,000 COP.** Tu trabajo vale eso y más. No regales tu tiempo.

2. **Cobra mantenimiento mensual.** Un colegio siempre va a necesitar ajustes, nuevas funcionalidades, reportes, etc. Esto te genera ingreso recurrente.

3. **Ofrece el plan de pagos.** Es más fácil para un colegio que está empezando pagar en cuotas.

4. **Incluye capacitación.** Dedica 2-3 horas a enseñarle cómo usar el sistema. Esto reduce las llamadas de soporte después.

5. **Deja claro el alcance.** Si pide nuevas funcionalidades después de la entrega, eso se cobra aparte.

6. **Firma un acuerdo simple.** Aunque sea un amigo, escribe lo que incluye y lo que no. Evita malentendidos.

7. **No cobres por debajo de $8,000,000 COP.** Este proyecto tiene ~10,500 líneas de código, 22 páginas, 50 endpoints, autenticación, calificaciones, Docker, documentación... es un proyecto serio.

---

## 📌 Resumen Rápido

| Concepto | Valor |
|---|---|
| **Valor de mercado** | $35,000,000 - $50,000,000 COP |
| **Precio justo** | $20,000,000 - $28,000,000 COP |
| ⭐ **Precio amigo recomendado** | **$12,000,000 - $18,000,000 COP** |
| **Precio mínimo absoluto** | $8,000,000 COP |
| **Hosting mensual** | $50,000 - $120,000 COP/mes |
| **Mantenimiento mensual** | $300,000 - $2,000,000 COP/mes |

---

*Este documento es una estimación basada en el análisis técnico del proyecto, las tarifas del mercado colombiano de desarrollo web, y la complejidad de las funcionalidades implementadas.*
