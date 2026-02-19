import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, BookOpen, Users, ChevronRight, Search, Filter } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function TeacherCourseSelector() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('all');

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

  const filteredCourses = courses.filter(course => {
    const matchesSearch = searchTerm === '' ||
      course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      getName(programs, course.program_id).toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSubject = subjectFilter === 'all' || course.subject_id === subjectFilter;
    
    return matchesSearch && matchesSubject;
  });

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
          <>
            {/* Search and Filters */}
            <Card className="shadow-card max-w-4xl mx-auto">
              <CardContent className="p-4">
                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Buscar por nombre de curso o programa..."
                      className="pl-9"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                  <Select value={subjectFilter} onValueChange={setSubjectFilter}>
                    <SelectTrigger className="w-full sm:w-[220px]">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Filtrar por materia" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todas las materias</SelectItem>
                      {subjects.map(subject => (
                        <SelectItem key={subject.id} value={subject.id}>
                          {subject.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {filteredCourses.length === 0 ? (
              <Card className="max-w-md mx-auto shadow-card">
                <CardContent className="p-10 text-center">
                  <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground">No se encontraron cursos</p>
                  <p className="text-sm text-muted-foreground mt-1">Intenta con otros criterios de búsqueda.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {filteredCourses.map((course) => (
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
      </>
        )}
      </div>
    </DashboardLayout>
  );
}
