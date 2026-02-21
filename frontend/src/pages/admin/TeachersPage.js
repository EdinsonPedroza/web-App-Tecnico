import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Checkbox } from '@/components/ui/checkbox';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from 'sonner';
import { Plus, Pencil, Trash2, Loader2, Users, Search, BookOpen } from 'lucide-react';
import api from '@/lib/api';

export default function TeachersPage() {
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', email: '', password: '', phone: '', subject_ids: [] });
  const [saving, setSaving] = useState(false);
  const [subjectSearch, setSubjectSearch] = useState('');
  const [viewSubjectsDialog, setViewSubjectsDialog] = useState(false);
  const [selectedTeacher, setSelectedTeacher] = useState(null);

  const fetchTeachers = useCallback(async () => {
    try {
      const [tRes, sRes, pRes] = await Promise.all([
        api.get('/users?role=profesor'),
        api.get('/subjects'),
        api.get('/programs')
      ]);
      setTeachers(tRes.data);
      setSubjects(sRes.data);
      setPrograms(pRes.data);
    } catch (err) {
      toast.error('Error cargando profesores');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchTeachers(); }, [fetchTeachers]);

  const filtered = teachers.filter(t => (t.name || '').toLowerCase().includes(search.toLowerCase()) || (t.email || '').toLowerCase().includes(search.toLowerCase()));
  
  // Filter subjects: only show unassigned subjects (or subjects already assigned to the teacher being edited)
  // This prevents assigning a subject that already belongs to another teacher
  const filteredSubjects = subjects.filter(subject => {
    // Always show subjects already assigned to the teacher being edited
    if (editing && (editing.subject_ids || []).includes(subject.id)) return true;
    // Check if subject is assigned to any other teacher
    const assignedToOther = teachers.some(t =>
      t.id !== (editing?.id) && (t.subject_ids || []).includes(subject.id)
    );
    if (assignedToOther) return false;
    return subject.name.toLowerCase().includes(subjectSearch.toLowerCase());
  }).filter(subject =>
    subject.name.toLowerCase().includes(subjectSearch.toLowerCase())
  );

  const openCreate = () => {
    setEditing(null);
    setForm({ name: '', email: '', password: '', phone: '', subject_ids: [] });
    setSubjectSearch('');
    setDialogOpen(true);
  };

  const openEdit = (teacher) => {
    setEditing(teacher);
    setForm({ name: teacher.name, email: teacher.email || '', password: '', phone: teacher.phone || '', subject_ids: teacher.subject_ids || [] });
    setSubjectSearch('');
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (!form.name.trim() || (!editing && !form.email.trim())) { toast.error('Nombre y correo requeridos'); return; }
    if (!editing && !form.password) { toast.error('Contraseña requerida'); return; }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (form.email && !emailRegex.test(form.email)) {
      toast.error('Por favor ingresa un correo electrónico válido (debe contener @ y un dominio)');
      return;
    }
    
    // Password length validation
    if (form.password && form.password.length < 6) {
      toast.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }
    
    setSaving(true);
    try {
      if (editing) {
        const updateData = { name: form.name, email: form.email, phone: form.phone, subject_ids: form.subject_ids };
        // Include password only if provided
        if (form.password && form.password.trim()) {
          updateData.password = form.password;
        }
        await api.put(`/users/${editing.id}`, updateData);
        toast.success('Profesor actualizado');
      } else {
        await api.post('/users', { ...form, role: 'profesor' });
        toast.success('Profesor creado');
      }
      setDialogOpen(false);
      fetchTeachers();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error guardando profesor');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este profesor?')) return;
    try {
      await api.delete(`/users/${id}`);
      toast.success('Profesor eliminado');
      fetchTeachers();
    } catch (err) {
      toast.error('Error eliminando profesor');
    }
  };

  const initials = (name) => {
    if (!name) return '??';
    return name.split(' ').filter(w => w.length > 0).map(w => w[0]).join('').substring(0, 2).toUpperCase();
  };

  const openViewSubjects = (teacher) => {
    setSelectedTeacher(teacher);
    setViewSubjectsDialog(true);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold font-heading">Profesores</h1>
            <p className="text-muted-foreground mt-1 text-lg">Gestiona el cuerpo docente</p>
          </div>
          <Button onClick={openCreate}><Plus className="h-4 w-4" /> Nuevo Profesor</Button>
        </div>

        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Buscar profesor..." className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : filtered.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <Users className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay profesores registrados</p>
          </CardContent></Card>
        ) : (
          <Card className="shadow-card">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-base">Profesor</TableHead>
                  <TableHead className="text-base">Correo</TableHead>
                  <TableHead className="text-base">Teléfono</TableHead>
                  <TableHead className="text-base">Materias</TableHead>
                  <TableHead className="text-base">Estado</TableHead>
                  <TableHead className="text-right text-base">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((t) => (
                  <TableRow key={t.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-10 w-10"><AvatarFallback className="bg-primary/10 text-primary text-sm">{initials(t.name)}</AvatarFallback></Avatar>
                        <span className="font-medium text-base">{t.name || 'Sin nombre'}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-base text-muted-foreground">{t.email}</TableCell>
                    <TableCell className="text-base text-muted-foreground">{t.phone || '-'}</TableCell>
                    <TableCell className="text-base">
                      {t.subject_ids && t.subject_ids.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {t.subject_ids.slice(0, 2).map(subId => {
                            const subj = subjects.find(s => s.id === subId);
                            return subj ? (
                              <Badge key={subId} variant="secondary" className="text-xs">
                                {subj.name.length > 20 ? subj.name.substring(0, 20) + '...' : subj.name}
                              </Badge>
                            ) : null;
                          })}
                          {t.subject_ids.length > 2 && (
                            <Badge 
                              variant="outline" 
                              className="text-xs cursor-pointer hover:bg-primary/10 transition-colors"
                              onClick={() => openViewSubjects(t)}
                            >
                              +{t.subject_ids.length - 2} más
                            </Badge>
                          )}
                        </div>
                      ) : (
                        <span className="text-sm text-muted-foreground">Sin materias</span>
                      )}
                    </TableCell>
                    <TableCell><Badge variant={t.active !== false ? 'success' : 'destructive'} className="text-sm">{t.active !== false ? 'Activo' : 'Inactivo'}</Badge></TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => openEdit(t)}><Pencil className="h-4 w-4" /></Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(t.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        )}
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editing ? 'Editar Profesor' : 'Nuevo Profesor'}</DialogTitle>
            <DialogDescription>Ingresa los datos del docente</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2"><Label>Nombre Completo</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Nombre del profesor" /></div>
            <div className="space-y-2">
              <Label>Correo Electrónico</Label>
              <Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="correo@educando.com" />
              {editing && <p className="text-xs text-amber-600 dark:text-amber-500">⚠️ Cambiar el correo puede afectar el acceso del profesor. Verifica que no exista duplicado.</p>}
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
            <div className="space-y-2"><Label>Teléfono</Label><Input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="300 123 4567" /></div>
            
            <div className="space-y-2">
              <Label>Materias que enseña (opcional)</Label>
              {subjects.length > 0 && (
                <div className="relative mb-2">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input 
                    placeholder="Buscar materias..." 
                    className="pl-9" 
                    value={subjectSearch} 
                    onChange={(e) => setSubjectSearch(e.target.value)} 
                  />
                </div>
              )}
              <div className="border rounded-lg p-3 max-h-60 overflow-y-auto space-y-2">
                {subjects.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No hay materias disponibles</p>
                ) : filteredSubjects.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No se encontraron materias</p>
                ) : (
                  filteredSubjects.map((subject) => (
                    <div key={subject.id} className="flex items-center gap-2">
                      <Checkbox
                        id={`subject-${subject.id}`}
                        checked={form.subject_ids.includes(subject.id)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setForm({ ...form, subject_ids: [...form.subject_ids, subject.id] });
                          } else {
                            setForm({ ...form, subject_ids: form.subject_ids.filter(id => id !== subject.id) });
                          }
                        }}
                      />
                      <label htmlFor={`subject-${subject.id}`} className="text-sm cursor-pointer flex-1">
                        {subject.name}{' '}
                        <span className="text-muted-foreground text-xs">
                          {(() => {
                            const prog = subject.program_id ? programs.find(p => p.id === subject.program_id) : null;
                            return `(Módulo ${subject.module_number}${prog ? ` · ${prog.name}` : ''})`;
                          })()}
                        </span>
                      </label>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
            <Button onClick={handleSave} disabled={saving}>{saving && <Loader2 className="h-4 w-4 animate-spin" />}{editing ? 'Actualizar' : 'Crear'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View All Subjects Dialog */}
      <Dialog open={viewSubjectsDialog} onOpenChange={setViewSubjectsDialog}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Materias de {selectedTeacher?.name}</DialogTitle>
            <DialogDescription>
              Todas las materias asignadas a este profesor
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            {selectedTeacher?.subject_ids && selectedTeacher.subject_ids.length > 0 ? (
              <div className="grid grid-cols-1 gap-2">
                {selectedTeacher.subject_ids.map(subId => {
                  const subj = subjects.find(s => s.id === subId);
                  return subj ? (
                    <Card key={subId} className="p-4 hover:bg-accent/50 transition-colors">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-base">{subj.name}</h4>
                          <p className="text-sm text-muted-foreground mt-1">
                            Programa: {programs.find(p => p.id === subj.program_id)?.name || 'N/A'}
                          </p>
                        </div>
                        <Badge variant="secondary" className="ml-3">
                          Módulo {subj.module_number}
                        </Badge>
                      </div>
                    </Card>
                  ) : null;
                })}
              </div>
            ) : (
              <div className="p-10 text-center">
                <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground">Este profesor no tiene materias asignadas</p>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button onClick={() => setViewSubjectsDialog(false)}>Cerrar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
