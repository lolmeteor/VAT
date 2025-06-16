"use client"

import { useEffect, useRef } from "react"
import { settings } from "@/app/config" // Frontend-конфиг

interface TelegramLoginButtonProps {
  onAuth: (data: any) => void // Тип данных от Telegram нужно будет уточнить
  buttonSize?: "large" | "medium" | "small"
  cornerRadius?: number
  requestAccess?: "write" // или другие значения, если нужны
  showUserPhoto?: boolean
}

declare global {
  interface Window {
    Telegram: {
      Login: {
        auth: (options: { bot_id: string; request_access?: string }, callback: (dataOrFalse: any) => void) => void
      }
    }
    onTelegramAuth: (data: any) => void
  }
}

export function TelegramLoginButton({
  onAuth,
  buttonSize = "large",
  cornerRadius,
  requestAccess,
  showUserPhoto = true,
}: TelegramLoginButtonProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!ref.current) return

    // Делаем функцию onAuth доступной глобально, чтобы скрипт Telegram мог ее вызвать
    window.onTelegramAuth = (data: any) => {
      if (data) {
        onAuth(data)
      } else {
        // Обработка случая, когда пользователь не авторизовался
        console.warn("Telegram authentication failed or was cancelled.")
      }
    }

    const script = document.createElement("script")
    script.src = "https://telegram.org/js/telegram-widget.js?22" // Версия виджета
    script.async = true
    script.setAttribute("data-telegram-login", settings.telegramBotName)
    script.setAttribute("data-size", buttonSize)
    if (cornerRadius !== undefined) {
      script.setAttribute("data-radius", cornerRadius.toString())
    }
    if (requestAccess) {
      script.setAttribute("data-request-access", requestAccess)
    }
    script.setAttribute("data-userpic", showUserPhoto ? "true" : "false")
    script.setAttribute("data-onauth", "onTelegramAuth(user)") // Вызываем глобальную функцию

    // Важно: data-auth-url не используется, т.к. мы обрабатываем данные на клиенте
    // и затем отправляем их на наш бэкенд через API-клиент.

    ref.current.appendChild(script)

    return () => {
      // Очистка при размонтировании компонента
      if (ref.current && ref.current.contains(script)) {
        ref.current.removeChild(script)
      }
      delete window.onTelegramAuth
    }
  }, [settings.telegramBotName, buttonSize, cornerRadius, requestAccess, showUserPhoto, onAuth])

  return <div ref={ref} />
}
