import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Users, BookOpen, GraduationCap, ClipboardList, Building2, FileText, Loader2 } from 'lucide-react';
import api from '@/lib/api';

export default function AdminDashboardHome() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/stats');
        setStats(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const statCards = [
    { label: 'Estudiantes', value: stats?.students || 0, icon: GraduationCap, color: 'text-primary' },
    { label: 'Profesores', value: stats?.teachers || 0, icon: Users, color: 'text-success' },
    { label: 'Programas', value: stats?.programs || 0, icon: Building2, color: 'text-warning' },
    { label: 'Cursos Activos', value: stats?.courses || 0, icon: ClipboardList, color: 'text-info' },
    { label: 'Actividades', value: stats?.activities || 0, icon: FileText, color: 'text-chart-4' },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold font-heading text-foreground">Panel de Administración</h1>
          <p className="text-muted-foreground mt-1">Resumen general de la plataforma</p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              {statCards.map((item) => {
                const Icon = item.icon;
                return (
                  <Card key={item.label} className="shadow-card hover:shadow-card-hover transition-shadow">
                    <CardContent className="p-5">
                      <div className="flex items-center justify-between mb-3">
                        <Icon className={`h-5 w-5 ${item.color}`} />
                        <Badge variant="secondary" className="text-xs">{item.label}</Badge>
                      </div>
                      <p className="text-3xl font-bold font-heading text-foreground">{item.value}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="shadow-card">
                <CardHeader>
                  <CardTitle className="text-lg font-heading">Accesos Rápidos</CardTitle>
                  <CardDescription>Gestiona la plataforma desde aquí</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { label: 'Gestionar Programas', desc: 'Crear o editar técnicos', path: '/admin/programs', icon: Building2 },
                    { label: 'Gestionar Materias', desc: 'Administrar plan de estudios', path: '/admin/subjects', icon: BookOpen },
                    { label: 'Gestionar Profesores', desc: 'Agregar o editar docentes', path: '/admin/teachers', icon: Users },
                    { label: 'Gestionar Estudiantes', desc: 'Inscribir o editar alumnos', path: '/admin/students', icon: GraduationCap },
                    { label: 'Gestionar Cursos', desc: 'Crear cursos y asignar grupos', path: '/admin/courses', icon: ClipboardList },
                  ].map((item) => {
                    const Icon = item.icon;
                    return (
                      <a
                        key={item.path}
                        href={item.path}
                        className="flex items-center gap-4 rounded-lg p-3 hover:bg-accent transition-colors group"
                      >
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                          <Icon className="h-5 w-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-foreground group-hover:text-primary transition-colors">{item.label}</p>
                          <p className="text-xs text-muted-foreground">{item.desc}</p>
                        </div>
                      </a>
                    );
                  })}
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader>
                  <CardTitle className="text-lg font-heading">Programas Técnicos</CardTitle>
                  <CardDescription>Programas ofrecidos actualmente</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {[
                    { name: 'Técnico en Asistencia Administrativa', duration: '12 meses', modules: 2 },
                    { name: 'Técnico en Atención a la Primera Infancia', duration: '12 meses', modules: 2 },
                    { name: 'Técnico en Seguridad y Salud en el Trabajo', duration: '12 meses', modules: 2 },
                  ].map((prog, i) => (
                    <div key={i} className="rounded-lg border p-4">
                      <p className="text-sm font-medium text-foreground">{prog.name}</p>
                      <div className="flex gap-3 mt-2">
                        <Badge variant="secondary">{prog.duration}</Badge>
                        <Badge variant="secondary">{prog.modules} módulos</Badge>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
