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
import { Plus, Pencil, Trash2, Loader2, GraduationCap, Search } from 'lucide-react';
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
  const [form, setForm] = useState({ name: '', cedula: '', password: '', phone: '', program_id: '', course_ids: [] });
  const [saving, setSaving] = useState(false);

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

  const filtered = students.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || (s.cedula || '').includes(search));
  const getProgramName = (id) => programs.find(p => p.id === id)?.name || 'Sin asignar';
  const initials = (name) => name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();

  // Get which courses a student is enrolled in
  const getStudentCourseIds = (studentId) => courses.filter(c => (c.student_ids || []).includes(studentId)).map(c => c.id);

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', cedula: '', password: '', phone: '', program_id: '', course_ids: [] });
    setDialogOpen(true);
  };

  const openEdit = (student) => {
    setEditing(student);
    setForm({
      name: student.name,
      cedula: student.cedula || '',
      password: '',
      phone: student.phone || '',
      program_id: student.program_id || '',
      course_ids: getStudentCourseIds(student.id)
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

  const handleSave = async () => {
    if (!form.name.trim() || (!editing && !form.cedula.trim())) { toast.error('Nombre y cédula requeridos'); return; }
    if (!editing && !form.password) { toast.error('Contraseña requerida'); return; }
    setSaving(true);
    try {
      let studentId;
      if (editing) {
        await api.put(`/users/${editing.id}`, { name: form.name, phone: form.phone, program_id: form.program_id || null });
        studentId = editing.id;
        toast.success('Estudiante actualizado');
      } else {
        const res = await api.post('/users', { ...form, role: 'estudiante' });
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

        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Buscar por nombre o cédula..." className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
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
                    <TableHead>Cursos</TableHead>
                    <TableHead>Teléfono</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filtered.map((s) => (
                    <TableRow key={s.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-8 w-8"><AvatarFallback className="bg-primary/10 text-primary text-xs">{initials(s.name)}</AvatarFallback></Avatar>
                          <span className="font-medium text-sm">{s.name}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground font-mono">{s.cedula}</TableCell>
                      <TableCell><Badge variant="secondary" className="text-xs truncate max-w-32">{getProgramName(s.program_id)}</Badge></TableCell>
                      <TableCell><Badge variant="outline" className="text-xs">{getStudentCourseIds(s.id).length} cursos</Badge></TableCell>
                      <TableCell className="text-sm text-muted-foreground">{s.phone || '-'}</TableCell>
                      <TableCell><Badge variant={s.active !== false ? 'success' : 'destructive'}>{s.active !== false ? 'Activo' : 'Inactivo'}</Badge></TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="icon" onClick={() => openEdit(s)}><Pencil className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete(s.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
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
            <div className="space-y-2"><Label>Cédula</Label><Input value={form.cedula} onChange={(e) => setForm({ ...form, cedula: e.target.value })} placeholder="Número de cédula" disabled={!!editing} /></div>
            {!editing && <div className="space-y-2"><Label>Contraseña</Label><Input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Contraseña inicial" /></div>}
            <div className="space-y-2">
              <Label>Programa</Label>
              <Select value={form.program_id} onValueChange={(v) => setForm({ ...form, program_id: v })}>
                <SelectTrigger><SelectValue placeholder="Seleccionar programa" /></SelectTrigger>
                <SelectContent>
                  {programs.map(p => <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>)}
                </SelectContent>
              </Select>
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
