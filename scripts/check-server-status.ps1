# PowerShell скрипт для проверки статуса сервера VAT
Write-Host "=== Проверка статуса сервера VAT ===" -ForegroundColor Green

# Проверяем доступность доменов
Write-Host "`n1. Проверка доступности доменов:" -ForegroundColor Yellow
$domains = @(
    "https://www.vertexassistant.ru",
    "https://www.vertexassistant.ru/api/health",
    "https://vertexassistant.ru"
)

foreach ($domain in $domains) {
    try {
        $response = Invoke-WebRequest -Uri $domain -Method GET -TimeoutSec 10 -UseBasicParsing
        Write-Host "✅ $domain - Status: $($response.StatusCode)" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $domain - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Проверяем CORS заголовки
Write-Host "`n2. Проверка CORS заголовков:" -ForegroundColor Yellow
try {
    $headers = @{
        'Origin' = 'https://www.vertexassistant.ru'
        'Access-Control-Request-Method' = 'POST'
        'Access-Control-Request-Headers' = 'Content-Type'
    }
    
    $response = Invoke-WebRequest -Uri "https://www.vertexassistant.ru/api/auth/me" -Method OPTIONS -Headers $headers -UseBasicParsing
    Write-Host "✅ CORS preflight успешен - Status: $($response.StatusCode)" -ForegroundColor Green
    
    # Показываем CORS заголовки
    $corsHeaders = $response.Headers | Where-Object { $_.Key -like "*Access-Control*" }
    foreach ($header in $corsHeaders) {
        Write-Host "   $($header.Key): $($header.Value)" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "❌ CORS preflight failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Проверяем SSL сертификаты
Write-Host "`n3. Проверка SSL сертификатов:" -ForegroundColor Yellow
try {
    $cert = [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
    $request = [System.Net.WebRequest]::Create("https://www.vertexassistant.ru")
    $response = $request.GetResponse()
    Write-Host "✅ SSL сертификат валиден" -ForegroundColor Green
    $response.Close()
}
catch {
    Write-Host "❌ Проблема с SSL: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Проверка завершена ===" -ForegroundColor Green
