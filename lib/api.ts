// Простой API клиент для взаимодействия с backend
import { settings } from "@/app/config" // Импортируем frontend-конфиг

const API_BASE_URL = settings.apiBaseUrl || "/api" // Используем относительный путь, если Next.js и FastAPI на одном домене, или полный URL

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const defaultOptions: RequestInit = {
    headers: {
      "Content-Type": "application/json",
      // Cookie 'session_id' будет автоматически отправляться браузером
    },
  }

  const config = { ...defaultOptions, ...options }

  try {
    const response = await fetch(url, config)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || `Ошибка API: ${response.status}`)
    }
    if (response.status === 204) {
      // No Content
      return null as T
    }
    return (await response.json()) as T
  } catch (error) {
    console.error("Ошибка API:", error)
    throw error
  }
}

export const apiClient = {
  get: (endpoint: string, options?: RequestInit) => request(endpoint, { ...options, method: "GET" }),
  post: (endpoint: string, data?: any, options?: RequestInit) =>
    request(endpoint, { ...options, method: "POST", body: data ? JSON.stringify(data) : null }),
  put: (endpoint: string, data: any, options?: RequestInit) =>
    request(endpoint, { ...options, method: "PUT", body: JSON.stringify(data) }),
  delete: (endpoint: string, options?: RequestInit) => request(endpoint, { ...options, method: "DELETE" }),

  // Специальный метод для загрузки файлов (FormData)
  upload: async (endpoint: string, formData: FormData, options?: RequestInit) => {
    const url = `${API_BASE_URL}${endpoint}`
    const config: RequestInit = {
      ...options,
      method: "POST",
      body: formData,
      // Content-Type будет установлен браузером автоматически для FormData
    }
    try {
      const response = await fetch(url, config)
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }))
        throw new Error(errorData.detail || `Ошибка API: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error("Ошибка загрузки файла:", error)
      throw error
    }
  },
}
