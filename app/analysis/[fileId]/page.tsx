"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2 } from "lucide-react"
import WithHeaderLayout from "@/app/with-header-layout"

interface AnalysisPageProps {
  params: { fileId: string }
}

const analysisTypes = [
  { id: "kp", label: "Коммерческое предложение", description: "ИИ превращает разговор с клиентом в готовое КП: боль → решение → выгоды → цена." },
  { id: "first_meeting", label: "Первая встреча", description: "Разбор: как выясняли потребности, презентовали продукт, отрабатывали возражения, итог." },
  { id: "follow_up_meeting", label: "Повторная встреча", description: "Разбор: как продвигаются переговоры, новые потребности, достигнутые договорённости." },
  { id: "protocol", label: "Анализ совещания, встречи  ", description: "Кто участвовал, о чём говорили, какие решения приняли и кто за что отвечает." },
  {
    id: "speaker1_psycho",
    label: "Психологический портрет спикера 1",
    description: "Анализ личности первого участника",
  },
  { id: "speaker1_negative", label: "Негативные моменты спикера 1", description: "Выявление проблемных аспектов" },
  {
    id: "speaker2_psycho",
    label: "Психологический портрет спикера 2",
    description: "Анализ личности второго участника",
  },
  { id: "speaker2_negative", label: "Негативные моменты спикера 2", description: "Выявление проблемных аспектов" },
]

function AnalysisContent({ params }: AnalysisPageProps) {
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set())
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fileInfo, setFileInfo] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const fetchFileInfo = async () => {
      try {
        const response = await fetch(`/api/files/${params.fileId}`, {
          credentials: "include",
        })

        if (response.ok) {
          const data = await response.json()
          setFileInfo(data)
        }
      } catch (error) {
        console.error("Ошибка загрузки информации о файле:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchFileInfo()
  }, [params.fileId])

  const handleTypeChange = (type: string, checked: boolean) => {
    setSelectedTypes((prev) => {
      const newSet = new Set(prev)
      if (checked) {
        newSet.add(type)
      } else {
        newSet.delete(type)
      }
      return newSet
    })
  }

  const handleStartAnalysis = async () => {
    if (selectedTypes.size === 0) {
      setError("Пожалуйста, выберите хотя бы один тип анализа.")
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      // Получаем transcription_id по file_id
      const transcriptionResponse = await fetch(`/api/files/${params.fileId}/transcription`, {
        credentials: "include",
      })

      if (!transcriptionResponse.ok) {
        throw new Error("Не удалось получить информацию о транскрипции")
      }

      const transcriptionData = await transcriptionResponse.json()

      const response = await fetch("/api/analyses/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          transcription_id: transcriptionData.transcription_id,
          analysis_types: Array.from(selectedTypes),
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Ошибка запуска анализа")
      }

      router.push(`/results/${params.fileId}`)
    } catch (error: any) {
      setError(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Загрузка...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Выбор типов анализа</CardTitle>
          <CardDescription>
            {fileInfo ? <>Файл: {fileInfo.original_file_name}</> : <>Файл ID: {params.fileId}</>}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="grid gap-4">
            {analysisTypes.map((type) => (
              <div key={type.id} className="flex items-start space-x-3 p-4 border rounded-lg">
                <Checkbox
                  id={type.id}
                  checked={selectedTypes.has(type.id)}
                  onCheckedChange={(checked) => handleTypeChange(type.id, checked as boolean)}
                />
                <div className="flex-1">
                  <Label htmlFor={type.id} className="text-sm font-medium cursor-pointer">
                    {type.label}
                  </Label>
                  <p className="text-sm text-muted-foreground mt-1">{type.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-between items-center pt-4">
            <p className="text-sm text-muted-foreground">Выбрано типов анализа: {selectedTypes.size}</p>
            <div className="space-x-2">
              <Button variant="outline" onClick={() => router.back()} disabled={isSubmitting}>
                Назад
              </Button>
              <Button
                onClick={handleStartAnalysis}
                disabled={isSubmitting || selectedTypes.size === 0}
                className="min-w-[150px]"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Запуск...
                  </>
                ) : (
                  "Запустить анализ"
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function AnalysisPage({ params }: AnalysisPageProps) {
  return (
    <WithHeaderLayout>
      <AnalysisContent params={params} />
    </WithHeaderLayout>
  )
}
