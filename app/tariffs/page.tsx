"use client"

import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

// TODO: Заменить на данные с API /api/user/tariffs
const tariffs = [
  {
    id: "basic",
    name: "Базовый пакет",
    minutes: 300,
    price: 500,
    is_popular: false,
  },
  {
    id: "popular",
    name: "Популярный",
    minutes: 500,
    price: 800,
    is_popular: true,
  },
  {
    id: "maximum",
    name: "Максимальный",
    minutes: 2000,
    price: 2500,
    is_popular: false,
  },
]

export default function TariffsPage() {
  const handlePurchase = (tariffId: string) => {
    // TODO: Реализовать логику перехода к оплате через Юкассу
    alert(`Выбран тариф: ${tariffId}. Здесь будет переход к оплате.`)
  }

  return (
    <div className="container mx-auto max-w-4xl py-10">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-secondary-foreground">Купить минуты</h1>
        <p className="mt-2 text-lg text-muted">Текущий баланс: 90 минут</p>
      </div>
      <div className="mt-8 grid gap-6 md:grid-cols-3">
        {tariffs.map((tariff) => (
          <Card
            key={tariff.id}
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
                onClick={() => handlePurchase(tariff.id)}
                className="w-full bg-secondary text-secondary-foreground hover:bg-secondary/90"
              >
                Купить
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}
