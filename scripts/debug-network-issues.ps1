# PowerShell скрипт для диагностики сетевых проблем
Write-Host "=== Диагностика сетевых проблем ===" -ForegroundColor Green

# Проверяем DNS резолюцию
Write-Host "`n1. Проверка DNS:" -ForegroundColor Yellow
$domains = @("www.vertexassistant.ru", "vertexassistant.ru")

foreach ($domain in $domains) {
    try {
        $dnsResult = Resolve-DnsName -Name $domain -Type A
        Write-Host "✅ $domain -> $($dnsResult.IPAddress)" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $domain - DNS ошибка: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Проверяем доступность по IP
Write-Host "`n2. Проверка доступности по IP:" -ForegroundColor Yellow
try {
    $ip = (Resolve-DnsName -Name "www.vertexassistant.ru" -Type A).IPAddress
    $pingResult = Test-Connection -ComputerName $ip -Count 2 -Quiet
    if ($pingResult) {
        Write-Host "✅ Сервер $ip доступен" -ForegroundColor Green
    } else {
        Write-Host "❌ Сервер $ip недоступен" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ Ошибка ping: $($_.Exception.Message)" -ForegroundColor Red
}

# Проверяем HTTP/HTTPS соединения
Write-Host "`n3. Проверка HTTP/HTTPS:" -ForegroundColor Yellow
$urls = @(
    "http://www.vertexassistant.ru",
    "https://www.vertexassistant.ru",
    "https://www.vertexassistant.ru/api/health"
)

foreach ($url in $urls) {
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 10 -UseBasicParsing
        Write-Host "✅ $url - Status: $($response.StatusCode)" -ForegroundColor Green
        
        # Показываем важные заголовки
        $importantHeaders = @("Server", "Content-Type", "Access-Control-Allow-Origin")
        foreach ($header in $importantHeaders) {
            if ($response.Headers[$header]) {
                Write-Host "   $header`: $($response.Headers[$header])" -ForegroundColor Cyan
            }
        }
    }
    catch {
        Write-Host "❌ $url - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Проверяем сертификат SSL
Write-Host "`n4. Детальная проверка SSL:" -ForegroundColor Yellow
try {
    $uri = [System.Uri]"https://www.vertexassistant.ru"
    $request = [System.Net.HttpWebRequest]::Create($uri)
    $request.Timeout = 10000
    $response = $request.GetResponse()
    
    Write-Host "✅ SSL соединение установлено" -ForegroundColor Green
    Write-Host "   Protocol: $($request.ServicePoint.SecurityProtocol)" -ForegroundColor Cyan
    
    $response.Close()
}
catch {
    Write-Host "❌ SSL ошибка: $($_.Exception.Message)" -ForegroundColor Red
}

# Проверяем файрвол (если на Windows Server)
Write-Host "`n5. Проверка файрвола:" -ForegroundColor Yellow
try {
    $firewallRules = Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*80*" -or $_.DisplayName -like "*443*" -or $_.DisplayName -like "*HTTP*"} | Select-Object DisplayName, Enabled, Direction
    if ($firewallRules) {
        foreach ($rule in $firewallRules) {
            $status = if ($rule.Enabled) { "✅" } else { "❌" }
            Write-Host "$status $($rule.DisplayName) - $($rule.Direction)" -ForegroundColor $(if ($rule.Enabled) { "Green" } else { "Red" })
        }
    } else {
        Write-Host "Правила файрвола для HTTP/HTTPS не найдены" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Не удалось проверить файрвол (возможно, не Windows Server)" -ForegroundColor Yellow
}

Write-Host "`n=== Диагностика завершена ===" -ForegroundColor Green
