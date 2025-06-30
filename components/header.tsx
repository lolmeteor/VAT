"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { User, Wallet, LogIn, LogOut } from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"
import { useRouter } from "next/navigation"

export function AppHeader() {
  const { user, isLoading, logout } = useAuth()
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await logout()
      router.push("/") // Перенаправляем на главную после выхода
    } catch (error) {
      console.error("Ошибка выхода:", error)
      // Можно показать уведомление об ошибке
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-accent/20 bg-primary/80 backdrop-blur-sm">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-xl font-bold text-secondary">VERTEX</span>
        </Link>
        <div className="flex items-center space-x-4">
          {isLoading ? (
            <div className="h-8 w-24 animate-pulse rounded-md bg-muted/50" />
          ) : user ? (
            <>
              <div className="flex items-center space-x-2 rounded-md bg-muted px-3 py-1.5 text-sm font-medium text-muted-foreground">
                <Wallet size={16} />
                <span>{user.balance_minutes} минут</span>
              </div>
              <Link href="/profile">
                <Button variant="secondary" size="icon" aria-label="Профиль">
                  <User size={20} />
                </Button>
              </Link>
              <Button variant="ghost" size="icon" onClick={handleLogout} aria-label="Выйти">
                <LogOut size={20} className="text-accent-foreground" />
              </Button>
            </>
          ) : (
            <Button variant="secondary" onClick={() => router.push("/")}>
              <LogIn size={18} className="mr-2" />
              Войти
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
