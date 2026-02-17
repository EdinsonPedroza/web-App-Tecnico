# Fix: Subjects Not Appearing in Admin Materias Tab

## Problem
The subjects for the three technical programs were not appearing in the Admin's "Materias" tab, even though they were defined in the code.

## Root Cause
The `create_initial_data()` function in `backend/server.py` was checking if the admin user existed at startup. If the admin existed (from a previous initialization), the function would return early without verifying or creating the programs and subjects. This meant that if the database was initialized before but the subjects weren't created, they would never be created.

## Solution
Modified the `create_initial_data()` function to:
1. Always ensure programs and subjects exist (using upsert operations)
2. Only skip user creation if the admin user already exists
3. Print a message indicating what was done

## Changes Made
**File**: `backend/server.py`

**Before**:
```python
async def create_initial_data():
    """Crea los usuarios y datos iniciales si no existen"""
    # Verificar si ya existe el admin
    admin = await db.users.find_one({"email": "admin@educando.com"})
    if admin:
        return  # Ya existen datos
    
    print("Creando datos iniciales...")
    
    # Crear programas con sus módulos y materias
    programs = [...]
```

**After**:
```python
async def create_initial_data():
    """Crea los usuarios y datos iniciales si no existen"""
    print("Verificando y creando datos iniciales...")
    
    # Crear programas con sus módulos y materias (siempre se verifican y crean si no existen)
    programs = [...]
    
    # ... (programs and subjects creation code)
    
    # Crear usuarios solo si no existe el admin
    admin = await db.users.find_one({"email": "admin@educando.com"})
    if admin:
        print("Los usuarios ya existen, solo se verificaron/actualizaron programas y materias")
        return  # Los usuarios ya existen
    
    print("Creando usuarios iniciales...")
    users = [...]
```

## Programs and Subjects Created
The following programs and their subjects are now ensured to exist:

### 1. Técnico en Asistencia Administrativa
- **MÓDULO 1**: Fundamentos de Administración, Herramientas Ofimáticas, Gestión Documental y Archivo, Atención al Cliente y Comunicación Organizacional, Legislación Laboral y Ética Profesional
- **MÓDULO 2**: Contabilidad Básica, Nómina y Seguridad Social Aplicada, Control de Inventarios y Logística, Inglés Técnico / Competencias Ciudadanas, Proyecto Integrador Virtual

### 2. Técnico en Seguridad y Salud en el Trabajo
- **MÓDULO 1**: Fundamentos en Seguridad y Salud en el Trabajo, Administración en salud, Condiciones de seguridad, Matemáticas, Psicología del Trabajo
- **MÓDULO 2**: Comunicación oral y escrita, Sistema de gestión de seguridad y salud del trabajo, Anatomía y fisiología, Medicina preventiva del trabajo, Ética profesional, Gestión ambiental, Proyecto de grado

### 3. Técnico Laboral en Atención a la Primera Infancia
- **MÓDULO 1**: Inglés I, Proyecto de vida, Construcción social de la infancia, Perspectiva del desarrollo infantil, Salud y nutrición, Lenguaje y educación infantil, Juego y otras formas de comunicación, Educación y pedagogía
- **MÓDULO 2**: Inglés II, Construcción del mundo Matemático, Dificultades en el aprendizaje, Estrategias del aula, Trabajo de grado, Investigación, Práctica - Informe

## Testing
To verify the fix:
1. Restart the backend server
2. Log in as admin (admin@educando.com / admin123)
3. Navigate to the "Materias" tab
4. All subjects for all three programs should now be visible
5. Use the filters to view subjects by program and module

## Note
The subjects are created using upsert operations, so running the startup function multiple times will not create duplicates. It will only create subjects that don't already exist.
