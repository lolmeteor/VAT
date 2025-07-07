"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"

// TODO: Заменить на данные с API /api/user/stats и /api/user/payments
const userStats = {
  balance_minutes: 180,
  used_minutes: 120,
  analyses_completed: 5,
}

const paymentHistory = [
  { id: "1", date: "16.06.2025", minutes: "+90 мин", amount: "Бесплатно" },
  { id: "2", date: "15.05.2025", minutes: "+300 мин", amount: "500₽" },
  { id: "3", date: "10.04.2025", minutes: "+90 мин", amount: "Бесплатно" },
]

export default function ProfilePage() {
  const router = useRouter()

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
              <p className="text-2xl font-bold text-secondary">{userStats.balance_minutes} мин</p>
            </div>
            <div className="rounded-lg bg-primary/5 p-4 text-center">
              <p className="text-sm text-primary/80">Использовано</p>
              <p className="text-2xl font-bold text-primary">{userStats.used_minutes} мин</p>
            </div>
            <div className="rounded-lg bg-primary/5 p-4 text-center">
              <p className="text-sm text-primary/80">Анализов выполнено</p>
              <p className="text-2xl font-bold text-primary">{userStats.analyses_completed}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-muted text-muted-foreground shadow-lg">
          <CardHeader>
            <CardTitle className="text-primary">История оплат</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {paymentHistory.map((payment) => (
                <li key={payment.id} className="flex items-center justify-between rounded-md bg-primary/5 p-3">
                  <div>
                    <p className="font-medium text-primary">{payment.minutes}</p>
                    <p className="text-xs text-primary/60">{payment.date}</p>
                  </div>
                  <p className="font-semibold text-secondary">{payment.amount}</p>
                </li>
              ))}
            </ul>
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
