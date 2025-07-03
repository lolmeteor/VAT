"use client"

import { CardFooter } from "@/components/ui/card"
import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { UploadCloud, FileCheck, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { useRouter } from "next/navigation"

export default function UploadAudioPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle")
  const [errorMessage, setErrorMessage] = useState("")
  const router = useRouter()

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

    try {
      const formData = new FormData()
      formData.append("file", file)

      // Симуляция прогресса загрузки
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) return prev
          return prev + Math.random() * 10
        })
      }, 500)

      const response = await fetch("/api/files/upload", {
        method: "POST",
        body: formData,
        credentials: "include",
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Ошибка загрузки файла")
      }

      const result = await response.json()
      setUploadStatus("success")

      // Перенаправляем на страницу анализа
      setTimeout(() => {
        router.push(`/analysis/${result.file_id}`)
      }, 1500)
    } catch (error) {
      setUploadStatus("error")
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка при загрузке")
      setUploadProgress(0)
    }
  }

  const renderContent = () => {
    switch (uploadStatus) {
      case "success":
        return (
          <div className="text-center">
            <FileCheck className="mx-auto h-12 w-12 text-green-500" />
            <p className="mt-2 font-semibold text-primary">Файл успешно загружен!</p>
            <p className="text-sm text-primary/80">{file?.name}</p>
            <p className="text-xs text-primary/60 mt-1">Перенаправление на страницу анализа...</p>
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
              <p className="mt-2 text-center text-sm text-primary">Загрузка... {Math.round(uploadProgress)}%</p>
            </div>
          )}
        </CardContent>
        <CardFooter>
          <Button
            onClick={handleUpload}
            disabled={!file || uploadStatus === "uploading" || uploadStatus === "success"}
            className="w-full bg-secondary text-secondary-foreground hover:bg-secondary/90"
          >
            {uploadStatus === "uploading" ? "Загрузка..." : "Загрузить и начать анализ"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
