"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { apiClient } from "@/lib/api"

interface UserResponse {
  user_id: string
  telegram_id: number
  username?: string
  first_name?: string
  last_name?: string
  balance_minutes: number
  agreed_to_personal_data: boolean
  agreed_to_terms: boolean
  onboarding_completed: boolean
  created_at: string
}

interface AuthContextType {
  user: UserResponse | null
  isLoading: boolean
  login: (telegramAuthData: any) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const checkAuth = async () => {
    setIsLoading(true)
    try {
      const currentUser = await apiClient.get<UserResponse>("/auth/me")
      setUser(currentUser)
    } catch (error) {
      setUser(null)
      // Ошибка означает, что пользователь не авторизован или сессия истекла
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  const login = async (telegramAuthData: any) => {
    setIsLoading(true)
    try {
      const loggedInUser = await apiClient.post<UserResponse>("/auth/telegram", telegramAuthData)
      setUser(loggedInUser)
    } catch (error) {
      setUser(null)
      console.error("Ошибка входа:", error)
      throw error // Передаем ошибку дальше для обработки в UI
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    setIsLoading(true)
    try {
      await apiClient.post("/auth/logout")
      setUser(null)
    } catch (error) {
      console.error("Ошибка выхода:", error)
      // Можно оставить пользователя в системе, если выход не удался, или обработать иначе
    } finally {
      setIsLoading(false)
    }
  }

  return <AuthContext.Provider value={{ user, isLoading, login, logout, checkAuth }}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth должен использоваться внутри AuthProvider")
  }
  return context
}
