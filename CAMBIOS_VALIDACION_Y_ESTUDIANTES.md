# Resumen de Cambios - Validación de Contraseñas y Gestión de Estudiantes

## Fecha: 2026-02-17

## Cambios Implementados

### 1. ✅ Validación de Contraseñas (Mínimo 6 Caracteres)

**Problema:** Cuando se creaba un usuario con una contraseña menor a 6 dígitos, el sistema arrojaba un error del backend sin previo aviso.

**Solución:** Se agregó validación en el frontend ANTES de enviar al backend:

#### Archivos Modificados:
- `frontend/src/pages/admin/StudentsPage.js`
- `frontend/src/pages/admin/TeachersPage.js`
- `frontend/src/pages/editor/EditorPage.js`

#### Cambios:
1. Validación en la función `handleSave`/`handleCreate`:
   ```javascript
   if (form.password && form.password.length < 6) {
     toast.error('La contraseña debe tener al menos 6 caracteres');
     return;
   }
   ```

2. Texto informativo debajo del campo de contraseña:
   - "Mínimo 6 caracteres" (para crear usuario)
   - "Mínimo 6 caracteres si se cambia" (para editar usuario)

**Resultado:** Ahora el usuario recibe un mensaje claro antes de intentar guardar, evitando errores del backend.

---

### 2. ✅ Validación de Programas y Grupos en Estudiantes

**Problema:** Un estudiante podía seleccionar 3 programas técnicos pero solo 1 grupo, lo cual es incorrecto ya que cada programa debe tener al menos un grupo asignado.

**Solución:** Se agregó validación para asegurar que cada programa técnico seleccionado tenga al menos un grupo.

#### Archivo Modificado:
- `frontend/src/pages/admin/StudentsPage.js`

#### Cambio:
```javascript
// Validate program-group relationship: each program should have at least one group
if (form.program_ids && form.program_ids.length > 0 && form.course_ids && form.course_ids.length > 0) {
  const selectedCourses = courses.filter(c => form.course_ids.includes(c.id));
  const courseProgramIds = selectedCourses.map(c => c.program_id);
  
  // Check that each selected program has at least one group
  for (const programId of form.program_ids) {
    if (!courseProgramIds.includes(programId)) {
      const programName = programs.find(p => p.id === programId)?.name || 'Programa';
      toast.error(`Debe seleccionar al menos un grupo para el programa: ${programName}`);
      return;
    }
  }
}
```

**Resultado:** El sistema ahora muestra un mensaje claro indicando qué programa necesita un grupo, por ejemplo:
- "Debe seleccionar al menos un grupo para el programa: Técnico en Sistemas"

---

### 3. ✅ Visualización de Programas Asignados

**Problema:** En la pestaña de gestión de estudiantes del admin, aparecía "Sin asignar" en la columna de programas, incluso cuando el estudiante estaba inscrito en programas.

**Causa:** El código solo mostraba `program_id` (singular) en lugar de `program_ids` (plural, que soporta múltiples programas).

**Solución:** Se creó una nueva función `getStudentPrograms()` que:
1. Soporta tanto `program_id` como `program_ids`
2. Muestra TODOS los programas en los que está inscrito el estudiante
3. Muestra "Sin asignar" solo si realmente no tiene programas

#### Archivo Modificado:
- `frontend/src/pages/admin/StudentsPage.js`

#### Cambios:
```javascript
// Get all program names for a student (supports both program_id and program_ids)
const getStudentPrograms = (student) => {
  const programIds = student.program_ids || (student.program_id ? [student.program_id] : []);
  if (programIds.length === 0) return [{ id: null, name: 'Sin asignar' }];
  return programIds.map(id => ({
    id,
    name: getProgramShortName(id)
  }));
};
```

Actualización del renderizado en la tabla:
```jsx
<TableCell>
  <div className="flex flex-col gap-1">
    {getStudentPrograms(s).map((prog, idx) => (
      <Badge key={prog.id || idx} variant="secondary" className="text-xs whitespace-normal">
        {prog.name}
      </Badge>
    ))}
  </div>
</TableCell>
```

**Resultado:** Ahora se muestran TODOS los programas técnicos en los que está inscrito cada estudiante, cada uno en su propio badge.

