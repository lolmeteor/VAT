"use client";

import { useState } from "react";
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
import { Zap, Gift, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface OnboardingStep {
  icon: LucideIcon;
  title: string;
  intro: string;
  bullets?: string[];
  checklist?: string[];
}

const onboardingSteps: OnboardingStep[] = [
  {
    icon: Zap,
    title: "Мощные инструменты анализа",
    intro:
      "Загрузите запись — выберите нужные отчёты — получите файл анализа за пару минут.",
    bullets: [
      "Полный текст с разбиением по спикерам",
      "Итоги встречи: темы, решения, ответственные",
      "Коммерческое предложение",
      "Разбор первой встречи",
      "Разбор повторной встречи",
      "Психопрофиль клиента",
      "Прогноз надёжности клиента",
    ],
  },
  {
    icon: Gift,
    title: "Начните сейчас со 180 бесплатными минутами",
    intro:
      "Тестируйте все модули, затем переключайтесь на гибкие тарифы без скрытых условий.",
    checklist: [
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

  const { icon: Icon, title, intro, bullets, checklist } =
    onboardingSteps[currentStep];

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
          {/* Вступительный текст */}
          <p className="text-sm text-primary/80 leading-snug">{intro}</p>

          {/* Список в две колонки */}
          {bullets && (
            <ul className="mt-4 columns-2 gap-4 list-disc text-left text-sm text-primary/80 pl-5 [column-fill:_balance]">
              {bullets.map((item) => (
                <li key={item} className="break-inside-avoid-column leading-snug">
                  {item}
                </li>
              ))}
            </ul>
          )}

          {/* Нумерованный список */}
          {checklist && (
            <ol className="mt-4 list-decimal space-y-1 pl-5 text-left text-sm text-primary/80">
              {checklist.map((item) => (
                <li key={item} className="leading-snug">
                  {item}
                </li>
              ))}
            </ol>
          )}
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          {/* Индикатор прогресса */}
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

          {/* Кнопки */}
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
