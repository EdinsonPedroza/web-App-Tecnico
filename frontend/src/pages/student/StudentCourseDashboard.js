import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, FileText, ClipboardList, Video, TrendingUp } from 'lucide-react';
import api from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

export default function StudentCourseDashboard() {
  const { courseId } = useParams();
  const [searchParams] = useSearchParams();
  const subjectId = searchParams.get('subjectId');
  const { user } = useAuth();
  const [course, setCourse] = useState(null);
  const [subject, setSubject] = useState(null);
  const [activities, setActivities] = useState([]);
  const [videos, setVideos] = useState([]);
  const [grades, setGrades] = useState([]);
  const [loading, setLoading] = useState(true);

  const PASSING_GRADE_THRESHOLD = 3;

  const fetchData = useCallback(async () => {
    try {
      let activitiesUrl = `/activities?course_id=${courseId}`;
      if (subjectId) activitiesUrl += `&subject_id=${subjectId}`;
      let videosUrl = `/class-videos?course_id=${courseId}`;
      if (subjectId) videosUrl += `&subject_id=${subjectId}`;
      let gradesUrl = `/grades?student_id=${user.id}&course_id=${courseId}`;
      if (subjectId) gradesUrl += `&subject_id=${subjectId}`;
      const requests = [
        api.get(`/courses/${courseId}`),
        api.get(activitiesUrl),
        api.get(videosUrl),
        api.get(gradesUrl)
      ];
      if (subjectId) {
        requests.push(api.get('/subjects'));
      }
      const results = await Promise.all(requests);
      const [cRes, aRes, vRes, gRes] = results;
      setCourse(cRes.data);
      setActivities(aRes.data);
      setVideos(vRes.data);
      setGrades(gRes.data);
      if (subjectId && results[4]) {
        const found = results[4].data.find(s => s.id === subjectId);
        setSubject(found || null);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [courseId, subjectId, user.id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) return <DashboardLayout courseId={courseId}><div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div></DashboardLayout>;

  const avgGrade = grades.length > 0 ? (grades.reduce((s, g) => s + g.value, 0) / grades.length).toFixed(1) : '-';
  const upcomingActivities = activities.filter(a => new Date(a.due_date) > new Date());
  
  const stats = [
    { label: 'Actividades Pendientes', value: upcomingActivities.length, icon: FileText, color: 'text-warning' },
    { label: 'Notas Registradas', value: grades.length, icon: ClipboardList, color: 'text-info' },
    { label: 'Promedio', value: avgGrade, icon: TrendingUp, color: 'text-success' },
    { label: 'Videos', value: videos.length, icon: Video, color: 'text-primary' },
  ];

  return (
    <DashboardLayout courseId={courseId}>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold font-heading">{subject?.name || course?.name}</h1>
          <p className="text-muted-foreground mt-1">Resumen del curso</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((item) => {
            const Icon = item.icon;
            return (
              <Card key={item.label} className="shadow-card">
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-3">
                    <Icon className={`h-5 w-5 ${item.color}`} />
                    <Badge variant="secondary" className="text-xs">{item.label}</Badge>
                  </div>
                  <p className="text-3xl font-bold font-heading">{item.value}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle className="text-lg font-heading">Próximas Actividades</CardTitle>
              <CardDescription>Entregas pendientes</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {upcomingActivities.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4 text-center">No hay actividades pendientes</p>
              ) : upcomingActivities.slice(0, 5).map((act) => {
                const due = new Date(act.due_date);
                const daysLeft = Math.ceil((due - new Date()) / (1000 * 60 * 60 * 24));
                return (
                  <div key={act.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs font-mono shrink-0">Act {act.activity_number || '?'}</Badge>
                        <p className="text-sm font-medium truncate">{act.title}</p>
                      </div>
                      <p className="text-xs text-muted-foreground">Vence: {due.toLocaleDateString('es-CO')}</p>
                    </div>
                    <Badge variant={daysLeft <= 3 ? 'destructive' : 'secondary'}>
                      {daysLeft} días
                    </Badge>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          <Card className="shadow-card">
            <CardHeader>
              <CardTitle className="text-lg font-heading">Últimas Notas</CardTitle>
              <CardDescription>Tus calificaciones recientes</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {grades.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4 text-center">No hay notas registradas</p>
              ) : grades.slice(0, 5).map((grade) => (
                <div key={grade.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">Calificación</p>
                    <p className="text-xs text-muted-foreground">{grade.comments || 'Sin comentarios'}</p>
                  </div>
                  <Badge variant={grade.value >= PASSING_GRADE_THRESHOLD ? 'success' : 'destructive'} className="text-base px-3">
                    {grade.value.toFixed(1)}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