---

### 4. ✅ Endpoint para Configurar Módulo 1 en Todos los Estudiantes

**Problema:** Se necesitaba que todos los estudiantes existentes estuvieran en Módulo 1.

**Solución:** Se creó un endpoint de administrador para actualizar todos los estudiantes a Módulo 1.

#### Archivo Modificado:
- `backend/server.py`

#### Cambio:
```python
@api_router.post("/admin/set-all-students-module-1")
async def set_all_students_module_1(user=Depends(get_current_user)):
    """Admin endpoint to set all existing students to Module 1"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede realizar esta operación")
    
    # Update all students to module 1
    result = await db.users.update_many(
        {"role": "estudiante"},
        {"$set": {"module": 1}}
    )
    
    return {
        "message": f"Se actualizaron {result.modified_count} estudiantes al Módulo 1",
        "modified_count": result.modified_count
    }
```

**Cómo ejecutar:** Se incluye un script bash en `/tmp/set_students_module_1.sh` que:
1. Se autentica como administrador
2. Llama al endpoint
3. Muestra el resultado

**Ejecución:**
```bash
# Configurar variables (opcional, valores por defecto incluidos)
export BACKEND_URL="http://localhost:8000"
export ADMIN_EMAIL="admin@educando.com"
export ADMIN_PASSWORD="admin123"

# Ejecutar script
./set_students_module_1.sh
```

---

## Resumen de Mejoras

| #  | Problema | Solución | Estado |
|----|----------|----------|--------|
| 1  | Error al crear contraseña < 6 caracteres | Validación frontend + mensaje claro | ✅ Resuelto |
| 2  | Permitía 3 programas con 1 solo grupo | Validación que requiere 1 grupo por programa | ✅ Resuelto |
| 3  | Mostraba "Sin asignar" cuando había programas | Muestra todos los programas inscritos (program_ids) | ✅ Resuelto |
| 4  | Estudiantes necesitaban estar en Módulo 1 | Endpoint + script para actualización masiva | ✅ Resuelto |

---

## Archivos Modificados

1. `frontend/src/pages/admin/StudentsPage.js`
2. `frontend/src/pages/admin/TeachersPage.js`
3. `frontend/src/pages/editor/EditorPage.js`
4. `backend/server.py`
5. `/tmp/set_students_module_1.sh` (script de utilidad)

---

## Notas Técnicas

### Sobre la Promoción de Módulos

El problema menciona que "SE DEBE PROMOVER POR SEPARADO EL MODULO DE SU RESPECTIVO TECNICO". El sistema actual tiene:
- Campo `module` global por estudiante (1 o 2)
- Cada curso/grupo tiene `module_dates` con fechas específicas por módulo
- Los estudiantes se inscriben en cursos/grupos específicos de cada programa

La promoción actual es global (un solo botón por estudiante). Para hacer promoción por programa técnico, se requeriría cambiar el modelo de datos para tener:
```javascript
student.module_progress = {
  "program_id_1": { module: 1 },
  "program_id_2": { module: 2 }
}
```

Esto sería un cambio mayor en el modelo de datos. Por ahora, el campo `module` del estudiante sirve como indicador general, mientras que el seguimiento real de progreso se hace a través de los cursos en los que está inscrito.

---

## Testing

Para probar los cambios manualmente:

1. **Contraseñas:**
   - Ir a Admin → Estudiantes → Nuevo Estudiante
   - Intentar crear con contraseña de 5 caracteres
   - Debe mostrar: "La contraseña debe tener al menos 6 caracteres"

2. **Programas y Grupos:**
   - Crear estudiante con 2 programas técnicos
   - Seleccionar grupo solo para 1 programa
   - Intentar guardar
   - Debe mostrar: "Debe seleccionar al menos un grupo para el programa: [nombre]"

3. **Visualización de Programas:**
   - Ir a Admin → Estudiantes
   - Ver la columna "Programa"
   - Debe mostrar todos los programas del estudiante, no "Sin asignar"

4. **Módulo 1:**
   - Ejecutar script `set_students_module_1.sh`
   - Verificar en Admin → Estudiantes que todos muestran "Módulo 1"
