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
import { Plus, Pencil, Trash2, Loader2, GraduationCap, Search, ChevronLeft, ChevronRight, ArrowUpCircle } from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';
import api from '@/lib/api';

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', cedula: '', password: '', phone: '', program_id: '', program_ids: [], course_ids: [], module: '', grupo: '' });
  const [saving, setSaving] = useState(false);
  const [filterProgram, setFilterProgram] = useState('');
  const [filterModule, setFilterModule] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const fetchData = useCallback(async () => {
    try {
      const [studRes, progRes, courseRes] = await Promise.all([
        api.get('/users?role=estudiante'),
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
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const filtered = students.filter(s => {
    const matchesSearch = (s.name || '').toLowerCase().includes(search.toLowerCase()) || (s.cedula || '').includes(search);
    const matchesProgram = !filterProgram || s.program_id === filterProgram;
    const matchesModule = !filterModule || String(s.module) === filterModule;
    return matchesSearch && matchesProgram && matchesModule;
  });
  
  const totalPages = Math.ceil(filtered.length / pageSize);
  const paginatedStudents = filtered.slice((page - 1) * pageSize, page * pageSize);
  
  const getProgramName = (id) => programs.find(p => p.id === id)?.name || 'Sin asignar';
  const getProgramShortName = (id) => {
    const program = programs.find(p => p.id === id);
    if (!program || !program.name) return 'N/A';
    const words = program.name.split(' ');
    return words.length > 3 ? words.slice(2, 5).join(' ') : program.name;
  };
  const initials = (name) => {
    if (!name) return '??';
    return name.split(' ').filter(w => w.length > 0).map(w => w[0]).join('').substring(0, 2).toUpperCase();
  };
  
  // Format: MOD1-ENERO-2026 (with program short name prefix)
  const formatCourseInfo = (student) => {
    if (!student.module || !student.program_id) return '-';
    const monthNames = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'];
    const currentMonth = monthNames[new Date().getMonth()];
    const currentYear = new Date().getFullYear();
    const programShort = getProgramShortName(student.program_id);
    return `${programShort}-MOD${student.module}-${currentMonth}-${currentYear}`;
  };

  // Get which courses a student is enrolled in
  const getStudentCourseIds = (studentId) => courses.filter(c => (c.student_ids || []).includes(studentId)).map(c => c.id);

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', cedula: '', password: '', phone: '', program_id: '', program_ids: [], course_ids: [], module: '', grupo: '' });
    setDialogOpen(true);
  };

  const openEdit = (student) => {
    setEditing(student);
    // Support both single program_id and multiple program_ids
    const studentProgramIds = student.program_ids || (student.program_id ? [student.program_id] : []);
    setForm({
      name: student.name,
      cedula: student.cedula || '',
      password: '',
      phone: student.phone || '',
      program_id: student.program_id || '',
      program_ids: studentProgramIds,
      course_ids: getStudentCourseIds(student.id),
      module: student.module || '',
      grupo: student.grupo || ''
    });
    setDialogOpen(true);
  };

  const toggleCourse = (courseId) => {
    setForm(prev => ({
      ...prev,
      course_ids: prev.course_ids.includes(courseId)
        ? prev.course_ids.filter(id => id !== courseId)
        : [...prev.course_ids, courseId]
    }));
  };

  const toggleProgram = (programId) => {
    setForm(prev => ({
      ...prev,
      program_ids: prev.program_ids.includes(programId)
        ? prev.program_ids.filter(id => id !== programId)
        : [...prev.program_ids, programId]
    }));
  };

  const handleSave = async () => {
    if (!form.name.trim() || (!editing && !form.cedula.trim())) { toast.error('Nombre y cédula requeridos'); return; }
    if (!editing && !form.password) { toast.error('Contraseña requerida'); return; }
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
          module: form.module ? parseInt(form.module) : null,
          grupo: form.grupo || null
        };
        // Include password only if provided (optional when editing)
        if (form.password && form.password.trim()) {
          updateData.password = form.password;
        }
        await api.put(`/users/${editing.id}`, updateData);
        studentId = editing.id;
        toast.success('Estudiante actualizado');
      } else {
        const createData = { 
          ...form, 
          role: 'estudiante',
          program_ids: form.program_ids && form.program_ids.length > 0 ? form.program_ids : null,
          module: form.module ? parseInt(form.module) : null
        };
        const res = await api.post('/users', createData);
        studentId = res.data.id;
        toast.success('Estudiante creado');
      }

      // Update course enrollments
      for (const course of courses) {
        const isEnrolled = (course.student_ids || []).includes(studentId);
        const shouldBeEnrolled = form.course_ids.includes(course.id);

        if (isEnrolled && !shouldBeEnrolled) {
          // Remove from course
          const newIds = (course.student_ids || []).filter(id => id !== studentId);
          await api.put(`/courses/${course.id}`, { student_ids: newIds });
        } else if (!isEnrolled && shouldBeEnrolled) {
          // Add to course
          const newIds = [...(course.student_ids || []), studentId];
          await api.put(`/courses/${course.id}`, { student_ids: newIds });
        }
      }

      setDialogOpen(false);
      fetchData();
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

  const handlePromote = async (student) => {
    if (!student.module || student.module >= 2) {
      toast.error('El estudiante ya está en el módulo final');
      return;
    }
    if (!window.confirm(`¿Promover a ${student.name} al Módulo ${student.module + 1}?`)) return;
    try {
      await api.put(`/users/${student.id}/promote`);
      toast.success('Estudiante promovido exitosamente');
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error promoviendo estudiante');
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
                <SelectItem value="">Todos los técnicos</SelectItem>
                {programs.map(p => <SelectItem key={p.id} value={String(p.id)}>{p.name}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={filterModule} onValueChange={setFilterModule}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="Filtrar por módulo" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos los módulos</SelectItem>
                <SelectItem value="1">Módulo 1</SelectItem>
                <SelectItem value="2">Módulo 2</SelectItem>
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
                    <TableHead>Programa</TableHead>
                    <TableHead>Técnico-Módulo-Curso</TableHead>
                    <TableHead>Grupo</TableHead>
                    <TableHead>Cursos</TableHead>
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
                      <TableCell><Badge variant="secondary" className="text-xs truncate max-w-32">{getProgramName(s.program_id)}</Badge></TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-xs font-mono">{formatCourseInfo(s)}</Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">{s.grupo || '-'}</TableCell>
                      <TableCell><Badge variant="outline" className="text-xs">{getStudentCourseIds(s.id).length} cursos</Badge></TableCell>
                      <TableCell className="text-sm text-muted-foreground">{s.phone || '-'}</TableCell>
                      <TableCell><Badge variant={s.active !== false ? 'success' : 'destructive'}>{s.active !== false ? 'Activo' : 'Inactivo'}</Badge></TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          {s.module && s.module < 2 && (
                            <Button 
                              variant="ghost" 
                              size="icon" 
                              onClick={() => handlePromote(s)}
                              title="Promover al siguiente módulo"
                            >
                              <ArrowUpCircle className="h-4 w-4 text-success" />
                            </Button>
                          )}
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
              <Input value={form.cedula} onChange={(e) => setForm({ ...form, cedula: e.target.value })} placeholder="Número de cédula" />
              {editing && <p className="text-xs text-amber-600 dark:text-amber-500">⚠️ Cambiar la cédula puede afectar el acceso del estudiante. Verifica que no exista duplicado.</p>}
            </div>
            <div className="space-y-2">
              <Label>{editing ? 'Nueva Contraseña (Opcional)' : 'Contraseña'}</Label>
              <Input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder={editing ? "Dejar vacío para no cambiar" : "Contraseña inicial"} />
              {editing && <p className="text-xs text-muted-foreground">Dejar vacío si no deseas cambiar la contraseña</p>}
            </div>
            <div className="space-y-2">
              <Label>Programas Técnicos (Puede seleccionar múltiples)</Label>
              <div className="max-h-40 overflow-y-auto rounded-lg border p-3 space-y-2 bg-muted/20">
                {programs.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No hay programas disponibles</p>
                ) : programs.map((p) => (
                  <div key={p.id} className="flex items-center gap-2">
                    <Checkbox 
                      checked={form.program_ids.includes(p.id)} 
                      onCheckedChange={() => toggleProgram(p.id)} 
                    />
                    <span className="text-sm">{p.name}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-muted-foreground">
                Los estudiantes pueden inscribirse en varios técnicos simultáneamente
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Módulo</Label>
                <Select value={form.module} onValueChange={(v) => setForm({ ...form, module: v })}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar módulo" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Módulo 1</SelectItem>
                    <SelectItem value="2">Módulo 2</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Grupo (Mes y Año)</Label>
                <Input value={form.grupo} onChange={(e) => setForm({ ...form, grupo: e.target.value })} placeholder="ej: Enero 2025, Febrero 2025" />
              </div>
            </div>
            <div className="space-y-2"><Label>Teléfono</Label><Input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="300 123 4567" /></div>
            <div className="space-y-2">
              <Label>Cursos Inscritos</Label>
              <div className="max-h-36 overflow-y-auto rounded-lg border p-3 space-y-2">
                {courses.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No hay cursos creados</p>
                ) : courses.map((c) => (
                  <div key={c.id} className="flex items-center gap-2">
                    <Checkbox checked={form.course_ids.includes(c.id)} onCheckedChange={() => toggleCourse(c.id)} />
                    <span className="text-sm">{c.name}</span>
                  </div>
                ))}
              </div>
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
