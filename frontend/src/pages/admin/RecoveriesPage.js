import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { toast } from 'sonner';
import { Loader2, CheckCircle, XCircle, RefreshCw, Search, Filter, Trash2, GraduationCap, AlertCircle, Download } from 'lucide-react';
import api from '@/lib/api';

export default function RecoveriesPage() {
  const [recoveryData, setRecoveryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [graduatedCount, setGraduatedCount] = useState(0);
  const [deletingGraduated, setDeletingGraduated] = useState(false);

  const fetchRecoveryPanel = useCallback(async () => {
    try {
      const [recoveryRes, graduatedRes] = await Promise.all([
        api.get('/admin/recovery-panel'),
        api.get('/admin/graduated-students-count')
      ]);
      setRecoveryData(recoveryRes.data);
      setGraduatedCount(graduatedRes.data.count);
    } catch (err) {
      toast.error('Error cargando panel de recuperaciones');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecoveryPanel();
  }, [fetchRecoveryPanel]);

  const handleApproveRecovery = async (failedSubjectId, approve) => {
    setProcessingId(failedSubjectId);
    try {
      await api.post('/admin/approve-recovery', null, {
        params: {
          failed_subject_id: failedSubjectId,
          approve: approve
        }
      });
      toast.success(approve ? 'Recuperación aprobada' : 'Recuperación rechazada');
      fetchRecoveryPanel();
    } catch (err) {
      toast.error('Error procesando recuperación');
      console.error(err);
    } finally {
      setProcessingId(null);
    }
  };

  const handleDeleteGraduated = async () => {
    if (!window.confirm(
      `¿Estás seguro de eliminar TODOS los ${graduatedCount} estudiantes egresados y sus datos?\n\nEsta acción es IRREVERSIBLE y eliminará:\n- Registros de estudiantes\n- Notas\n- Entregas\n- Datos de recuperaciones\n\n¿Continuar?`
    )) {
      return;
    }

    setDeletingGraduated(true);
    try {
      const res = await api.delete('/admin/delete-graduated-students');
      toast.success(res.data.message);
      fetchRecoveryPanel();
    } catch (err) {
      toast.error('Error eliminando estudiantes egresados');
      console.error(err);
    } finally {
      setDeletingGraduated(false);
    }
  };

  const handleDownloadRecoveryReport = async () => {
    try {
      const response = await api.get('/reports/recovery-results?format=xlsx', {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'reporte_recuperaciones.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      toast.error('Error descargando reporte de recuperaciones');
    }
  };

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
            <h1 className="text-3xl font-bold font-heading">Recuperaciones</h1>
            <p className="text-muted-foreground mt-1 text-lg">
              Gestiona las materias reprobadas y aprueba recuperaciones. El cierre de módulo es automático según la fecha configurada.
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={fetchRecoveryPanel} variant="outline">
              <RefreshCw className="h-4 w-4" /> Actualizar
            </Button>
            <Button onClick={handleDownloadRecoveryReport} variant="outline">
              <Download className="h-4 w-4" /> Descargar Reporte
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card className="shadow-card">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-2">
                <AlertCircle className="h-5 w-5 text-warning" />
                <Badge variant="secondary">Total</Badge>
              </div>
              <p className="text-3xl font-bold font-heading">{recoveryData?.total_students || 0}</p>
              <p className="text-sm text-muted-foreground mt-1">Estudiantes con materias reprobadas</p>
            </CardContent>
          </Card>
          <Card className="shadow-card">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-2">
                <XCircle className="h-5 w-5 text-destructive" />
                <Badge variant="secondary">Materias</Badge>
              </div>
              <p className="text-3xl font-bold font-heading">{recoveryData?.total_failed_subjects || 0}</p>
              <p className="text-sm text-muted-foreground mt-1">Total de materias reprobadas</p>
            </CardContent>
          </Card>
          <Card className="shadow-card">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-2">
                <CheckCircle className="h-5 w-5 text-success" />
                <Badge variant="secondary">Aprobadas</Badge>
              </div>
              <p className="text-3xl font-bold font-heading">
                {recoveryData?.students?.reduce((sum, s) => 
                  sum + s.failed_subjects.filter(f => f.recovery_approved).length, 0) || 0}
              </p>
              <p className="text-sm text-muted-foreground mt-1">Recuperaciones aprobadas</p>
            </CardContent>
          </Card>
        </div>

        {/* Graduated Students Management */}
        {graduatedCount > 0 && (
          <Alert className="border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950">
            <GraduationCap className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            <AlertDescription className="flex items-center justify-between">
              <div className="flex-1">
                <p className="font-semibold text-amber-900 dark:text-amber-100">
                  Estudiantes Egresados: {graduatedCount}
                </p>
                <p className="text-sm text-amber-800 dark:text-amber-200 mt-1">
                  Los estudiantes egresados están archivados. Puedes eliminarlos permanentemente para liberar espacio.
                </p>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDeleteGraduated}
                disabled={deletingGraduated}
                className="ml-4 whitespace-nowrap"
              >
                {deletingGraduated ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Eliminando...
                  </>
                ) : (
                  <>
                    <Trash2 className="h-4 w-4 mr-2" />
                    Eliminar Egresados
                  </>
                )}
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Search and Filters */}
        <Card className="shadow-card">
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por nombre, cédula o materia..."
                  className="pl-9"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-[200px]">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos en proceso</SelectItem>
                  <SelectItem value="pending">Solo pendientes</SelectItem>
                  <SelectItem value="approved">Aprobadas por admin</SelectItem>
                  <SelectItem value="graded">Calificadas por profesor</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Students with Failed Subjects */}
        {!recoveryData?.students || recoveryData.students.length === 0 ? (
          <Card className="shadow-card">
            <CardContent className="p-10 text-center">
              <CheckCircle className="h-12 w-12 text-success mx-auto mb-3" />
              <p className="text-lg font-medium">No hay estudiantes pendientes de recuperación</p>
              <p className="text-sm text-muted-foreground mt-1">
                Todos los estudiantes han aprobado sus materias o ya fueron procesados
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {(() => {
              const today = new Date().toISOString().slice(0, 10);
              return recoveryData.students
              .filter(student => {
                // Remove students whose ALL subjects belong to modules where
                // the next module has already started (they should no longer appear).
                const hasActiveSubjects = student.failed_subjects.some(s => {
                  if (s.next_module_start && s.next_module_start <= today) return false;
                  return true;
                });
                if (!hasActiveSubjects) return false;

                // Search filter
                const matchesSearch = searchTerm === '' || 
                  student.student_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  (student.student_cedula && student.student_cedula.includes(searchTerm)) ||
                  student.failed_subjects.some(s =>
                    s.course_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    (s.subject_name && s.subject_name.toLowerCase().includes(searchTerm.toLowerCase()))
                  );
                
                // Status filter
                const matchesStatus = statusFilter === 'all' ||
                  (statusFilter === 'pending' && student.failed_subjects.some(s => !s.recovery_approved)) ||
                  (statusFilter === 'approved' && student.failed_subjects.some(s => s.recovery_approved && !s.recovery_completed)) ||
                  (statusFilter === 'graded' && student.failed_subjects.some(s => s.teacher_graded_status !== null && s.teacher_graded_status !== undefined));
                
                return matchesSearch && matchesStatus;
              })
              .map((student) => {
                // Visible subjects: exclude those whose next module has already started
                const visibleSubjects = student.failed_subjects.filter(s =>
                  !s.next_module_start || s.next_module_start > today
                );
                return (
              <Card key={student.student_id} className="shadow-card">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl">{student.student_name}</CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">
                        {student.student_cedula ? `Cédula: ${student.student_cedula}` : `ID: ${student.student_id.slice(0, 8)}…`} • {visibleSubjects.length} materia(s) reprobada(s)
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="destructive" className="text-sm">
                        En Recuperación
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Materia(s)</TableHead>
                        <TableHead>Grupo</TableHead>
                        <TableHead>Programa</TableHead>
                        <TableHead>Módulo</TableHead>
                        <TableHead>Promedio</TableHead>
                        <TableHead>Estado</TableHead>
                        <TableHead className="text-right">Acciones</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {visibleSubjects.map((subject) => {
                        const recoveryClosed = subject.recovery_close && subject.recovery_close <= today;
                        // When recovery period is closed: show final result (Aprobado/Reprobado)
                        const isFinalApproved = recoveryClosed && (
                          subject.status === 'processed_passed' ||
                          subject.status === 'teacher_approved'
                        );
                        const isFinalRejected = recoveryClosed && !isFinalApproved;
                        return (
                        <TableRow key={subject.id}>
                          <TableCell className="font-medium">
                            {subject.subject_name || subject.course_name}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground max-w-[160px] truncate" title={subject.course_name}>
                            {subject.course_name}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {subject.program_name}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline" className="text-xs">
                              Módulo {subject.module_number}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant="destructive" className="text-xs">
                              {subject.average_grade.toFixed(2)}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {isFinalApproved ? (
                              <Badge variant="outline" className="text-xs bg-green-100 text-green-800 border-green-300 dark:bg-green-900/30 dark:text-green-400 dark:border-green-700">
                                ✅ Aprobado
                              </Badge>
                            ) : isFinalRejected ? (
                              <Badge variant="outline" className="text-xs bg-red-100 text-red-800 border-red-300 dark:bg-red-900/30 dark:text-red-400 dark:border-red-700">
                                ❌ Reprobado
                              </Badge>
                            ) : subject.teacher_graded_status === 'approved' ? (
                              <Badge variant="outline" className="text-xs bg-green-100 text-green-800 border-green-300 dark:bg-green-900/30 dark:text-green-400 dark:border-green-700">
                                ✅ Aprobado por profesor
                              </Badge>
                            ) : subject.teacher_graded_status === 'rejected' ? (
                              <Badge variant="outline" className="text-xs bg-red-100 text-red-800 border-red-300 dark:bg-red-900/30 dark:text-red-400 dark:border-red-700">
                                ❌ Rechazado por profesor
                              </Badge>
                            ) : subject.recovery_approved === true && (subject.teacher_graded_status === null || subject.teacher_graded_status === undefined) ? (
                              <Badge variant="warning" className="text-xs bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-700">
                                ⏳ En espera de calificación del profesor
                              </Badge>
                            ) : subject.recovery_completed ? (
                              <Badge variant="secondary" className="text-xs">
                                Completada
                              </Badge>
                            ) : (
                              <Badge variant="secondary" className="text-xs">
                                <AlertCircle className="h-3 w-3 mr-1" />
                                Pendiente
                              </Badge>
                            )}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-1">
                              {!subject.recovery_approved && !recoveryClosed && (
                                <>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => handleApproveRecovery(subject.id, true)}
                                    disabled={processingId === subject.id}
                                    className="text-success hover:text-success hover:bg-success/10"
                                  >
                                    {processingId === subject.id ? (
                                      <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                      <>
                                        <CheckCircle className="h-4 w-4" />
                                        Aprobar
                                      </>
                                    )}
                                  </Button>
                                </>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
                );
              })}
            )()}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
