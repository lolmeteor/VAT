"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Loader2, Check } from "lucide-react"

interface Tariff {
  id: string
  name: string
  description: string
  price: number
  minutes: number
  features: string[]
  is_popular?: boolean
}

export default function TariffsPage() {
  const [tariffs, setTariffs] = useState<Tariff[]>([])
  const [loading, setLoading] = useState(true)
  const [purchasing, setPurchasing] = useState<string | null>(null)

  useEffect(() => {
    const fetchTariffs = async () => {
      try {
        const response = await fetch("/api/user/tariffs", {
          credentials: "include",
        })

        if (response.ok) {
          const data = await response.json()
          setTariffs(data.tariffs || [])
        }
      } catch (error) {
        console.error("Ошибка загрузки тарифов:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchTariffs()
  }, [])

  const handlePurchase = async (tariffId: string) => {
    setPurchasing(tariffId)

    try {
      const response = await fetch("/api/payments/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ tariff_id: tariffId }),
      })

      if (response.ok) {
        const data = await response.json()
        // Перенаправляем на страницу оплаты или показываем успешное сообщение
        window.location.href = data.payment_url || "/profile"
      } else {
        const errorData = await response.json()
        alert(errorData.detail || "Ошибка создания платежа")
      }
    } catch (error) {
      alert("Произошла ошибка при создании платежа")
    } finally {
      setPurchasing(null)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Загрузка тарифов...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">Тарифные планы</h1>
        <p className="text-muted-foreground">Выберите подходящий тариф для анализа ваших аудиозаписей</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tariffs.map((tariff) => (
          <Card key={tariff.id} className={`relative ${tariff.is_popular ? "border-primary" : ""}`}>
            {tariff.is_popular && (
              <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2">Популярный</Badge>
            )}
            <CardHeader>
              <CardTitle className="text-xl">{tariff.name}</CardTitle>
              <CardDescription>{tariff.description}</CardDescription>
              <div className="text-3xl font-bold">
                {tariff.price} ₽
                <span className="text-sm font-normal text-muted-foreground">/ {tariff.minutes} мин</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2">
                {tariff.features.map((feature, index) => (
                  <li key={index} className="flex items-center">
                    <Check className="h-4 w-4 text-green-500 mr-2" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button
                className="w-full"
                onClick={() => handlePurchase(tariff.id)}
                disabled={purchasing === tariff.id}
                variant={tariff.is_popular ? "default" : "outline"}
              >
                {purchasing === tariff.id ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Обработка...
                  </>
                ) : (
                  "Купить"
                )}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
