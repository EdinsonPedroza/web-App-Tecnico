import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { Toaster } from '@/components/ui/sonner';
import '@/App.css';

// Pages
import LoginPage from '@/pages/LoginPage';
import AdminDashboard from '@/pages/admin/AdminDashboard';
import ProgramsPage from '@/pages/admin/ProgramsPage';
import SubjectsPage from '@/pages/admin/SubjectsPage';
import TeachersPage from '@/pages/admin/TeachersPage';
import StudentsPage from '@/pages/admin/StudentsPage';
import CoursesPage from '@/pages/admin/CoursesPage';
import TeacherCourseSelector from '@/pages/teacher/TeacherCourseSelector';
import TeacherCourseDashboard from '@/pages/teacher/TeacherCourseDashboard';
import TeacherActivities from '@/pages/teacher/TeacherActivities';
import TeacherGrades from '@/pages/teacher/TeacherGrades';
import TeacherVideos from '@/pages/teacher/TeacherVideos';
import TeacherStudents from '@/pages/teacher/TeacherStudents';
import StudentDashboard from '@/pages/student/StudentDashboard';
import StudentCourses from '@/pages/student/StudentCourses';
import StudentActivities from '@/pages/student/StudentActivities';
import StudentGrades from '@/pages/student/StudentGrades';
import StudentVideos from '@/pages/student/StudentVideos';

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
    if (user.role === 'admin') return <Navigate to="/admin" replace />;
    if (user.role === 'profesor') return <Navigate to="/teacher" replace />;
    return <Navigate to="/student" replace />;
  }
  return children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/" element={<PublicRoute><LoginPage /></PublicRoute>} />

          {/* Admin Routes */}
          <Route path="/admin" element={<ProtectedRoute allowedRoles={['admin']}><AdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/programs" element={<ProtectedRoute allowedRoles={['admin']}><ProgramsPage /></ProtectedRoute>} />
          <Route path="/admin/subjects" element={<ProtectedRoute allowedRoles={['admin']}><SubjectsPage /></ProtectedRoute>} />
          <Route path="/admin/teachers" element={<ProtectedRoute allowedRoles={['admin']}><TeachersPage /></ProtectedRoute>} />
          <Route path="/admin/students" element={<ProtectedRoute allowedRoles={['admin']}><StudentsPage /></ProtectedRoute>} />
          <Route path="/admin/courses" element={<ProtectedRoute allowedRoles={['admin']}><CoursesPage /></ProtectedRoute>} />

          {/* Teacher Routes */}
          <Route path="/teacher" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherCourseSelector /></ProtectedRoute>} />
          <Route path="/teacher/course/:courseId" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherCourseDashboard /></ProtectedRoute>} />
          <Route path="/teacher/course/:courseId/activities" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherActivities /></ProtectedRoute>} />
          <Route path="/teacher/course/:courseId/grades" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherGrades /></ProtectedRoute>} />
          <Route path="/teacher/course/:courseId/videos" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherVideos /></ProtectedRoute>} />
          <Route path="/teacher/course/:courseId/students" element={<ProtectedRoute allowedRoles={['profesor']}><TeacherStudents /></ProtectedRoute>} />

          {/* Student Routes */}
          <Route path="/student" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentDashboard /></ProtectedRoute>} />
          <Route path="/student/courses" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentCourses /></ProtectedRoute>} />
          <Route path="/student/activities" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentActivities /></ProtectedRoute>} />
          <Route path="/student/grades" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentGrades /></ProtectedRoute>} />
          <Route path="/student/videos" element={<ProtectedRoute allowedRoles={['estudiante']}><StudentVideos /></ProtectedRoute>} />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </AuthProvider>
  );
}

export default App;
