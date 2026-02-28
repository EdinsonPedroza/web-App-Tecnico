import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { Toaster } from '@/components/ui/sonner';
import ErrorBoundary from '@/components/ErrorBoundary';
import EnvironmentCheck from '@/components/EnvironmentCheck';
import '@/App.css';

// Pages
import LoginPage from '@/pages/LoginPage';
import NotFoundPage from '@/pages/NotFoundPage';
import EditorPage from '@/pages/editor/EditorPage';
import AdminDashboard from '@/pages/admin/AdminDashboard';
import ProgramsPage from '@/pages/admin/ProgramsPage';
import SubjectsPage from '@/pages/admin/SubjectsPage';
import TeachersPage from '@/pages/admin/TeachersPage';
import StudentsPage from '@/pages/admin/StudentsPage';
import CoursesPage from '@/pages/admin/CoursesPage';
import RecoveriesPage from '@/pages/admin/RecoveriesPage';
import RecoverySimulatorPage from '@/pages/admin/RecoverySimulatorPage';
import TeacherCourseSelector from '@/pages/teacher/TeacherCourseSelector';
import TeacherCourseDashboard from '@/pages/teacher/TeacherCourseDashboard';
import TeacherActivities from '@/pages/teacher/TeacherActivities';
import TeacherGrades from '@/pages/teacher/TeacherGrades';
import TeacherVideos from '@/pages/teacher/TeacherVideos';
import TeacherStudents from '@/pages/teacher/TeacherStudents';
import StudentProgramSelector from '@/pages/student/StudentProgramSelector';
import StudentCourseSelector from '@/pages/student/StudentCourseSelector';
import StudentCourseDashboard from '@/pages/student/StudentCourseDashboard';
import StudentActivities from '@/pages/student/StudentActivities';
import StudentGrades from '@/pages/student/StudentGrades';
import StudentVideos from '@/pages/student/StudentVideos';
import StudentRecoveriesPage from '@/pages/student/StudentRecoveriesPage';

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
              <Route path="/admin/recovery-simulator" element={<ProtectedRoute allowedRoles={['admin']}><RecoverySimulatorPage /></ProtectedRoute>} />

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
          </BrowserRouter>
          <Toaster position="top-right" richColors />
        </AuthProvider>
      </EnvironmentCheck>
    </ErrorBoundary>
  );
}

export default App;
