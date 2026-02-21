import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, BookOpen, Users, Building2 } from 'lucide-react';
import api from '@/lib/api';

export default function StudentCourses() {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [cRes, pRes, sRes, tRes] = await Promise.all([
        api.get(`/courses?student_id=${user.id}`),
        api.get('/programs'),
        api.get('/subjects'),
        api.get('/users?role=profesor')
      ]);
      setCourses(cRes.data);
      setPrograms(pRes.data);
      setSubjects(sRes.data);
      setTeachers(tRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user.id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const getName = (arr, id) => arr.find(i => i.id === id)?.name || '-';
  
  // Group courses by module
  const coursesByModule = courses.reduce((acc, course) => {
    const subject = subjects.find(s => s.id === course.subject_id);
    const moduleNum = subject?.module_number || 0;
    if (!acc[moduleNum]) acc[moduleNum] = [];
    acc[moduleNum].push(course);
    return acc;
  }, {});
  
  // Sort modules descending (Module 2 first)
  const sortedModuleNumbers = Object.keys(coursesByModule).map(Number).sort((a, b) => b - a);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold font-heading">Mis Cursos</h1>
          <p className="text-muted-foreground mt-1 text-base">Cursos en los que estás inscrito</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-10 w-10 animate-spin text-primary" /></div>
        ) : courses.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-12 text-center">
            <BookOpen className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground text-lg">No estás inscrito en ningún curso</p>
          </CardContent></Card>
        ) : (
          <div className="space-y-8">
            {sortedModuleNumbers.map(moduleNum => (
              <div key={moduleNum} className="space-y-4">
                <div className="flex items-center gap-3">
                  <Badge variant="default" className="text-lg px-6 py-2 font-semibold">
                    MÓDULO {moduleNum}
                  </Badge>
                  <div className="flex-1 h-px bg-border"></div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {coursesByModule[moduleNum].map((course) => (
                    <Card key={course.id} className="shadow-card hover:shadow-lg transition-all duration-200 hover:scale-[1.02]">
                      <CardHeader className="pb-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary mb-3">
                          <BookOpen className="h-6 w-6" />
                        </div>
                        <CardTitle className="text-2xl font-heading font-bold">{getName(subjects, course.subject_id)}</CardTitle>
                        <CardDescription className="text-base mt-1.5">{course.name}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2.5">
                          <div className="flex items-center gap-2 text-base text-muted-foreground">
                            <Building2 className="h-5 w-5" />
                            <span className="truncate">{getName(programs, course.program_id)}</span>
                          </div>
                          <div className="flex items-center gap-2 text-base text-muted-foreground">
                            <Users className="h-5 w-5" />
                            <span>Prof: {getName(teachers, course.teacher_id)}</span>
                          </div>
                          <Badge variant="secondary" className="text-sm px-3 py-1">{course.year}</Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
