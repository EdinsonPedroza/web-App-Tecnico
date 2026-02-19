import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2, BookOpen, Users, ChevronRight, ArrowLeft, Search } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function TeacherCourseSelector() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

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

  // Get unique subject IDs from all teacher's courses
  const teacherSubjectIds = [...new Set(
    courses.flatMap(course => {
      const ids = course.subject_ids && course.subject_ids.length > 0
        ? course.subject_ids
        : (course.subject_id ? [course.subject_id] : []);
      return ids;
    })
  )];

  // Build subject list with their info
  const teacherSubjects = teacherSubjectIds
    .map(subjectId => subjects.find(s => s.id === subjectId))
    .filter(Boolean);

  // Filter subjects by search query
  const filteredSubjects = searchQuery.trim()
    ? teacherSubjects.filter(s =>
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (getName(programs, s.program_id) || '').toLowerCase().includes(searchQuery.toLowerCase())
      )
    : teacherSubjects;

  // Get courses (groups) that include the selected subject
  const groupsForSubject = selectedSubject
    ? courses.filter(course => {
        const ids = course.subject_ids && course.subject_ids.length > 0
          ? course.subject_ids
          : (course.subject_id ? [course.subject_id] : []);
        return ids.includes(selectedSubject.id);
      })
    : [];

  // Filter groups by search query
  const filteredGroups = searchQuery.trim()
    ? groupsForSubject.filter(c =>
        (c.grupo || c.name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (getName(programs, c.program_id) || '').toLowerCase().includes(searchQuery.toLowerCase())
      )
    : groupsForSubject;

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {!selectedSubject ? (
          /* Step 1: Show subjects the teacher teaches */
          <>
            <div className="text-center max-w-xl mx-auto">
              <h1 className="text-2xl sm:text-3xl font-bold font-heading text-foreground">
                ¡Bienvenido, {user?.name?.split(' ')[0]}!
              </h1>
              <p className="text-muted-foreground mt-2">
                Selecciona una materia para ver los grupos y gestionar actividades.
              </p>
            </div>

            {loading ? (
              <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
            ) : teacherSubjects.length === 0 ? (
              <Card className="max-w-md mx-auto shadow-card">
                <CardContent className="p-10 text-center">
                  <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground">No tienes materias asignadas</p>
                  <p className="text-sm text-muted-foreground mt-1">Contacta al administrador para que te asigne materias.</p>
                </CardContent>
              </Card>
            ) : (
              <>
                <div className="max-w-md mx-auto">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Buscar materia..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {filteredSubjects.map((subject) => {
                  // Count groups that include this subject
                  const groupCount = courses.filter(course => {
                    const ids = course.subject_ids && course.subject_ids.length > 0
                      ? course.subject_ids
                      : (course.subject_id ? [course.subject_id] : []);
                    return ids.includes(subject.id);
                  }).length;

                  return (
                    <Card
                      key={subject.id}
                      className="shadow-card hover:shadow-card-hover transition-all cursor-pointer group border-2 border-border/50 hover:border-primary/40"
                      onClick={() => { setSelectedSubject(subject); setSearchQuery(''); }}
                    >
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                            <BookOpen className="h-6 w-6" />
                          </div>
                          <ChevronRight className="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors" />
                        </div>
                        <CardTitle className="text-xl font-heading leading-tight">
                          {subject.name}
                        </CardTitle>
                        {subject.program_id && (
                          <CardDescription className="text-sm mt-1">
                            {getName(programs, subject.program_id)}
                          </CardDescription>
                        )}
                      </CardHeader>
                      <CardContent>
                        <Badge variant="secondary" className="text-sm px-3 py-1">
                          <Users className="h-3.5 w-3.5 mr-1.5" />
                          {groupCount} {groupCount === 1 ? 'grupo' : 'grupos'}
                        </Badge>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
              </>
            )}
          </>
        ) : (
          /* Step 2: Show groups for the selected subject */
          <>
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => { setSelectedSubject(null); setSearchQuery(''); }}
                className="gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Volver a materias
              </Button>
              <Badge variant="secondary" className="text-base px-4 py-2">
                {selectedSubject.name}
              </Badge>
            </div>

            <div className="text-center max-w-xl mx-auto">
              <h1 className="text-2xl sm:text-3xl font-bold font-heading text-foreground">
                Grupos
              </h1>
              <p className="text-muted-foreground mt-2">
                Selecciona un grupo para gestionar actividades, notas y material de clase.
              </p>
            </div>

            {groupsForSubject.length === 0 ? (
              <Card className="max-w-md mx-auto shadow-card">
                <CardContent className="p-10 text-center">
                  <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                  <p className="text-muted-foreground">No hay grupos para esta materia</p>
                </CardContent>
              </Card>
            ) : (
              <>
                {groupsForSubject.length > 3 && (
                  <div className="max-w-md mx-auto">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Buscar grupo..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9"
                      />
                    </div>
                  </div>
                )}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {filteredGroups.map((course) => (
                  <Card
                    key={course.id}
                    className="shadow-card hover:shadow-card-hover transition-all cursor-pointer group border-2 border-border/50 hover:border-primary/40"
                    onClick={() => navigate(`/teacher/course/${course.id}?subjectId=${selectedSubject.id}`)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                          <Users className="h-5 w-5" />
                        </div>
                        <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                      </div>
                      <CardTitle className="text-lg font-heading mt-2">
                        {course.grupo || course.name}
                      </CardTitle>
                      <CardDescription className="text-xs">
                        {getName(programs, course.program_id)}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex gap-2 flex-wrap">
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
              </>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
