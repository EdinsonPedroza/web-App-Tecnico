import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from 'sonner';
import { Plus, Pencil, Trash2, Loader2, ClipboardList, Users, BookOpen } from 'lucide-react';
import api from '@/lib/api';

export default function CoursesPage() {
  const [courses, setCourses] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', program_id: '', subject_id: '', teacher_id: '', year: 2025, student_ids: [] });
  const [saving, setSaving] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [cRes, pRes, sRes, tRes, stRes] = await Promise.all([
        api.get('/courses'), api.get('/programs'), api.get('/subjects'),
        api.get('/users?role=profesor'), api.get('/users?role=estudiante')
      ]);
      setCourses(cRes.data); setPrograms(pRes.data); setSubjects(sRes.data);
      setTeachers(tRes.data); setStudents(stRes.data);
    } catch (err) {
      toast.error('Error cargando datos');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const getName = (arr, id) => arr.find(i => i.id === id)?.name || '-';
  const filteredSubjects = form.program_id ? subjects.filter(s => s.program_id === form.program_id) : subjects;

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', program_id: '', subject_id: '', teacher_id: '', year: 2025, student_ids: [] });
    setDialogOpen(true);
  };

  const openEdit = (course) => {
    setEditing(course);
    setForm({ name: course.name, program_id: course.program_id, subject_id: course.subject_id, teacher_id: course.teacher_id, year: course.year, student_ids: course.student_ids || [] });
    setDialogOpen(true);
  };

  const toggleStudent = (studentId) => {
    setForm(prev => ({
      ...prev,
      student_ids: prev.student_ids.includes(studentId)
        ? prev.student_ids.filter(id => id !== studentId)
        : [...prev.student_ids, studentId]
    }));
  };

  const handleSave = async () => {
    if (!form.name.trim()) { toast.error('Nombre del curso requerido'); return; }
    setSaving(true);
    try {
      if (editing) {
        await api.put(`/courses/${editing.id}`, { name: form.name, teacher_id: form.teacher_id, student_ids: form.student_ids });
        toast.success('Curso actualizado');
      } else {
        await api.post('/courses', form);
        toast.success('Curso creado');
      }
      setDialogOpen(false);
      fetchData();
    } catch (err) {
      toast.error('Error guardando curso');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este curso?')) return;
    try { await api.delete(`/courses/${id}`); toast.success('Curso eliminado'); fetchData(); }
    catch (err) { toast.error('Error eliminando curso'); }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold font-heading">Cursos</h1>
            <p className="text-muted-foreground mt-1">Gestiona cursos y grupos</p>
          </div>
          <Button onClick={openCreate}><Plus className="h-4 w-4" /> Nuevo Curso</Button>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : courses.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <ClipboardList className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay cursos creados</p>
          </CardContent></Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {courses.map((c) => (
              <Card key={c.id} className="shadow-card hover:shadow-card-hover transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-sm font-heading">{c.name}</CardTitle>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => openEdit(c)}><Pencil className="h-3 w-3" /></Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleDelete(c.id)}><Trash2 className="h-3 w-3 text-destructive" /></Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <BookOpen className="h-4 w-4" />
                      <span className="truncate">{getName(programs, c.program_id)}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Users className="h-4 w-4" />
                      <span>Prof: {getName(teachers, c.teacher_id)}</span>
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      <Badge variant="secondary">{c.year}</Badge>
                      <Badge variant="outline">{c.student_ids?.length || 0} estudiantes</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editing ? 'Editar Curso' : 'Nuevo Curso'}</DialogTitle>
            <DialogDescription>Configura el curso y asigna estudiantes</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2"><Label>Nombre del Curso</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Ej: Fundamentos Admin - Grupo A" /></div>
            {!editing && (
              <>
                <div className="space-y-2">
                  <Label>Programa</Label>
                  <Select value={form.program_id} onValueChange={(v) => setForm({ ...form, program_id: v, subject_id: '' })}>
                    <SelectTrigger><SelectValue placeholder="Seleccionar" /></SelectTrigger>
                    <SelectContent>{programs.map(p => <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Materia</Label>
                  <Select value={form.subject_id} onValueChange={(v) => setForm({ ...form, subject_id: v })}>
                    <SelectTrigger><SelectValue placeholder="Seleccionar materia" /></SelectTrigger>
                    <SelectContent>{filteredSubjects.map(s => <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
              </>
            )}
            <div className="space-y-2">
              <Label>Profesor</Label>
              <Select value={form.teacher_id} onValueChange={(v) => setForm({ ...form, teacher_id: v })}>
                <SelectTrigger><SelectValue placeholder="Asignar profesor" /></SelectTrigger>
                <SelectContent>{teachers.map(t => <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Estudiantes Inscritos</Label>
              <div className="max-h-40 overflow-y-auto rounded-lg border p-3 space-y-2">
                {students.length === 0 ? <p className="text-sm text-muted-foreground">No hay estudiantes</p> : students.map((s) => (
                  <div key={s.id} className="flex items-center gap-2">
                    <Checkbox checked={form.student_ids.includes(s.id)} onCheckedChange={() => toggleStudent(s.id)} />
                    <span className="text-sm">{s.name} <span className="text-muted-foreground">({s.cedula})</span></span>
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
