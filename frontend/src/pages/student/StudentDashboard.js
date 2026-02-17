import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Loader2, BookOpen, FileText, ClipboardList, Clock, Calendar, TrendingUp } from 'lucide-react';
import { formatShortDate, formatRelativeDate } from '@/lib/utils';
import api from '@/lib/api';

export default function StudentDashboard() {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [activities, setActivities] = useState([]);
  const [grades, setGrades] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [cRes, gRes, sRes] = await Promise.all([
        api.get(`/courses?student_id=${user.id}`),
        api.get(`/grades?student_id=${user.id}`),
        api.get(`/submissions?student_id=${user.id}`)
      ]);
      setCourses(cRes.data);
      setGrades(gRes.data);
      setSubmissions(sRes.data);

      const allActivities = [];
      for (const course of cRes.data) {
        const aRes = await api.get(`/activities?course_id=${course.id}`);
        allActivities.push(...aRes.data.map(a => ({ ...a, courseName: course.name })));
      }
      setActivities(allActivities);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user.id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const avgGrade = grades.length > 0 ? (grades.reduce((s, g) => s + g.value, 0) / grades.length).toFixed(1) : '-';
  
  // Filter out activities that have submissions
  const hasSubmission = (actId) => submissions.find(s => s.activity_id === actId);
  const now = new Date();
  const pendingActivities = activities.filter(a => {
    const dueDate = new Date(a.due_date);
    const startDate = a.start_date ? new Date(a.start_date) : null;
    // Activity is pending if: not submitted, due date hasn't passed, and start date has passed (or no start date)
    return !hasSubmission(a.id) && dueDate > now && (!startDate || startDate <= now);
  });
  // Sort by due date and limit to 5 activities
  const upcomingActivities = pendingActivities.sort((a, b) => new Date(a.due_date) - new Date(b.due_date)).slice(0, 5);
  const overdueActivities = activities.filter(a => new Date(a.due_date) < new Date());

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold font-heading">Hola, {user?.name?.split(' ')[0]}!</h1>
          <p className="text-muted-foreground mt-1 text-lg">Tu resumen académico</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Mis Cursos', value: courses.length, icon: BookOpen, color: 'text-primary' },
                { label: 'Actividades Pendientes', value: pendingActivities.length, icon: FileText, color: 'text-warning' },
                { label: 'Promedio General', value: avgGrade, icon: TrendingUp, color: 'text-success' },
                { label: 'Notas Registradas', value: grades.length, icon: ClipboardList, color: 'text-info' },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <Card key={item.label} className="shadow-card">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-3">
                        <Icon className={`h-7 w-7 ${item.color}`} />
                        <Badge variant="secondary" className="text-sm font-medium">{item.label}</Badge>
                      </div>
                      <p className="text-4xl font-bold font-heading">{item.value}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="shadow-card">
                <CardHeader>
                  <CardTitle className="text-xl font-heading">Próximas Actividades</CardTitle>
                  <CardDescription className="text-base">
                    {upcomingActivities.length > 0 
                      ? `Mostrando las ${upcomingActivities.length} entregas más próximas ${pendingActivities.length > 5 ? `de ${pendingActivities.length} pendientes` : ''}`
                      : 'Entregas pendientes'
                    }
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {upcomingActivities.length === 0 ? (
                    <p className="text-base text-muted-foreground py-6 text-center">🎉 ¡No hay actividades pendientes!</p>
                  ) : upcomingActivities.map((act) => {
                    const due = new Date(act.due_date);
                    const daysLeft = Math.ceil((due - new Date()) / (1000 * 60 * 60 * 24));
                    return (
                      <div key={act.id} className="flex items-center justify-between rounded-lg border p-4 hover:bg-accent/50 transition-colors">
                        <div className="min-w-0 flex-1">
                          <p className="text-base font-medium truncate">{act.title}</p>
                          <p className="text-sm text-muted-foreground mt-0.5">{act.courseName}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            <Clock className="h-3 w-3 inline mr-1" />
                            Vence: {formatShortDate(act.due_date)}
                          </p>
                        </div>
                        <div className="text-right shrink-0 ml-4">
                          <Badge variant={daysLeft <= 3 ? 'warning' : 'secondary'} className="text-sm px-3 py-1">
                            {daysLeft} {daysLeft === 1 ? 'día' : 'días'}
                          </Badge>
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader>
                  <CardTitle className="text-xl font-heading">Últimas Notas</CardTitle>
                  <CardDescription className="text-base">Tus calificaciones recientes</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {grades.length === 0 ? (
                    <p className="text-base text-muted-foreground py-6 text-center">No hay notas registradas</p>
                  ) : grades.slice(0, 5).map((grade) => (
                    <div key={grade.id} className="flex items-center justify-between rounded-lg border p-4 hover:bg-accent/50 transition-colors">
                      <div className="min-w-0 flex-1">
                        <p className="text-base font-medium">Calificación</p>
                        <p className="text-sm text-muted-foreground mt-0.5">{grade.comments || 'Sin comentarios'}</p>
                      </div>
                      <Badge variant={grade.value >= 3 ? 'success' : 'destructive'} className="text-lg px-4 py-1.5 font-semibold">
                        {grade.value.toFixed(1)}
                      </Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
