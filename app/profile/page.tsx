"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { apiClient } from "@/lib/api"
import { Loader2 } from "lucide-react"
import { toast } from "sonner"

interface UserStats {
  balance_minutes: number
  used_minutes: number
  analyses_completed: number
  files_uploaded: number
}

interface Payment {
  payment_id: string
  created_at: string
  minutes_added: number
  amount: number
  status: string
  tariff?: { name: string }
}

export default function ProfilePage() {
  const router = useRouter()
  const [stats, setStats] = useState<UserStats | null>(null)
  const [payments, setPayments] = useState<Payment[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, paymentsData] = await Promise.all([
          apiClient.get<UserStats>("/user/stats"),
          apiClient.get<Payment[]>("/user/payments"),
        ])
        setStats(statsData)
        setPayments(paymentsData)
      } catch (error) {
        toast.error("Не удалось загрузить данные профиля.")
        console.error("Ошибка загрузки профиля:", error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [])

  if (isLoading) {
    return (
      <div className="container mx-auto flex max-w-2xl justify-center py-10">
        <Loader2 className="h-12 w-12 animate-spin text-secondary" />
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-2xl py-10">
      <div className="space-y-8">
        <Card className="bg-muted text-muted-foreground shadow-lg">
          <CardHeader>
            <CardTitle className="text-primary">Статистика</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-lg bg-primary/5 p-4 text-center">
              <p className="text-sm text-primary/80">Остаток минут</p>
              <p className="text-2xl font-bold text-secondary">{stats?.balance_minutes ?? "..."} мин</p>
            </div>
            <div className="rounded-lg bg-primary/5 p-4 text-center">
              <p className="text-sm text-primary/80">Использовано</p>
              <p className="text-2xl font-bold text-primary">{stats?.used_minutes ?? "..."} мин</p>
            </div>
            <div className="rounded-lg bg-primary/5 p-4 text-center">
              <p className="text-sm text-primary/80">Анализов выполнено</p>
              <p className="text-2xl font-bold text-primary">{stats?.analyses_completed ?? "..."}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-muted text-muted-foreground shadow-lg">
          <CardHeader>
            <CardTitle className="text-primary">История оплат</CardTitle>
          </CardHeader>
          <CardContent>
            {payments.length > 0 ? (
              <ul className="space-y-3">
                {payments.map((payment) => (
                  <li
                    key={payment.payment_id}
                    className="flex items-center justify-between rounded-md bg-primary/5 p-3"
                  >
                    <div>
                      <p className="font-medium text-primary">
                        {payment.tariff?.name || `+${payment.minutes_added} мин`}
                      </p>
                      <p className="text-xs text-primary/60">
                        {new Date(payment.created_at).toLocaleDateString("ru-RU")}
                      </p>
                    </div>
                    <p className="font-semibold text-secondary">
                      {payment.amount > 0 ? `${payment.amount}₽` : "Бесплатно"}
                    </p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-center text-primary/70">История платежей пуста.</p>
            )}
          </CardContent>
        </Card>

        <Button
          onClick={() => router.push("/tariffs")}
          className="w-full bg-secondary text-secondary-foreground hover:bg-secondary/90"
        >
          Купить минуты
        </Button>
      </div>
    </div>
  )
}
