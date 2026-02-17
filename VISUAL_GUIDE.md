# Visual Guide: Admin Materias Tab

## What the Admin Will See

After deploying this fix, when the admin logs into the system and navigates to the **Materias** (Subjects) tab, they will see:

### Page Header
```
Materias
Plan de estudios por programa y módulo

[Filter: Todos los programas ▼]  [Filter: Todos los módulos ▼]  [+ Nueva Materia]
```

### Filter Options

**Program Filter:**
- Todos los programas
- Técnico en Asistencia Administrativa
- Técnico Laboral en Atención a la Primera Infancia
- Técnico en Seguridad y Salud en el Trabajo

**Module Filter:**
- Todos los módulos
- Módulo 1
- Módulo 2

### Subject Cards (37 total)

Each subject appears as a card with:
- **Subject Name** (as the title)
- **Description** (or "Sin descripción")
- **Module Badge** (e.g., "Módulo 1")
- **Program Badge** (showing the program name)
- **Edit Button** (pencil icon)
- **Delete Button** (trash icon)

### Example Cards

#### Card 1
```
┌─────────────────────────────────────────────┐
│ Fundamentos de Administración          ✏️ 🗑️│
├─────────────────────────────────────────────┤
│ Sin descripción                             │
│                                              │
│ [Módulo 1]  [Técnico en Asistencia Admin...│
└─────────────────────────────────────────────┘
```

#### Card 2
```
┌─────────────────────────────────────────────┐
│ Inglés I                                ✏️ 🗑️│
├─────────────────────────────────────────────┤
│ Sin descripción                             │
│                                              │
│ [Módulo 1]  [Técnico Laboral en Atención...│
└─────────────────────────────────────────────┘
```

#### Card 3
```
┌─────────────────────────────────────────────┐
│ Fundamentos en Seguridad y Salud...    ✏️ 🗑️│
├─────────────────────────────────────────────┤
│ Sin descripción                             │
│                                              │
│ [Módulo 1]  [Técnico en Seguridad y Sal...│
└─────────────────────────────────────────────┘
```

### Complete Subject List (37 subjects)

#### Técnico en Asistencia Administrativa (10)

**MÓDULO 1:**
1. Fundamentos de Administración
2. Herramientas Ofimáticas
3. Gestión Documental y Archivo
4. Atención al Cliente y Comunicación Organizacional
5. Legislación Laboral y Ética Profesional

**MÓDULO 2:**
6. Contabilidad Básica
7. Nómina y Seguridad Social Aplicada
8. Control de Inventarios y Logística
9. Inglés Técnico / Competencias Ciudadanas
10. Proyecto Integrador Virtual

#### Técnico Laboral en Atención a la Primera Infancia (15)

**MÓDULO 1:**
1. Inglés I
2. Proyecto de vida
3. Construcción social de la infancia
4. Perspectiva del desarrollo infantil
5. Salud y nutrición
6. Lenguaje y educación infantil
7. Juego y otras formas de comunicación
8. Educación y pedagogía

**MÓDULO 2:**
9. Inglés II
10. Construcción del mundo Matemático
11. Dificultades en el aprendizaje
12. Estrategias del aula
13. Trabajo de grado
14. Investigación
15. Práctica - Informe

#### Técnico en Seguridad y Salud en el Trabajo (12)

**MÓDULO 1:**
1. Fundamentos en Seguridad y Salud en el Trabajo
2. Administración en salud
3. Condiciones de seguridad
4. Matemáticas
5. Psicología del Trabajo

**MÓDULO 2:**
6. Comunicación oral y escrita
7. Sistema de gestión de seguridad y salud del trabajo
8. Anatomía y fisiología
9. Medicina preventiva del trabajo
10. Ética profesional
11. Gestión ambiental
12. Proyecto de grado

### Grid Layout

The subjects are displayed in a responsive grid:
- **Desktop (xl)**: 3 columns
- **Tablet (md)**: 2 columns
- **Mobile**: 1 column

### Interactive Features

1. **Filter by Program**: Click the program dropdown to show only subjects from a specific program
2. **Filter by Module**: Click the module dropdown to show only subjects from a specific module
3. **Edit Subject**: Click the pencil icon to edit a subject's details
4. **Delete Subject**: Click the trash icon to delete a subject (with confirmation)
5. **Create New Subject**: Click the "Nueva Materia" button to add a new subject

### Visual Style

- Clean, modern interface with shadcn/ui components
- Steel blue color theme
- Card-based layout with hover effects
- Responsive design that works on all devices
- Clear visual hierarchy with badges and icons

### Empty State

If no subjects match the current filters, the page shows:
```
┌──────────────────────────────┐
│            📚                 │
│ No hay materias registradas  │
└──────────────────────────────┘
```

## Verification Steps

To verify the fix is working:

1. ✅ Log in as admin: `admin@educando.com` / `admin123`
2. ✅ Navigate to "Materias" in the sidebar
3. ✅ Verify you see 37 subject cards
4. ✅ Test the program filter - should show all 3 programs
5. ✅ Test the module filter - should show Módulo 1 and Módulo 2
6. ✅ Filter by each program to see its specific subjects
7. ✅ Verify all subject names match the list above

## Technical Details

- **Frontend**: `/frontend/src/pages/admin/SubjectsPage.js`
- **Backend API**: `GET /api/subjects` (returns all subjects)
- **Backend API**: `GET /api/programs` (returns all programs)
- **Database**: MongoDB collections: `subjects` and `programs`
- **Subject Schema**: `{id, name, program_id, module_number, description, active}`

## Success Criteria

✅ All 37 subjects are visible in the Admin panel
✅ Subjects are correctly associated with their programs
✅ Subjects are correctly associated with their modules
✅ Filters work correctly
✅ Edit and delete functions work for each subject
✅ Create new subject function works
