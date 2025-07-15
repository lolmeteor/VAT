"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { useTelegramWebApp } from "@/hooks/useTelegramWebApp"
import { TelegramLoginButton } from "@/components/telegram-login-button"
import { Loader2 } from "lucide-react"

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

interface HybridTelegramAuthProps {
  onAuth: (user: TelegramUser) => void
  disabled?: boolean
}

export function HybridTelegramAuth({ onAuth, disabled = false }: HybridTelegramAuthProps) {
  const { isWebApp, webApp, isReady, user, initData } = useTelegramWebApp()
  const [isAuthenticating, setIsAuthenticating] = useState(false)

  const handleWebAppAuth = async () => {
    if (!webApp || !user || !initData) return

    setIsAuthenticating(true)
    try {
      // Отправляем initData на сервер для валидации
      const response = await fetch("/api/auth/telegram-webapp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ initData }),
      })

      if (response.ok) {
        const userData = await response.json()
        // Преобразуем данные в формат, ожидаемый onAuth
        const telegramUser: TelegramUser = {
          id: user.id,
          first_name: user.first_name,
          last_name: user.last_name,
          username: user.username,
          photo_url: user.photo_url,
          auth_date: Math.floor(Date.now() / 1000),
          hash: "webapp_validated", // Специальный маркер для Web App
        }
        onAuth(telegramUser)
      } else {
        throw new Error("Ошибка авторизации через Web App")
      }
    } catch (error) {
      console.error("Ошибка Web App авторизации:", error)
      alert("Ошибка авторизации. Попробуйте снова.")
    } finally {
      setIsAuthenticating(false)
    }
  }

  if (!isReady) {
    return (
      <div className="flex items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2">Инициализация...</span>
      </div>
    )
  }

  if (isWebApp && user) {
    return (
      <div className="flex flex-col items-center space-y-4">
        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            Привет, {user.first_name}! Нажмите кнопку для входа в систему.
          </p>
        </div>
        <Button
          onClick={handleWebAppAuth}
          disabled={disabled || isAuthenticating}
          className="w-full bg-[#0088cc] hover:bg-[#0077bb] text-white"
        >
          {isAuthenticating ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Авторизация...
            </>
          ) : (
            "Войти через Telegram"
          )}
        </Button>
      </div>
    )
  }

  // Обычный Login Widget для веб-браузера
  return <TelegramLoginButton onAuth={onAuth} buttonSize="large" />
}
