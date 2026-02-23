import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Loader2, Download, RefreshCw, Search } from 'lucide-react';
import api from '@/lib/api';

const ACTION_OPTIONS = [
  { value: 'all', label: 'Todas las acciones' },
  { value: 'login_success', label: 'Inicio de sesión' },
  { value: 'student_created', label: 'Estudiante creado' },
  { value: 'user_created', label: 'Usuario creado' },
  { value: 'user_updated', label: 'Usuario actualizado' },
  { value: 'user_deleted', label: 'Usuario eliminado' },
  { value: 'course_created', label: 'Grupo creado' },
  { value: 'course_deleted', label: 'Grupo eliminado' },
  { value: 'program_created', label: 'Programa creado' },
  { value: 'program_deleted', label: 'Programa eliminado' },
  { value: 'activity_created', label: 'Actividad creada' },
  { value: 'activity_deleted', label: 'Actividad eliminada' },
  { value: 'grade_assigned', label: 'Nota asignada' },
  { value: 'recovery_approved', label: 'Recuperación aprobada (admin)' },
  { value: 'recovery_graded', label: 'Recuperación calificada (profesor)' },
  { value: 'module_closed', label: 'Módulo cerrado' },
  { value: 'student_promoted', label: 'Estudiante promovido' },
  { value: 'student_graduated', label: 'Estudiante graduado' },
  { value: 'student_removed_from_group', label: 'Estudiante removido del grupo' },
];

const ACTION_BADGE_VARIANT = {
  login_success: 'success',
  student_created: 'success',
  user_created: 'success',
  user_updated: 'secondary',
  user_deleted: 'destructive',
  course_created: 'success',
  course_deleted: 'destructive',
  program_created: 'success',
  program_deleted: 'destructive',
  activity_created: 'success',
  activity_deleted: 'destructive',
  grade_assigned: 'secondary',
  recovery_approved: 'success',
  recovery_graded: 'secondary',
  module_closed: 'warning',
  student_promoted: 'success',
  student_graduated: 'blue',
  student_removed_from_group: 'destructive',
};

function formatTimestamp(ts) {
  if (!ts) return '-';
  try {
    return new Date(ts).toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' });
  } catch {
    return ts;
  }
}

function formatDetails(details) {
  if (!details || typeof details !== 'object') return '-';
  return Object.entries(details)
    .filter(([, v]) => v !== undefined && v !== null && v !== '')
    .map(([k, v]) => `${k}: ${v}`)
    .join(', ');
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  const [actionFilter, setActionFilter] = useState('all');
  const [userIdFilter, setUserIdFilter] = useState('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (actionFilter && actionFilter !== 'all') params.set('action', actionFilter);
      if (userIdFilter.trim()) params.set('user_id', userIdFilter.trim());
      if (fromDate) params.set('from_date', fromDate);
      if (toDate) params.set('to_date', toDate);
      params.set('page', String(page));
      params.set('page_size', String(pageSize));
      const res = await api.get(`/admin/audit-logs?${params.toString()}`);
      setLogs(res.data.logs || []);
      setTotal(res.data.total || 0);
      setTotalPages(res.data.total_pages || 1);
    } catch (err) {
      toast.error('Error cargando registros de auditoría');
    } finally {
      setLoading(false);
    }
  }, [actionFilter, userIdFilter, fromDate, toDate, page]);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
  };

  const exportCsv = () => {
    if (logs.length === 0) {
      toast.info('No hay registros para exportar');
      return;
    }
    const headers = ['Fecha', 'Acción', 'Usuario ID', 'Nombre', 'Rol', 'Detalles'];
    const rows = logs.map(log => [
      formatTimestamp(log.timestamp),
      log.action,
      log.user_id,
      log.user_name || '',
      log.user_role,
      formatDetails(log.details)
    ]);
    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
      .join('\n');
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `auditoria_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h1 className="text-2xl font-bold">Registro de Auditoría</h1>
            <p className="text-muted-foreground text-sm">Historial de acciones del sistema</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={fetchLogs} disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Actualizar
            </Button>
            <Button variant="outline" size="sm" onClick={exportCsv} disabled={logs.length === 0}>
              <Download className="h-4 w-4 mr-2" />
              Exportar CSV
            </Button>
          </div>
        </div>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Filtros</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearch} className="flex flex-wrap gap-3 items-end">
              <div className="flex flex-col gap-1 min-w-[180px]">
                <Label className="text-xs">Acción</Label>
                <Select value={actionFilter} onValueChange={v => { setActionFilter(v); setPage(1); }}>
                  <SelectTrigger className="h-8 text-xs">
                    <SelectValue placeholder="Todas" />
                  </SelectTrigger>
                  <SelectContent>
                    {ACTION_OPTIONS.map(opt => (
                      <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex flex-col gap-1 min-w-[160px]">
                <Label className="text-xs">ID de usuario</Label>
                <Input
                  className="h-8 text-xs"
                  placeholder="ID exacto..."
                  value={userIdFilter}
                  onChange={e => setUserIdFilter(e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-1">
                <Label className="text-xs">Desde</Label>
                <Input
                  type="date"
                  className="h-8 text-xs"
                  value={fromDate}
                  onChange={e => { setFromDate(e.target.value); setPage(1); }}
                />
              </div>
              <div className="flex flex-col gap-1">
                <Label className="text-xs">Hasta</Label>
                <Input
                  type="date"
                  className="h-8 text-xs"
                  value={toDate}
                  onChange={e => { setToDate(e.target.value); setPage(1); }}
                />
              </div>
              <Button type="submit" size="sm" className="h-8">
                <Search className="h-4 w-4 mr-1" />
                Buscar
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-0">
            {loading ? (
              <div className="flex justify-center items-center py-16">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : logs.length === 0 ? (
              <div className="text-center text-muted-foreground py-16 text-sm">
                No se encontraron registros con los filtros aplicados.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="text-xs w-36">Fecha</TableHead>
                      <TableHead className="text-xs w-44">Acción</TableHead>
                      <TableHead className="text-xs">Usuario</TableHead>
                      <TableHead className="text-xs w-20">Rol</TableHead>
                      <TableHead className="text-xs">Detalles</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {logs.map(log => (
                      <TableRow key={log.id}>
                        <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                          {formatTimestamp(log.timestamp)}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={ACTION_BADGE_VARIANT[log.action] || 'secondary'}
                            className="text-xs font-semibold px-2 py-0.5 whitespace-nowrap"
                          >
                            {log.action}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs">
                          <span className="font-medium">{log.user_name || log.user_id || '-'}</span>
                          {log.user_name && log.user_name !== log.user_id && (
                            <span className="text-muted-foreground ml-1">({log.user_id})</span>
                          )}
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground capitalize">{log.user_role}</TableCell>
                        <TableCell className="text-xs text-muted-foreground max-w-xs truncate" title={formatDetails(log.details)}>
                          {formatDetails(log.details)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>

        {totalPages > 1 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              {total} registro{total !== 1 ? 's' : ''} — Página {page} de {totalPages}
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
              >
                Anterior
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              >
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
