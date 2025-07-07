"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { FastAPI, Request } from "fastapi"
import { CORSMiddleware } from "fastapi.middleware.cors"
import { JSONResponse } from "fastapi.responses"
import { asynccontextmanager } from "contextlib"
import uvicorn from "uvicorn"
import logging from "logging"

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

// ──────────────────────────── Логирование ──────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

// ──────────────────────── Lifespan (startup/shutdown) ───────────────────
const lifespan = async (app: FastAPI) => {
    """Создаём/обновляем структуру БД при запуске сервера."""
    logger.info("Запуск VAT backend… создаём таблицы, если их нет…")
    Base.metadata.create_all(bind=engine)  // если используете Alembic, удалите
    yield
    logger.info("Остановка VAT backend…")
}

// ─────────────────────────────── App ────────────────────────────────────
const app = FastAPI(
    title="VAT – Voice Analysis Tool",
    description="Сервис транскрибации и анализа аудиофайлов",
    version="1.0.0",
    lifespan=lifespan,
)

// ─────────────────────────────── CORS ───────────────────────────────────
const origins: string[] = (
    settings.cors_allowed_origins.split(",")
    if settings.cors_allowed_origins !== "*"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=true,
    allow_methods=["*"],
    allow_headers=["*"],
)

// ──────────────────────────── Роутеры API ───────────────────────────────
for (const router of [common, auth, user, files, analyses, webhooks]) {
    app.include_router(router.router, { prefix: "/api" })
}

// ─────────────────────── Глобальный обработчик ошибок ──────────────────
app.exception_handler(Exception)((request: Request, exc: Exception) => {
    logger.error(`Глобальная ошибка: ${exc}`, exc_info=true)
    return JSONResponse({
        status_code: 500,
        content: {
            success: false,
            message: "Внутренняя ошибка сервера",
            detail: settings.app_env === "development" ? exc.toString() : "Обратитесь в поддержку",
        }
    })
})

// ─────────────────────────── Служебные эндпоинты ────────────────────────
app.get("/") = async (request: Request) => {
    return {
        success: true,
        message: "VAT API работает",
        version: "1.0.0",
        environment: settings.app_env
    }
}

app.get("/health") = async (request: Request) => {
    return {
        status: "healthy",
        service: "VAT API",
        timestamp: new Date().toISOString() + "Z",
    }
}

// ─────────────────────────────── main ───────────────────────────────────
if (require.main === module) {
    uvicorn.run({
        app: "main:app",
        host: "0.0.0.0",
        port: 8000,
        reload: settings.app_env === "development",
        log_level: "info"
    })
}

export default AnalysisPage
