"use client"

import { CardFooter } from "@/components/ui/card"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Download, FileText, RefreshCw, Upload, Loader2 } from "lucide-react"
import { useRouter } from "next/navigation"

// TODO: Заменить на данные с API /api/analyses/transcription/{transcriptionId}
const analysisResults = [
  { id: "1", name: "Структурный анализ", status: "completed", docx_link: "#" },
  { id: "2", name: "Анализ участников", status: "completed", docx_link: "#" },
  { id: "3", name: "Анализ тональности", status: "processing" },
]

export default function ResultsPage({ params }: { params: { fileId: string } }) {
  const router = useRouter()

  const handleDownload = (link: string) => {
    // TODO: Реализовать скачивание
    alert(`Скачивание по ссылке: ${link}`)
  }

  return (
    <div className="container mx-auto max-w-2xl py-10">
      <Card className="bg-muted text-muted-foreground shadow-lg">
        <CardHeader className="text-center">
          <FileText className="mx-auto h-12 w-12 text-secondary" />
          <CardTitle className="mt-4 text-2xl font-bold text-primary">Результат анализа</CardTitle>
          <CardDescription className="text-primary/80">
            Анализ завершен: {new Date().toLocaleDateString("ru-RU")}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {analysisResults.map((result) => (
            <div key={result.id} className="flex items-center justify-between rounded-lg bg-primary/5 p-4">
              <div>
                <p className="font-semibold text-primary">{result.name}</p>
                <p className={`text-sm ${result.status === "completed" ? "text-green-600" : "text-yellow-600"}`}>
                  {result.status === "completed" ? "Результаты готовы к скачиванию" : "В обработке..."}
                </p>
              </div>
              {result.status === "completed" && result.docx_link && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownload(result.docx_link)}
                  className="border-accent bg-transparent text-accent-foreground hover:bg-accent hover:text-accent-foreground"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Скачать .docx
                </Button>
              )}
              {result.status === "processing" && <Loader2 className="h-5 w-5 animate-spin text-accent" />}
            </div>
          ))}
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
