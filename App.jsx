import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { Toaster } from '@/components/ui/toaster'
import LoginPage from './pages/auth/LoginPage'
import AdminDashboard from './pages/admin/AdminDashboard'
import TeacherDashboard from './pages/teacher/TeacherDashboard'
import StudentDashboard from './pages/student/StudentDashboard'
import ParentDashboard from './pages/parent/ParentDashboard'
import StaffDashboard from './pages/staff/StaffDashboard'
import LoadingSpinner from './components/common/LoadingSpinner'
import './App.css'

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <LoadingSpinner />
  }
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role_type)) {
    return <Navigate to="/unauthorized" replace />
  }
  
  return children
}

// Dashboard Router Component
const DashboardRouter = () => {
  const { user } = useAuth()
  
  if (!user) return null
  
  switch (user.role_type) {
    case 'admin':
      return <AdminDashboard />
    case 'teacher':
      return <TeacherDashboard />
    case 'student':
      return <StudentDashboard />
    case 'parent':
      return <ParentDashboard />
    case 'staff':
      return <StaffDashboard />
    default:
      return <Navigate to="/login" replace />
  }
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-background">
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<LoginPage />} />
              
              {/* Protected Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardRouter />
                  </ProtectedRoute>
                }
              />
              
              {/* Role-specific Routes */}
              <Route
                path="/admin/*"
                element={
                  <ProtectedRoute allowedRoles={['admin']}>
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/teacher/*"
                element={
                  <ProtectedRoute allowedRoles={['teacher']}>
                    <TeacherDashboard />
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/student/*"
                element={
                  <ProtectedRoute allowedRoles={['student']}>
                    <StudentDashboard />
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/parent/*"
                element={
                  <ProtectedRoute allowedRoles={['parent']}>
                    <ParentDashboard />
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/staff/*"
                element={
                  <ProtectedRoute allowedRoles={['staff']}>
                    <StaffDashboard />
                  </ProtectedRoute>
                }
              />
              
              {/* Default redirect */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              
              {/* Unauthorized page */}
              <Route
                path="/unauthorized"
                element={
                  <div className="min-h-screen flex items-center justify-center">
                    <div className="text-center">
                      <h1 className="text-2xl font-bold text-destructive mb-4">
                        Access Denied
                      </h1>
                      <p className="text-muted-foreground">
                        You don't have permission to access this page.
                      </p>
                    </div>
                  </div>
                }
              />
              
              {/* 404 page */}
              <Route
                path="*"
                element={
                  <div className="min-h-screen flex items-center justify-center">
                    <div className="text-center">
                      <h1 className="text-2xl font-bold mb-4">Page Not Found</h1>
                      <p className="text-muted-foreground">
                        The page you're looking for doesn't exist.
                      </p>
                    </div>
                  </div>
                }
              />
            </Routes>
            <Toaster />
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App

