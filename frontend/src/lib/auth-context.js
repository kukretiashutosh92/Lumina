'use client'

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from 'react'
import { api } from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    const token =
      typeof window !== 'undefined'
        ? localStorage.getItem('token')
        : null

    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }

    try {
      const u = await api.auth.me()
      setUser(u)
    } catch (error) {
      localStorage.removeItem('token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const login = useCallback(
    async (email, password) => {
      const { access_token } = await api.auth.login(email, password)
      localStorage.setItem('token', access_token)
      await refresh()
    },
    [refresh]
  )

  const signup = useCallback(
    async (email, password, fullName) => {
      await api.auth.signup(email, password, fullName)
      await login(email, password)
    },
    [login]
  )

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider
      value={{ user, loading, login, signup, logout, refresh }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return ctx
}