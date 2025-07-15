"use client"

import { useEffect, useState } from "react"

interface TelegramWebApp {
  initData: string
  initDataUnsafe: {
    user?: {
      id: number
      first_name: string
      last_name?: string
      username?: string
      photo_url?: string
      language_code?: string
    }
    auth_date: number
    hash: string
  }
  ready: () => void
  close: () => void
  expand: () => void
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp
    }
  }
}

export function useTelegramWebApp() {
  const [isWebApp, setIsWebApp] = useState(false)
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null)
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    // Проверяем, запущено ли приложение в Telegram Web App
    if (typeof window !== "undefined" && window.Telegram?.WebApp) {
      setIsWebApp(true)
      setWebApp(window.Telegram.WebApp)

      // Инициализируем Web App
      window.Telegram.WebApp.ready()
      window.Telegram.WebApp.expand()

      setIsReady(true)
    } else {
      setIsReady(true)
    }
  }, [])

  return {
    isWebApp,
    webApp,
    isReady,
    user: webApp?.initDataUnsafe?.user,
    initData: webApp?.initData,
  }
}
