"use client"

import { Checkbox } from "@/components/ui/checkbox"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Loader2 } from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"
import { HybridTelegramAuth } from "@/components/hybrid-telegram-auth"

export default function WelcomePage() {
  const [agreedPersonalData, setAgreedPersonalData] = useState(false)
  const [agreedTerms, setAgreedTerms] = useState(false)
  const [isClient, setIsClient] = useState(false)
  const router = useRouter()
  const { user, login, isLoading: authIsLoading } = useAuth()

  const allAgreementsChecked = agreedPersonalData && agreedTerms

  // Определяем, что код выполняется на клиенте
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Если пользователь авторизован, проверяем завершён ли онбординг
  useEffect(() => {
    if (isClient && user && !authIsLoading) {
      checkOnboardingStatus()
    }
  }, [user, authIsLoading, isClient])

  const checkOnboardingStatus = async () => {
    try {
      const response = await fetch("/api/user/onboarding-status", {
        credentials: "include",
      })

      if (response.ok) {
        const data = await response.json()
        if (data.onboarding_completed) {
          router.push("/upload-audio")
        } else {
          router.push("/onboarding")
        }
      } else {
        router.push("/onboarding")
      }
    } catch (error) {
      console.error("Ошибка проверки статуса онбординга:", error)
      router.push("/onboarding")
    }
  }

  const handleTelegramAuth = async (telegramUserData: any) => {
    if (!allAgreementsChecked) {
      alert("Пожалуйста, примите все условия для продолжения.")
      return
    }
    try {
      await login(telegramUserData)
      await checkOnboardingStatus()
    } catch (error: any) {
      alert(`Ошибка авторизации: ${error.message || "Попробуйте снова."}`)
    }
  }

  // Лоадер, пока проверяем сессию или работаем на сервере
  if (!isClient || authIsLoading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-primary p-4">
        <Loader2 className="h-16 w-16 animate-spin text-secondary" />
        <p className="mt-4 text-lg text-primary-foreground">Проверка авторизации...</p>
      </div>
    )
  }

  // Если юзер уже авторизован, показываем редирект
  if (user) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-primary p-4">
        <Loader2 className="h-16 w-16 animate-spin text-secondary" />
        <p className="mt-4 text-lg text-primary-foreground">Перенаправление...</p>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-primary p-4">
      <Card className="w-full max-w-md relative overflow-hidden shadow-xl bg-transparent border-none">
        {/* Фоновое изображение */}
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: "url('/images/welcome-bg.jpg')",
          }}
        />
        {/* Полупрозрачный оверлей для лучшей читаемости текста */}
        <div className="absolute inset-0 bg-black/30" />

        {/* Контент поверх фона */}
        <div className="relative z-10">
          <CardHeader className="items-center text-center pb-4">
            <CardTitle className="text-6xl md:text-7xl font-bold text-white leading-tight">
              VERTEX AI ASSISTANT
            </CardTitle>
            <CardDescription className="text-xl md:text-2xl text-white font-medium leading-tight mt-2">
              вы говорите - мы создаём аналитику
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 py-4">
            <div className="space-y-2">
              <div className="flex items-center justify-center space-x-2">
                <Checkbox
                  id="personal-data"
                  checked={agreedPersonalData}
                  onCheckedChange={(checked) => setAgreedPersonalData(Boolean(checked))}
                  className="border-white/50 data-[state=checked]:bg-white data-[state=checked]:text-black"
                />
                <Label
                  htmlFor="personal-data"
                  className="text-base md:text-lg font-medium text-white text-center leading-tight"
                >
                  Согласен на обработку персональных данных
                </Label>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <Checkbox
                  id="terms"
                  checked={agreedTerms}
                  onCheckedChange={(checked) => setAgreedTerms(Boolean(checked))}
                  className="border-white/50 data-[state=checked]:bg-white data-[state=checked]:text-black"
                />
                <Label
                  htmlFor="terms"
                  className="text-base md:text-lg font-medium text-white text-center leading-tight"
                >
                  Согласен с пользовательским соглашением
                </Label>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col items-center space-y-4 text-white">
            <HybridTelegramAuth onAuth={handleTelegramAuth} disabled={!allAgreementsChecked} />
          </CardFooter>
        </div>
      </Card>
    </div>
  )
}
