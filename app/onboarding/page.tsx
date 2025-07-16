"use client";

import { useState, Fragment } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Zap, Gift, ArrowDown, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface OnboardingStep {
  icon: LucideIcon;
  title: string;
  intro: string;
  flow: string[]; // последовательность рамок + стрелки
}

const onboardingSteps: OnboardingStep[] = [
  {
    icon: Zap,
    title: "Мощные инструменты анализа",
    intro: "Готово к работе за 3 шага",
    flow: [
      "Загрузите запись",
      "Выберите нужные отчёты",
      "Получите файл анализа за пару минут",
    ],
  },
  {
    icon: Gift,
    title: "Начните сейчас со 180 бесплатными минутами",
    intro:
      "Тестируйте все модули, затем переключайтесь на гибкие тарифы без скрытых условий.",
    flow: [
      "Загрузите аудиофайл встречи",
      "Отметьте галочками нужные виды анализа",
      "Получите готовый TXT‑отчёт",
    ],
  },
];

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isCompleting, setIsCompleting] = useState(false);
  const router = useRouter();

  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === onboardingSteps.length - 1;

  const handleNext = async () => {
    if (!isLastStep) {
      setCurrentStep((prev) => prev + 1);
      return;
    }

    await completeOnboarding();
  };

  const handleBack = () => {
    if (!isFirstStep) {
      setCurrentStep((prev) => prev - 1);
    } else {
      router.push("/");
    }
  };

  const handleSkip = async () => {
    await completeOnboarding();
  };

  const completeOnboarding = async () => {
    setIsCompleting(true);
    try {
      await fetch("/api/user/complete-onboarding", {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Ошибка при завершении онбординга", error);
    } finally {
      router.push("/upload-audio");
      setIsCompleting(false);
    }
  };

  const { icon: Icon, title, intro, flow } = onboardingSteps[currentStep];

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-primary p-4">
      <Card className="w-full max-w-md bg-muted text-muted-foreground shadow-xl">
        <CardHeader className="items-center text-center">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary">
            <Icon size={32} className="text-secondary-foreground" />
          </div>
          <CardTitle className="text-2xl font-bold text-primary">{title}</CardTitle>
          <CardDescription className="text-primary/90" />
        </CardHeader>
        <CardContent className="text-center">
          <p className="mb-6 text-base font-semibold leading-snug text-primary max-w-xs mx-auto">
            {intro}
          </p>

          {/* Унифицированный flow */}
          <div className="mt-6 flex flex-col items-center space-y-2">
            {flow.map((line, idx) => (
              <Fragment key={idx}>
                <div className="w-full max-w-xs rounded-md border-2 border-secondary px-3 py-2 text-sm font-medium text-primary bg-transparent">
                  {line}
                </div>
                {idx < flow.length - 1 && (
                  <ArrowDown size={20} className="text-primary" />
                )}
              </Fragment>
            ))}
          </div>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <div className="flex w-full items-center justify-center">
            {onboardingSteps.map((_, index) => (
              <div
                key={index}
                className={cn(
                  "mx-1 h-2 w-8 rounded-full",
                  currentStep === index ? "bg-secondary" : "bg-accent/50"
                )}
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
              {isCompleting ? "…" : isLastStep ? "Начать" : "Далее"}
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}
