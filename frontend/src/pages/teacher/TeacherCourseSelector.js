import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, BookOpen, Users, ChevronRight } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function TeacherCourseSelector() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [cRes, pRes, sRes] = await Promise.all([
        api.get(`/courses?teacher_id=${user.id}`),
        api.get('/programs'),
        api.get('/subjects')
      ]);
      setCourses(cRes.data);
      setPrograms(pRes.data);
      setSubjects(sRes.data);
    } catch (err) {
      toast.error('Error cargando cursos');
    } finally {
      setLoading(false);
    }
  }, [user.id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const getName = (arr, id) => arr.find(i => i.id === id)?.name || '-';

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="text-center max-w-xl mx-auto">
          <h1 className="text-2xl sm:text-3xl font-bold font-heading text-foreground">
            ¡Bienvenido, {user?.name?.split(' ')[0]}!
          </h1>
          <p className="text-muted-foreground mt-2">
            Selecciona un curso para comenzar a gestionar actividades, notas y material de clase.
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : courses.length === 0 ? (
          <Card className="max-w-md mx-auto shadow-card">
            <CardContent className="p-10 text-center">
              <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground">No tienes cursos asignados</p>
              <p className="text-sm text-muted-foreground mt-1">Contacta al administrador para que te asigne cursos.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {courses.map((course) => (
              <Card
                key={course.id}
                className="shadow-card hover:shadow-card-hover transition-all cursor-pointer group border-border/50 hover:border-primary/30"
                onClick={() => navigate(`/teacher/course/${course.id}`)}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <BookOpen className="h-5 w-5" />
                    </div>
                    <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <CardTitle className="text-base font-heading mt-3">{course.name}</CardTitle>
                  <CardDescription className="text-xs">
                    {getName(programs, course.program_id)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
                    <BookOpen className="h-3.5 w-3.5" />
                    <span className="truncate">{getName(subjects, course.subject_id)}</span>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant="secondary">
                      <Users className="h-3 w-3 mr-1" />
                      {course.student_ids?.length || 0} estudiantes
                    </Badge>
                    <Badge variant="outline">{course.year}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
