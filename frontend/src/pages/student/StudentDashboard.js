import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Loader2, BookOpen, FileText, ClipboardList, Clock, Calendar, TrendingUp } from 'lucide-react';
import api from '@/lib/api';

export default function StudentDashboard() {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [activities, setActivities] = useState([]);
  const [grades, setGrades] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [cRes, gRes] = await Promise.all([
        api.get(`/courses?student_id=${user.id}`),
        api.get(`/grades?student_id=${user.id}`)
      ]);
      setCourses(cRes.data);
      setGrades(gRes.data);

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
  const upcomingActivities = activities.filter(a => new Date(a.due_date) > new Date()).sort((a, b) => new Date(a.due_date) - new Date(b.due_date));
  const overdueActivities = activities.filter(a => new Date(a.due_date) < new Date());

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold font-heading">Hola, {user?.name?.split(' ')[0]}!</h1>
          <p className="text-muted-foreground mt-1">Tu resumen académico</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Mis Cursos', value: courses.length, icon: BookOpen, color: 'text-primary' },
                { label: 'Actividades Pendientes', value: upcomingActivities.length, icon: FileText, color: 'text-warning' },
                { label: 'Promedio General', value: avgGrade, icon: TrendingUp, color: 'text-success' },
                { label: 'Notas Registradas', value: grades.length, icon: ClipboardList, color: 'text-info' },
              ].map((item) => {
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
                          <p className="text-sm font-medium truncate">{act.title}</p>
                          <p className="text-xs text-muted-foreground">{act.courseName}</p>
                        </div>
                        <div className="text-right shrink-0 ml-3">
                          <Badge variant={daysLeft <= 3 ? 'warning' : 'secondary'}>
                            <Clock className="h-3 w-3 mr-1" />
                            {daysLeft} días
                          </Badge>
                        </div>
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
                      <Badge variant={grade.value >= 3 ? 'success' : 'destructive'} className="text-base px-3">
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
