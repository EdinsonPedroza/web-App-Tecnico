import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, GraduationCap, ChevronRight } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function StudentProgramSelector() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPrograms = async () => {
      try {
        const response = await api.get('/student/programs');
        setPrograms(response.data);
      } catch (err) {
        toast.error('Error cargando programas');
      } finally {
        setLoading(false);
      }
    };

    fetchPrograms();
  }, []);

  const handleSelectProgram = (programId) => {
    // Store selected program in session storage
    sessionStorage.setItem('selectedProgramId', programId);
    navigate('/student/courses');
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        <div className="text-center max-w-2xl mx-auto">
          <h1 className="text-4xl sm:text-5xl font-bold font-heading text-foreground">
            ¡Bienvenido, {user?.name?.split(' ')[0]}!
          </h1>
          <p className="text-muted-foreground mt-3 text-xl">
            Selecciona el programa técnico para ver tus materias y actividades.
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="h-10 w-10 animate-spin text-primary" />
          </div>
        ) : programs.length === 0 ? (
          <Card className="max-w-lg mx-auto shadow-card">
            <CardContent className="p-12 text-center">
              <GraduationCap className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground text-lg">No estás inscrito en ningún programa</p>
              <p className="text-sm text-muted-foreground mt-2">
                Contacta al administrador para inscribirte en un programa técnico.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
            {programs.map((program) => (
              <Card
                key={program.id}
                className="shadow-card hover:shadow-card-hover transition-all cursor-pointer group border-2 border-border/50 hover:border-primary/40"
                onClick={() => handleSelectProgram(program.id)}
              >
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <GraduationCap className="h-8 w-8" />
                    </div>
                    <ChevronRight className="h-7 w-7 text-muted-foreground group-hover:text-primary transition-colors" />
                  </div>
                  <CardTitle className="text-2xl font-heading leading-tight">
                    {program.name}
                  </CardTitle>
                  <CardDescription className="text-base mt-2">
                    {program.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-base px-4 py-1.5">
                      {program.duration || '12 meses'}
                    </Badge>
                    {program.modules && (
                      <Badge variant="secondary" className="text-base px-4 py-1.5">
                        {program.modules.length} módulos
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
