"use client"

import { CardFooter } from "@/components/ui/card"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { UploadCloud, FileCheck, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"

export default function UploadAudioPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle")
  const [errorMessage, setErrorMessage] = useState("")

  const onDrop = useCallback((acceptedFiles: File[], fileRejections: any[]) => {
    setUploadStatus("idle")
    setErrorMessage("")
    setUploadProgress(0)

    if (fileRejections.length > 0) {
      setUploadStatus("error")
      setErrorMessage(fileRejections[0].errors[0].message)
      setFile(null)
      return
    }

    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "audio/mpeg": [".mp3"],
      "audio/wav": [".wav"],
      "audio/mp4": [".m4a"],
      "audio/flac": [".flac"],
      "audio/ogg": [".ogg"],
    },
    maxSize: 1073741824, // 1 GB
    multiple: false,
  })

  const handleUpload = async () => {
    if (!file) return

    setUploadStatus("uploading")
    setUploadProgress(0)

    // TODO: Заменить на реальную загрузку на backend API
    // Имитация загрузки
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 95) {
          return prev
        }
        return prev + 5
      })
    }, 200)

    // Имитация ответа сервера
    setTimeout(() => {
      clearInterval(interval)
      setUploadProgress(100)
      setUploadStatus("success")
      // TODO: После успешной загрузки, перенаправить на страницу выбора анализа
      // router.push(`/analysis/${fileId}`)
    }, 4000)
  }

  const renderContent = () => {
    switch (uploadStatus) {
      case "success":
        return (
          <div className="text-center">
            <FileCheck className="mx-auto h-12 w-12 text-green-500" />
            <p className="mt-2 font-semibold text-primary">Файл успешно загружен!</p>
            <p className="text-sm text-primary/80">{file?.name}</p>
          </div>
        )
      case "error":
        return (
          <div className="text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
            <p className="mt-2 font-semibold text-red-600">Ошибка загрузки</p>
            <p className="text-sm text-primary/80">{errorMessage}</p>
          </div>
        )
      default:
        return (
          <div className="text-center">
            <UploadCloud className="mx-auto h-12 w-12 text-accent" />
            <p className="mt-2 font-semibold text-primary">
              {file ? file.name : "Перетащите файл сюда или нажмите для выбора"}
            </p>
            <p className="text-xs text-primary/60">
              Поддерживаемые форматы: MP3, WAV, M4A, FLAC, OGG. Максимальный размер: 1 ГБ.
            </p>
          </div>
        )
    }
  }

  return (
    <div className="container mx-auto max-w-2xl py-10">
      <Card className="bg-muted text-muted-foreground shadow-lg">
        <CardHeader>
          <CardTitle className="text-primary">Загрузка аудио</CardTitle>
          <CardDescription className="text-primary/80">
            Загрузите ваш аудиофайл для транскрибации и анализа
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={cn(
              "flex h-48 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-accent bg-primary/5 p-8 text-center transition-colors",
              isDragActive && "border-secondary bg-secondary/10",
            )}
          >
            <input {...getInputProps()} />
            {renderContent()}
          </div>
          {uploadStatus === "uploading" && (
            <div className="mt-4">
              <Progress value={uploadProgress} className="w-full [&>div]:bg-accent" />
              <p className="mt-2 text-center text-sm text-primary">Загрузка... {uploadProgress}%</p>
            </div>
          )}
        </CardContent>
        <CardFooter>
          <Button
            onClick={handleUpload}
            disabled={!file || uploadStatus === "uploading" || uploadStatus === "success"}
            className="w-full bg-secondary text-secondary-foreground hover:bg-secondary/90"
          >
            Загрузить и начать анализ
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
