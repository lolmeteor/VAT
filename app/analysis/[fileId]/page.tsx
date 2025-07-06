"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { HelpCircle, Loader2, AlertTriangle } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useRouter } from "next/navigation"
import { apiClient } from "@/lib/api"
import { toast } from "sonner"

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
  const [error, setError] = useState<string | null>(null)
  const [transcriptionId, setTranscriptionId] = useState<string>("")
  const router = useRouter()

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const transcriptionResponse = await apiClient.get<{ transcription_id: string }>(
          `/files/${params.fileId}/transcription`,
        )
        setTranscriptionId(transcriptionResponse.transcription_id)

        const typesResponse = await apiClient.get<{ data: { types: AnalysisType[] } }>("/analyses/types/available")
        setAnalysisTypes(typesResponse.data.types)
      } catch (err: any) {
        setError(err.message || "Не удалось загрузить данные для анализа.")
        toast.error(err.message || "Ошибка загрузки данных.")
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [params.fileId])

  const handleSelectType = (typeId: string, checked: boolean) => {
    const newSelectedTypes = new Set(selectedTypes)
    if (checked) newSelectedTypes.add(typeId)
    else newSelectedTypes.delete(typeId)
    setSelectedTypes(newSelectedTypes)
  }

  const handleStartAnalysis = async () => {
    if (selectedTypes.size === 0) {
      toast.warning("Пожалуйста, выберите хотя бы один тип анализа.")
      return
    }
    setIsSubmitting(true)
    try {
      await apiClient.post("/analyses/start", {
        transcription_id: transcriptionId,
        analysis_types: Array.from(selectedTypes),
      })
      toast.success("Анализ успешно запущен!")
      router.push(`/results/${params.fileId}`)
    } catch (err: any) {
      toast.error(`Ошибка запуска анализа: ${err.message}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-secondary" />
        </div>
      )
    }
    if (error) {
      return (
        <div className="flex flex-col items-center justify-center py-8 text-center text-destructive">
          <AlertTriangle className="h-8 w-8" />
          <p className="mt-2 font-semibold">Ошибка</p>
          <p className="text-sm">{error}</p>
        </div>
      )
    }
    return (
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
    )
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
        <CardContent>{renderContent()}</CardContent>
        <CardFooter>
          <Button
            onClick={handleStartAnalysis}
            disabled={isLoading || isSubmitting || selectedTypes.size === 0 || !!error}
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
