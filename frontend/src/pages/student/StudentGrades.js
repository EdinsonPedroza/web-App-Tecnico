import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Loader2, ClipboardList, TrendingUp, BookOpen } from 'lucide-react';
import api from '@/lib/api';

export default function StudentGrades() {
  const { user } = useAuth();
  const [grades, setGrades] = useState([]);
  const [courses, setCourses] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [gRes, cRes] = await Promise.all([
        api.get(`/grades?student_id=${user.id}`),
        api.get(`/courses?student_id=${user.id}`)
      ]);
      setGrades(gRes.data);
      setCourses(cRes.data);

      const allActs = [];
      for (const course of cRes.data) {
        const aRes = await api.get(`/activities?course_id=${course.id}`);
        allActs.push(...aRes.data);
      }
      setActivities(allActs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user.id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const getActivityName = (id) => {
    const act = activities.find(a => a.id === id);
    return act ? `Act ${act.activity_number || '?'}: ${act.title}` : 'Nota General';
  };

  const overallAvg = grades.length > 0 ? (grades.reduce((s, g) => s + g.value, 0) / grades.length).toFixed(1) : '-';

  // Group grades by course
  const gradesByCourse = courses.map(course => {
    const courseGrades = grades.filter(g => g.course_id === course.id);
    const courseActivities = activities.filter(a => a.course_id === course.id)
      .sort((a, b) => (a.activity_number || 0) - (b.activity_number || 0));
    const avg = courseGrades.length > 0
      ? (courseGrades.reduce((s, g) => s + g.value, 0) / courseGrades.length).toFixed(1)
      : null;
    return { course, grades: courseGrades, activities: courseActivities, avg };
  });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold font-heading">Mis Notas</h1>
            <p className="text-muted-foreground mt-1">Calificaciones por materia</p>
          </div>
          <Card className="shadow-card">
            <CardContent className="p-4 flex items-center gap-3">
              <TrendingUp className="h-5 w-5 text-primary" />
              <div>
                <p className="text-xs text-muted-foreground">Promedio General</p>
                <p className="text-2xl font-bold font-heading">{overallAvg}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : courses.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <ClipboardList className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No estás inscrito en ningún curso</p>
          </CardContent></Card>
        ) : (
          <div className="space-y-6">
            {gradesByCourse.map(({ course, grades: cGrades, activities: cActivities, avg }) => (
              <Card key={course.id} className="shadow-card overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <BookOpen className="h-5 w-5" />
                      </div>
                      <div>
                        <CardTitle className="text-base font-heading">{course.name}</CardTitle>
                        <CardDescription className="text-xs">{course.year}</CardDescription>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">Promedio Materia</p>
                      {avg !== null ? (
                        <Badge variant={parseFloat(avg) >= 3 ? 'success' : 'destructive'} className="text-lg px-3 py-1 font-bold">
                          {avg}
                        </Badge>
                      ) : (
                        <span className="text-sm text-muted-foreground">Sin notas</span>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <Separator />
                <CardContent className="pt-4">
                  {cActivities.length === 0 && cGrades.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">No hay actividades ni notas aún</p>
                  ) : (
                    <div className="space-y-2">
                      {cActivities.map((act) => {
                        const grade = cGrades.find(g => g.activity_id === act.id);
                        return (
                          <div key={act.id} className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/20 transition-colors">
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center gap-2">
                                <Badge variant="outline" className="text-xs font-mono shrink-0">Act {act.activity_number || '?'}</Badge>
                                <p className="text-sm font-medium truncate">{act.title}</p>
                              </div>
                              {grade?.comments && (
                                <p className="text-xs text-muted-foreground mt-1 ml-14">{grade.comments}</p>
                              )}
                            </div>
                            <div className="shrink-0 ml-3">
                              {grade ? (
                                <Badge
                                  variant={grade.value >= 3 ? 'success' : 'destructive'}
                                  className="text-base px-3 py-1 font-bold"
                                >
                                  {grade.value.toFixed(1)}
                                </Badge>
                              ) : (
                                <span className="text-sm text-muted-foreground">Pendiente</span>
                              )}
                            </div>
                          </div>
                        );
                      })}
                      {/* Show any general grades (not linked to specific activities) */}
                      {cGrades.filter(g => !g.activity_id).map((grade) => (
                        <div key={grade.id} className="flex items-center justify-between rounded-lg border p-3 bg-primary/5">
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium">Nota General</p>
                            {grade.comments && (
                              <p className="text-xs text-muted-foreground mt-1">{grade.comments}</p>
                            )}
                          </div>
                          <Badge
                            variant={grade.value >= 3 ? 'success' : 'destructive'}
                            className="text-base px-3 py-1 font-bold"
                          >
                            {grade.value.toFixed(1)}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
