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
          <h1 className="text-4xl sm:text-5xl font-bold font-heading text-foreground">
            Mis Cursos
          </h1>
          <p className="text-muted-foreground mt-3 text-xl">
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
            {filteredCourses.map((course) => {
              const subjectName = getName(subjects, course.subject_id);
              const programName = getName(programs, course.program_id);
              
              return (
                <Card
                  key={course.id}
                  className="shadow-card hover:shadow-card-hover transition-all cursor-pointer group border-2 border-border/50 hover:border-primary/40"
                  onClick={() => navigate(`/student/course/${course.id}`)}
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                        <BookOpen className="h-7 w-7" />
                      </div>
                      <ChevronRight className="h-7 w-7 text-muted-foreground group-hover:text-primary transition-colors" />
                    </div>
                    {/* Show SUBJECT name large */}
                    <CardTitle className="text-2xl font-heading leading-tight">
                      {subjectName}
                    </CardTitle>
                    {/* Show GROUP below (e.g., ENERO-2026) */}
                    {course.grupo && (
                      <div className="mt-3">
                        <Badge 
                          variant="secondary" 
                          className="text-base px-4 py-2"
                        >
                          {course.grupo}
                        </Badge>
                      </div>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <CardDescription className="text-base">
                      {programName}
                    </CardDescription>
                    <div className="flex gap-2 flex-wrap">
                      <Badge variant="outline" className="text-base px-3 py-1">{course.year}</Badge>
                      <Badge variant="outline" className="text-base px-3 py-1">{course.name}</Badge>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
