import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Loader2, GraduationCap } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function TeacherStudents() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [students, setStudents] = useState([]);
  const [grades, setGrades] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [cRes, uRes, gRes] = await Promise.all([
        api.get(`/courses/${courseId}`),
        api.get('/users?role=estudiante'),
        api.get(`/grades?course_id=${courseId}`)
      ]);
      setCourse(cRes.data);
      setGrades(gRes.data);
      setStudents(uRes.data.filter(u => (cRes.data.student_ids || []).includes(u.id)));
    } catch (err) {
      toast.error('Error cargando datos');
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const initials = (name) => name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();

  const getAvg = (studentId) => {
    const sg = grades.filter(g => g.student_id === studentId);
    if (sg.length === 0) return '-';
    return (sg.reduce((s, g) => s + g.value, 0) / sg.length).toFixed(1);
  };

  return (
    <DashboardLayout courseId={courseId}>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold font-heading">Estudiantes del Curso</h1>
          <p className="text-muted-foreground mt-1">{course?.name}</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>
        ) : students.length === 0 ? (
          <Card className="shadow-card"><CardContent className="p-10 text-center">
            <GraduationCap className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">No hay estudiantes inscritos</p>
          </CardContent></Card>
        ) : (
          <Card className="shadow-card overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Estudiante</TableHead>
                    <TableHead>Cédula</TableHead>
                    <TableHead>Teléfono</TableHead>
                    <TableHead>Promedio</TableHead>
                    <TableHead>Estado</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {students.map((s) => (
                    <TableRow key={s.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-8 w-8"><AvatarFallback className="bg-primary/10 text-primary text-xs">{initials(s.name)}</AvatarFallback></Avatar>
                          <span className="font-medium text-sm">{s.name}</span>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono text-sm text-muted-foreground">{s.cedula}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">{s.phone || '-'}</TableCell>
                      <TableCell>
                        <Badge variant={getAvg(s.id) !== '-' && parseFloat(getAvg(s.id)) >= 3 ? 'success' : getAvg(s.id) !== '-' ? 'destructive' : 'secondary'}>
                          {getAvg(s.id)}
                        </Badge>
                      </TableCell>
                      <TableCell><Badge variant="success">Activo</Badge></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
