import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, FileText, ClipboardList, Video, Users } from 'lucide-react';
import api from '@/lib/api';

export default function TeacherCourseDashboard() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [activities, setActivities] = useState([]);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [cRes, aRes, vRes] = await Promise.all([
        api.get(`/courses/${courseId}`),
        api.get(`/activities?course_id=${courseId}`),
        api.get(`/class-videos?course_id=${courseId}`)
      ]);
      setCourse(cRes.data);
      setActivities(aRes.data);
      setVideos(vRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) return <DashboardLayout courseId={courseId}><div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div></DashboardLayout>;

  const stats = [
    { label: 'Estudiantes', value: course?.student_ids?.length || 0, icon: Users, color: 'text-primary' },
    { label: 'Actividades', value: activities.length, icon: FileText, color: 'text-success' },
    { label: 'Videos', value: videos.length, icon: Video, color: 'text-warning' },
  ];

  return (
    <DashboardLayout courseId={courseId}>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold font-heading">{course?.name}</h1>
          <p className="text-muted-foreground mt-1">Resumen del curso</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {stats.map((item) => {
            const Icon = item.icon;
            return (
              <Card key={item.label} className="shadow-card">
                <CardContent className="p-5 flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                    <Icon className={`h-6 w-6 ${item.color}`} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold font-heading">{item.value}</p>
                    <p className="text-sm text-muted-foreground">{item.label}</p>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle className="text-lg font-heading">Actividades Recientes</CardTitle>
              <CardDescription>Últimas actividades creadas</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {activities.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4 text-center">No hay actividades</p>
              ) : activities.slice(0, 5).map((act) => {
                const due = new Date(act.due_date);
                const isOverdue = due < new Date();
                return (
                  <div key={act.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs font-mono shrink-0">Act {act.activity_number || '?'}</Badge>
                        <p className="text-sm font-medium truncate">{act.title}</p>
                      </div>
                      <p className="text-xs text-muted-foreground">Vence: {due.toLocaleDateString('es-CO')}</p>
                    </div>
                    <Badge variant={isOverdue ? 'destructive' : 'success'}>
                      {isOverdue ? 'Vencida' : 'Activa'}
                    </Badge>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          <Card className="shadow-card">
            <CardHeader>
              <CardTitle className="text-lg font-heading">Videos de Clase</CardTitle>
              <CardDescription>Material audiovisual subido</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {videos.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4 text-center">No hay videos subidos</p>
              ) : videos.slice(0, 5).map((vid) => (
                <div key={vid.id} className="flex items-center gap-3 rounded-lg border p-3">
                  <Video className="h-5 w-5 text-primary shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate">{vid.title}</p>
                    <p className="text-xs text-muted-foreground truncate">{vid.description}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
