import React, { createContext, useContext, useState, useEffect } from 'react'
import { useToast } from '@/hooks/use-toast'

const AuthContext = createContext({})

const API_BASE_URL = 'https://3dhkilcqyg19.manus.space/api'

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  // Check for existing token on app load
  useEffect(() => {
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData)
        setUser(parsedUser)
      } catch (error) {
        console.error('Error parsing user data:', error)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
    
    setLoading(false)
  }, [])

  const login = async (credentials) => {
    try {
      setLoading(true)
      
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Login failed')
      }

      // Store token and user data
      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      setUser(data.user)
      
      toast({
        title: 'Login Successful',
        description: `Welcome back, ${data.user.username}!`,
      })

      return { success: true, user: data.user }
    } catch (error) {
      console.error('Login error:', error)
      
      toast({
        title: 'Login Failed',
        description: error.message || 'Please check your credentials and try again.',
        variant: 'destructive',
      })

      return { success: false, error: error.message }
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    
    toast({
      title: 'Logged Out',
      description: 'You have been successfully logged out.',
    })
  }

  const register = async (userData) => {
    try {
      setLoading(true)
      
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Registration failed')
      }

      toast({
        title: 'Registration Successful',
        description: 'Your account has been created successfully.',
      })

      return { success: true, data }
    } catch (error) {
      console.error('Registration error:', error)
      
      toast({
        title: 'Registration Failed',
        description: error.message || 'Please try again.',
        variant: 'destructive',
      })

      return { success: false, error: error.message }
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (profileData) => {
    try {
      const token = localStorage.getItem('token')
      
      const response = await fetch(`${API_BASE_URL}/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profileData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Profile update failed')
      }

      // Update local user data
      const updatedUser = { ...user, ...data.user }
      localStorage.setItem('user', JSON.stringify(updatedUser))
      setUser(updatedUser)

      toast({
        title: 'Profile Updated',
        description: 'Your profile has been updated successfully.',
      })

      return { success: true, user: updatedUser }
    } catch (error) {
      console.error('Profile update error:', error)
      
      toast({
        title: 'Update Failed',
        description: error.message || 'Please try again.',
        variant: 'destructive',
      })

      return { success: false, error: error.message }
    }
  }

  const changePassword = async (passwordData) => {
    try {
      const token = localStorage.getItem('token')
      
      const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(passwordData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Password change failed')
      }

      toast({
        title: 'Password Changed',
        description: 'Your password has been changed successfully.',
      })

      return { success: true }
    } catch (error) {
      console.error('Password change error:', error)
      
      toast({
        title: 'Password Change Failed',
        description: error.message || 'Please try again.',
        variant: 'destructive',
      })

      return { success: false, error: error.message }
    }
  }

  // API helper function with authentication
  const apiCall = async (endpoint, options = {}) => {
    const token = localStorage.getItem('token')
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
    }

    const mergedOptions = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers,
      },
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, mergedOptions)
      
      // Handle unauthorized responses
      if (response.status === 401) {
        logout()
        throw new Error('Session expired. Please login again.')
      }

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`)
      }

      return data
    } catch (error) {
      console.error('API call error:', error)
      throw error
    }
  }

  const value = {
    user,
    loading,
    login,
    logout,
    register,
    updateProfile,
    changePassword,
    apiCall,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

