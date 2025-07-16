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

  useEffect(() => {
    setIsClient(true)
  }, [])

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
    } catch (error: any) {
      alert(`Ошибка авторизации: ${error.message || "Попробуйте снова."}`)
    }
  }

  const renderLoader = (text: string) => (
    <div
      className="min-h-screen w-full bg-cover bg-center"
      style={{ backgroundImage: "url('/images/welcome-bg.jpg')" }}
    >
      <div className="flex min-h-screen flex-col items-center justify-center bg-black/50 p-4">
        <Loader2 className="h-16 w-16 animate-spin text-white/50" />
        <p className="mt-4 text-lg text-white/80 font-bold">{text}</p>
      </div>
    </div>
  )

  if (!isClient || authIsLoading) {
    return renderLoader("Проверка авторизации...")
  }

  if (user) {
    return renderLoader("Перенаправление...")
  }

  return (
    <div
      className="min-h-screen w-full bg-cover bg-center"
      style={{ backgroundImage: "url('/images/welcome-bg.jpg')" }}
    >
      <div className="flex min-h-screen flex-col items-center justify-center bg-black/30 p-4">
        <Card className="w-full max-w-md overflow-hidden rounded-2xl border border-white/10 bg-black/20 shadow-2xl backdrop-blur-lg">
          <CardHeader className="items-center text-center pt-8 sm:pt-10 pb-4 sm:pb-6">
            <CardTitle className="text-6xl sm:text-7xl lg:text-8xl font-bold text-white tracking-tight leading-none mb-2">
              VERTEX
            </CardTitle>
            <CardTitle className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white tracking-tight leading-none mb-4">
              AI ASSISTANT
            </CardTitle>
            <CardDescription className="text-lg sm:text-xl font-medium text-white/90 leading-tight">
              вы говорите - мы создаём аналитику
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 px-6 sm:px-8 pt-4 pb-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <Checkbox
                  id="personal-data"
                  checked={agreedPersonalData}
                  onCheckedChange={(checked) => setAgreedPersonalData(Boolean(checked))}
                  className="h-5 w-5 border-2 border-white/60 data-[state=checked]:bg-white data-[state=checked]:text-black"
                />
                <Label
                  htmlFor="personal-data"
                  className="text-sm sm:text-base font-semibold text-white/95 leading-tight"
                >
                  Согласен на обработку персональных данных
                </Label>
              </div>
              <div className="flex items-center space-x-3">
                <Checkbox
                  id="terms"
                  checked={agreedTerms}
                  onCheckedChange={(checked) => setAgreedTerms(Boolean(checked))}
                  className="h-5 w-5 border-2 border-white/60 data-[state=checked]:bg-white data-[state=checked]:text-black"
                />
                <Label htmlFor="terms" className="text-sm sm:text-base font-semibold text-white/95 leading-tight">
                  Согласен с пользовательским соглашением
                </Label>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col items-center space-y-4 px-6 sm:px-8 pb-8 sm:pb-10">
            <HybridTelegramAuth onAuth={handleTelegramAuth} disabled={!allAgreementsChecked} />
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
