import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { Toaster } from '@/components/ui/sonner';
import ErrorBoundary from '@/components/ErrorBoundary';
import EnvironmentCheck from '@/components/EnvironmentCheck';
import '@/App.css';

// Pages - lazy loaded to reduce initial bundle size
const LoginPage = lazy(() => import('@/pages/LoginPage'));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));
const EditorPage = lazy(() => import('@/pages/editor/EditorPage'));
const AdminDashboard = lazy(() => import('@/pages/admin/AdminDashboard'));
const ProgramsPage = lazy(() => import('@/pages/admin/ProgramsPage'));
const SubjectsPage = lazy(() => import('@/pages/admin/SubjectsPage'));
const TeachersPage = lazy(() => import('@/pages/admin/TeachersPage'));
const StudentsPage = lazy(() => import('@/pages/admin/StudentsPage'));
const CoursesPage = lazy(() => import('@/pages/admin/CoursesPage'));
const RecoveriesPage = lazy(() => import('@/pages/admin/RecoveriesPage'));
const TeacherCourseSelector = lazy(() => import('@/pages/teacher/TeacherCourseSelector'));
const TeacherCourseDashboard = lazy(() => import('@/pages/teacher/TeacherCourseDashboard'));
const TeacherActivities = lazy(() => import('@/pages/teacher/TeacherActivities'));
const TeacherGrades = lazy(() => import('@/pages/teacher/TeacherGrades'));
const TeacherVideos = lazy(() => import('@/pages/teacher/TeacherVideos'));
const TeacherStudents = lazy(() => import('@/pages/teacher/TeacherStudents'));
const StudentProgramSelector = lazy(() => import('@/pages/student/StudentProgramSelector'));
const StudentCourseSelector = lazy(() => import('@/pages/student/StudentCourseSelector'));
const StudentCourseDashboard = lazy(() => import('@/pages/student/StudentCourseDashboard'));
const StudentActivities = lazy(() => import('@/pages/student/StudentActivities'));
const StudentGrades = lazy(() => import('@/pages/student/StudentGrades'));
const StudentVideos = lazy(() => import('@/pages/student/StudentVideos'));
const StudentRecoveriesPage = lazy(() => import('@/pages/student/StudentRecoveriesPage'));

function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-3">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="text-sm text-muted-foreground">Cargando...</p>
      </div>
    </div>
  );
}

// Protected Route wrapper
function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!user) return <Navigate to="/" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    if (user.role === 'editor') return <Navigate to="/editor" replace />;
    if (user.role === 'admin') return <Navigate to="/admin" replace />;
    if (user.role === 'profesor') return <Navigate to="/teacher" replace />;
    return <Navigate to="/student" replace />;
  }

  return children;
}

// Login redirect if already authenticated
function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (user) {
    if (user.role === 'editor') return <Navigate to="/editor" replace />;
    if (user.role === 'admin') return <Navigate to="/admin" replace />;
    if (user.role === 'profesor') return <Navigate to="/teacher" replace />;
    return <Navigate to="/student" replace />;
  }
  return children;
}

function App() {
  return (
    <ErrorBoundary>
      <EnvironmentCheck>
        <AuthProvider>
          <BrowserRouter>
            <Suspense fallback={<PageLoader />}>
            <Routes>
              {/* Public */}
              <Route path="/" element={<PublicRoute><LoginPage /></PublicRoute>} />

              {/* Editor Route */}
              <Route path="/editor" element={<ProtectedRoute allowedRoles={['editor']}><EditorPage /></ProtectedRoute>} />

              {/* Admin Routes */}
              <Route path="/admin" element={<ProtectedRoute allowedRoles={['admin']}><AdminDashboard /></ProtectedRoute>} />
              <Route path="/admin/programs" element={<ProtectedRoute allowedRoles={['admin']}><ProgramsPage /></ProtectedRoute>} />
              <Route path="/admin/subjects" element={<ProtectedRoute allowedRoles={['admin']}><SubjectsPage /></ProtectedRoute>} />
              <Route path="/admin/teachers" element={<ProtectedRoute allowedRoles={['admin']}><TeachersPage /></ProtectedRoute>} />
              <Route path="/admin/students" element={<ProtectedRoute allowedRoles={['admin']}><StudentsPage /></ProtectedRoute>} />
              <Route path="/admin/courses" element={<ProtectedRoute allowedRoles={['admin']}><CoursesPage /></ProtectedRoute>} />
              <Route path="/admin/recoveries" element={<ProtectedRoute allowedRoles={['admin']}><RecoveriesPage /></ProtectedRoute>} />

              {/* Teacher Routes */}
              <Route path="/teacher" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherCourseSelector /></ProtectedRoute>} />
              <Route path="/teacher/course/:courseId" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherCourseDashboard /></ProtectedRoute>} />
              <Route path="/teacher/course/:courseId/activities" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherActivities /></ProtectedRoute>} />
              <Route path="/teacher/course/:courseId/grades" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherGrades /></ProtectedRoute>} />
              <Route path="/teacher/course/:courseId/videos" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherVideos /></ProtectedRoute>} />
              <Route path="/teacher/course/:courseId/students" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherStudents /></ProtectedRoute>} />

              {/* Student Routes */}
              <Route path="/student" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentProgramSelector /></ProtectedRoute>} />
              <Route path="/student/courses" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentCourseSelector /></ProtectedRoute>} />
              <Route path="/student/recoveries" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentRecoveriesPage /></ProtectedRoute>} />
              <Route path="/student/course/:courseId" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentCourseDashboard /></ProtectedRoute>} />
              <Route path="/student/course/:courseId/activities" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentActivities /></ProtectedRoute>} />
              <Route path="/student/course/:courseId/grades" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentGrades /></ProtectedRoute>} />
              <Route path="/student/course/:courseId/videos" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentVideos /></ProtectedRoute>} />
              {/* Legacy routes - redirect to course selector */}
              <Route path="/student/dashboard" element={<Navigate to="/student" replace />} />
              <Route path="/student/activities" element={<Navigate to="/student" replace />} />
              <Route path="/student/grades" element={<Navigate to="/student" replace />} />
              <Route path="/student/videos" element={<Navigate to="/student" replace />} />

              {/* Catch all - Show 404 page instead of redirecting */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
            </Suspense>
          </BrowserRouter>
          <Toaster position="top-right" richColors />
        </AuthProvider>
      </EnvironmentCheck>
    </ErrorBoundary>
  );
}

export default App;
