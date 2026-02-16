import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, BookOpen, ChevronRight, ArrowLeft } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function StudentCourseSelector() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProgram, setSelectedProgram] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      // Get selected program from session storage
      const programId = sessionStorage.getItem('selectedProgramId');
      
      const [cRes, pRes, sRes] = await Promise.all([
        api.get(`/courses?student_id=${user.id}`),
        api.get('/programs'),
        api.get('/subjects')
      ]);
      
      setCourses(cRes.data);
      setPrograms(pRes.data);
      setSubjects(sRes.data);
      
      if (programId) {
        setSelectedProgram(pRes.data.find(p => p.id === programId));
      }
    } catch (err) {
      toast.error('Error cargando cursos');
    } finally {
      setLoading(false);
    }
  }, [user.id]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const getName = (arr, id) => arr.find(i => i.id === id)?.name || '-';
  
  // Filter courses by selected program
  const filteredCourses = selectedProgram 
    ? courses.filter(c => c.program_id === selectedProgram.id)
    : courses;

  const handleBackToPrograms = () => {
    sessionStorage.removeItem('selectedProgramId');
    navigate('/student');
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {selectedProgram && (
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBackToPrograms}
              className="gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Cambiar programa
            </Button>
            <Badge variant="secondary" className="text-base px-4 py-2">
              {selectedProgram.name}
            </Badge>
          </div>
        )}
        
        <div className="text-center max-w-xl mx-auto">
          <h1 className="text-3xl sm:text-4xl font-bold font-heading text-foreground">
            Mis Cursos
          </h1>
          <p className="text-muted-foreground mt-3 text-lg">
            Selecciona un curso para ver tus notas, actividades y clases.
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-10 w-10 animate-spin text-primary" /></div>
        ) : filteredCourses.length === 0 ? (
          <Card className="max-w-md mx-auto shadow-card">
            <CardContent className="p-12 text-center">
              <BookOpen className="h-14 w-14 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground text-lg">No estás inscrito en ningún curso</p>
              <p className="text-sm text-muted-foreground mt-2">Contacta al administrador para inscribirte en cursos.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.map((course) => (
              <Card
                key={course.id}
                className="shadow-card hover:shadow-card-hover transition-all cursor-pointer group border-2 border-border/50 hover:border-primary/40"
                onClick={() => navigate(`/student/course/${course.id}`)}
              >
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <BookOpen className="h-6 w-6" />
                    </div>
                    <ChevronRight className="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <CardTitle className="text-lg font-heading mt-4 leading-tight">{course.name}</CardTitle>
                  <CardDescription className="text-sm mt-2">
                    {getName(programs, course.program_id)}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <BookOpen className="h-4 w-4" />
                    <span className="truncate">{getName(subjects, course.subject_id)}</span>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant="outline" className="text-sm">{course.year}</Badge>
                    {course.grupo && (
                      <Badge 
                        variant="secondary" 
                        className="text-sm truncate max-w-[150px]"
                        title={course.grupo}
                      >
                        {course.grupo}
                      </Badge>
                    )}
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
