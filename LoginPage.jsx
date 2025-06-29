import React, { useState, useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useTheme } from '../../contexts/ThemeContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Eye, EyeOff, Moon, Sun, GraduationCap, Users, BookOpen, Calculator } from 'lucide-react'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const LoginPage = () => {
  const { user, login, loading } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  // Redirect if already logged in
  if (user && !loading) {
    return <Navigate to="/dashboard" replace />
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error when user starts typing
    if (error) setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    if (!formData.username || !formData.password) {
      setError('Please fill in all fields')
      return
    }

    setIsLoading(true)
    
    const result = await login(formData)
    
    if (!result.success) {
      setError(result.error)
    }
    
    setIsLoading(false)
  }

  const demoCredentials = [
    { role: 'Admin', username: 'admin', password: 'admin123', icon: Users, color: 'text-blue-600' },
    { role: 'Teacher', username: 'teacher', password: 'teacher123', icon: GraduationCap, color: 'text-green-600' },
    { role: 'Student', username: 'student', password: 'student123', icon: BookOpen, color: 'text-purple-600' },
    { role: 'Staff', username: 'staff', password: 'staff123', icon: Calculator, color: 'text-orange-600' },
  ]

  const fillDemoCredentials = (username, password) => {
    setFormData({ username, password })
    setError('')
  }

  if (loading) {
    return <LoadingSpinner text="Initializing..." />
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4">
      {/* Theme Toggle */}
      <Button
        variant="ghost"
        size="icon"
        onClick={toggleTheme}
        className="absolute top-4 right-4 z-10"
      >
        {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
      </Button>

      <div className="w-full max-w-4xl grid md:grid-cols-2 gap-8 items-center">
        {/* Left Side - Branding */}
        <div className="text-center md:text-left space-y-6">
          <div className="flex items-center justify-center md:justify-start space-x-3">
            <div className="p-3 bg-primary rounded-xl">
              <GraduationCap className="h-8 w-8 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">EduManage Pro</h1>
              <p className="text-muted-foreground">School Management System</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-foreground">
              Streamline Your Educational Institution
            </h2>
            <p className="text-muted-foreground text-lg leading-relaxed">
              Comprehensive solution for managing students, teachers, academics, finances, 
              and administrative tasks all in one powerful platform.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-card rounded-lg border">
              <Users className="h-6 w-6 mx-auto mb-2 text-blue-600" />
              <p className="text-sm font-medium">User Management</p>
            </div>
            <div className="text-center p-4 bg-card rounded-lg border">
              <BookOpen className="h-6 w-6 mx-auto mb-2 text-green-600" />
              <p className="text-sm font-medium">Academic Tracking</p>
            </div>
            <div className="text-center p-4 bg-card rounded-lg border">
              <Calculator className="h-6 w-6 mx-auto mb-2 text-purple-600" />
              <p className="text-sm font-medium">Financial Management</p>
            </div>
            <div className="text-center p-4 bg-card rounded-lg border">
              <GraduationCap className="h-6 w-6 mx-auto mb-2 text-orange-600" />
              <p className="text-sm font-medium">Reports & Analytics</p>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full max-w-md mx-auto">
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="demo">Demo Access</TabsTrigger>
            </TabsList>
            
            <TabsContent value="login">
              <Card>
                <CardHeader className="space-y-1">
                  <CardTitle className="text-2xl text-center">Welcome Back</CardTitle>
                  <CardDescription className="text-center">
                    Enter your credentials to access your account
                  </CardDescription>
                </CardHeader>
                
                <form onSubmit={handleSubmit}>
                  <CardContent className="space-y-4">
                    {error && (
                      <Alert variant="destructive">
                        <AlertDescription>{error}</AlertDescription>
                      </Alert>
                    )}
                    
                    <div className="space-y-2">
                      <Label htmlFor="username">Username or Email</Label>
                      <Input
                        id="username"
                        name="username"
                        type="text"
                        placeholder="Enter your username or email"
                        value={formData.username}
                        onChange={handleInputChange}
                        disabled={isLoading}
                        className="h-11"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="password">Password</Label>
                      <div className="relative">
                        <Input
                          id="password"
                          name="password"
                          type={showPassword ? 'text' : 'password'}
                          placeholder="Enter your password"
                          value={formData.password}
                          onChange={handleInputChange}
                          disabled={isLoading}
                          className="h-11 pr-10"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="absolute right-0 top-0 h-11 w-11"
                          onClick={() => setShowPassword(!showPassword)}
                          disabled={isLoading}
                        >
                          {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                  
                  <CardFooter className="flex flex-col space-y-4">
                    <Button 
                      type="submit" 
                      className="w-full h-11" 
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <LoadingSpinner size="sm" text="" />
                          <span className="ml-2">Signing In...</span>
                        </>
                      ) : (
                        'Sign In'
                      )}
                    </Button>
                    
                    <div className="text-center text-sm text-muted-foreground">
                      <p>Don't have an account? Contact your administrator</p>
                    </div>
                  </CardFooter>
                </form>
              </Card>
            </TabsContent>
            
            <TabsContent value="demo">
              <Card>
                <CardHeader>
                  <CardTitle className="text-center">Demo Access</CardTitle>
                  <CardDescription className="text-center">
                    Try the system with different user roles
                  </CardDescription>
                </CardHeader>
                
                <CardContent className="space-y-3">
                  {demoCredentials.map((demo) => {
                    const Icon = demo.icon
                    return (
                      <Button
                        key={demo.role}
                        variant="outline"
                        className="w-full justify-start h-12"
                        onClick={() => fillDemoCredentials(demo.username, demo.password)}
                      >
                        <Icon className={`h-5 w-5 mr-3 ${demo.color}`} />
                        <div className="text-left">
                          <p className="font-medium">Login as {demo.role}</p>
                          <p className="text-xs text-muted-foreground">
                            {demo.username} / {demo.password}
                          </p>
                        </div>
                      </Button>
                    )
                  })}
                </CardContent>
                
                <CardFooter>
                  <p className="text-xs text-muted-foreground text-center w-full">
                    Click any role above to auto-fill credentials, then switch to Login tab
                  </p>
                </CardFooter>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}

export default LoginPage

