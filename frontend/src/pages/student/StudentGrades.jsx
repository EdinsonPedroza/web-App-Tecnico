import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useParams, useSearchParams } from 'react-router-dom';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Loader2, ClipboardList, TrendingUp, BookOpen } from 'lucide-react';
import api from '@/lib/api';

export default function StudentGrades() {
  const { user } = useAuth();
  const { courseId } = useParams();
  const [searchParams] = useSearchParams();
  const subjectId = searchParams.get('subjectId');
  const [grades, setGrades] = useState([]);
  const [courses, setCourses] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      let gradeQuery = courseId ? `student_id=${user.id}&course_id=${courseId}` : `student_id=${user.id}`;
      if (subjectId) gradeQuery += `&subject_id=${subjectId}`;
      const courseQuery = `student_id=${user.id}`;
      
      const [gRes, cRes] = await Promise.all([
        api.get(`/grades?${gradeQuery}`),
        api.get(`/courses?${courseQuery}`)
      ]);
      setGrades(gRes.data);
      
      // Filter courses if courseId is provided
      const filteredCourses = courseId ? cRes.data.filter(c => c.id === courseId) : cRes.data;
      setCourses(filteredCourses);

      // Fetch activities for all courses in parallel
      const actResponses = await Promise.all(
        filteredCourses.map(course => {
          let actUrl = `/activities?course_id=${course.id}`;
          if (subjectId) actUrl += `&subject_id=${subjectId}`;
          return api.get(actUrl);
        })
      );
      setActivities(actResponses.flatMap(r => r.data));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user.id, courseId, subjectId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const getActivityName = (id) => {
    const act = activities.find(a => a.id === id);
    return act ? `Act ${act.activity_number || '?'}: ${act.title}` : 'Nota General';
  };

  const regularActivityIds = new Set(activities.filter(a => !a.is_recovery).map(a => a.id));
  const regularGrades = grades.filter(g => !g.activity_id || regularActivityIds.has(g.activity_id));
  const overallAvg = regularGrades.length > 0 ? (regularGrades.reduce((s, g) => s + g.value, 0) / regularGrades.length).toFixed(1) : '-';

  // Group grades by course
  const gradesByCourse = courses.map(course => {
    const courseGrades = grades.filter(g => g.course_id === course.id);
    const courseActivities = activities.filter(a => a.course_id === course.id)
      .sort((a, b) => (a.activity_number || 0) - (b.activity_number || 0));
    const courseRegularActIds = new Set(courseActivities.filter(a => !a.is_recovery).map(a => a.id));
    const courseRegularGrades = courseGrades.filter(g => !g.activity_id || courseRegularActIds.has(g.activity_id));
    const avg = courseRegularGrades.length > 0
      ? (courseRegularGrades.reduce((s, g) => s + g.value, 0) / courseRegularGrades.length).toFixed(1)
      : null;
    return { course, grades: courseGrades, activities: courseActivities, avg };
  });

  return (
    <DashboardLayout courseId={courseId}>
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
