import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Plus, Pencil, Trash2, Loader2, FileText, Calendar, Clock, Lock, Unlock, Upload, Download, File, Eye, Image, Check } from 'lucide-react';
import api from '@/lib/api';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function TeacherActivities() {
  const { courseId } = useParams();
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ title: '', description: '', start_date: '', due_date: '', files: [] });
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [submissionsDialog, setSubmissionsDialog] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [loadingSubmissions, setLoadingSubmissions] = useState(false);
  const [students, setStudents] = useState([]);
  const [grades, setGrades] = useState({});
  const [savingGrade, setSavingGrade] = useState(null);

  const fetchActivities = useCallback(async () => {
    try {
      const res = await api.get(`/activities?course_id=${courseId}`);
      setActivities(res.data);
    } catch (err) {
      toast.error('Error cargando actividades');
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => { fetchActivities(); }, [fetchActivities]);

  const openSubmissions = async (activity) => {
    setSubmissionsDialog(activity);
    setLoadingSubmissions(true);
    setGrades({});
    try {
      const [subsRes, studentsRes, gradesRes] = await Promise.all([
        api.get(`/submissions?activity_id=${activity.id}`),
        api.get(`/courses/${courseId}`),
        api.get(`/grades?activity_id=${activity.id}`)
      ]);
      setSubmissions(subsRes.data);
      // Cargar notas existentes
      const gradesMap = {};
      gradesRes.data.forEach(g => { gradesMap[g.student_id] = g.value; });
      setGrades(gradesMap);
      // Obtener lista de estudiantes del curso
      const courseData = studentsRes.data;
      if (courseData.student_ids && courseData.student_ids.length > 0) {
        const usersRes = await api.get('/users?role=estudiante');
        const enrolled = usersRes.data.filter(u => courseData.student_ids.includes(u.id));
        setStudents(enrolled);
      } else {
        setStudents([]);
      }
    } catch (err) {
      toast.error('Error cargando entregas');
    } finally {
      setLoadingSubmissions(false);
    }
  };

  const handleGradeChange = (studentId, value) => {
    setGrades(prev => ({ ...prev, [studentId]: value }));
  };

  const saveGrade = async (studentId) => {
    const value = parseFloat(grades[studentId]);
    if (isNaN(value) || value < 0 || value > 5) {
      toast.error('La nota debe ser entre 0 y 5');
      return;
    }
    setSavingGrade(studentId);
    try {
      await api.post('/grades', {
        student_id: studentId,
        course_id: courseId,
        activity_id: submissionsDialog.id,
        value: value
      });
      toast.success('Nota guardada');
    } catch (err) {
      toast.error('Error guardando nota');
    } finally {
      setSavingGrade(null);
    }
  };

  const openCreate = () => {
    setEditing(null);
    const now = new Date();
    const defaultStart = new Date(now);
    const defaultDue = new Date(now);
    defaultDue.setDate(defaultDue.getDate() + 7);
    setForm({
      title: '',
      description: '',
      start_date: defaultStart.toISOString().slice(0, 16),
      due_date: defaultDue.toISOString().slice(0, 16),
      files: []
    });
    setDialogOpen(true);
  };

  const openEdit = (act) => {
    setEditing(act);
    setForm({
      title: act.title,
      description: act.description || '',
      start_date: act.start_date ? new Date(act.start_date).toISOString().slice(0, 16) : '',
      due_date: act.due_date ? new Date(act.due_date).toISOString().slice(0, 16) : '',
      files: act.files || []
    });
    setDialogOpen(true);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setForm(prev => ({
        ...prev,
        files: [...prev.files, { name: res.data.filename, url: `${BACKEND_URL}${res.data.url}` }]
      }));
      toast.success(`Archivo "${file.name}" subido`);
    } catch (err) {
      toast.error('Error subiendo archivo');
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (index) => {
    setForm(prev => ({
      ...prev,
      files: prev.files.filter((_, i) => i !== index)
    }));
  };

  const handleSave = async () => {
    if (!form.title.trim() || !form.due_date) { toast.error('Título y fecha de entrega requeridos'); return; }
    setSaving(true);
    try {
      const startDate = form.start_date ? new Date(form.start_date).toISOString() : null;
      const dueDate = new Date(form.due_date).toISOString();
      if (editing) {
        await api.put(`/activities/${editing.id}`, {
          title: form.title,
          description: form.description,
          start_date: startDate,
          due_date: dueDate,
          files: form.files
        });
        toast.success('Actividad actualizada');
      } else {
        await api.post('/activities', {
          course_id: courseId,
          title: form.title,
          description: form.description,
          start_date: startDate,
          due_date: dueDate,
          files: form.files
        });
        toast.success('Actividad creada');
      }
      setDialogOpen(false);
      fetchActivities();
    } catch (err) {
      toast.error('Error guardando actividad');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar esta actividad?')) return;
    try { await api.delete(`/activities/${id}`); toast.success('Actividad eliminada'); fetchActivities(); }
    catch (err) { toast.error('Error eliminando actividad'); }
  };

  const formatDate = (d) => new Date(d).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  const getStatus = (act) => {
    const now = new Date();
    const due = new Date(act.due_date);
    const start = act.start_date ? new Date(act.start_date) : null;
    if (now > due) return { label: 'Bloqueada', variant: 'destructive', icon: Lock };
    if (start && now < start) return { label: 'Programada', variant: 'secondary', icon: Clock };
    return { label: 'Activa', variant: 'success', icon: Unlock };
  };

  return (
    <DashboardLayout courseId={courseId}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold font-heading">Actividades</h1>
            <p className="text-muted-foreground mt-1">Crea y gestiona las actividades del curso</p>
          </div>
          <Button onClick={openCreate}><Plus className="h-4 w-4" /> Nueva Actividad</Button>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : activities.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay actividades creadas</p>
            <Button className="mt-4" onClick={openCreate}><Plus className="h-4 w-4" /> Crear Actividad</Button>
          </CardContent></Card>
        ) : (
          <div className="space-y-3">
            {activities.map((act) => {
              const status = getStatus(act);
              const due = new Date(act.due_date);
              const now = new Date();
              const daysLeft = Math.ceil((due - now) / (1000 * 60 * 60 * 24));
              const StatusIcon = status.icon;
              const actNum = act.activity_number || '?';

              return (
                <Card key={act.id} className="shadow-card hover:shadow-card-hover transition-shadow">
                  <CardContent className="p-5">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="outline" className="shrink-0 text-xs font-mono">Act {actNum}</Badge>
                          <StatusIcon className={`h-4 w-4 shrink-0 ${status.variant === 'destructive' ? 'text-destructive' : status.variant === 'success' ? 'text-success' : 'text-muted-foreground'}`} />
                          <h3 className="text-sm font-semibold text-foreground truncate">{act.title}</h3>
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-2 mb-2">{act.description}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                          {act.start_date && (
                            <span className="flex items-center gap-1"><Calendar className="h-3 w-3" /> Inicia: {formatDate(act.start_date)}</span>
                          )}
                          <span className="flex items-center gap-1"><Calendar className="h-3 w-3" /> Vence: {formatDate(act.due_date)}</span>
                          {status.variant === 'success' && daysLeft > 0 && (
                            <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {daysLeft} días restantes</span>
                          )}
                        </div>
                        {act.files && act.files.length > 0 && (
                          <div className="flex items-center gap-2 mt-2 flex-wrap">
                            {act.files.map((f, i) => (
                              <a
                                key={i}
                                href={f.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1 text-xs text-primary hover:underline bg-primary/5 rounded-md px-2 py-1"
                              >
                                <File className="h-3 w-3" />
                                {f.name}
                                <Download className="h-3 w-3" />
                              </a>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <Badge variant={status.variant}>{status.label}</Badge>
                        <Button variant="outline" size="sm" onClick={() => openSubmissions(act)}><Eye className="h-4 w-4" /> Entregas</Button>
                        <Button variant="ghost" size="icon" onClick={() => openEdit(act)}><Pencil className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDelete(act.id)}><Trash2 className="h-4 w-4 text-destructive" /></Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editing ? 'Editar Actividad' : 'Nueva Actividad'}</DialogTitle>
            <DialogDescription>Las actividades solo estarán disponibles entre la fecha de inicio y la fecha límite</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Título</Label>
              <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Nombre de la actividad" />
            </div>
            <div className="space-y-2">
              <Label>Descripción</Label>
              <Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Instrucciones de la actividad..." rows={4} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label>Fecha de Inicio</Label>
                <Input type="datetime-local" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label>Fecha Límite</Label>
                <Input type="datetime-local" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
              </div>
            </div>

            {/* File Upload */}
            <div className="space-y-2">
              <Label>Archivo Adjunto (PDF, DOC, etc.)</Label>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-2 cursor-pointer rounded-lg border border-dashed border-input px-4 py-3 w-full hover:bg-accent transition-colors">
                  <Upload className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    {uploading ? 'Subiendo...' : 'Seleccionar archivo'}
                  </span>
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.png"
                    onChange={handleFileUpload}
                    disabled={uploading}
                  />
                  {uploading && <Loader2 className="h-4 w-4 animate-spin" />}
                </label>
              </div>
              {form.files.length > 0 && (
                <div className="space-y-1 mt-2">
                  {form.files.map((f, i) => (
                    <div key={i} className="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2">
                      <span className="flex items-center gap-2 text-sm">
                        <File className="h-4 w-4 text-primary" />
                        {f.name}
                      </span>
                      <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => removeFile(i)}>
                        <Trash2 className="h-3 w-3 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving && <Loader2 className="h-4 w-4 animate-spin" />}
              {editing ? 'Actualizar' : 'Crear'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog Ver Entregas */}
      <Dialog open={!!submissionsDialog} onOpenChange={() => setSubmissionsDialog(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Entregas - {submissionsDialog?.title}</DialogTitle>
            <DialogDescription>Revisa las entregas de los estudiantes</DialogDescription>
          </DialogHeader>
          {loadingSubmissions ? (
            <div className="flex justify-center py-10"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
          ) : (
            <div className="space-y-3">
              {students.length === 0 ? (
                <p className="text-center text-muted-foreground py-6">No hay estudiantes inscritos en este curso</p>
              ) : students.map((student) => {
                const sub = submissions.find(s => s.student_id === student.id);
                const currentGrade = grades[student.id] !== undefined ? grades[student.id] : '';
                return (
                  <Card key={student.id} className={`${sub ? 'border-success/30 bg-success/5' : 'border-destructive/30 bg-destructive/5'}`}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-sm">{student.name}</span>
                            <Badge variant={sub ? 'success' : 'destructive'} className="text-xs">
                              {sub ? 'Entregado' : 'Sin entregar'}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground">Cédula: {student.cedula}</p>
                          {sub && (
                            <>
                              <p className="text-xs text-muted-foreground mt-1">
                                Entregado: {new Date(sub.submitted_at).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                              </p>
                              {sub.content && (
                                <div className="mt-2 p-2 bg-card rounded-md border">
                                  <p className="text-sm">{sub.content}</p>
                                </div>
                              )}
                              {sub.files && sub.files.length > 0 && (
                                <div className="flex items-center gap-2 mt-2 flex-wrap">
                                  {sub.files.map((f, i) => (
                                    <a
                                      key={i}
                                      href={f.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="flex items-center gap-1 text-xs text-primary hover:underline bg-primary/10 rounded-md px-2 py-1"
                                    >
                                      {/\.(jpg|jpeg|png|gif|webp)$/i.test(f.name) ? <Image className="h-3 w-3" /> : <File className="h-3 w-3" />}
                                      {f.name}
                                      <Download className="h-3 w-3" />
                                    </a>
                                  ))}
                                </div>
                              )}
                            </>
                          )}
                        </div>
                        {/* Campo de calificación */}
                        <div className="flex items-center gap-2 shrink-0">
                          <div className="flex items-center gap-1">
                            <Input
                              type="number"
                              min="0"
                              max="5"
                              step="0.1"
                              placeholder="Nota"
                              className="w-20 h-8 text-center text-sm"
                              value={currentGrade}
                              onChange={(e) => handleGradeChange(student.id, e.target.value)}
                            />
                            <span className="text-xs text-muted-foreground">/5</span>
                          </div>
                          <Button
                            size="sm"
                            className="h-8"
                            onClick={() => saveGrade(student.id)}
                            disabled={savingGrade === student.id || currentGrade === ''}
                          >
                            {savingGrade === student.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <Check className="h-3 w-3" />}
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSubmissionsDialog(null)}>Cerrar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
