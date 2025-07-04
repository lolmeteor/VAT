# PowerShell скрипт для проверки сервисов на сервере (выполнять на сервере)
Write-Host "=== Проверка сервисов VAT на сервере ===" -ForegroundColor Green

# Проверяем статус systemd сервисов
Write-Host "`n1. Статус сервисов:" -ForegroundColor Yellow
$services = @("vat-frontend", "vat-fastapi", "nginx", "mysql")

foreach ($service in $services) {
    try {
        $status = systemctl is-active $service 2>$null
        if ($status -eq "active") {
            Write-Host "✅ $service - активен" -ForegroundColor Green
        } else {
            Write-Host "❌ $service - неактивен ($status)" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ $service - ошибка проверки" -ForegroundColor Red
    }
}

# Проверяем порты
Write-Host "`n2. Проверка портов:" -ForegroundColor Yellow
$ports = @(
    @{Port=80; Service="HTTP"},
    @{Port=443; Service="HTTPS"},
    @{Port=3000; Service="Next.js"},
    @{Port=8000; Service="FastAPI"},
    @{Port=3306; Service="MySQL"}
)

foreach ($portInfo in $ports) {
    $port = $portInfo.Port
    $service = $portInfo.Service
    
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-Host "✅ Port $port ($service) - открыт" -ForegroundColor Green
        } else {
            Write-Host "❌ Port $port ($service) - закрыт" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Port $port ($service) - ошибка проверки" -ForegroundColor Red
    }
}

# Проверяем логи сервисов
Write-Host "`n3. Последние ошибки в логах:" -ForegroundColor Yellow
$logServices = @("vat-frontend", "vat-fastapi", "nginx")

foreach ($service in $logServices) {
    Write-Host "`n--- Логи $service ---" -ForegroundColor Cyan
    try {
        $logs = journalctl -u $service --no-pager -l --since "10 minutes ago" | Select-String -Pattern "error|Error|ERROR|failed|Failed|FAILED" | Select-Object -Last 3
        if ($logs) {
            foreach ($log in $logs) {
                Write-Host $log -ForegroundColor Red
            }
        } else {
            Write-Host "Ошибок не найдено" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "Не удалось получить логи для $service" -ForegroundColor Red
    }
}

Write-Host "`n=== Проверка завершена ===" -ForegroundColor Green
