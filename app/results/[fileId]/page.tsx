"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Download, FileText, RefreshCw, Upload, Loader2 } from "lucide-react"
import { useRouter } from "next/navigation"
import { apiClient } from "@/lib/api"
import { toast } from "sonner"

interface AnalysisResult {
  analysis_id: string
  analysis_type: string
  status: "completed" | "processing" | "failed"
  // s3_docx_link и s3_pdf_link не используются напрямую, скачивание идет через API
}

interface AnalysisTypeName {
  [key: string]: string
}

const analysisTypeNames: AnalysisTypeName = {
  kp: "КП",
  first_meeting: "Первая встреча",
  follow_up_meeting: "Повторная встреча",
  protocol: "Протокол",
  speaker1_psycho: "Анализ Спикер 1 (психологический)",
  speaker1_negative: "Анализ Спикер 1 (негативные факторы)",
  speaker2_psycho: "Анализ Спикер 2 (психологический)",
  speaker2_negative: "Анализ Спикер 2 (негативные факторы)",
  speaker3_psycho: "Анализ Спикер 3 (психологический)",
  speaker3_negative: "Анализ Спикер 3 (негативные факторы)",
  speaker4_psycho: "Анализ Спикер 4 (психологический)",
  speaker4_negative: "Анализ Спикер 4 (негативные факторы)",
}

export default function ResultsPage({ params }: { params: { fileId: string } }) {
  const router = useRouter()
  const [results, setResults] = useState<AnalysisResult[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isPolling, setIsPolling] = useState(false)

  const fetchResults = async () => {
    setIsLoading(true)
    try {
      const transcriptionRes = await apiClient.get<{ transcription_id: string }>(
        `/files/${params.fileId}/transcription`,
      )
      const analysesRes = await apiClient.get<AnalysisResult[]>(
        `/analyses/transcription/${transcriptionRes.transcription_id}`,
      )
      setResults(analysesRes)

      // Проверяем, есть ли анализы в обработке, чтобы запустить опрос
      if (analysesRes.some((r) => r.status === "processing")) {
        setIsPolling(true)
      } else {
        setIsPolling(false)
      }
    } catch (error) {
      toast.error("Не удалось загрузить результаты анализа.")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchResults()
  }, [params.fileId])

  // Опрос статуса каждые 5 секунд, если есть что-то в обработке
  useEffect(() => {
    if (!isPolling) return
    const interval = setInterval(() => {
      fetchResults()
    }, 5000)
    return () => clearInterval(interval)
  }, [isPolling])

  const handleDownload = async (analysisId: string) => {
    try {
      const response = await fetch(`/api/analyses/${analysisId}/download/docx`, { credentials: "include" })
      if (!response.ok) {
        throw new Error("Ошибка при скачивании файла")
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `analysis_${analysisId}.docx`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      toast.error("Не удалось скачать файл.")
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "completed":
        return "Результаты готовы к скачиванию"
      case "processing":
        return "В обработке..."
      case "failed":
        return "Ошибка анализа"
      default:
        return "Неизвестный статус"
    }
  }

  return (
    <div className="container mx-auto max-w-2xl py-10">
      <Card className="bg-muted text-muted-foreground shadow-lg">
        <CardHeader className="text-center">
          <FileText className="mx-auto h-12 w-12 text-secondary" />
          <CardTitle className="mt-4 text-2xl font-bold text-primary">Результаты анализов</CardTitle>
          <CardDescription className="text-primary/80">Файл: {params.fileId}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-secondary" />
            </div>
          ) : results.length > 0 ? (
            results.map((result) => (
              <div key={result.analysis_id} className="flex items-center justify-between rounded-lg bg-primary/5 p-4">
                <div>
                  <p className="font-semibold text-primary">
                    {analysisTypeNames[result.analysis_type] || result.analysis_type}
                  </p>
                  <p
                    className={`text-sm ${result.status === "completed" ? "text-green-600" : result.status === "failed" ? "text-red-600" : "text-yellow-600"}`}
                  >
                    {getStatusText(result.status)}
                  </p>
                </div>
                {result.status === "completed" && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownload(result.analysis_id)}
                    className="border-accent bg-transparent text-accent-foreground hover:bg-accent hover:text-accent-foreground"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Скачать .docx
                  </Button>
                )}
                {result.status === "processing" && <Loader2 className="h-5 w-5 animate-spin text-accent" />}
              </div>
            ))
          ) : (
            <p className="text-center text-primary/70">Для этого файла еще нет анализов.</p>
          )}
        </CardContent>
        <CardFooter className="grid grid-cols-1 gap-2 md:grid-cols-2">
          <Button
            variant="outline"
            onClick={() => router.push(`/analysis/${params.fileId}`)}
            className="border-accent bg-transparent text-accent-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Выбрать другой анализ
          </Button>
          <Button
            onClick={() => router.push("/upload-audio")}
            className="bg-secondary text-secondary-foreground hover:bg-secondary/90"
          >
            <Upload className="mr-2 h-4 w-4" />
            Загрузить новый файл
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
