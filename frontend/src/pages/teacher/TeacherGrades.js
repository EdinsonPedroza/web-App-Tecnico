import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { Loader2, ClipboardList, Save } from 'lucide-react';
import api from '@/lib/api';

export default function TeacherGrades() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [students, setStudents] = useState([]);
  const [activities, setActivities] = useState([]);
  const [grades, setGrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editedGrades, setEditedGrades] = useState({});
  const [savingGrades, setSavingGrades] = useState({});

  const fetchData = useCallback(async () => {
    try {
      const [cRes, aRes, gRes, uRes] = await Promise.all([
        api.get(`/courses/${courseId}`),
        api.get(`/activities?course_id=${courseId}`),
        api.get(`/grades?course_id=${courseId}`),
        api.get('/users?role=estudiante')
      ]);
      setCourse(cRes.data);
      setActivities(aRes.data.sort((a, b) => (a.activity_number || 0) - (b.activity_number || 0)));
      setGrades(gRes.data);
      const courseStudents = uRes.data.filter(u => (cRes.data.student_ids || []).includes(u.id));
      setStudents(courseStudents);
    } catch (err) {
      toast.error('Error cargando datos');
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Key format: "studentId-activityId"
  const getGradeValue = (studentId, activityId) => {
    const key = `${studentId}-${activityId}`;
    if (editedGrades[key] !== undefined) return editedGrades[key];
    const grade = grades.find(g => g.student_id === studentId && g.activity_id === activityId);
    return grade ? String(grade.value) : '';
  };

  const handleGradeChange = (studentId, activityId, value) => {
    const key = `${studentId}-${activityId}`;
    setEditedGrades(prev => ({ ...prev, [key]: value }));
  };

  const saveGrade = async (studentId, activityId) => {
    const key = `${studentId}-${activityId}`;
    const value = parseFloat(editedGrades[key]);
    if (isNaN(value) || value < 0 || value > 5) {
      toast.error('La nota debe estar entre 0.0 y 5.0');
      return;
    }
    setSavingGrades(prev => ({ ...prev, [key]: true }));
    try {
      await api.post('/grades', {
        student_id: studentId,
        course_id: courseId,
        activity_id: activityId,
        value,
        comments: ''
      });
      toast.success('Nota guardada');
      const gRes = await api.get(`/grades?course_id=${courseId}`);
      setGrades(gRes.data);
      setEditedGrades(prev => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
    } catch (err) {
      toast.error('Error guardando nota');
    } finally {
      setSavingGrades(prev => ({ ...prev, [key]: false }));
    }
  };

  const saveAllEdited = async () => {
    const keys = Object.keys(editedGrades);
    if (keys.length === 0) { toast.info('No hay cambios por guardar'); return; }
    for (const key of keys) {
      const [studentId, activityId] = key.split('-');
      await saveGrade(studentId, activityId);
    }
  };

  const initials = (name) => name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();

  const getStudentAverage = (studentId) => {
    const studentGrades = grades.filter(g => g.student_id === studentId);
    if (studentGrades.length === 0) return null;
    return studentGrades.reduce((sum, g) => sum + g.value, 0) / studentGrades.length;
  };

  const editedCount = Object.keys(editedGrades).length;

  return (
    <DashboardLayout courseId={courseId}>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold font-heading">Notas</h1>
            <p className="text-muted-foreground mt-1">Califica y modifica las notas de los estudiantes (escala 0-5)</p>
          </div>
          {editedCount > 0 && (
            <Button onClick={saveAllEdited}>
              <Save className="h-4 w-4" /> Guardar Todo ({editedCount})
            </Button>
          )}
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : students.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <ClipboardList className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay estudiantes inscritos en este curso</p>
          </CardContent></Card>
        ) : (
          <Card className="shadow-card overflow-hidden">
            <ScrollArea className="w-full">
              <div className="min-w-max">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b bg-muted/30">
                      <th className="sticky left-0 z-10 bg-muted/50 backdrop-blur-sm text-left px-4 py-3 text-xs font-semibold text-muted-foreground min-w-52 border-r">
                        Estudiante
                      </th>
                      {activities.map((act) => (
                        <th key={act.id} className="text-center px-3 py-3 text-xs font-semibold text-muted-foreground min-w-24 border-r">
                          <div className="flex flex-col items-center gap-0.5">
                            <Badge variant="outline" className="text-xs font-mono">Act {act.activity_number || '?'}</Badge>
                            <span className="truncate max-w-24 block" title={act.title}>{act.title}</span>
                          </div>
                        </th>
                      ))}
                      <th className="text-center px-4 py-3 text-xs font-semibold text-foreground min-w-20 bg-primary/5">
                        Promedio
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((student, idx) => {
                      const avg = getStudentAverage(student.id);
                      return (
                        <tr key={student.id} className={`border-b hover:bg-muted/20 transition-colors ${idx % 2 === 0 ? '' : 'bg-muted/10'}`}>
                          <td className="sticky left-0 z-10 bg-card backdrop-blur-sm px-4 py-3 border-r">
                            <div className="flex items-center gap-3">
                              <Avatar className="h-7 w-7">
                                <AvatarFallback className="bg-primary/10 text-primary text-xs">{initials(student.name)}</AvatarFallback>
                              </Avatar>
                              <div className="min-w-0">
                                <p className="text-sm font-medium truncate">{student.name}</p>
                                <p className="text-xs text-muted-foreground font-mono">{student.cedula}</p>
                              </div>
                            </div>
                          </td>
                          {activities.map((act) => {
                            const key = `${student.id}-${act.id}`;
                            const value = getGradeValue(student.id, act.id);
                            const isEdited = editedGrades[key] !== undefined;
                            const isSaving = savingGrades[key];
                            return (
                              <td key={act.id} className="text-center px-2 py-2 border-r">
                                <div className="relative">
                                  <Input
                                    type="number"
                                    min="0"
                                    max="5"
                                    step="0.1"
                                    className={`w-20 h-8 text-center mx-auto text-sm ${isEdited ? 'border-primary ring-1 ring-primary/30' : ''} ${value && parseFloat(value) >= 3 ? 'text-success' : value ? 'text-destructive' : ''}`}
                                    value={value}
                                    onChange={(e) => handleGradeChange(student.id, act.id, e.target.value)}
                                    onBlur={() => {
                                      if (isEdited) saveGrade(student.id, act.id);
                                    }}
                                    placeholder="-"
                                    disabled={isSaving}
                                  />
                                  {isSaving && (
                                    <div className="absolute inset-0 flex items-center justify-center bg-card/50">
                                      <Loader2 className="h-3 w-3 animate-spin text-primary" />
                                    </div>
                                  )}
                                </div>
                              </td>
                            );
                          })}
                          <td className="text-center px-4 py-2 bg-primary/5">
                            {avg !== null ? (
                              <Badge
                                variant={avg >= 3 ? 'success' : 'destructive'}
                                className="text-sm px-3 py-1 font-bold"
                              >
                                {avg.toFixed(1)}
                              </Badge>
                            ) : (
                              <span className="text-sm text-muted-foreground">-</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </ScrollArea>
          </Card>
        )}

        {activities.length === 0 && students.length > 0 && (
          <Card className="shadow-card border-warning/30">
            <CardContent className="p-5 flex items-center gap-3">
              <ClipboardList className="h-5 w-5 text-warning" />
              <p className="text-sm text-muted-foreground">Crea actividades primero para poder asignar notas a cada una.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
