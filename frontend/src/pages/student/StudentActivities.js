import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useParams, useSearchParams } from 'react-router-dom';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion';
import { toast } from 'sonner';
import { Loader2, FileText, Calendar, Clock, Lock, Unlock, Send, Download, File, TimerOff, Upload, Trash2, Image } from 'lucide-react';
import api from '@/lib/api';
import { ensureProtocol } from '@/utils/url';

const BACKEND_URL = ensureProtocol(process.env.REACT_APP_BACKEND_URL);

export default function StudentActivities() {
  const { user } = useAuth();
  const { courseId } = useParams();
  const [searchParams] = useSearchParams();
  const subjectId = searchParams.get('subjectId');
  const [activities, setActivities] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitDialog, setSubmitDialog] = useState(null);
  const [submitContent, setSubmitContent] = useState('');
  const [submitFiles, setSubmitFiles] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      let url = '/activities';
      const params = [];
      if (courseId) params.push(`course_id=${courseId}`);
      if (subjectId) params.push(`subject_id=${subjectId}`);
      if (params.length > 0) url += '?' + params.join('&');
      const aRes = await api.get(url);
      setActivities(aRes.data);
      const sRes = await api.get(`/submissions?student_id=${user.id}`);
      setSubmissions(sRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user.id, courseId, subjectId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const hasSubmission = (actId) => submissions.find(s => s.activity_id === actId);

  const getActivityStatus = (act) => {
    const now = new Date();
    const due = new Date(act.due_date);
    const start = act.start_date ? new Date(act.start_date) : null;

    if (now > due) return { key: 'expired', label: 'Bloqueada (Vencida)', variant: 'destructive', icon: Lock };
    if (start && now < start) return { key: 'upcoming', label: 'No Disponible', variant: 'secondary', icon: TimerOff };
    return { key: 'active', label: 'Activa', variant: 'success', icon: Unlock };
  };

  const isDownloadOnly = (filename) => /\.(doc|docx|xls|xlsx|ppt|pptx)$/i.test(filename || '');

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    setUploadingFile(true);
    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        const res = await api.post('/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setSubmitFiles(prev => [...prev, { name: res.data.filename, url: res.data.url.startsWith('http') ? res.data.url : `${BACKEND_URL}${res.data.url}` }]);
      }
      toast.success(`${files.length} archivo(s) subido(s)`);
    } catch (err) {
      toast.error('Error subiendo archivo');
    } finally {
      setUploadingFile(false);
      e.target.value = '';
    }
  };

  const removeSubmitFile = (index) => {
    setSubmitFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (!submitContent.trim() && submitFiles.length === 0) { toast.error('Escribe una respuesta o adjunta archivos'); return; }
    setSubmitting(true);
    try {
      await api.post('/submissions', { activity_id: submitDialog.id, content: submitContent, files: submitFiles });
      toast.success('Actividad entregada exitosamente');
      setSubmitDialog(null);
      setSubmitContent('');
      setSubmitFiles([]);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Error entregando actividad');
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (d) => new Date(d).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  const handleEditSubmission = (act, submission, e) => {
    e.stopPropagation();
    toast.warning('⚠️ Importante: Solo puedes editar tu actividad UNA VEZ. Asegúrate de revisar bien antes de guardar.', {
      duration: 6000,
      important: true
    });
    setSubmitDialog(act);
    setSubmitContent(submission.content || '');
    setSubmitFiles(submission.files || []);
  };

  const handleSubmitActivity = (act, e) => {
    e.stopPropagation();
    setSubmitDialog(act);
    setSubmitContent('');
    setSubmitFiles([]);
  };

  return (
    <DashboardLayout courseId={courseId}>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold font-heading">Actividades</h1>
          <p className="text-muted-foreground mt-1 text-lg">Tus actividades pendientes y entregadas</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : activities.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay actividades disponibles</p>
          </CardContent></Card>
        ) : (
          <Accordion type="multiple" className="space-y-4">
            {activities.map((act) => {
              const status = getActivityStatus(act);
              const due = new Date(act.due_date);
              const start = act.start_date ? new Date(act.start_date) : null;
              const now = new Date();
              const daysLeft = Math.ceil((due - now) / (1000 * 60 * 60 * 24));
              const submission = hasSubmission(act.id);
              const StatusIcon = status.icon;
              const actNum = act.activity_number || '?';

              return (
                <Card key={act.id} className={`shadow-card transition-all border-2 ${status.key !== 'active' && !submission ? 'opacity-70 border-muted' : 'hover:shadow-card-hover border-primary/20 hover:border-primary/40'} ${submission ? 'bg-success/5' : ''}`}>
                  <AccordionItem value={`activity-${act.id}`} className="border-none">
                    <CardContent className="p-4">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        {/* Compact header - always visible */}
                        <AccordionTrigger className="flex-1 hover:no-underline py-2">
                          <div className="flex items-center gap-2 w-full">
                            <Badge variant="outline" className="shrink-0 text-xs font-mono">Act {actNum}</Badge>
                            {act.is_recovery && <Badge variant="warning" className="shrink-0 text-xs">Recuperación</Badge>}
                            <StatusIcon className={`h-4 w-4 shrink-0 ${status.variant === 'destructive' ? 'text-destructive' : status.variant === 'success' ? 'text-success' : 'text-muted-foreground'}`} />
                            <h3 className="text-sm font-semibold truncate">{act.title}</h3>
                            <span className="ml-auto text-xs text-muted-foreground hidden sm:flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {formatDate(act.due_date)}
                            </span>
                          </div>
                        </AccordionTrigger>
                        
                        {/* Action buttons - always visible */}
                        <div className="flex items-center gap-2 shrink-0 ml-auto sm:ml-0">
                          {submission ? (
                            <>
                              <Badge variant="success" className="text-xs">Entregada</Badge>
                              {submission.edited !== true && status.key === 'active' && (
                                <Button size="sm" variant="outline" onClick={(e) => handleEditSubmission(act, submission, e)}>
                                  Editar
                                </Button>
                              )}
                            </>
                          ) : status.key === 'active' ? (
                            <Button size="sm" onClick={(e) => handleSubmitActivity(act, e)}>
                              <Send className="h-3 w-3" /> Entregar
                            </Button>
                          ) : (
                            <Badge variant={status.variant} className="text-xs">{status.label}</Badge>
                          )}
                        </div>
                      </div>

                      {/* Expandable content - shows when clicked */}
                      <AccordionContent>
                        <div className="pt-3 space-y-3">
                          <p className="text-xs text-primary">{act.courseName}</p>
                          <p className="text-sm text-muted-foreground">{act.description}</p>

                          <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                            {start && (
                              <span className="flex items-center gap-1"><Calendar className="h-3 w-3" /> Disponible: {formatDate(act.start_date)}</span>
                            )}
                            <span className="flex items-center gap-1"><Calendar className="h-3 w-3" /> Vence: {formatDate(act.due_date)}</span>
                            {status.key === 'active' && daysLeft > 0 && (
                              <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {daysLeft} días restantes</span>
                            )}
                            {status.key === 'upcoming' && start && (
                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                Disponible en {Math.ceil((start - now) / (1000 * 60 * 60 * 24))} días
                              </span>
                            )}
                          </div>

                          {/* Attached files */}
                          {act.files && act.files.length > 0 && (
                            <div className="p-3 bg-primary/10 border-l-4 border-primary rounded-md">
                              <p className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                                <File className="h-4 w-4" />
                                Archivos del profesor:
                              </p>
                              <div className="flex flex-col gap-2">
                                {act.files.map((f, i) => (
                                  <a
                                    key={i}
                                    href={f.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    {...(isDownloadOnly(f.name) ? { download: f.name } : {})}
                                    className="flex items-center justify-between gap-2 text-sm text-primary hover:text-primary/80 bg-background hover:bg-background/80 rounded-md px-3 py-2 border border-primary/30 hover:border-primary transition-all font-medium group"
                                  >
                                    <span className="flex items-center gap-2">
                                      <File className="h-4 w-4" />
                                      {f.name}
                                    </span>
                                    <Download className="h-4 w-4 group-hover:scale-110 transition-transform" />
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </AccordionContent>
                    </CardContent>
                  </AccordionItem>
                </Card>
              );
            })}
          </Accordion>
        )}
      </div>

      <Dialog open={!!submitDialog} onOpenChange={() => setSubmitDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Entregar Actividad</DialogTitle>
            <DialogDescription>{submitDialog?.title}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {/* Show warning if editing an already submitted activity */}
            {submissions.find(s => s.activity_id === submitDialog?.id) && (
              <div className="rounded-lg bg-warning/15 border-2 border-warning p-4">
                <p className="text-sm font-bold text-warning flex items-center gap-2">
                  <span className="text-xl">⚠️</span>
                  ¡IMPORTANTE! Solo puedes editar tu actividad UNA VEZ
                </p>
                <p className="text-sm text-foreground mt-1">
                  Revisa cuidadosamente tu respuesta y archivos antes de entregar. Una vez editada, no podrás volver a modificarla.
                </p>
              </div>
            )}
            <div className="rounded-lg bg-muted/50 p-3">
              <p className="text-sm text-muted-foreground">{submitDialog?.description}</p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Tu Respuesta (opcional si adjuntas archivos)</label>
              <Textarea
                value={submitContent}
                onChange={(e) => setSubmitContent(e.target.value)}
                placeholder="Escribe tu respuesta aquí..."
                rows={4}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Adjuntar Archivos (fotos, PDF, etc.)</label>
              <label className="flex items-center gap-2 cursor-pointer rounded-lg border border-dashed border-input px-4 py-3 w-full hover:bg-accent transition-colors">
                <Upload className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  {uploadingFile ? 'Subiendo...' : 'Seleccionar archivos'}
                </span>
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.webp,.xls,.xlsx,.ppt,.pptx,.txt"
                  multiple
                  onChange={handleFileUpload}
                  disabled={uploadingFile}
                />
                {uploadingFile && <Loader2 className="h-4 w-4 animate-spin" />}
              </label>
              {submitFiles.length > 0 && (
                <div className="space-y-1 mt-2">
                  {submitFiles.map((f, i) => (
                    <div key={i} className="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2">
                      <span className="flex items-center gap-2 text-sm truncate">
                        {/\.(jpg|jpeg|png|gif|webp)$/i.test(f.name) ? <Image className="h-4 w-4 text-primary shrink-0" /> : <File className="h-4 w-4 text-primary shrink-0" />}
                        {f.name}
                      </span>
                      <Button variant="ghost" size="icon" className="h-6 w-6 shrink-0" onClick={() => removeSubmitFile(i)}>
                        <Trash2 className="h-3 w-3 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSubmitDialog(null)}>Cancelar</Button>
            <Button onClick={handleSubmit} disabled={submitting}>
              {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
              <Send className="h-4 w-4" /> Entregar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
