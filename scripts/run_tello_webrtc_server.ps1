[CmdletBinding()]
param(
    [switch]$SkipSetup
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"

Set-Location $repoRoot
$env:PYTHONIOENCODING = "utf-8"

function Test-TelloWebRtcPortsAvailable {
    $udpPorts = @(9000, 11111, 8890, 8899)
    $busyUdpEndpoints = @(Get-NetUDPEndpoint -LocalPort $udpPorts -ErrorAction SilentlyContinue)

    if ($busyUdpEndpoints.Count -gt 0) {
        Write-Host "Portas UDP do Tello ocupadas. Feche os processos abaixo antes de abrir o servidor WebRTC:"
        foreach ($endpoint in $busyUdpEndpoints) {
            $process = Get-CimInstance Win32_Process -Filter "ProcessId = $($endpoint.OwningProcess)" -ErrorAction SilentlyContinue
            $processName = if ($process) { Split-Path -Leaf $process.ExecutablePath } else { "processo desconhecido" }
            Write-Host "  UDP $($endpoint.LocalPort) -> PID $($endpoint.OwningProcess) ($processName)"
            if ($process -and $process.CommandLine) {
                Write-Host "    $($process.CommandLine)"
            }
        }

        exit 2
    }

    $webRtcPort = if ($env:TELLO_WEBRTC_PORT) { [int]$env:TELLO_WEBRTC_PORT } else { 8765 }
    $busyTcpEndpoints = @(Get-NetTCPConnection -LocalPort $webRtcPort -State Listen -ErrorAction SilentlyContinue)

    if ($busyTcpEndpoints.Count -gt 0) {
        Write-Host "Porta TCP $webRtcPort ocupada. Feche o processo abaixo antes de abrir o servidor WebRTC:"
        foreach ($endpoint in $busyTcpEndpoints) {
            $process = Get-CimInstance Win32_Process -Filter "ProcessId = $($endpoint.OwningProcess)" -ErrorAction SilentlyContinue
            $processName = if ($process) { Split-Path -Leaf $process.ExecutablePath } else { "processo desconhecido" }
            Write-Host "  TCP $webRtcPort -> PID $($endpoint.OwningProcess) ($processName)"
            if ($process -and $process.CommandLine) {
                Write-Host "    $($process.CommandLine)"
            }
        }

        exit 2
    }
}

function Test-TelloNetworkProfile {
    $profiles = @(Get-NetConnectionProfile -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "TELLO*" -or $_.Name -like "Tello*" })

    foreach ($profile in $profiles) {
        if ($profile.NetworkCategory -eq "Public") {
            Write-Host "A rede do Tello esta como Public no Windows."
            Write-Host "Para receber video UDP 11111, altere para Private em PowerShell como Administrador:"
            Write-Host "  Set-NetConnectionProfile -InterfaceAlias '$($profile.InterfaceAlias)' -NetworkCategory Private"
            exit 3
        }
    }
}

if (-not (Test-Path -LiteralPath $pythonPath)) {
    Write-Host "Ambiente .venv nao encontrado. Preparando ambiente Tello..."
    & (Join-Path $repoRoot "scripts\setup_tello_cli_env.ps1")
} elseif (-not $SkipSetup) {
    Write-Host "Validando ambiente Tello CLI/WebRTC..."
    & $pythonPath (Join-Path $repoRoot "scripts\check_tello_cli_env.py")
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Ambiente invalido. Recriando/verificando dependencias..."
        & (Join-Path $repoRoot "scripts\setup_tello_cli_env.ps1")
    }
}

Test-TelloWebRtcPortsAvailable
Test-TelloNetworkProfile

Write-Host ""
Write-Host "Antes do voo, garanta que a regra de firewall foi aplicada como Administrador:"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\enable_tello_video_firewall_rule.ps1"
Write-Host ""
Write-Host "Abrindo servidor WebRTC do Tello em http://localhost:8765"
Write-Host ""

& $pythonPath -m src.drone.drone_webrtc_server
