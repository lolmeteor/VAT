"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Loader2 } from "lucide-react"

interface AnalysisType {
  id: string
  name: string
  description: string
}

const analysisTypes: AnalysisType[] = [
  { id: "kp", name: "Ключевые пункты", description: "Выделение основных моментов разговора" },
  { id: "first_meeting", name: "Первая встреча", description: "Анализ первичного контакта с клиентом" },
  { id: "follow_up_meeting", name: "Повторная встреча", description: "Анализ последующих встреч" },
  { id: "protocol", name: "Протокол", description: "Структурированный протокол встречи" },
  {
    id: "speaker1_psycho",
    name: "Психологический портрет спикера 1",
    description: "Анализ личности первого участника",
  },
  { id: "speaker1_negative", name: "Негативные аспекты спикера 1", description: "Выявление проблемных моментов" },
  {
    id: "speaker2_psycho",
    name: "Психологический портрет спикера 2",
    description: "Анализ личности второго участника",
  },
  { id: "speaker2_negative", name: "Негативные аспекты спикера 2", description: "Выявление проблемных моментов" },
]

export default function AnalysisPage({ params }: { params: { fileId: string } }) {
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
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

  const handleTypeChange = (typeId: string, checked: boolean) => {
    setSelectedTypes((prev) => (checked ? [...prev, typeId] : prev.filter((id) => id !== typeId)))
  }

  const handleStartAnalysis = async () => {
    if (selectedTypes.length === 0) {
      alert("Пожалуйста, выберите хотя бы один тип анализа.")
      return
    }

    setIsSubmitting(true)

    try {
      // Получаем transcription_id из информации о файле
      const transcriptionId = fileInfo?.transcription?.transcription_id

      if (!transcriptionId) {
        throw new Error("Транскрипция для данного файла не найдена")
      }

      const response = await fetch("/api/analyses/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          transcription_id: transcriptionId,
          analysis_types: selectedTypes,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Ошибка запуска анализа")
      }

      router.push(`/results/${params.fileId}`)
    } catch (error: any) {
      alert(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Загрузка...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Выбор типов анализа</CardTitle>
          <CardDescription>Файл: {fileInfo?.original_file_name || params.fileId}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysisTypes.map((type) => (
              <div key={type.id} className="flex items-start space-x-3 p-4 border rounded-lg">
                <Checkbox
                  id={type.id}
                  checked={selectedTypes.includes(type.id)}
                  onCheckedChange={(checked) => handleTypeChange(type.id, checked as boolean)}
                />
                <div className="flex-1">
                  <Label htmlFor={type.id} className="font-medium cursor-pointer">
                    {type.name}
                  </Label>
                  <p className="text-sm text-muted-foreground mt-1">{type.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-between items-center pt-4">
            <p className="text-sm text-muted-foreground">
              Выбрано: {selectedTypes.length} из {analysisTypes.length}
            </p>
            <Button
              onClick={handleStartAnalysis}
              disabled={isSubmitting || selectedTypes.length === 0}
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
        </CardContent>
      </Card>
    </div>
  )
}
