[CmdletBinding()]
param(
    [string]$TelloIp = "192.168.10.1",
    [int]$CommandPort = 8889,
    [int]$TimeoutMs = 3000,
    [switch]$ProbeDrone,
    [switch]$TestInternet,
    [switch]$RequireInternet,
    [string]$InternetUrl = "https://api.ipify.org",
    [string]$InternetSourceIp = ""
)

$ErrorActionPreference = "Stop"

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "== $Title =="
}

function Get-TelloInterfaces {
    Get-NetIPAddress -AddressFamily IPv4 -ErrorAction Stop |
        Where-Object { $_.IPAddress -like "192.168.10.*" -and $_.IPAddress -ne $TelloIp } |
        Sort-Object InterfaceAlias, IPAddress
}

Write-Section "Interfaces IPv4"
$ipRows = Get-NetIPAddress -AddressFamily IPv4 |
    Sort-Object InterfaceAlias, IPAddress |
    Select-Object InterfaceAlias, InterfaceIndex, IPAddress, PrefixLength
$ipRows | Format-Table -AutoSize

Write-Section "Interfaces candidatas ao Tello"
$telloInterfaces = @(Get-TelloInterfaces)
if ($telloInterfaces.Count -eq 0) {
    Write-Warning "Nenhuma interface local em 192.168.10.0/24 foi encontrada. Conecte o Wi-Fi do PC ao SSID Tello-XXXXXX."
} else {
    $telloInterfaces |
        Select-Object InterfaceAlias, InterfaceIndex, IPAddress, PrefixLength |
        Format-Table -AutoSize
}

Write-Section "Rotas default"
$defaultRoutes = @(Get-NetRoute -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
    Sort-Object RouteMetric, InterfaceMetric, InterfaceIndex)
if ($defaultRoutes.Count -eq 0) {
    Write-Warning "Nenhuma rota default IPv4 encontrada. A Internet provavelmente nao esta roteada."
} else {
    $defaultRoutes |
        Select-Object InterfaceAlias, InterfaceIndex, NextHop, RouteMetric, InterfaceMetric |
        Format-Table -AutoSize
}

if ($telloInterfaces.Count -gt 0 -and $defaultRoutes.Count -gt 0) {
    $telloIndexes = @($telloInterfaces | ForEach-Object { $_.InterfaceIndex })
    $bestDefault = $defaultRoutes[0]
    if ($telloIndexes -contains $bestDefault.InterfaceIndex) {
        Write-Warning "A melhor rota default parece sair pela interface do Tello. Ajuste a metrica para que Ethernet/USB/4G seja preferida para Internet."
    } else {
        Write-Host "OK: a melhor rota default nao usa a interface 192.168.10.x do Tello."
    }
}

if ($TestInternet) {
    Write-Section "Teste de Internet/API"
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue

    if (-not $curl) {
        $message = "curl.exe nao encontrado. Nao foi possivel testar $InternetUrl."
        if ($RequireInternet) {
            throw $message
        }
        Write-Warning $message
    } else {
        $maxTimeSeconds = [Math]::Max(1, [Math]::Ceiling($TimeoutMs / 1000))
        $curlArgs = @("--ipv4", "--silent", "--show-error", "--max-time", "$maxTimeSeconds")

        if (-not [string]::IsNullOrWhiteSpace($InternetSourceIp)) {
            $curlArgs += @("--interface", $InternetSourceIp)
            Write-Host "Usando IP de origem informado: $InternetSourceIp"
        } else {
            Write-Host "Usando a rota default do sistema operacional."
        }

        $curlArgs += $InternetUrl
        $response = & $curl.Source @curlArgs

        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: $InternetUrl respondeu: $response"
        } else {
            $message = "Falha ao acessar $InternetUrl. Codigo curl: $LASTEXITCODE"
            if ($RequireInternet) {
                throw $message
            }
            Write-Warning $message
        }
    }
}

if (-not $ProbeDrone) {
    Write-Host ""
    Write-Host "Use -ProbeDrone para enviar 'command' e 'battery?' por UDP ao Tello. Esse probe nao decola nem move o drone."
    Write-Host "Use -TestInternet para validar a saida das APIs pela rota default ou por -InternetSourceIp."
    Write-Host "Adicione -RequireInternet quando a falha de Internet precisar bloquear o preflight."
    exit 0
}

if ($telloInterfaces.Count -eq 0) {
    throw "Nao ha interface local para bind UDP com o Tello."
}

Write-Section "Probe UDP do Tello"
$localIp = [System.Net.IPAddress]::Parse($telloInterfaces[0].IPAddress)
$remoteIp = [System.Net.IPAddress]::Parse($TelloIp)
$localEndpoint = [System.Net.IPEndPoint]::new($localIp, 0)
$remoteEndpoint = [System.Net.IPEndPoint]::new($remoteIp, $CommandPort)
$udp = [System.Net.Sockets.UdpClient]::new($localEndpoint)
$udp.Client.ReceiveTimeout = $TimeoutMs

try {
    $udp.Connect($remoteEndpoint)
    foreach ($command in @("command", "battery?")) {
        $bytes = [System.Text.Encoding]::ASCII.GetBytes($command)
        [void]$udp.Send($bytes, $bytes.Length)
        $sender = [System.Net.IPEndPoint]::new([System.Net.IPAddress]::Any, 0)
        $response = $udp.Receive([ref]$sender)
        $text = [System.Text.Encoding]::ASCII.GetString($response)
        Write-Host "$command -> $text"
    }
} finally {
    $udp.Dispose()
}
