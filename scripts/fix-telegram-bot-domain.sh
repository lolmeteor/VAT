#!/bin/bash

echo "=== Исправление домена Telegram бота ==="

echo "1. Для исправления 'Bot domain invalid' нужно:"
echo "   - Открыть @BotFather в Telegram"
echo "   - Отправить команду: /setdomain"
echo "   - Выбрать бота: @VertexAIassistantBOT"
echo "   - Указать домен: www.vertexassistant.ru"

echo ""
echo "2. Альтернативно, можно добавить домен через команды:"
echo "   /mybots -> @VertexAIassistantBOT -> Bot Settings -> Domain"

echo ""
echo "3. После настройки домена в BotFather, перезапустим сервисы:"

# Перезапускаем frontend для применения новых переменных окружения
echo "Перезапускаем frontend..."
systemctl restart vat-frontend

sleep 5

echo "✅ Настройка завершена"
echo "🔧 Не забудьте настроить домен в @BotFather!"
