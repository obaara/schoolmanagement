import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useTheme } from '../../contexts/ThemeContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'
import { 
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
  TrendingUp,
  Award,
  DollarSign
} from 'lucide-react'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const StudentDashboard = () => {
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
      // Simulate API call for student dashboard data
      const data = {
        stats: {
          currentGPA: 3.75,
          attendanceRate: 92,
          pendingAssignments: 3,
          upcomingExams: 2,
          outstandingFees: 500
        },
        todaySchedule: [
          { id: 1, subject: 'Mathematics', teacher: 'Mr. Johnson', time: '09:00 AM', room: 'Room 101' },
          { id: 2, subject: 'Physics', teacher: 'Dr. Smith', time: '10:00 AM', room: 'Lab 201' },
          { id: 3, subject: 'English', teacher: 'Ms. Davis', time: '02:00 PM', room: 'Room 105' },
          { id: 4, subject: 'Chemistry', teacher: 'Dr. Wilson', time: '03:00 PM', room: 'Lab 301' },
        ],
        recentGrades: [
          { id: 1, subject: 'Mathematics', assignment: 'Algebra Test', grade: 'A-', points: '87/100' },
          { id: 2, subject: 'Physics', assignment: 'Lab Report', grade: 'B+', points: '85/100' },
          { id: 3, subject: 'English', assignment: 'Essay Writing', grade: 'A', points: '92/100' },
        ],
        upcomingAssignments: [
          { id: 1, subject: 'Chemistry', title: 'Organic Compounds Lab', dueDate: '2024-01-15', priority: 'high' },
          { id: 2, subject: 'Mathematics', title: 'Calculus Problem Set', dueDate: '2024-01-17', priority: 'medium' },
          { id: 3, subject: 'English', title: 'Literature Review', dueDate: '2024-01-20', priority: 'low' },
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

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'default'
    }
  }

  if (loading) {
    return <LoadingSpinner text="Loading student dashboard..." />
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
            <h1 className="text-xl font-semibold">Student Portal</h1>
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Current GPA
              </CardTitle>
              <Award className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.currentGPA}</div>
              <p className="text-xs text-muted-foreground">Out of 4.0</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Attendance
              </CardTitle>
              <Calendar className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.attendanceRate}%</div>
              <Progress value={dashboardData?.stats.attendanceRate} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Pending Tasks
              </CardTitle>
              <ClipboardList className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.pendingAssignments}</div>
              <p className="text-xs text-muted-foreground">Assignments due</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Upcoming Exams
              </CardTitle>
              <FileText className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.upcomingExams}</div>
              <p className="text-xs text-muted-foreground">This month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Outstanding Fees
              </CardTitle>
              <DollarSign className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${dashboardData?.stats.outstandingFees}</div>
              <p className="text-xs text-muted-foreground">Due this term</p>
            </CardContent>
          </Card>
        </div>

        {/* Today's Schedule and Recent Grades */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Today's Classes</CardTitle>
              <CardDescription>Your schedule for today</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboardData?.todaySchedule.map((schedule) => (
                <div key={schedule.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <BookOpen className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{schedule.subject}</p>
                      <p className="text-sm text-muted-foreground">{schedule.teacher}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{schedule.time}</p>
                    <p className="text-xs text-muted-foreground">{schedule.room}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Grades</CardTitle>
              <CardDescription>Your latest assignment results</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboardData?.recentGrades.map((grade) => (
                <div key={grade.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">{grade.assignment}</p>
                    <p className="text-sm text-muted-foreground">{grade.subject}</p>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline" className="mb-1">
                      {grade.grade}
                    </Badge>
                    <p className="text-xs text-muted-foreground">{grade.points}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Upcoming Assignments */}
        <Card>
          <CardHeader>
            <CardTitle>Upcoming Assignments</CardTitle>
            <CardDescription>Tasks that need your attention</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboardData?.upcomingAssignments.map((assignment) => (
                <div key={assignment.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <ClipboardList className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{assignment.title}</p>
                      <p className="text-sm text-muted-foreground">{assignment.subject}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Badge variant={getPriorityColor(assignment.priority)}>
                      {assignment.priority} priority
                    </Badge>
                    <div className="text-right">
                      <p className="text-sm font-medium">Due: {assignment.dueDate}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Access your student tools</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <BookOpen className="h-6 w-6" />
                <span className="text-sm">View Grades</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <Calendar className="h-6 w-6" />
                <span className="text-sm">Class Schedule</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <ClipboardList className="h-6 w-6" />
                <span className="text-sm">Assignments</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <DollarSign className="h-6 w-6" />
                <span className="text-sm">Pay Fees</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

export default StudentDashboard

