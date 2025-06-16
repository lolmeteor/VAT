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
      "Выберите один из множества типов анализа, включая анализ тональности, ключевых фраз, структурный анализ и многое другое, чтобы получить именно те инсайты, которые вам нужны.",
    englishTitle: "Powerful Analysis Tools",
    englishDescription:
      "Choose from various analysis types including tone analysis, key phrases, structural analysis, and more to get exactly the insights you need.",
  },
  {
    icon: Gift,
    title: "Начните сейчас",
    description:
      "Начните с бесплатными минутами и обновляйте тариф в любое время. Наши гибкие планы соответствуют вашим растущим потребностям.",
    englishTitle: "Start Now",
    englishDescription:
      "Begin with your complimentary minutes and upgrade anytime. Our flexible plans fit your needs as they grow.",
  },
]

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const router = useRouter()

  const isFirstStep = currentStep === 0
  const isLastStep = currentStep === onboardingSteps.length - 1

  const handleNext = () => {
    if (!isLastStep) {
      setCurrentStep((prev) => prev + 1)
    } else {
      // Переход на основную страницу приложения после онбординга
      localStorage.setItem("onboardingCompleted", "true") // Сохраняем отметку
      router.push("/upload-audio")
    }
  }

  const handleBack = () => {
    if (!isFirstStep) {
      setCurrentStep((prev) => prev - 1)
    } else {
      router.push("/") // Возврат на главную страницу
    }
  }

  const handleSkip = () => {
    localStorage.setItem("onboardingCompleted", "true") // Сохраняем отметку
    router.push("/upload-audio")
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
            <Button variant="ghost" onClick={handleBack} className="text-accent-foreground hover:bg-accent/20">
              Назад
            </Button>
            <Button variant="ghost" onClick={handleSkip} className="text-accent-foreground hover:bg-accent/20">
              Пропустить
            </Button>
            <Button onClick={handleNext} className="bg-secondary text-secondary-foreground hover:bg-secondary/90">
              {isLastStep ? "Начать" : "Далее"}
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
