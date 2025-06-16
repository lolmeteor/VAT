// Frontend-специфичная конфигурация
// Этот файл будет использоваться только на клиенте

export const settings = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "/api", // Если backend на том же домене
  telegramBotName: process.env.NEXT_PUBLIC_TELEGRAM_BOT_NAME || "voiceanalysis_bot",
  // Другие публичные настройки, если нужны
}
