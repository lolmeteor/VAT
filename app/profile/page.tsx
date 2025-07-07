"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2, User, Clock, CreditCard } from "lucide-react"

interface UserProfile {
  user_id: string
  first_name?: string
  last_name?: string
  username?: string
  balance_minutes: number
  created_at: string
}

interface UserStats {
  total_files: number
  total_analyses: number
  minutes_used: number
  last_activity: string
}

interface Payment {
  payment_id: string
  amount: number
  currency: string
  minutes_added: number
  tariff_description: string
  status: string
  created_at: string
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        // Загружаем профиль пользователя
        const profileResponse = await fetch("/api/user/profile", {
          credentials: "include",
        })

        if (profileResponse.ok) {
          const profileData = await profileResponse.json()
          setProfile(profileData)
        }

        // Загружаем статистику
        const statsResponse = await fetch("/api/user/stats", {
          credentials: "include",
        })

        if (statsResponse.ok) {
          const statsData = await statsResponse.json()
          setStats(statsData)
        }

        // Загружаем историю платежей
        const paymentsResponse = await fetch("/api/user/payments", {
          credentials: "include",
        })

        if (paymentsResponse.ok) {
          const paymentsData = await paymentsResponse.json()
          setPayments(paymentsData.payments || [])
        }
      } catch (error) {
        console.error("Ошибка загрузки данных профиля:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchProfileData()
  }, [])

  const getStatusBadge = (status: string) => {
    const statusMap = {
      pending: { label: "Ожидает", variant: "secondary" as const },
      succeeded: { label: "Успешно", variant: "default" as const },
      canceled: { label: "Отменен", variant: "destructive" as const },
    }
    return statusMap[status as keyof typeof statusMap] || { label: status, variant: "secondary" as const }
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Загрузка профиля...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Профиль пользователя</h1>
        <p className="text-muted-foreground">Управление аккаунтом и просмотр статистики</p>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Обзор</TabsTrigger>
          <TabsTrigger value="payments">Платежи</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Информация о пользователе */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="mr-2 h-5 w-5" />
                  Личная информация
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {profile && (
                  <>
                    <div>
                      <p className="text-sm text-muted-foreground">Имя</p>
                      <p className="font-medium">
                        {profile.first_name || profile.last_name
                          ? `${profile.first_name || ""} ${profile.last_name || ""}`.trim()
                          : "Не указано"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Username</p>
                      <p className="font-medium">{profile.username || "Не указан"}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Дата регистрации</p>
                      <p className="font-medium">{new Date(profile.created_at).toLocaleDateString("ru-RU")}</p>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Баланс */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="mr-2 h-5 w-5" />
                  Баланс минут
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-primary">{profile?.balance_minutes || 0} мин</div>
                <p className="text-sm text-muted-foreground mt-2">Доступно для анализа аудиозаписей</p>
                <Button className="mt-4" onClick={() => (window.location.href = "/tariffs")}>
                  Пополнить баланс
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Статистика */}
          {stats && (
            <Card>
              <CardHeader>
                <CardTitle>Статистика использования</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">{stats.total_files}</div>
                    <p className="text-sm text-muted-foreground">Загружено файлов</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">{stats.total_analyses}</div>
                    <p className="text-sm text-muted-foreground">Выполнено анализов</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">{stats.minutes_used}</div>
                    <p className="text-sm text-muted-foreground">Минут использовано</p>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-medium">
                      {stats.last_activity ? new Date(stats.last_activity).toLocaleDateString("ru-RU") : "Нет данных"}
                    </div>
                    <p className="text-sm text-muted-foreground">Последняя активность</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="payments">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CreditCard className="mr-2 h-5 w-5" />
                История платежей
              </CardTitle>
              <CardDescription>Все ваши транзакции и пополнения баланса</CardDescription>
            </CardHeader>
            <CardContent>
              {payments.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">История платежей пуста</p>
                  <Button className="mt-4" onClick={() => (window.location.href = "/tariffs")}>
                    Совершить первую покупку
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {payments.map((payment) => (
                    <div key={payment.payment_id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <p className="font-medium">{payment.tariff_description}</p>
                          <Badge variant={getStatusBadge(payment.status).variant}>
                            {getStatusBadge(payment.status).label}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {new Date(payment.created_at).toLocaleDateString("ru-RU")} • {payment.minutes_added} минут
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold">
                          {payment.amount} {payment.currency}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
