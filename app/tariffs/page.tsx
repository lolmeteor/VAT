"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useAuth } from "@/contexts/AuthContext"
import { apiClient } from "@/lib/api"
import { Loader2 } from "lucide-react"
import { toast } from "sonner"

interface Tariff {
  tariff_id: string
  name: string
  minutes: number
  price: number
  is_popular: boolean
}

export default function TariffsPage() {
  const { user } = useAuth()
  const [tariffs, setTariffs] = useState<Tariff[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isPurchasing, setIsPurchasing] = useState<string | null>(null)

  useEffect(() => {
    const fetchTariffs = async () => {
      try {
        const data = await apiClient.get<Tariff[]>("/user/tariffs")
        setTariffs(data)
      } catch (error) {
        toast.error("Не удалось загрузить тарифы. Попробуйте позже.")
        console.error("Ошибка загрузки тарифов:", error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchTariffs()
  }, [])

  const handlePurchase = async (tariffId: string) => {
    setIsPurchasing(tariffId)
    try {
      const response = await apiClient.post<{ confirmation_url: string }>("/payments/create", { tariff_id: tariffId })
      toast.success("Создан заказ на оплату. Перенаправляем...")
      // В реальном приложении здесь будет редирект на страницу оплаты
      window.location.href = response.confirmation_url
    } catch (error: any) {
      toast.error(`Ошибка при покупке: ${error.message || "Попробуйте снова"}`)
    } finally {
      setIsPurchasing(null)
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto flex max-w-4xl justify-center py-10">
        <Loader2 className="h-12 w-12 animate-spin text-secondary" />
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-4xl py-10">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-secondary-foreground">Купить минуты</h1>
        {user && <p className="mt-2 text-lg text-muted-foreground">Текущий баланс: {user.balance_minutes} минут</p>}
      </div>
      <div className="mt-8 grid gap-6 md:grid-cols-3">
        {tariffs.map((tariff) => (
          <Card
            key={tariff.tariff_id}
            className={cn(
              "flex flex-col bg-muted text-muted-foreground shadow-lg",
              tariff.is_popular && "border-2 border-accent",
            )}
          >
            {tariff.is_popular && (
              <div className="rounded-t-lg bg-accent py-1 text-center text-sm font-semibold text-accent-foreground">
                Популярный
              </div>
            )}
            <CardHeader className="items-center text-center">
              <CardTitle className="text-2xl text-primary">{tariff.name}</CardTitle>
              <p className="text-4xl font-bold text-secondary">{tariff.price}₽</p>
            </CardHeader>
            <CardContent className="flex-grow text-center">
              <p className="text-2xl font-semibold text-primary">{tariff.minutes} минут</p>
            </CardContent>
            <CardFooter>
              <Button
                onClick={() => handlePurchase(tariff.tariff_id)}
                disabled={isPurchasing === tariff.tariff_id}
                className="w-full bg-secondary text-secondary-foreground hover:bg-secondary/90"
              >
                {isPurchasing === tariff.tariff_id && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Купить
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}
