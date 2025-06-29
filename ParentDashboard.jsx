import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useTheme } from '../../contexts/ThemeContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'
import { 
  Users, 
  Calendar, 
  DollarSign, 
  Bell, 
  LogOut, 
  Moon, 
  Sun,
  GraduationCap,
  MessageSquare,
  TrendingUp,
  Award,
  AlertTriangle
} from 'lucide-react'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const ParentDashboard = () => {
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
      // Simulate API call for parent dashboard data
      const data = {
        children: [
          { id: 1, name: 'Emma Johnson', class: 'Grade 10-A', gpa: 3.8, attendance: 95 },
          { id: 2, name: 'Liam Johnson', class: 'Grade 8-B', gpa: 3.6, attendance: 92 },
        ],
        stats: {
          totalChildren: 2,
          averageGPA: 3.7,
          averageAttendance: 93.5,
          outstandingFees: 1200,
          unreadMessages: 3
        },
        recentActivities: [
          { id: 1, child: 'Emma Johnson', message: 'Received grade A in Mathematics test', time: '2 hours ago', type: 'grade' },
          { id: 2, child: 'Liam Johnson', message: 'Absent from school today', time: '1 day ago', type: 'attendance' },
          { id: 3, child: 'Emma Johnson', message: 'Parent-teacher meeting scheduled', time: '2 days ago', type: 'meeting' },
        ],
        upcomingEvents: [
          { id: 1, title: 'Parent-Teacher Conference', date: '2024-01-15', child: 'Emma Johnson' },
          { id: 2, title: 'Science Fair Presentation', date: '2024-01-20', child: 'Liam Johnson' },
          { id: 3, title: 'Fee Payment Due', date: '2024-01-25', child: 'Both Children' },
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

  const getActivityIcon = (type) => {
    switch (type) {
      case 'grade': return <Award className="h-4 w-4 text-green-600" />
      case 'attendance': return <AlertTriangle className="h-4 w-4 text-orange-600" />
      case 'meeting': return <MessageSquare className="h-4 w-4 text-blue-600" />
      default: return <Bell className="h-4 w-4 text-gray-600" />
    }
  }

  if (loading) {
    return <LoadingSpinner text="Loading parent dashboard..." />
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-2 bg-primary rounded-lg">
            <Users className="h-6 w-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Parent Portal</h1>
            <p className="text-sm text-muted-foreground">
              Welcome back, {user?.username}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
            {dashboardData?.stats.unreadMessages > 0 && (
              <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs">
                {dashboardData.stats.unreadMessages}
              </Badge>
            )}
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
        {/* Children Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {dashboardData?.children.map((child) => (
            <Card key={child.id}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <GraduationCap className="h-5 w-5" />
                  <span>{child.name}</span>
                </CardTitle>
                <CardDescription>{child.class}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">GPA</span>
                  <span className="font-semibold">{child.gpa}/4.0</span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Attendance</span>
                    <span className="font-semibold">{child.attendance}%</span>
                  </div>
                  <Progress value={child.attendance} />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Children
              </CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.totalChildren}</div>
              <p className="text-xs text-muted-foreground">Enrolled students</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Average GPA
              </CardTitle>
              <Award className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.averageGPA}</div>
              <p className="text-xs text-muted-foreground">Across all children</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Avg Attendance
              </CardTitle>
              <Calendar className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.averageAttendance}%</div>
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
              <p className="text-xs text-muted-foreground">Total due</p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activities and Upcoming Events */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activities</CardTitle>
              <CardDescription>Latest updates about your children</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboardData?.recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  {getActivityIcon(activity.type)}
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.child}</p>
                    <p className="text-sm text-muted-foreground">{activity.message}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Upcoming Events</CardTitle>
              <CardDescription>Important dates and deadlines</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboardData?.upcomingEvents.map((event) => (
                <div key={event.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">{event.title}</p>
                    <p className="text-sm text-muted-foreground">{event.child}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{event.date}</p>
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
            <CardDescription>Manage your children's education</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <Award className="h-6 w-6" />
                <span className="text-sm">View Grades</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <Calendar className="h-6 w-6" />
                <span className="text-sm">Attendance</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <DollarSign className="h-6 w-6" />
                <span className="text-sm">Pay Fees</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <MessageSquare className="h-6 w-6" />
                <span className="text-sm">Contact Teacher</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

export default ParentDashboard

