"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { FastAPI, Request } from "fastapi"
import { CORSMiddleware } from "fastapi.middleware.cors"
import { JSONResponse } from "fastapi.responses"
import { asynccontextmanager } from "contextlib"
import uvicorn from "uvicorn"

import { settings } from "app.config"
import { engine, Base } from "app.database"
import { auth, files, analyses, webhooks, user, common } from "app.api"

const AnalysisPage = ({ params }: { params: { fileId: string } }) => {
  const [selectedTypes, setSelectedTypes] = useState(new Set<string>())
  const [isSubmitting, setIsSubmitting] = useState(false)
  const router = useRouter()

  const handleTypeChange = (type: string) => {
    setSelectedTypes((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(type)) {
        newSet.delete(type)
      } else {
        newSet.add(type)
      }
      return newSet
    })
  }

  const handleStartAnalysis = async () => {
    if (selectedTypes.size === 0) {
      alert("Пожалуйста, выберите хотя бы один тип анализа.")
      return
    }
    setIsSubmitting(true)

    try {
      // ИСПРАВЛЕНО: Сначала получаем transcription_id по file_id
      const transcriptionResponse = await fetch(`/api/files/${params.fileId}`, {
        credentials: "include",
      })
      
      if (!transcriptionResponse.ok) {
        throw new Error("Не удалось получить информацию о файле")
      }
      
      const fileData = await transcriptionResponse.json()
      
      // Получаем transcription_id из связанной транскрипции
      const transcriptionId = fileData.transcription_id || params.fileId // fallback
      
      const response = await fetch("/api/analyses/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          transcription_id: transcriptionId, // ИСПРАВЛЕНО: используем правильный transcription_id
          analysis_types: Array.from(selectedTypes),
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

  return (
    <div>
      <h1>Анализ файла {params.fileId}</h1>
      <div>
        <label>
          <input
            type="checkbox"
            checked={selectedTypes.has("sentiment")}
            onChange={() => handleTypeChange("sentiment")}
          />
          Анализ тональности
        </label>
        <label>
          <input
            type="checkbox"
            checked={selectedTypes.has("topic")}
            onChange={() => handleTypeChange("topic")}
          />
          Анализ темы
        </label>
      </div>
      <button onClick={handleStartAnalysis} disabled={isSubmitting}>
        {isSubmitting ? "Запуск..." : "Запустить анализ"}
      </button>
    </div>
  )
}

// FastAPI application setup
const app = FastAPI({
  title: "VAT - Voice Analysis Tool",
  description: "Сервис транскрибации и анализа аудиофайлов",
  version: "1.0.0",
})

// CORS middleware setup
const origins = [
  "https://www.vertexassistant.ru",
  "https://www.vertexassistant.ru:443",
  "https://vertexassistant.ru",
  "https://vertexassistant.ru:443"
]

app.add_middleware(
  CORSMiddleware,
  {
    allow_origins: origins,
    allow_credentials: true,
    allow_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers: ["*"],
  }
)

// Include routers
app.include_router(auth.router, { prefix: "/api" })
app.include_router(files.router, { prefix: "/api" })
app.include_router(analyses.router, { prefix: "/api" })
app.include_router(webhooks.router, { prefix: "/api" })
app.include_router(user.router, { prefix: "/api" })
app.include_router(common.router, { prefix: "/api" })

// Global exception handler
app.exception_handler(Exception)((request: Request, exc: Exception) => {
  console.error(`Глобальная ошибка: ${exc}`)
  return JSONResponse({
    status_code: 500,
    content: {
      success: false,
      message: "Внутренняя ошибка сервера",
      detail: "Произошла непредвиденная ошибка. Обратитесь в поддержку."
    }
  })
})

// Lifespan context manager
const lifespan = async (app: FastAPI) => {
  // Startup
  console.log("Запуск приложения VAT...")
  Base.metadata.create_all(bind=engine)
  yield
  // Shutdown
  console.log("Остановка приложения VAT...")
}

// Run the FastAPI application
if (require.main === module) {
  uvicorn.run({
    app: "main:app",
    host: "127.0.0.1",
    port: 8000,
    reload: false
  })
}

export default AnalysisPage
