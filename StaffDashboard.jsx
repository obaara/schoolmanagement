import React, { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useTheme } from '../../contexts/ThemeContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  Users, 
  Calendar, 
  ClipboardList, 
  Bell, 
  LogOut, 
  Moon, 
  Sun,
  UserCheck,
  FileText,
  Clock,
  CheckCircle,
  Package,
  Library,
  Bus
} from 'lucide-react'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const StaffDashboard = () => {
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
      // Simulate API call for staff dashboard data
      const data = {
        stats: {
          pendingTasks: 8,
          completedToday: 12,
          totalStudents: 1250,
          activeStaff: 32
        },
        todayTasks: [
          { id: 1, task: 'Process new student admissions', priority: 'high', department: 'Admissions' },
          { id: 2, task: 'Update library book inventory', priority: 'medium', department: 'Library' },
          { id: 3, task: 'Prepare monthly financial report', priority: 'high', department: 'Finance' },
          { id: 4, task: 'Schedule parent-teacher meetings', priority: 'low', department: 'Administration' },
        ],
        recentActivities: [
          { id: 1, message: 'New student enrollment completed - John Smith', time: '1 hour ago' },
          { id: 2, message: 'Library books returned by Grade 10 students', time: '3 hours ago' },
          { id: 3, message: 'Monthly fee collection report generated', time: '5 hours ago' },
        ],
        departmentStats: [
          { department: 'Admissions', pending: 5, completed: 15 },
          { department: 'Library', pending: 2, completed: 8 },
          { department: 'Finance', pending: 3, completed: 12 },
          { department: 'Transport', pending: 1, completed: 6 },
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

  const getDepartmentIcon = (department) => {
    switch (department.toLowerCase()) {
      case 'library': return <Library className="h-4 w-4" />
      case 'transport': return <Bus className="h-4 w-4" />
      case 'finance': return <FileText className="h-4 w-4" />
      default: return <ClipboardList className="h-4 w-4" />
    }
  }

  if (loading) {
    return <LoadingSpinner text="Loading staff dashboard..." />
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-2 bg-primary rounded-lg">
            <UserCheck className="h-6 w-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Staff Dashboard</h1>
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
                Pending Tasks
              </CardTitle>
              <ClipboardList className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.pendingTasks}</div>
              <p className="text-xs text-muted-foreground">Need attention</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Completed Today
              </CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.completedToday}</div>
              <p className="text-xs text-muted-foreground">Tasks finished</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Students
              </CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.totalStudents.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">Currently enrolled</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Staff
              </CardTitle>
              <UserCheck className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData?.stats.activeStaff}</div>
              <p className="text-xs text-muted-foreground">Staff members</p>
            </CardContent>
          </Card>
        </div>

        {/* Today's Tasks and Recent Activities */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Today's Tasks</CardTitle>
              <CardDescription>Your assigned tasks for today</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {dashboardData?.todayTasks.map((task) => (
                <div key={task.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      {getDepartmentIcon(task.department)}
                    </div>
                    <div>
                      <p className="font-medium">{task.task}</p>
                      <p className="text-sm text-muted-foreground">{task.department}</p>
                    </div>
                  </div>
                  <Badge variant={getPriorityColor(task.priority)}>
                    {task.priority}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Activities</CardTitle>
              <CardDescription>Latest system activities</CardDescription>
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

        {/* Department Statistics */}
        <Card>
          <CardHeader>
            <CardTitle>Department Overview</CardTitle>
            <CardDescription>Task completion status by department</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {dashboardData?.departmentStats.map((dept) => (
                <div key={dept.department} className="p-4 border rounded-lg">
                  <div className="flex items-center space-x-2 mb-3">
                    {getDepartmentIcon(dept.department)}
                    <h3 className="font-medium">{dept.department}</h3>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Pending:</span>
                      <span className="font-medium text-orange-600">{dept.pending}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Completed:</span>
                      <span className="font-medium text-green-600">{dept.completed}</span>
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
            <CardDescription>Frequently used administrative tools</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <Users className="h-6 w-6" />
                <span className="text-sm">Student Records</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <Library className="h-6 w-6" />
                <span className="text-sm">Library System</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <Package className="h-6 w-6" />
                <span className="text-sm">Inventory</span>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2">
                <FileText className="h-6 w-6" />
                <span className="text-sm">Generate Report</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

export default StaffDashboard

