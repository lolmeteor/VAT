"use client"

import { Checkbox } from "@/components/ui/checkbox"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Mic, Loader2 } from "lucide-react"
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
      <Card className="w-full max-w-md bg-muted text-muted-foreground shadow-xl">
        <CardHeader className="items-center text-center">
          <Mic size={64} className="mb-4 text-secondary" />
          <CardTitle className="text-3xl font-bold text-primary">Добро пожаловать!</CardTitle>
          <CardDescription className="text-primary/90">
            Сервис транскрибации и анализа аудио. Начните с 90 бесплатными минутами!
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-primary">VERTEX AI ASSISTANT</h2>
            <p className="text-sm text-primary/80">
              Say it. We'll map it. Загрузите аудиофайл для получения комплексного анализа.
            </p>
          </div>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="personal-data"
                checked={agreedPersonalData}
                onCheckedChange={(checked) => setAgreedPersonalData(Boolean(checked))}
                className="border-accent data-[state=checked]:bg-accent data-[state=checked]:text-accent-foreground"
              />
              <Label htmlFor="personal-data" className="text-sm font-medium text-primary/90">
                Согласен на обработку персональных данных
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="terms"
                checked={agreedTerms}
                onCheckedChange={(checked) => setAgreedTerms(Boolean(checked))}
                className="border-accent data-[state=checked]:bg-accent data-[state=checked]:text-accent-foreground"
              />
              <Label htmlFor="terms" className="text-sm font-medium text-primary/90">
                Согласен с пользовательским соглашением
              </Label>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex flex-col items-center space-y-4">
          <HybridTelegramAuth onAuth={handleTelegramAuth} disabled={!allAgreementsChecked} />
        </CardFooter>
      </Card>
    </div>
  )
}
