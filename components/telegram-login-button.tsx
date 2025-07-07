"use client"

import { useEffect } from "react"
import { settings } from "@/app/config"

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

interface TelegramLoginButtonProps {
  onAuth: (user: TelegramUser) => void
  buttonSize?: "large" | "medium" | "small"
  cornerRadius?: number
  requestAccess?: boolean
}

declare global {
  interface Window {
    TelegramLoginWidget: {
      dataOnauth: (user: TelegramUser) => void
    }
  }
}

export function TelegramLoginButton({
  onAuth,
  buttonSize = "large",
  cornerRadius = 10,
  requestAccess = true,
}: TelegramLoginButtonProps) {
  useEffect(() => {
    // Устанавливаем глобальный обработчик для Telegram Widget
    window.TelegramLoginWidget = {
      dataOnauth: (user: TelegramUser) => {
        onAuth(user)
      },
    }

    // Создаем скрипт для загрузки Telegram Widget
    const script = document.createElement("script")
    script.src = "https://telegram.org/js/telegram-widget.js?22"
    script.setAttribute("data-telegram-login", settings.telegramBotName)
    script.setAttribute("data-size", buttonSize)
    script.setAttribute("data-corner-radius", cornerRadius.toString())
    script.setAttribute("data-request-access", requestAccess ? "write" : "")
    script.setAttribute("data-onauth", "TelegramLoginWidget.dataOnauth(user)")
    script.async = true

    const container = document.getElementById("telegram-login-container")
    if (container) {
      container.appendChild(script)
    }

    return () => {
      // Очищаем контейнер при размонтировании
      if (container) {
        container.innerHTML = ""
      }
    }
  }, [buttonSize, cornerRadius, requestAccess, onAuth])

  return (
    <div className="flex flex-col items-center space-y-4">
      <div id="telegram-login-container" />
      <p className="text-sm text-muted-foreground text-center">Войдите через Telegram для доступа к сервису</p>
    </div>
  )
}
