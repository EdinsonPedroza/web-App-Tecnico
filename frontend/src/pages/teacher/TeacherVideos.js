import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Plus, Pencil, Trash2, Loader2, Video, ExternalLink, Calendar } from 'lucide-react';
import api from '@/lib/api';

export default function TeacherVideos() {
  const { courseId } = useParams();
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ title: '', url: '', description: '' });
  const [saving, setSaving] = useState(false);

  const fetchVideos = useCallback(async () => {
    try {
      const res = await api.get(`/class-videos?course_id=${courseId}`);
      setVideos(res.data);
    } catch (err) {
      toast.error('Error cargando videos');
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => { fetchVideos(); }, [fetchVideos]);

  const openCreate = () => {
    setEditing(null);
    setForm({ title: '', url: '', description: '' });
    setDialogOpen(true);
  };

  const openEdit = (vid) => {
    setEditing(vid);
    setForm({ title: vid.title, url: vid.url, description: vid.description || '' });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (!form.title.trim() || !form.url.trim()) { toast.error('Título y URL requeridos'); return; }
    setSaving(true);
    try {
      if (editing) {
        await api.put(`/class-videos/${editing.id}`, form);
        toast.success('Video actualizado');
      } else {
        await api.post('/class-videos', { course_id: courseId, ...form });
        toast.success('Video subido exitosamente');
      }
      setDialogOpen(false);
      fetchVideos();
    } catch (err) {
      toast.error('Error guardando video');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este video?')) return;
    try { await api.delete(`/class-videos/${id}`); toast.success('Video eliminado'); fetchVideos(); }
    catch (err) { toast.error('Error eliminando video'); }
  };

  const formatDate = (d) => new Date(d).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' });

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
              return (
                <Card key={vid.id} className="shadow-card hover:shadow-card-hover transition-shadow overflow-hidden flex flex-col">
                  {thumb && (
                    <div className="aspect-video bg-muted overflow-hidden">
                      <img src={thumb} alt={vid.title} className="w-full h-full object-cover" />
                    </div>
                  )}
                  <CardContent className="p-4 flex-1 flex flex-col">
                    <h3 className="text-sm font-semibold text-foreground mb-1">{vid.title}</h3>
                    <p className="text-xs text-muted-foreground mb-3 flex-1">{vid.description}</p>
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
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => handleDelete(vid.id)}>
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

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? 'Editar Video' : 'Subir Video de Clase'}</DialogTitle>
            <DialogDescription>Pega el enlace de YouTube del video</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2"><Label>Título</Label><Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Ej: Clase 3 - Tema..." /></div>
            <div className="space-y-2"><Label>URL de YouTube</Label><Input value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} placeholder="https://youtube.com/watch?v=..." /></div>
            <div className="space-y-2"><Label>Descripción (opcional)</Label><Textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Breve descripción del contenido..." rows={3} /></div>
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
    </DashboardLayout>
  );
}
