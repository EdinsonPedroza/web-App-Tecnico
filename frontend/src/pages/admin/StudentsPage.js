import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from 'sonner';
import { Plus, Pencil, Trash2, Loader2, GraduationCap, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';
import api from '@/lib/api';

const DEFAULT_MODULE = 1;

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', cedula: '', password: '', phone: '', program_id: '', program_ids: [], course_ids: [], program_modules: {}, program_statuses: {}, estado: 'activo' });
  const [saving, setSaving] = useState(false);
  const [filterProgram, setFilterProgram] = useState('all');
  const [filterModule, setFilterModule] = useState('all');
  const [filterEstado, setFilterEstado] = useState('all'); // Show all students by default, including recovery/failed
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [programSearch, setProgramSearch] = useState('');
  const [courseSearch, setCourseSearch] = useState('');

  const fetchData = useCallback(async () => {
    try {
      // Fetch students with optional estado filter
      const studentParams = filterEstado === 'all' ? '?role=estudiante' : `?role=estudiante&estado=${filterEstado}`;
      const [studRes, progRes, courseRes] = await Promise.all([
        api.get(`/users${studentParams}`),
        api.get('/programs'),
        api.get('/courses')
      ]);
      setStudents(studRes.data);
      setPrograms(progRes.data);
      setCourses(courseRes.data);
    } catch (err) {
      toast.error('Error cargando datos');
    } finally {
      setLoading(false);
    }
  }, [filterEstado]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const filtered = students.filter(s => {
    const matchesSearch = (s.name || '').toLowerCase().includes(search.toLowerCase()) || (s.cedula || '').includes(search);
    
    // For program filter: check if student has this program
    let matchesProgram = filterProgram === 'all';
    if (!matchesProgram) {
      const studentProgramIds = s.program_ids || (s.program_id ? [s.program_id] : []);
      matchesProgram = studentProgramIds.some(id => String(id) === String(filterProgram));
    }
    
    // For module filter: check if student has this module in any of their programs
    let matchesModule = filterModule === 'all';
    if (!matchesModule) {
      if (s.program_modules) {
        // New structure: check if any program has this module
        matchesModule = Object.values(s.program_modules).some(m => String(m) === filterModule);
      } else if (s.module) {
        // Old structure: fallback to global module
        matchesModule = String(s.module) === filterModule;
      }
    }
    
    const matchesEstado = filterEstado === 'all' || (s.estado || 'activo') === filterEstado;
    return matchesSearch && matchesProgram && matchesModule && matchesEstado;
  });
  
  const totalPages = Math.ceil(filtered.length / pageSize);
  const paginatedStudents = filtered.slice((page - 1) * pageSize, page * pageSize);
  
  const getProgramName = (id) => programs.find(p => p.id === id)?.name || 'Sin asignar';
  const getProgramShortName = (id) => {
    const program = programs.find(p => p.id === id);
    if (!program || !program.name) return 'N/A';
    // Strip leading "Técnico [Laboral] [en/de/para]" prefix for cleaner display
    const cleaned = program.name.replace(/^[Tt][eé]cnico\s+([Ll]aboral\s+)?([Ee]n\s+|[Dd]e\s+|[Pp]ara\s+)?/, '');
    return cleaned.length > 0 ? cleaned : program.name;
  };
  
  // Get all program names for a student (supports both program_id and program_ids)
  const getStudentPrograms = (student) => {
    const programIds = student.program_ids || (student.program_id ? [student.program_id] : []);
    if (programIds.length === 0) return [{ id: null, name: 'Sin asignar' }];
    return programIds.map(id => ({
      id,
      name: getProgramShortName(id)
    }));
  };
  
  const initials = (name) => {
    if (!name) return '??';
    return name.split(' ').filter(w => w.length > 0).map(w => w[0]).join('').substring(0, 2).toUpperCase();
  };

  // Get which courses a student is enrolled in
  const getStudentCourseIds = (studentId) => courses.filter(c => (c.student_ids || []).includes(studentId)).map(c => c.id);

  // Determine if a group/course is compatible with a student's current module for a given program.
  // - If studentModule == 1: student can join groups where module 1 hasn't started yet (today < module_dates["1"].start)
  // - If studentModule == 2: student can join groups where module 1 has already started (module_dates["1"].start <= today)
  const isCourseCompatibleWithModule = (course, studentModule) => {
    const today = new Date().toISOString().slice(0, 10);
    const moduleDates = course.module_dates || {};
    const mod1Dates = moduleDates['1'] || moduleDates[1] || null;
    const mod1Start = mod1Dates?.start || null;

    if (studentModule === 1) {
      // Student is in module 1: only show groups where module 1 hasn't started yet
      return !mod1Start || mod1Start > today;
    } else if (studentModule >= 2) {
      // Student is in module 2+: only show groups where module 1 has already started
      return mod1Start && mod1Start <= today;
    }
    return true;
  };

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', cedula: '', password: '', phone: '', program_id: '', program_ids: [], course_ids: [], program_modules: {}, program_statuses: {}, estado: 'activo' });
    setProgramSearch('');
    setCourseSearch('');
    setDialogOpen(true);
  };

  const openEdit = (student) => {
    setEditing(student);
    // Support both single program_id and multiple program_ids
    const studentProgramIds = student.program_ids || (student.program_id ? [student.program_id] : []);
    
    // Initialize program_modules from student data or create empty object
    const programModules = student.program_modules || {};
    // If student has old 'module' field but no program_modules, migrate it
    if (!student.program_modules && student.module && studentProgramIds.length > 0) {
      studentProgramIds.forEach(progId => {
        programModules[progId] = student.module;
      });
    }

    const programStatuses = student.program_statuses || {};
    
    setForm({
      name: student.name,
      cedula: student.cedula || '',
      password: '',
      phone: student.phone || '',
      program_id: student.program_id || '',
      program_ids: studentProgramIds,
      course_ids: getStudentCourseIds(student.id),
      program_modules: programModules,
      program_statuses: programStatuses,
      estado: student.estado || 'activo'
    });
    setProgramSearch('');
    setCourseSearch('');
    setDialogOpen(true);
  };

  const toggleCourse = (courseId) => {
    setForm(prev => {
      const courseIds = prev.course_ids || [];
      const isRemoving = courseIds.includes(courseId);
      if (isRemoving) {
        return { ...prev, course_ids: courseIds.filter(id => id !== courseId) };
      }
      // Enforce one group per program: remove any existing group for the same program
      const selectedCourse = courses.find(c => c.id === courseId);
      const sameProgramIds = selectedCourse
        ? courseIds.filter(id => {
            const c = courses.find(x => x.id === id);
            return c && c.program_id === selectedCourse.program_id;
          })
        : [];
      const filteredIds = courseIds.filter(id => !sameProgramIds.includes(id));
      return { ...prev, course_ids: [...filteredIds, courseId] };
    });
  };

  const toggleProgram = (programId) => {
    setForm(prev => {
      const programIds = prev.program_ids || [];
      const programModules = prev.program_modules || {};
      const programStatuses = prev.program_statuses || {};
      const isAdding = !programIds.includes(programId);
      
      const newProgramIds = isAdding
        ? [...programIds, programId]
        : programIds.filter(id => id !== programId);
      
      // Initialize module to DEFAULT_MODULE when adding a new program, remove when removing program
      const newProgramModules = { ...programModules };
      const newProgramStatuses = { ...programStatuses };
      if (isAdding) {
        newProgramModules[programId] = DEFAULT_MODULE;
        newProgramStatuses[programId] = "activo";
      } else {
        delete newProgramModules[programId];
        delete newProgramStatuses[programId];
      }
      
      return {
        ...prev,
        program_ids: newProgramIds,
        program_modules: newProgramModules,
        program_statuses: newProgramStatuses,
      };
    });
  };

  const handleSave = async () => {
    if (!form.name.trim() || (!editing && !form.cedula.trim())) { toast.error('Nombre y cédula requeridos'); return; }
    if (!editing && !form.password) { toast.error('Contraseña requerida'); return; }
    
    // Rule 1: Students must be enrolled in at least one technical program
    if (!form.program_ids || form.program_ids.length === 0) {
      toast.error('Debes seleccionar al menos un programa técnico');
      return;
    }
    
    // Validate cédula: only numbers
    if (form.cedula && !/^\d+$/.test(form.cedula)) {
      toast.error('La cédula solo debe contener números');
      return;
    }
    
    // Password length validation
    if (form.password && form.password.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }
    
    // Validate program-group relationship: each program should have at least one group
    if (form.program_ids && form.program_ids.length > 0 && form.course_ids && form.course_ids.length > 0) {
      // Get the programs for each selected course
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
    
    setSaving(true);
    try {
      let studentId;
      if (editing) {
        const updateData = { 
          name: form.name, 
          cedula: form.cedula, // Always include cedula
          phone: form.phone, 
          program_id: form.program_id || null,
          program_ids: form.program_ids && form.program_ids.length > 0 ? form.program_ids : null,
          program_modules: form.program_modules && Object.keys(form.program_modules).length > 0 ? form.program_modules : null,
          program_statuses: form.program_statuses && Object.keys(form.program_statuses).length > 0 ? form.program_statuses : null,
          // Do not send estado when editing — let backend derive it from program_statuses
        };
        // Include password only if provided (optional when editing)
        if (form.password && form.password.trim()) {
          updateData.password = form.password;
        }
        await api.put(`/users/${editing.id}`, updateData);
        studentId = editing.id;
      } else {
        const createData = { 
          ...form, 
          role: 'estudiante',
          program_ids: form.program_ids && form.program_ids.length > 0 ? form.program_ids : null,
          program_modules: form.program_modules && Object.keys(form.program_modules).length > 0 ? form.program_modules : null,
          estado: form.estado || 'activo'
        };
        const res = await api.post('/users', createData);
        studentId = res.data.id;
      }

      // Update course enrollments — handle failures independently so a created student
      // is never silently lost if a particular enrollment request fails.
      const enrollmentErrors = [];
      for (const course of courses) {
        const isEnrolled = (course.student_ids || []).includes(studentId);
        const shouldBeEnrolled = (form.course_ids || []).includes(course.id);

        if (isEnrolled && !shouldBeEnrolled) {
          // Remove from course
          const newIds = (course.student_ids || []).filter(id => id !== studentId);
          try {
            await api.put(`/courses/${course.id}`, { student_ids: newIds });
          } catch (enrollErr) {
            enrollmentErrors.push(`Error al desinscribir del grupo "${course.name}": ${enrollErr.response?.data?.detail || enrollErr.message}`);
          }
        } else if (!isEnrolled && shouldBeEnrolled) {
          // Add to course
          const newIds = [...(course.student_ids || []), studentId];
          try {
            await api.put(`/courses/${course.id}`, { student_ids: newIds });
          } catch (enrollErr) {
            enrollmentErrors.push(`Inscripción en grupo "${course.name}" fallida: ${enrollErr.response?.data?.detail || enrollErr.message}`);
          }
        }
      }

      setDialogOpen(false);
      fetchData();

      // Show success only if all operations completed without enrollment errors
      if (enrollmentErrors.length === 0) {
        toast.success(editing ? 'Estudiante actualizado' : 'Estudiante creado');
      } else {
        // Show warning for each enrollment error so the user knows what failed
        const suffix = editing ? '' : ' (estudiante quedó creado sin inscribir en ese grupo)';
        enrollmentErrors.forEach(msg => {
          toast.warning(msg + suffix, { duration: 8000 });
        });
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error guardando estudiante');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este estudiante?')) return;
    try {
      await api.delete(`/users/${id}`);
      toast.success('Estudiante eliminado');
      fetchData();
    } catch (err) {
      toast.error('Error eliminando estudiante');
    }
  };


  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold font-heading">Estudiantes</h1>
            <p className="text-muted-foreground mt-1">Gestiona los estudiantes inscritos</p>
          </div>
          <Button onClick={openCreate}><Plus className="h-4 w-4" /> Nuevo Estudiante</Button>
        </div>

        <div className="flex flex-col gap-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Buscar por nombre o cédula..." className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            <Select value={filterProgram} onValueChange={setFilterProgram}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filtrar por técnico" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los técnicos</SelectItem>
                {programs.map(p => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={filterModule} onValueChange={setFilterModule}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Filtrar por módulo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los módulos</SelectItem>
                <SelectItem value="1">Módulo 1</SelectItem>
                <SelectItem value="2">Módulo 2</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterEstado} onValueChange={setFilterEstado}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Filtrar por estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="activo">Activos</SelectItem>
                <SelectItem value="egresado">Egresados</SelectItem>
                <SelectItem value="pendiente_recuperacion">Pendiente Recuperación</SelectItem>
                <SelectItem value="retirado">Retirados</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="text-sm text-muted-foreground">
            Mostrando {paginatedStudents.length > 0 ? ((page - 1) * pageSize + 1) : 0}-{Math.min(page * pageSize, filtered.length)} de {filtered.length} estudiantes
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : filtered.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <GraduationCap className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay estudiantes registrados</p>
          </CardContent></Card>
        ) : (
          <Card className="shadow-card overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Estudiante</TableHead>
                    <TableHead>Cédula</TableHead>
                    <TableHead className="min-w-[200px]">Programa</TableHead>
                    <TableHead>Módulo Actual</TableHead>
                    <TableHead>Grupos Inscritos</TableHead>
                    <TableHead>Teléfono</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paginatedStudents.map((s) => (
                    <TableRow key={s.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-8 w-8"><AvatarFallback className="bg-primary/10 text-primary text-xs">{initials(s.name)}</AvatarFallback></Avatar>
                          <span className="font-medium text-sm">{s.name || 'Sin nombre'}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground font-mono">{s.cedula}</TableCell>
                      <TableCell>
                        <div className="flex flex-col gap-1">
                          {getStudentPrograms(s).map((prog, idx) => (
                            <Badge key={prog.id ?? `unassigned-${idx}`} variant="secondary" className="text-xs whitespace-normal">
                              {prog.name}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        {(() => {
                          const studentProgramIds = s.program_ids || (s.program_id ? [s.program_id] : []);
                          if (studentProgramIds.length === 0) {
                            return <Badge variant="outline" className="text-xs font-mono">-</Badge>;
                          }
                          
                          // Use program_modules if available, otherwise fall back to global module
                          if (s.program_modules && Object.keys(s.program_modules).length > 0) {
                            return (
                              <div className="flex flex-col gap-1">
                                {studentProgramIds.map(progId => {
                                  const module = s.program_modules[progId];
                                  const progName = getProgramShortName(progId);
                                  return (
                                    <Badge key={progId} variant="outline" className="text-xs font-mono whitespace-nowrap">
                                      {progName}: Módulo {module || 1}
                                    </Badge>
                                  );
                                })}
                              </div>
                            );
                          } else if (s.module) {
                            // Fallback to old structure
                            return <Badge variant="outline" className="text-xs font-mono">Módulo {s.module}</Badge>;
                          } else {
                            return <Badge variant="outline" className="text-xs font-mono">-</Badge>;
                          }
                        })()}
                      </TableCell>
                      <TableCell>
                        {(() => {
                          const studentCourseIds = getStudentCourseIds(s.id);
                          if (studentCourseIds.length === 0) {
                            return <span className="text-sm text-muted-foreground">Sin grupos</span>;
                          }
                          const studentCourses = courses.filter(c => studentCourseIds.includes(c.id));
                          return (
                             <div className="flex flex-col gap-1">
                               {studentCourses.map(course => {
                                 const programName = getProgramShortName(course.program_id);
                                 return (
                                   <Badge key={course.id} variant="outline" className="text-xs rounded-md px-3 py-1">
                                     {course.name} <span className="text-muted-foreground ml-1">({programName})</span>
                                   </Badge>
                                 );
                               })}
                             </div>
                          );
                        })()}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">{s.phone || '-'}</TableCell>
                      <TableCell>
                        {(() => {
                          const studentProgramIds = s.program_ids || (s.program_id ? [s.program_id] : []);
                          if (s.program_statuses && studentProgramIds.length > 0) {
                            const statusLabel = (st) => {
                              if (st === 'activo') return 'Activo';
                              if (st === 'egresado') return 'Egresado';
                              if (st === 'retirado') return 'Retirado';
                              if (st === 'pendiente_recuperacion') return 'Pend. Rec.';
                              return st || 'Activo';
                            };
                            const statusVariant = (st) => {
                              if (st === 'activo') return 'success';
                              if (st === 'pendiente_recuperacion') return 'warning';
                              if (st === 'retirado') return 'destructive';
                              return 'secondary';
                            };
                            return (
                              <div className="flex flex-col gap-1">
                                {studentProgramIds.map(progId => {
                                  const st = s.program_statuses[progId] || s.estado || 'activo';
                                  return (
                                    <Badge key={progId} variant={statusVariant(st)} className="text-xs rounded-md font-medium">
                                      {getProgramShortName(progId)}: {statusLabel(st)}
                                    </Badge>
                                  );
                                })}
                              </div>
                            );
                          }
                          return (
                            <Badge variant={(s.estado || 'activo') === 'activo' ? 'success' : 'secondary'}>
                              {(s.estado || 'activo') === 'activo' ? 'Activo' : 'Egresado'}
                            </Badge>
                          );
                        })()}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Button variant="ghost" size="icon" onClick={() => openEdit(s)}><Pencil className="h-4 w-4" /></Button>
                          <Button variant="ghost" size="icon" onClick={() => handleDelete(s.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t">
                <div className="text-sm text-muted-foreground">
                  Página {page} de {totalPages}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Anterior
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    Siguiente
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </Card>
        )}
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editing ? 'Editar Estudiante' : 'Nuevo Estudiante'}</DialogTitle>
            <DialogDescription>Ingresa los datos del estudiante</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2"><Label>Nombre Completo</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Nombre del estudiante" /></div>
            <div className="space-y-2">
              <Label>Cédula</Label>
              <Input 
                type="text" 
                inputMode="numeric" 
                pattern="[0-9]*"
                value={form.cedula} 
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '');
                  setForm({ ...form, cedula: value });
                }} 
                placeholder="Número de cédula (solo números)" 
              />
              {editing && <p className="text-xs text-amber-600 dark:text-amber-500">⚠️ Cambiar la cédula puede afectar el acceso del estudiante. Verifica que no exista duplicado.</p>}
              <p className="text-xs text-muted-foreground">Solo se permiten números</p>
            </div>
            <div className="space-y-2">
              <Label>{editing ? 'Nueva Contraseña (Opcional)' : 'Contraseña'}</Label>
              <Input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder={editing ? "Dejar vacío para no cambiar" : "Contraseña inicial"} />
              {editing ? (
                <p className="text-xs text-muted-foreground">Dejar vacío si no deseas cambiar la contraseña. Mínimo 6 caracteres si se cambia.</p>
              ) : (
                <p className="text-xs text-muted-foreground">Mínimo 6 caracteres</p>
              )}
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-base">Programas Técnicos <span className="text-destructive">*</span> ({form.program_ids.length} seleccionados)</Label>
                {programs.length > 0 && (
                  <Button 
                    type="button" 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => {
                      if (form.program_ids.length === programs.length) {
                        setForm({ ...form, program_ids: [], course_ids: [] });
                      } else {
                        setForm({ ...form, program_ids: programs.map(p => p.id) });
                      }
                    }}
                  >
                    {form.program_ids.length === programs.length ? 'Deseleccionar todos' : 'Seleccionar todos'}
                  </Button>
                )}
              </div>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input 
                  placeholder="Buscar programas técnicos..." 
                  value={programSearch}
                  onChange={(e) => setProgramSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
              <div className="max-h-40 overflow-y-auto rounded-lg border p-3 space-y-2 bg-muted/20">
                {programs.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No hay programas disponibles</p>
                ) : (
                  programs
                    .filter(p => {
                      const name = String(p.name || '');
                      return name.toLowerCase().includes(programSearch.toLowerCase());
                    })
                    .map((p) => (
                      <div key={p.id} className="flex items-center gap-2">
                        <Checkbox 
                          checked={(form.program_ids || []).includes(p.id)} 
                          onCheckedChange={() => toggleProgram(p.id)} 
                        />
                        <span className="text-sm">{p.name}</span>
                      </div>
                    ))
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                <span className="text-destructive">Requerido.</span> Los estudiantes pueden inscribirse en varios técnicos simultáneamente
              </p>
            </div>
            <div className="space-y-2"><Label>Teléfono</Label><Input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="300 123 4567" /></div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-base">Grupos Inscritos ({form.course_ids.length} seleccionados)</Label>
                {(() => {
                  const filteredCourses = courses.filter(c => {
                    const matchesProgram = !form.program_ids.length || form.program_ids.includes(c.program_id);
                    if (!matchesProgram) return false;
                    if (form.program_modules && c.program_id) {
                      const studentModule = form.program_modules[c.program_id];
                      if (studentModule) {
                        const isCurrentlyEnrolled = (form.course_ids || []).includes(c.id);
                        if (!isCurrentlyEnrolled && !isCourseCompatibleWithModule(c, studentModule)) return false;
                      }
                    }
                    return true;
                  });
                  return filteredCourses.length > 0 && (
                    <Button 
                      type="button" 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => {
                        if (form.course_ids.length === filteredCourses.length) {
                          setForm({ ...form, course_ids: [] });
                        } else {
                          setForm({ ...form, course_ids: filteredCourses.map(c => c.id) });
                        }
                      }}
                    >
                      {form.course_ids.length === filteredCourses.length ? 'Deseleccionar todos' : 'Seleccionar todos'}
                    </Button>
                  );
                })()}
              </div>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input 
                  placeholder="Buscar grupos..." 
                  value={courseSearch}
                  onChange={(e) => setCourseSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
              <div className="max-h-36 overflow-y-auto rounded-lg border p-3 space-y-2">
                {(() => {
                  const today = new Date().toISOString().slice(0, 10);
                  const filteredCourses = courses.filter(c => {
                    const matchesProgram = !form.program_ids.length || form.program_ids.includes(c.program_id);
                    if (!matchesProgram) return false;
                    const courseName = String(c.name || '');
                    const matchesSearch = courseName.toLowerCase().includes(courseSearch.toLowerCase());
                    if (!matchesSearch) return false;
                    // Filter by module compatibility per program (applies to both new and existing students)
                    if (form.program_modules && c.program_id) {
                      const studentModule = form.program_modules[c.program_id];
                      if (studentModule) {
                        // Allow currently enrolled groups regardless of module (don't lock out existing)
                        const isCurrentlyEnrolled = (form.course_ids || []).includes(c.id);
                        if (!isCurrentlyEnrolled && !isCourseCompatibleWithModule(c, studentModule)) {
                          return false;
                        }
                      }
                    }
                    return true;
                  });
                  
                  if (courses.length === 0) {
                    return <p className="text-sm text-muted-foreground">No hay grupos creados</p>;
                  }
                  
                  if (filteredCourses.length === 0 && form.program_ids.length > 0) {
                    return <p className="text-sm text-muted-foreground">No hay grupos compatibles con el módulo del estudiante para los técnicos seleccionados</p>;
                  }
                  
                  if (filteredCourses.length === 0 && courseSearch) {
                    return <p className="text-sm text-muted-foreground">No se encontraron grupos que coincidan con la búsqueda</p>;
                  }
                  
                  return filteredCourses.map((c) => {
                    const programName = getProgramShortName(c.program_id);
                    const studentModule = form.program_modules?.[c.program_id];
                    const mod1Dates = c.module_dates?.['1'] || c.module_dates?.[1];
                    const mod1Start = mod1Dates?.start;
                    const moduleInfo = mod1Start
                      ? (mod1Start <= today ? 'Inscripción cerrada' : 'Inscripción abierta')
                      : 'Nuevo grupo';
                    return (
                      <div key={c.id} className="flex items-center gap-2">
                        <Checkbox checked={(form.course_ids || []).includes(c.id)} onCheckedChange={() => toggleCourse(c.id)} />
                        <span className="text-sm flex-1">{c.name}</span>
                        <span className="text-xs text-muted-foreground">({programName})</span>
                        <span className="text-xs text-muted-foreground italic">{moduleInfo}</span>
                      </div>
                    );
                  });
                })()}
              </div>
              <p className="text-xs text-muted-foreground">
                Se muestran grupos compatibles con el módulo del estudiante. Solo se puede elegir un grupo por técnico.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
            <Button onClick={handleSave} disabled={saving}>{saving && <Loader2 className="h-4 w-4 animate-spin" />}{editing ? 'Actualizar' : 'Crear'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
