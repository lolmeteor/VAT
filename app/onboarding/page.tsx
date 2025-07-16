"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Zap, Gift } from "lucide-react"
import { cn } from "@/lib/utils"

const onboardingSteps = [
  {
    icon: Zap,
    title: "Мощные инструменты анализа",
    description:
      "Загрузите запись - выберите нужные отчёты - получите файл анализа через пару минут.
      • Полный текст c ролями спикеров
• Отчёт о встрече: темы, решения, ответственные
• Готовое коммерческое предложение
• Разбор первой встречи с клиентом
• Разбор повторной встречи
• Психопрофиль клиента
• Прогноз надёжности клиента"
  },
  {
    icon: Gift,
    title: "Начните сейчас со 180 бесплатными минутами",
    description:
      "Тестируйте все модули, затем переключайтесь на гибкие тарифы без скрытых условий.
      1. Загрузите аудиофай встречи.
2. Отметьте галочками нужные виды анализа.
3. Получите готовый TXT файл для скачивания"
  },
]

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const [isCompleting, setIsCompleting] = useState(false)
  const router = useRouter()

  const isFirstStep = currentStep === 0
  const isLastStep = currentStep === onboardingSteps.length - 1

  const handleNext = async () => {
    if (!isLastStep) {
      setCurrentStep((prev) => prev + 1)
    } else {
      // ИСПРАВЛЕНО: Отправляем запрос на сервер для отметки завершения онбординга
      setIsCompleting(true)
      try {
        const response = await fetch("/api/user/complete-onboarding", {
          method: "POST",
          credentials: "include",
        })

        if (response.ok) {
          // ИСПРАВЛЕНО: Убираем localStorage, полагаемся только на сервер
          router.push("/upload-audio")
        } else {
          console.error("Ошибка завершения онбординга")
          router.push("/upload-audio") // Все равно переходим
        }
      } catch (error) {
        console.error("Ошибка завершения онбординга:", error)
        router.push("/upload-audio") // Все равно переходим
      } finally {
        setIsCompleting(false)
      }
    }
  }

  const handleBack = () => {
    if (!isFirstStep) {
      setCurrentStep((prev) => prev - 1)
    } else {
      router.push("/") // Возврат на главную страницу
    }
  }

  const handleSkip = async () => {
    // ИСПРАВЛЕНО: Отправляем запрос на сервер для отметки завершения онбординга
    setIsCompleting(true)
    try {
      const response = await fetch("/api/user/complete-onboarding", {
        method: "POST",
        credentials: "include",
      })

      if (response.ok) {
        // ИСПРАВЛЕНО: Убираем localStorage, полагаемся только на сервер
        router.push("/upload-audio")
      } else {
        console.error("Ошибка завершения онбординга")
        router.push("/upload-audio") // Все равно переходим
      }
    } catch (error) {
      console.error("Ошибка завершения онбординга:", error)
      router.push("/upload-audio") // Все равно переходим
    } finally {
      setIsCompleting(false)
    }
  }

  const { icon: Icon, title, description, englishTitle, englishDescription } = onboardingSteps[currentStep]

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-primary p-4">
      <Card className="w-full max-w-md bg-muted text-muted-foreground shadow-xl">
        <CardHeader className="items-center text-center">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary">
            <Icon size={32} className="text-secondary-foreground" />
          </div>
          <CardTitle className="text-2xl font-bold text-primary">{title}</CardTitle>
          <CardDescription className="text-primary/90">{englishTitle}</CardDescription>
        </CardHeader>
        <CardContent className="text-center">
          <p className="text-sm text-primary/80">{description}</p>
          <p className="mt-2 text-xs text-primary/60">{englishDescription}</p>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <div className="flex w-full items-center justify-center">
            {onboardingSteps.map((_, index) => (
              <div
                key={index}
                className={cn("mx-1 h-2 w-8 rounded-full", currentStep === index ? "bg-secondary" : "bg-accent/50")}
              />
            ))}
          </div>
          <div className="grid w-full grid-cols-3 gap-2">
            <Button
              variant="ghost"
              onClick={handleBack}
              className="text-accent-foreground hover:bg-accent/20"
              disabled={isCompleting}
            >
              Назад
            </Button>
            <Button
              variant="ghost"
              onClick={handleSkip}
              className="text-accent-foreground hover:bg-accent/20"
              disabled={isCompleting}
            >
              Пропустить
            </Button>
            <Button
              onClick={handleNext}
              className="bg-secondary text-secondary-foreground hover:bg-secondary/90"
              disabled={isCompleting}
            >
              {isCompleting ? "..." : isLastStep ? "Начать" : "Далее"}
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
