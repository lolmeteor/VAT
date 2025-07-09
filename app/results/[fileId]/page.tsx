"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2, Download, FileText, RefreshCw } from "lucide-react"
import WithHeaderLayout from "@/app/with-header-layout"

interface Analysis {
  analysis_id: string
  analysis_type: string
  status: string
  s3_docx_link?: string
  s3_pdf_link?: string
  analysis_summary?: string
  key_points?: any[]
  error_message?: string
  created_at: string
  updated_at: string
}

interface FileInfo {
  file_id: string
  original_file_name: string
  duration_seconds?: number
  status: string
  created_at: string
}

interface Transcription {
  transcription_id: string
  transcription_text?: string
  speakers_count?: number
  language_detected?: string
  status: string
  s3_link_text?: string
}

function ResultsContent({ params }: { params: { fileId: string } }) {
  const [fileInfo, setFileInfo] = useState<FileInfo | null>(null)
  const [transcription, setTranscription] = useState<Transcription | null>(null)
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchData = async () => {
    try {
      // Загружаем информацию о файле
      const fileResponse = await fetch(`/api/files/${params.fileId}`, {
        credentials: "include",
      })

      if (fileResponse.ok) {
        const fileData = await fileResponse.json()
        setFileInfo(fileData)
      }

      // Загружаем транскрипцию
      const transcriptionResponse = await fetch(`/api/files/${params.fileId}/transcription`, {
        credentials: "include",
      })

      if (transcriptionResponse.ok) {
        const transcriptionData = await transcriptionResponse.json()
        setTranscription(transcriptionData)

        // Загружаем ВСЕ анализы для этой транскрипции (без фильтрации по времени)
        const analysesResponse = await fetch(
          `/api/analyses/transcription/${transcriptionData.transcription_id}?all=true`,
          {
            credentials: "include",
          },
        )

        if (analysesResponse.ok) {
          const analysesData = await analysesResponse.json()
          setAnalyses(analysesData || [])
        }
      }
    } catch (error) {
      console.error("Ошибка загрузки данных:", error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [params.fileId])

  const handleRefresh = () => {
    setRefreshing(true)
    fetchData()
  }

  const getStatusBadge = (status: string) => {
    const statusMap = {
      pending: { label: "Ожидает", variant: "secondary" as const },
      processing: { label: "Обработка", variant: "default" as const },
      completed: { label: "Готово", variant: "default" as const },
      failed: { label: "Ошибка", variant: "destructive" as const },
    }
    return statusMap[status as keyof typeof statusMap] || { label: status, variant: "secondary" as const }
  }

  const getAnalysisTypeName = (type: string) => {
    const typeMap: { [key: string]: string } = {
      kp: "Ключевые пункты",
      first_meeting: "Первая встреча",
      follow_up_meeting: "Повторная встреча",
      protocol: "Протокол встречи",
      speaker1_psycho: "Психологический портрет спикера 1",
      speaker1_negative: "Негативные моменты спикера 1",
      speaker2_psycho: "Психологический портрет спикера 2",
      speaker2_negative: "Негативные моменты спикера 2",
      speaker3_psycho: "Психологический портрет спикера 3",
      speaker3_negative: "Негативные моменты спикера 3",
      speaker4_psycho: "Психологический портрет спикера 4",
      speaker4_negative: "Негативные моменты спикера 4",
    }
    return typeMap[type] || type
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Загрузка результатов...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Результаты анализа</h1>
          <p className="text-muted-foreground">{fileInfo?.original_file_name || `Файл ${params.fileId}`}</p>
        </div>
        <Button onClick={handleRefresh} disabled={refreshing} variant="outline">
          <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
          Обновить
        </Button>
      </div>

      <Tabs defaultValue="analyses" className="space-y-6">
        <TabsList>
          <TabsTrigger value="analyses">Анализы</TabsTrigger>
          <TabsTrigger value="transcription">Транскрипция</TabsTrigger>
          <TabsTrigger value="file-info">Информация о файле</TabsTrigger>
        </TabsList>

        <TabsContent value="analyses">
          <div className="space-y-4">
            {analyses.length === 0 ? (
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-muted-foreground">Анализы не найдены</p>
                  <Button className="mt-4" onClick={() => (window.location.href = `/analysis/${params.fileId}`)}>
                    Запустить анализ
                  </Button>
                </CardContent>
              </Card>
            ) : (
              analyses.map((analysis) => (
                <Card key={analysis.analysis_id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{getAnalysisTypeName(analysis.analysis_type)}</CardTitle>
                      <Badge variant={getStatusBadge(analysis.status).variant}>
                        {getStatusBadge(analysis.status).label}
                      </Badge>
                    </div>
                    <CardDescription>
                      Создан: {new Date(analysis.created_at).toLocaleString("ru-RU")}
                      {analysis.updated_at !== analysis.created_at && (
                        <> • Обновлен: {new Date(analysis.updated_at).toLocaleString("ru-RU")}</>
                      )}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {analysis.status === "failed" && analysis.error_message && (
                      <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                        <p className="text-sm text-destructive">{analysis.error_message}</p>
                      </div>
                    )}

                    {analysis.analysis_summary && (
                      <div>
                        <h4 className="font-medium mb-2">Краткое содержание:</h4>
                        <p className="text-sm text-muted-foreground">{analysis.analysis_summary}</p>
                      </div>
                    )}

                    {analysis.key_points && analysis.key_points.length > 0 && (
                      <div>
                        <h4 className="font-medium mb-2">Ключевые моменты:</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {analysis.key_points.map((point, index) => (
                            <li key={index} className="text-sm text-muted-foreground">
                              {typeof point === "string" ? point : JSON.stringify(point)}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {analysis.status === "completed" && (
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline" asChild>
                          <a
                            href={`/api/analyses/${analysis.analysis_id}/download/docx`}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <Download className="mr-2 h-4 w-4" />
                            DOCX
                          </a>
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="transcription">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Транскрипция</span>
                {transcription && (
                  <Badge variant={getStatusBadge(transcription.status).variant}>
                    {getStatusBadge(transcription.status).label}
                  </Badge>
                )}
              </CardTitle>
              {transcription && (
                <CardDescription>
                  {transcription.speakers_count && <>Количество спикеров: {transcription.speakers_count} • </>}
                  {transcription.language_detected && <>Язык: {transcription.language_detected}</>}
                </CardDescription>
              )}
            </CardHeader>
            <CardContent>
              {transcription?.transcription_text ? (
                <div className="space-y-4">
                  <div className="p-4 bg-muted rounded-lg">
                    <pre className="whitespace-pre-wrap text-sm">{transcription.transcription_text}</pre>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="outline" asChild>
                      <a
                        href={`/api/files/${params.fileId}/transcription/download/txt`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <FileText className="mr-2 h-4 w-4" />
                        TXT
                      </a>
                    </Button>
                    <Button variant="outline" asChild>
                      <a
                        href={`/api/files/${params.fileId}/transcription/download/docx`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Download className="mr-2 h-4 w-4" />
                        DOCX
                      </a>
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  {transcription?.status === "pending" || transcription?.status === "processing"
                    ? "Транскрипция в процессе обработки..."
                    : "Транскрипция недоступна"}
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="file-info">
          <Card>
            <CardHeader>
              <CardTitle>Информация о файле</CardTitle>
            </CardHeader>
            <CardContent>
              {fileInfo && (
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Название файла</p>
                    <p className="font-medium">{fileInfo.original_file_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Статус</p>
                    <Badge variant={getStatusBadge(fileInfo.status).variant}>
                      {getStatusBadge(fileInfo.status).label}
                    </Badge>
                  </div>
                  {fileInfo.duration_seconds && (
                    <div>
                      <p className="text-sm text-muted-foreground">Длительность</p>
                      <p className="font-medium">
                        {Math.floor(fileInfo.duration_seconds / 60)}:
                        {(fileInfo.duration_seconds % 60).toString().padStart(2, "0")}
                      </p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm text-muted-foreground">Дата загрузки</p>
                    <p className="font-medium">{new Date(fileInfo.created_at).toLocaleString("ru-RU")}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default function ResultsPage({ params }: { params: { fileId: string } }) {
  return (
    <WithHeaderLayout>
      <ResultsContent params={params} />
    </WithHeaderLayout>
  )
}
