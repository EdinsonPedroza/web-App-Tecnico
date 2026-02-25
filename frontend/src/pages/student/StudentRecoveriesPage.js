import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Loader2, AlertCircle, CheckCircle, BookOpen, RefreshCw, CalendarX, Clock } from 'lucide-react';
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
                Has aprobado todas tus materias o no tienes recuperaciones pendientes
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
                      Solo puedes entregar actividades en las materias que el administrador ha aprobado para recuperación
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recovery Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recoveries.map((recovery) => {
                const isApproved = recovery.recovery_approved;
                const isClosed = recovery.recovery_closed;
                const canNavigate = isApproved && !isClosed;

                return (
                  <Card
                    key={recovery.id}
                    className={`shadow-card transition-all ${isClosed ? 'opacity-75 grayscale border-destructive/30' : !isApproved ? 'opacity-80 border-muted' : 'hover:shadow-lg hover-lift cursor-pointer'}`}
                    onClick={() => canNavigate && navigate(`/student/course/${recovery.course_id}`)}
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between gap-2">
                        {isClosed
                          ? <CalendarX className="h-5 w-5 text-destructive shrink-0 mt-1" />
                          : isApproved
                            ? <BookOpen className="h-5 w-5 text-primary shrink-0 mt-1" />
                            : <Clock className="h-5 w-5 text-muted-foreground shrink-0 mt-1" />
                        }
                        {isClosed
                          ? <Badge variant="outline" className="text-xs text-destructive border-destructive">Plazo vencido</Badge>
                          : isApproved
                            ? <Badge variant="destructive" className="text-xs">Recuperación</Badge>
                            : <Badge variant="secondary" className="text-xs">Pendiente aprobación</Badge>
                        }
                      </div>
                      <CardTitle className="text-lg mt-3">{recovery.subject_name || recovery.course_name}</CardTitle>
                      <div className="mt-1">
                        <Badge variant="destructive" className="text-xs">
                          Materia: {recovery.subject_name || 'General'}
                        </Badge>
                      </div>
                      <CardDescription className="text-sm">
                        Grupo: {recovery.course_name}
                      </CardDescription>
                      <p className="text-xs text-muted-foreground mt-0.5">{recovery.program_name}</p>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {recovery.subject_name && (
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Materia:</span>
                          <span className="text-xs font-medium text-right max-w-[60%] truncate" title={recovery.subject_name}>
                            {recovery.subject_name}
                          </span>
                        </div>
                      )}
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
                          <span className={`text-xs font-medium ${isClosed ? 'text-destructive' : 'text-foreground'}`}>
                            {recovery.recovery_close_date}
                          </span>
                        </div>
                      )}
                      <div className="pt-2 border-t">
                        {isClosed ? (
                          <p className="text-xs text-destructive font-medium">
                            El plazo de recuperación ha vencido
                          </p>
                        ) : !isApproved ? (
                          <p className="text-xs text-muted-foreground">
                            El administrador aún no ha aprobado tu solicitud de recuperación
                          </p>
                        ) : (
                          <p className="text-xs text-muted-foreground">
                            Haz clic para ver las actividades de recuperación
                          </p>
                        )}
                      </div>
                      <Button
                        className="w-full"
                        disabled={!canNavigate}
                        variant={isApproved ? 'default' : 'outline'}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (canNavigate) navigate(`/student/course/${recovery.course_id}`);
                        }}
                      >
                        {isClosed ? 'Plazo vencido' : !isApproved ? 'Pendiente aprobación' : 'Ver Actividades'}
                      </Button>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Instructions Card */}
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="text-lg">¿Cómo funciona la recuperación?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                <ol className="list-decimal list-inside space-y-2">
                  <li>El administrador debe aprobar tu recuperación primero</li>
                  <li>Una vez aprobada, ingresa al curso haciendo clic en la tarjeta de la materia</li>
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
