import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Loader2, AlertCircle, CheckCircle, BookOpen, RefreshCw, CalendarX } from 'lucide-react';
import api from '@/lib/api';
import { useNavigate } from 'react-router-dom';

export default function StudentRecoveriesPage() {
  const [recoveries, setRecoveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchRecoveries = useCallback(async () => {
    try {
      const res = await api.get('/student/my-recoveries');
      setRecoveries(res.data.recoveries || []);
    } catch (err) {
      toast.error('Error cargando recuperaciones');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecoveries();
  }, [fetchRecoveries]);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold font-heading">Mis Recuperaciones</h1>
            <p className="text-muted-foreground mt-1 text-lg">
              Materias que puedes recuperar
            </p>
          </div>
          <Button onClick={fetchRecoveries} variant="outline">
            <RefreshCw className="h-4 w-4" /> Actualizar
          </Button>
        </div>

        {recoveries.length === 0 ? (
          <Card className="shadow-card">
            <CardContent className="p-10 text-center">
              <CheckCircle className="h-12 w-12 text-success mx-auto mb-3" />
              <p className="text-lg font-medium">¡No tienes materias pendientes de recuperación!</p>
              <p className="text-sm text-muted-foreground mt-1">
                Has aprobado todas tus materias o no tienes recuperaciones aprobadas aún
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {/* Info Card */}
            <Card className="shadow-card bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
              <CardContent className="p-5">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                      Tienes {recoveries.length} materia{recoveries.length !== 1 ? 's' : ''} pendiente{recoveries.length !== 1 ? 's' : ''} de recuperación
                    </p>
                    <p className="text-xs text-blue-800 dark:text-blue-200 mt-1">
                      Completa las actividades de recuperación en cada curso para mejorar tu calificación
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recovery Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recoveries.map((recovery) => (
                <Card 
                  key={recovery.id} 
                  className={`shadow-card transition-all ${recovery.recovery_closed ? 'opacity-75 grayscale border-destructive/30' : 'hover:shadow-lg hover-lift cursor-pointer'}`}
                  onClick={() => !recovery.recovery_closed && navigate(`/student/course/${recovery.course_id}`)}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between gap-2">
                      {recovery.recovery_closed
                        ? <CalendarX className="h-5 w-5 text-destructive shrink-0 mt-1" />
                        : <BookOpen className="h-5 w-5 text-primary shrink-0 mt-1" />
                      }
                      {recovery.recovery_closed
                        ? <Badge variant="outline" className="text-xs text-destructive border-destructive">Plazo vencido</Badge>
                        : <Badge variant="destructive" className="text-xs">Recuperación</Badge>
                      }
                    </div>
                    <CardTitle className="text-lg mt-3">{recovery.course_name}</CardTitle>
                    <CardDescription className="text-sm">
                      {recovery.program_name}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Módulo:</span>
                      <Badge variant="outline" className="text-xs">
                        Módulo {recovery.module_number}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Promedio anterior:</span>
                      <Badge variant="destructive" className="text-xs font-mono">
                        {recovery.average_grade.toFixed(2)}
                      </Badge>
                    </div>
                    {recovery.recovery_close_date && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Cierre recuperación:</span>
                        <span className={`text-xs font-medium ${recovery.recovery_closed ? 'text-destructive' : 'text-foreground'}`}>
                          {recovery.recovery_close_date}
                        </span>
                      </div>
                    )}
                    <div className="pt-2 border-t">
                      {recovery.recovery_closed ? (
                        <p className="text-xs text-destructive font-medium">
                          El plazo de recuperación ha vencido
                        </p>
                      ) : (
                        <p className="text-xs text-muted-foreground">
                          Haz clic para ver las actividades de recuperación
                        </p>
                      )}
                    </div>
                    <Button 
                      className="w-full" 
                      disabled={recovery.recovery_closed}
                      onClick={(e) => {
                        e.stopPropagation();
                        if (!recovery.recovery_closed) navigate(`/student/course/${recovery.course_id}`);
                      }}
                    >
                      {recovery.recovery_closed ? 'Plazo vencido' : 'Ver Actividades'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Instructions Card */}
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="text-lg">¿Cómo funciona la recuperación?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                <ol className="list-decimal list-inside space-y-2">
                  <li>Ingresa al curso haciendo clic en la tarjeta de la materia</li>
                  <li>Busca las actividades marcadas como "Recuperación"</li>
                  <li>Completa las actividades de recuperación según las instrucciones</li>
                  <li>Tu profesor calificará tu trabajo de recuperación</li>
                  <li>Si apruebas, tu calificación será actualizada y podrás continuar</li>
                </ol>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
