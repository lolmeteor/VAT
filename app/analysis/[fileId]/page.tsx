"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { HelpCircle, Loader2 } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

// Тип для анализа, полученного с API
type AnalysisType = {
  id: string
  name: string
  description: string
}

export default function SelectAnalysisPage({ params }: { params: { fileId: string } }) {
  const [analysisTypes, setAnalysisTypes] = useState<AnalysisType[]>([])
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set())
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    // TODO: Заменить на реальный вызов API /api/analyses/types/available
    const fetchAnalysisTypes = async () => {
      setIsLoading(true)
      // Имитация вызова API
      await new Promise((resolve) => setTimeout(resolve, 500))
      const mockData = {
        success: true,
        data: {
          types: [
            { id: "kp", name: "КП", description: "Анализ коммерческого предложения" },
            { id: "first_meeting", name: "Первая встреча", description: "Анализ первой встречи с клиентом" },
            { id: "protocol", name: "Протокол", description: "Формирование протокола встречи" },
            {
              id: "speaker1_psycho",
              name: "Анализ Спикер 1 (псих.)",
              description: "Психологический анализ речи спикера 1",
            },
            {
              id: "speaker1_negative",
              name: "Анализ Спикер 1 (негатив)",
              description: "Выявление негативных факторов в речи спикера 1",
            },
          ],
        },
      }
      setAnalysisTypes(mockData.data.types)
      setIsLoading(false)
    }
    fetchAnalysisTypes()
  }, [])

  const handleSelectType = (typeId: string, checked: boolean) => {
    const newSelectedTypes = new Set(selectedTypes)
    if (checked) {
      newSelectedTypes.add(typeId)
    } else {
      newSelectedTypes.delete(typeId)
    }
    setSelectedTypes(newSelectedTypes)
  }

  const handleStartAnalysis = async () => {
    if (selectedTypes.size === 0) {
      alert("Пожалуйста, выберите хотя бы один тип анализа.")
      return
    }
    setIsSubmitting(true)
    console.log("Запуск анализа для файла:", params.fileId)
    console.log("Выбранные типы:", Array.from(selectedTypes))
    // TODO: Реальный вызов API POST /api/analyses/start
    await new Promise((resolve) => setTimeout(resolve, 1500))
    setIsSubmitting(false)
    alert("Анализ запущен! Вы будете перенаправлены на страницу результатов.")
    // TODO: Перенаправить на страницу результатов
    // router.push(`/results/${params.fileId}`)
  }

  return (
    <div className="container mx-auto max-w-2xl py-10">
      <Card className="bg-muted text-muted-foreground shadow-lg">
        <CardHeader>
          <CardTitle className="text-primary">Выберите анализ</CardTitle>
          <CardDescription className="text-primary/80">
            Транскрибация файла завершена. Выберите один или несколько видов анализа.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-secondary" />
            </div>
          ) : (
            <div className="space-y-4">
              <TooltipProvider>
                {analysisTypes.map((type) => (
                  <div key={type.id} className="flex items-center justify-between rounded-lg bg-primary/5 p-4">
                    <div className="flex items-center space-x-3">
                      <Checkbox
                        id={type.id}
                        onCheckedChange={(checked) => handleSelectType(type.id, Boolean(checked))}
                        className="border-accent data-[state=checked]:bg-accent data-[state=checked]:text-accent-foreground"
                      />
                      <Label htmlFor={type.id} className="text-lg font-medium text-primary">
                        {type.name}
                      </Label>
                    </div>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="h-5 w-5 text-accent" />
                      </TooltipTrigger>
                      <TooltipContent className="bg-primary text-primary-foreground">
                        <p>{type.description}</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                ))}
              </TooltipProvider>
            </div>
          )}
        </CardContent>
        <CardFooter>
          <Button
            onClick={handleStartAnalysis}
            disabled={isLoading || isSubmitting || selectedTypes.size === 0}
            className="w-full bg-secondary text-secondary-foreground hover:bg-secondary/90"
          >
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Запустить анализ
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
