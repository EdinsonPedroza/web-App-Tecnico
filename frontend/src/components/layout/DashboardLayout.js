import React, { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import {
  LayoutDashboard, Users, BookOpen, GraduationCap,
  FileText, Video, ClipboardList, Settings, LogOut,
  Menu, X, ChevronRight, Building2
} from 'lucide-react';
import { cn } from '@/lib/utils';

const adminLinks = [
  { label: 'Dashboard', icon: LayoutDashboard, path: '/admin' },
  { label: 'Programas', icon: Building2, path: '/admin/programs' },
  { label: 'Materias', icon: BookOpen, path: '/admin/subjects' },
  { label: 'Profesores', icon: Users, path: '/admin/teachers' },
  { label: 'Estudiantes', icon: GraduationCap, path: '/admin/students' },
  { label: 'Cursos', icon: ClipboardList, path: '/admin/courses' },
];

const teacherLinks = [
  { label: 'Mis Cursos', icon: LayoutDashboard, path: '/teacher' },
];

const teacherCourseLinks = [
  { label: 'Resumen', icon: LayoutDashboard, path: '' },
  { label: 'Actividades', icon: FileText, path: '/activities' },
  { label: 'Notas', icon: ClipboardList, path: '/grades' },
  { label: 'Videos de Clase', icon: Video, path: '/videos' },
  { label: 'Estudiantes', icon: GraduationCap, path: '/students' },
];

const studentLinks = [
  { label: 'Dashboard', icon: LayoutDashboard, path: '/student' },
  { label: 'Mis Cursos', icon: BookOpen, path: '/student/courses' },
  { label: 'Actividades', icon: FileText, path: '/student/activities' },
  { label: 'Mis Notas', icon: ClipboardList, path: '/student/grades' },
  { label: 'Videos de Clase', icon: Video, path: '/student/videos' },
];

export default function DashboardLayout({ children, courseId }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  let links = [];
  if (user?.role === 'admin') links = adminLinks;
  else if (user?.role === 'profesor') {
    if (courseId) {
      links = teacherCourseLinks.map(l => ({
        ...l,
        path: `/teacher/course/${courseId}${l.path}`
      }));
    } else {
      links = teacherLinks;
    }
  } else {
    links = studentLinks;
  }

  const initials = user?.name?.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase() || 'U';

  const roleLabels = {
    admin: 'Administrador',
    profesor: 'Profesor',
    estudiante: 'Estudiante'
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-sidebar-bg transition-transform duration-300 lg:relative lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-5">
          <img src="/logo.png" alt="Logo" className="h-10 w-10 rounded-full bg-card object-cover" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-sidebar-foreground font-heading">
              Educando
            </p>
            <p className="truncate text-xs text-sidebar-muted">
              {roleLabels[user?.role] || 'Usuario'}
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden text-sidebar-foreground hover:bg-sidebar-accent"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <Separator className="bg-sidebar-accent" />

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
          {user?.role === 'profesor' && courseId && (
            <Button
              variant="ghost"
              className="w-full justify-start gap-2 mb-3 text-sidebar-muted hover:text-sidebar-foreground hover:bg-sidebar-accent text-xs"
              onClick={() => navigate('/teacher')}
            >
              <ChevronRight className="h-3 w-3 rotate-180" />
              Volver a mis cursos
            </Button>
          )}
          {links.map((link) => {
            const isActive = location.pathname === link.path;
            const Icon = link.icon;
            return (
              <Button
                key={link.path}
                variant="ghost"
                className={cn(
                  "w-full justify-start gap-3 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-foreground"
                    : "text-sidebar-muted hover:text-sidebar-foreground hover:bg-sidebar-accent"
                )}
                onClick={() => {
                  navigate(link.path);
                  setSidebarOpen(false);
                }}
              >
                <Icon className="h-4 w-4" />
                {link.label}
              </Button>
            );
          })}
        </nav>

        {/* User info at bottom */}
        <div className="border-t border-sidebar-accent p-4">
          <div className="flex items-center gap-3">
            <Avatar className="h-8 w-8 border border-sidebar-accent">
              <AvatarFallback className="bg-sidebar-accent text-sidebar-foreground text-xs">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-sidebar-foreground">{user?.name}</p>
              <p className="truncate text-xs text-sidebar-muted">{user?.email || user?.cedula}</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Top bar */}
        <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-card/80 backdrop-blur-md px-4 lg:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>

          <div className="flex-1" />

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="gap-2">
                <Avatar className="h-7 w-7">
                  <AvatarFallback className="bg-primary/10 text-primary text-xs">
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <span className="hidden sm:inline text-sm">{user?.name}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>Mi Cuenta</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Cerrar Sesión
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
