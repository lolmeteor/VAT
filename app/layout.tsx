import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { cn } from "@/lib/utils"
import { AppHeader } from "@/components/header"
import { AuthProvider } from "@/contexts/AuthContext" // Импортируем AuthProvider
import { Toaster } from "sonner" // Для уведомлений

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" })

export const metadata: Metadata = {
  title: "VAT - Сервис транскрибации и анализа аудио",
  description: "Автоматическая транскрибация аудиофайлов и проведение текстового анализа.",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className={cn("min-h-screen bg-primary font-sans antialiased", inter.variable)}>
        <AuthProvider>
          {" "}
          {/* Оборачиваем приложение в AuthProvider */}
          <div className="relative flex min-h-screen flex-col">
            <AppHeader />
            <main className="flex-1">{children}</main>
            <Toaster richColors position="top-right" /> {/* Компонент для уведомлений */}
          </div>
        </AuthProvider>
      </body>
    </html>
  )
}
