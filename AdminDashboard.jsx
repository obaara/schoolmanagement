import React, { useState, useEffect } from 'react'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useTheme } from '../../contexts/ThemeContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  Users, 
  GraduationCap, 
  BookOpen, 
  Calendar, 
  DollarSign, 
  BarChart3, 
  Settings, 
  Bell, 
  LogOut, 
  Moon, 
  Sun,
  Menu,
  X,
  Home,
  UserCheck,
  Building,
  FileText,
  MessageSquare,
  TrendingUp,
  School,
  CreditCard,
  Bus,
  Library,
  Package
} from 'lucide-react'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const AdminDashboard = () => {
  const { user, logout, apiCall } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)

  const menuItems = [
    { 
      id: 'overview', 
      label: 'Overview', 
      icon: Home, 
      path: '/admin',
      description: 'Dashboard overview and statistics'
    },
    { 
      id: 'students', 
      label: 'Students', 
      icon: Users, 
      path: '/admin/students',
      description: 'Manage student information and enrollment'
    },
    { 
      id: 'teachers', 
      label: 'Teachers', 
      icon: GraduationCap, 
      path: '/admin/teachers',
      description: 'Manage teaching staff and assignments'
    },
    { 
      id: 'staff', 
      label: 'Staff', 
      icon: UserCheck, 
      path: '/admin/staff',
      description: 'Manage administrative staff'
    },
    { 
      id: 'academics', 
      label: 'Academics', 
      icon: BookOpen, 
      path: '/admin/academics',
      description: 'Classes, subjects, and curriculum'
    },
    { 
      id: 'attendance', 
      label: 'Attendance', 
      icon: Calendar, 
      path: '/admin/attendance',
      description: 'Track student and staff attendance'
    },
    { 
      id: 'finances', 
      label: 'Finances', 
      icon: DollarSign, 
      path: '/admin/finances',
      description: 'Fees, payments, and accounting'
    },
    { 
      id: 'library', 
      label: 'Library', 
      icon: Library, 
      path: '/admin/library',
      description: 'Books and library management'
    },
    { 
      id: 'transport', 
      label: 'Transport', 
      icon: Bus, 
      path: '/admin/transport',
      description: 'Vehicle and route management'
    },
    { 
      id: 'inventory', 
      label: 'Inventory', 
      icon: Package, 
      path: '/admin/inventory',
      description: 'School assets and supplies'
    },
    { 
      id: 'reports', 
      label: 'Reports', 
      icon: BarChart3, 
      path: '/admin/reports',
      description: 'Analytics and reporting'
    },
    { 
      id: 'communications', 
      label: 'Communications', 
      icon: MessageSquare, 
      path: '/admin/communications',
      description: 'Announcements and notifications'
    },
    { 
      id: 'settings', 
      label: 'Settings', 
      icon: Settings, 
      path: '/admin/settings',
      description: 'System configuration'
    },
  ]

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      // Simulate API calls for dashboard data
      const data = {
        stats: {
          totalStudents: 1250,
          totalTeachers: 85,
          totalStaff: 32,
          totalClasses: 45,
          pendingFees: 125000,
          collectedFees: 875000,
          attendanceRate: 94.5,
          activeAnnouncements: 8
        },
        recentActivities: [
          { id: 1, type: 'enrollment', message: 'New student John Doe enrolled in Grade 10-A', time: '2 hours ago' },
          { id: 2, type: 'payment', message: 'Fee payment of $500 received from Sarah Wilson', time: '4 hours ago' },
          { id: 3, type: 'attendance', message: 'Daily attendance marked for all classes', time: '6 hours ago' },
          { id: 4, type: 'announcement', message: 'Parent-Teacher meeting scheduled for next week', time: '1 day ago' },
        ],
        upcomingEvents: [
          { id: 1, title: 'Parent-Teacher Conference', date: '2024-01-15', type: 'meeting' },
          { id: 2, title: 'Mid-term Examinations', date: '2024-01-20', type: 'exam' },
          { id: 3, title: 'Science Fair', date: '2024-01-25', type: 'event' },
          { id: 4, title: 'Sports Day', date: '2024-02-01', type: 'event' },
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
    navigate('/login')
  }

  const StatCard = ({ title, value, icon: Icon, color, description, trend }) => (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className={`h-4 w-4 ${color}`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">
            {description}
          </p>
        )}
        {trend && (
          <div className="flex items-center mt-2">
            <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
            <span className="text-xs text-green-600">{trend}</span>
          </div>
        )}
      </CardContent>
    </Card>
  )

  if (loading) {
    return <LoadingSpinner text="Loading dashboard..." />
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 bg-card border-r transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-primary rounded-lg">
              <School className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <h2 className="font-semibold">EduManage Pro</h2>
              <p className="text-xs text-muted-foreground">Admin Panel</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Button
                key={item.id}
                variant={isActive ? "default" : "ghost"}
                className="w-full justify-start h-10"
                onClick={() => {
                  navigate(item.path)
                  setSidebarOpen(false)
                }}
              >
                <Icon className="h-4 w-4 mr-3" />
                {item.label}
              </Button>
            )
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-card border-b px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-xl font-semibold">Admin Dashboard</h1>
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

        {/* Dashboard Content */}
        <main className="flex-1 overflow-auto p-6">
          <Routes>
            <Route path="/" element={
              <div className="space-y-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <StatCard
                    title="Total Students"
                    value={dashboardData?.stats.totalStudents.toLocaleString()}
                    icon={Users}
                    color="text-blue-600"
                    description="Active enrollments"
                    trend="+12% from last month"
                  />
                  <StatCard
                    title="Teaching Staff"
                    value={dashboardData?.stats.totalTeachers}
                    icon={GraduationCap}
                    color="text-green-600"
                    description="Active teachers"
                    trend="+3% from last month"
                  />
                  <StatCard
                    title="Fee Collection"
                    value={`$${(dashboardData?.stats.collectedFees / 1000).toFixed(0)}K`}
                    icon={DollarSign}
                    color="text-purple-600"
                    description="This academic year"
                    trend="+8% from last year"
                  />
                  <StatCard
                    title="Attendance Rate"
                    value={`${dashboardData?.stats.attendanceRate}%`}
                    icon={Calendar}
                    color="text-orange-600"
                    description="This month average"
                    trend="+2.1% from last month"
                  />
                </div>

                {/* Recent Activities and Upcoming Events */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Recent Activities</CardTitle>
                      <CardDescription>Latest system activities and updates</CardDescription>
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

                  <Card>
                    <CardHeader>
                      <CardTitle>Upcoming Events</CardTitle>
                      <CardDescription>Important dates and deadlines</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {dashboardData?.upcomingEvents.map((event) => (
                        <div key={event.id} className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium">{event.title}</p>
                            <p className="text-xs text-muted-foreground">{event.date}</p>
                          </div>
                          <Badge variant="outline">
                            {event.type}
                          </Badge>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                </div>

                {/* Quick Actions */}
                <Card>
                  <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                    <CardDescription>Frequently used administrative tasks</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <Button variant="outline" className="h-20 flex-col space-y-2">
                        <Users className="h-6 w-6" />
                        <span className="text-sm">Add Student</span>
                      </Button>
                      <Button variant="outline" className="h-20 flex-col space-y-2">
                        <GraduationCap className="h-6 w-6" />
                        <span className="text-sm">Add Teacher</span>
                      </Button>
                      <Button variant="outline" className="h-20 flex-col space-y-2">
                        <CreditCard className="h-6 w-6" />
                        <span className="text-sm">Process Payment</span>
                      </Button>
                      <Button variant="outline" className="h-20 flex-col space-y-2">
                        <MessageSquare className="h-6 w-6" />
                        <span className="text-sm">Send Notice</span>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            } />
            
            {/* Placeholder routes for other sections */}
            <Route path="/students" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Student Management</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/teachers" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Teacher Management</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/staff" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Staff Management</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/academics" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Academic Management</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/attendance" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Attendance Management</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/finances" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Financial Management</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/library" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Library Management</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/transport" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Transport Management</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/inventory" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Inventory Management</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/reports" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Reports & Analytics</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/communications" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">Communications</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
            <Route path="/settings" element={<div className="text-center py-20"><h2 className="text-2xl font-bold">System Settings</h2><p className="text-muted-foreground">Coming soon...</p></div>} />
          </Routes>
        </main>
      </div>

      {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

export default AdminDashboard

