import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useTheme } from '../../contexts/ThemeContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  Users, 
  BookOpen, 
  Calendar, 
  ClipboardList, 
  Bell, 
  LogOut, 
  Moon, 
  Sun,
  GraduationCap,
  FileText,
  Clock,
  CheckCircle
} from 'lucide-react'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const TeacherDashboard = () => {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      // Simulate API call for teacher dashboard data
      const data = {
        stats: {
          totalClasses: 6,
          totalStudents: 180,
          pendingAssignments: 12,
          upcomingClasses: 4
        },
        todaySchedule: [
          { id: 1, subject: 'Mathematics', class: 'Grade 10-A', time: '09:00 AM', duration: '45 min' },
          { id: 2, subject: 'Mathematics', class: 'Grade 10-B', time: '10:00 AM', duration: '45 min' },
          { id: 3, subject: 'Algebra', class: 'Grade 11-A', time: '02:00 PM', duration: '45 min' },
          { id: 4, subject: 'Calculus', class: 'Grade 12-A', time: '03:00 PM', duration: '45 min' },
        ],
        recentActivities: [
          { id: 1, message: 'Assignment submitted by John Doe - Algebra Homework', time: '2 hours ago' },
          { id: 2, message: 'Grade 10-A attendance marked for today', time: '4 hours ago' },
          { id: 3, message: 'New assignment created: Quadratic Equations', time: '1 day ago' },
        ]
      }
      setDashboardData(data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
  }

  if (loading) {
    return <LoadingSpinner text="Loading teacher dashboard..." />
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-2 bg-primary rounded-lg">
            <GraduationCap className="h-6 w-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Teacher Dashboard</h1>
            <p className="text-sm text-muted-foreground">
              Welcome back, {user?.username}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" onClick={toggleTheme}>
            {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
          <div className="flex items-center space-x-2">
            <Avatar className="h-8 w-8">
              <AvatarImage src={user?.avatar} />
              <AvatarFallback>
                {user?.username?.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6 space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                My Classes
              </CardTitle>
              <BookOpen className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.totalClasses}</div>
              <p className="text-xs text-muted-foreground">Active classes assigned</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Students
              </CardTitle>
              <Users className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.totalStudents}</div>
              <p className="text-xs text-muted-foreground">Across all classes</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Pending Assignments
              </CardTitle>
              <ClipboardList className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.pendingAssignments}</div>
              <p className="text-xs text-muted-foreground">Need to be graded</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Today's Classes
              </CardTitle>
              <Calendar className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.upcomingClasses}</div>
              <p className="text-xs text-muted-foreground">Scheduled for today</p>
            </CardContent>
          </Card>
        </div>

        {/* Today's Schedule and Recent Activities */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Today's Schedule</CardTitle>
              <CardDescription>Your classes for today</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboardData?.todaySchedule.map((schedule) => (
                <div key={schedule.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <Clock className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{schedule.subject}</p>
                      <p className="text-sm text-muted-foreground">{schedule.class}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{schedule.time}</p>
                    <p className="text-xs text-muted-foreground">{schedule.duration}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Activities</CardTitle>
              <CardDescription>Latest updates and notifications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboardData?.recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                  <div className="flex-1">
                    <p className="text-sm">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Frequently used teaching tools</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <ClipboardList className="h-6 w-6" />
                <span className="text-sm">Take Attendance</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <FileText className="h-6 w-6" />
                <span className="text-sm">Create Assignment</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <CheckCircle className="h-6 w-6" />
                <span className="text-sm">Grade Papers</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <Users className="h-6 w-6" />
                <span className="text-sm">View Students</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

export default TeacherDashboard

