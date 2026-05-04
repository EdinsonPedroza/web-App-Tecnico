import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Plus, Pencil, Trash2, Loader2, Video, ExternalLink, Calendar, Clock, Users } from 'lucide-react';
import api from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

export default function TeacherVideos() {
  const { courseId } = useParams();
  const [searchParams] = useSearchParams();
  const subjectId = searchParams.get('subjectId');
  const { user } = useAuth();

  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ title: '', url: '', description: '', available_from: '' });
  const [saving, setSaving] = useState(false);

  // Multi-group state
  const [availableCourses, setAvailableCourses] = useState([]);
  const [selectedCourseIds, setSelectedCourseIds] = useState([]);
  const [courseSearch, setCourseSearch] = useState('');
  const [groupConfirmDialog, setGroupConfirmDialog] = useState({ open: false, resolve: null, count: 0 });
  const groupConfirmResolveRef = useRef(null);

  const fetchVideos = useCallback(async () => {
    try {
      let url = `/class-videos?course_id=${courseId}`;
      if (subjectId) url += `&subject_id=${subjectId}`;
      const res = await api.get(url);
      setVideos(res.data);
    } catch (err) {
      toast.error('Error cargando videos');
    } finally {
      setLoading(false);
    }
  }, [courseId, subjectId]);

  useEffect(() => { fetchVideos(); }, [fetchVideos]);

  const openCreate = async () => {
    setEditing(null);
    setForm({ title: '', url: '', description: '', available_from: '' });
    setSelectedCourseIds([courseId]);
    setCourseSearch('');

    // Fetch teacher's sibling courses for the same subject
    try {
      const res = await api.get(`/courses?teacher_id=${user?.id}&fields=summary&limit=100`);
      const courses = (res.data?.courses || res.data || []).filter(c =>
        !subjectId || (c.subject_ids || []).includes(subjectId) || c.subject_id === subjectId
      );
      setAvailableCourses(courses.length > 0 ? courses : []);
    } catch {
      setAvailableCourses([]);
    }

    setDialogOpen(true);
  };

  const openEdit = (vid) => {
    setEditing(vid);
    const af = vid.available_from ? new Date(vid.available_from).toISOString().slice(0, 16) : '';
    setForm({ title: vid.title, url: vid.url, description: vid.description || '', available_from: af });
    setAvailableCourses([]);
    setSelectedCourseIds([]);
    setDialogOpen(true);
  };

  const toggleCourseSelection = (id) => {
    setSelectedCourseIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const isValidYoutubeUrl = (url) =>
    /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?.*v=|embed\/|shorts\/)|youtu\.be\/)[\w\-]{11}/.test(url.trim());

  // Returns Promise resolved with 'single' | 'group'
  const askGroupAction = (count) =>
    new Promise((resolve) => {
      groupConfirmResolveRef.current = resolve;
      setGroupConfirmDialog({ open: true, resolve, count });
    });

  const resolveGroupDialog = (choice) => {
    groupConfirmResolveRef.current?.(choice);
    groupConfirmResolveRef.current = null;
    setGroupConfirmDialog({ open: false, resolve: null, count: 0 });
  };

  const handleSave = async () => {
    if (!form.title.trim() || !form.url.trim()) { toast.error('Título y URL requeridos'); return; }
    if (!isValidYoutubeUrl(form.url)) {
      toast.error('La URL debe ser un enlace válido de YouTube (youtube.com o youtu.be)');
      return;
    }
    setSaving(true);
    try {
      const payload = {
        title: form.title,
        url: form.url,
        description: form.description,
        available_from: form.available_from ? new Date(form.available_from).toISOString() : null,
      };

      if (editing) {
        // Edit: ask group vs single if video belongs to a group
        if (editing.video_group_id) {
          const choice = await askGroupAction(null);
          if (choice === 'group') {
            // No group-update endpoint for videos yet — fall back to single update
            // (backend only has group-delete; edit applies to single video)
            toast.info('La edición se aplica solo a este video');
          }
        }
        await api.put(`/class-videos/${editing.id}`, payload);
        toast.success('Video actualizado');
      } else {
        // Create: include selected course_ids for multi-group
        const courseIds = selectedCourseIds.length > 0 ? selectedCourseIds : [courseId];
        await api.post('/class-videos', {
          course_id: courseId,
          subject_id: subjectId,
          course_ids: courseIds.length > 1 ? courseIds : undefined,
          ...payload,
        });
        const msg = courseIds.length > 1
          ? `Video publicado en ${courseIds.length} grupos`
          : 'Video subido exitosamente';
        toast.success(msg);
      }
      setDialogOpen(false);
      fetchVideos();
    } catch (err) {
      toast.error('Error guardando video');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (vid) => {
    if (vid.video_group_id) {
      const choice = await askGroupAction(null);
      if (choice === 'group') {
        if (!window.confirm('¿Eliminar este video en TODOS los grupos?')) return;
        try {
          await api.delete(`/class-videos/group/${vid.video_group_id}`);
          toast.success('Grupo de videos eliminado');
          fetchVideos();
        } catch { toast.error('Error eliminando grupo'); }
        return;
      }
    } else {
      if (!window.confirm('¿Eliminar este video?')) return;
    }
    try {
      await api.delete(`/class-videos/${vid.id}`);
      toast.success('Video eliminado');
      fetchVideos();
    } catch { toast.error('Error eliminando video'); }
  };

  const formatDate = (d) => new Date(d).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' });
  const isScheduled = (vid) => vid.available_from && new Date(vid.available_from) > new Date();

  const getEmbedUrl = (url) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&?/]+)/);
    return match ? `https://img.youtube.com/vi/${match[1]}/mqdefault.jpg` : null;
  };

  return (
    <DashboardLayout courseId={courseId}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold font-heading">Videos de Clase</h1>
            <p className="text-muted-foreground mt-1">Sube enlaces de YouTube para tus estudiantes</p>
          </div>
          <Button onClick={openCreate}><Plus className="h-4 w-4" /> Subir Video</Button>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : videos.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <Video className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay videos subidos</p>
            <Button className="mt-4" onClick={openCreate}><Plus className="h-4 w-4" /> Subir primer video</Button>
          </CardContent></Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {videos.map((vid) => {
              const thumb = getEmbedUrl(vid.url);
              const scheduled = isScheduled(vid);
              return (
                <Card key={vid.id} className="shadow-card hover:shadow-card-hover transition-shadow overflow-hidden flex flex-col">
                  {thumb && (
                    <div className="aspect-video bg-muted overflow-hidden relative">
                      <img src={thumb} alt={vid.title} className={`w-full h-full object-cover ${scheduled ? 'opacity-50' : ''}`} />
                      {scheduled && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <Badge variant="secondary" className="gap-1 text-xs">
                            <Clock className="h-3 w-3" /> Programado
                          </Badge>
                        </div>
                      )}
                    </div>
                  )}
                  <CardContent className="p-4 flex-1 flex flex-col">
                    <div className="flex items-start gap-2 mb-1">
                      <h3 className="text-sm font-semibold text-foreground flex-1">{vid.title}</h3>
                      {vid.video_group_id && (
                        <Badge variant="secondary" className="text-xs gap-1 shrink-0">
                          <Users className="h-3 w-3" /> Multi-grupo
                        </Badge>
                      )}
                    </div>
                    {scheduled && (
                      <Badge variant="outline" className="w-fit text-xs mb-2 gap-1 text-warning border-warning">
                        <Clock className="h-3 w-3" /> No visible para estudiantes aún
                      </Badge>
                    )}
                    <p className="text-xs text-muted-foreground mb-3 flex-1">{vid.description}</p>
                    {vid.available_from && (
                      <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        Disponible desde: {formatDate(vid.available_from)}
                      </p>
                    )}
                    <div className="flex items-center justify-between mt-auto">
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(vid.created_at)}
                      </span>
                      <div className="flex gap-1">
                        <Button variant="outline" size="sm" asChild>
                          <a href={vid.url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-3 w-3" /> Ver
                          </a>
                        </Button>
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => openEdit(vid)}>
                          <Pencil className="h-3 w-3" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleDelete(vid)}>
                          <Trash2 className="h-3 w-3 text-destructive" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Create / Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editing ? 'Editar Video' : 'Subir Video de Clase'}</DialogTitle>
            <DialogDescription>Pega el enlace de YouTube del video</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-1">
            <div className="space-y-2">
              <Label>Título</Label>
              <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Ej: Clase 3 - Tema..." />
            </div>
            <div className="space-y-2">
              <Label>URL de YouTube</Label>
              <Input value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} placeholder="https://youtube.com/watch?v=..." />
            </div>
            <div className="space-y-2">
              <Label>Descripción (opcional)</Label>
              <Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Breve descripción del contenido..." rows={3} />
            </div>
            <div className="space-y-2">
              <Label>Disponible a partir de (opcional)</Label>
              <Input
                type="datetime-local"
                value={form.available_from}
                onChange={(e) => setForm({ ...form, available_from: e.target.value })}
              />
              <p className="text-xs text-muted-foreground">Si se define, los estudiantes solo verán este video a partir de esa fecha y hora.</p>
            </div>

            {/* Multi-group selector — only on create when there are sibling courses */}
            {!editing && availableCourses.length > 0 && (
              <div className="space-y-2 border rounded-md p-3 bg-muted/30">
                <Label className="flex items-center gap-1 text-sm font-medium">
                  <Users className="h-4 w-4" /> Publicar en varios grupos
                </Label>
                <p className="text-xs text-muted-foreground">Selecciona los grupos donde se publicará este video.</p>
                <Input
                  placeholder="Buscar grupo..."
                  value={courseSearch}
                  onChange={(e) => setCourseSearch(e.target.value)}
                  className="h-8 text-sm"
                />
                <div className="flex gap-2 text-xs">
                  <button
                    type="button"
                    className="text-primary underline underline-offset-2"
                    onClick={() => setSelectedCourseIds(availableCourses.map(c => c.id))}
                  >Todos</button>
                  <button
                    type="button"
                    className="text-muted-foreground underline underline-offset-2"
                    onClick={() => setSelectedCourseIds([courseId])}
                  >Solo este</button>
                </div>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {availableCourses
                    .filter(c => (c.name || c.id).toLowerCase().includes(courseSearch.toLowerCase()))
                    .map((c) => (
                      <div key={c.id} className="flex items-center gap-2">
                        <Checkbox
                          id={`vc-${c.id}`}
                          checked={selectedCourseIds.includes(c.id)}
                          onCheckedChange={() => toggleCourseSelection(c.id)}
                        />
                        <label htmlFor={`vc-${c.id}`} className="text-sm cursor-pointer">
                          {c.name} {c.grupo ? `— ${c.grupo}` : ''}
                          {c.id === courseId && <span className="text-xs text-muted-foreground ml-1">(este)</span>}
                        </label>
                      </div>
                    ))}
                </div>
                {selectedCourseIds.length > 1 && (
                  <p className="text-xs text-primary font-medium">
                    Este video se publicará en {selectedCourseIds.length} grupos.
                  </p>
                )}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving && <Loader2 className="h-4 w-4 animate-spin" />}
              {editing ? 'Actualizar' : 'Subir Video'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Group action confirmation dialog */}
      <Dialog open={groupConfirmDialog.open} onOpenChange={(open) => { if (!open) resolveGroupDialog('single'); }}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>¿A cuántos grupos aplicar?</DialogTitle>
            <DialogDescription>
              Este video pertenece a un grupo publicado en varios cursos.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex-col gap-2 sm:flex-col">
            <Button variant="destructive" onClick={() => resolveGroupDialog('group')}>
              <Users className="h-4 w-4" /> Todos los grupos
            </Button>
            <Button variant="outline" onClick={() => resolveGroupDialog('single')}>
              Solo este grupo
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
