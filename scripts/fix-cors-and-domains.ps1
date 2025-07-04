# PowerShell скрипт для исправления CORS и доменов
Write-Host "=== Исправление CORS и доменов ===" -ForegroundColor Green

# Переходим в директорию проекта
Set-Location "/opt/vat"

Write-Host "`n1. Обновляем конфигурацию Frontend..." -ForegroundColor Yellow

# Создаем правильный .env.local
@"
NEXT_PUBLIC_API_BASE_URL=https://www.vertexassistant.ru/api
NEXT_PUBLIC_TELEGRAM_BOT_NAME=VertexAIassistantBOT
"@ | Out-File -FilePath ".env.local" -Encoding UTF8

Write-Host "✅ .env.local обновлен" -ForegroundColor Green

# Обновляем Python конфигурацию
Write-Host "`n2. Обновляем Python конфигурацию..." -ForegroundColor Yellow

# Создаем новый .env файл для Python
@"
# Продакшн переменные окружения
APP_ENV=production
APP_SECRET_KEY=aG3yL4zO2ryD2yQ8_VAT_SECRET_2025
APP_BASE_URL=https://www.vertexassistant.ru
CORS_ALLOWED_ORIGINS=https://www.vertexassistant.ru,https://www.vertexassistant.ru:443,https://vertexassistant.ru

# База данных
DB_HOST=server268.hosting.reg.ru
DB_PORT=3306
DB_NAME=u3151465_VAT2
DB_USER=u3151465_Aleksey
DB_PASSWORD=your_password_here

# Telegram
TELEGRAM_BOT_TOKEN=7693655467:AAHMKYv6F8U5TVz-CPgNoOV-d52NgAETmp0
TELEGRAM_LOGIN_WIDGET_BOT_NAME=VertexAIassistantBOT

# S3 Reg.ru
S3_ENDPOINT_URL=https://s3.regru.cloud
S3_ACCESS_KEY_ID=8TVU2GJ3DLFZVS5MUI3L
S3_SECRET_ACCESS_KEY=1ARu78H9fvqqDmDpDLJFVkVt0U5RQ1v8qlNdhpgb
S3_BUCKET_NAME=smartmashabot
S3_REGION=ru-central1

# Make.com
MAKE_TRANSCRIPTION_WEBHOOK_URL=https://hook.eu2.make.com/osl3us5x5bk8uqytihx73d8o24ebw57q
"@ | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "✅ .env обновлен" -ForegroundColor Green

# Пересобираем приложение
Write-Host "`n3. Пересобираем Next.js приложение..." -ForegroundColor Yellow
try {
    & npm run build
    Write-Host "✅ Next.js приложение пересобрано" -ForegroundColor Green
}
catch {
    Write-Host "❌ Ошибка сборки Next.js: $($_.Exception.Message)" -ForegroundColor Red
}

# Перезапускаем сервисы
Write-Host "`n4. Перезапускаем сервисы..." -ForegroundColor Yellow
$services = @("vat-frontend", "vat-fastapi", "nginx")

foreach ($service in $services) {
    try {
        systemctl restart $service
        Start-Sleep -Seconds 2
        $status = systemctl is-active $service
        if ($status -eq "active") {
            Write-Host "✅ $service перезапущен успешно" -ForegroundColor Green
        } else {
            Write-Host "❌ $service не запустился" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Ошибка перезапуска $service" -ForegroundColor Red
    }
}

Write-Host "`n5. Проверяем результат..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "https://www.vertexassistant.ru/api/health" -UseBasicParsing
    Write-Host "✅ API доступен - Status: $($response.StatusCode)" -ForegroundColor Green
}
catch {
    Write-Host "❌ API недоступен: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Исправление завершено ===" -ForegroundColor Green
Write-Host "🌐 Проверьте сайт: https://www.vertexassistant.ru" -ForegroundColor Cyan
