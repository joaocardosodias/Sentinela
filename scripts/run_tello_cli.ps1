[CmdletBinding()]
param(
    [switch]$SkipSetup
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$pythonPath = Join-Path $repoRoot ".venv\Scripts\python.exe"

Set-Location $repoRoot
$env:PYTHONIOENCODING = "utf-8"

function Test-TelloUdpPortsAvailable {
    $ports = @(9000, 11111, 8890, 8899)
    $busyEndpoints = @(Get-NetUDPEndpoint -LocalPort $ports -ErrorAction SilentlyContinue)

    if ($busyEndpoints.Count -eq 0) {
        return
    }

    Write-Host "Portas UDP do Tello ocupadas. Feche os processos abaixo antes de abrir a CLI:"
    foreach ($endpoint in $busyEndpoints) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId = $($endpoint.OwningProcess)" -ErrorAction SilentlyContinue
        $processName = if ($process) { Split-Path -Leaf $process.ExecutablePath } else { "processo desconhecido" }
        Write-Host "  porta $($endpoint.LocalPort) -> PID $($endpoint.OwningProcess) ($processName)"
        if ($process -and $process.CommandLine) {
            Write-Host "    $($process.CommandLine)"
        }
    }

    exit 2
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
    Write-Host "Ambiente .venv nao encontrado. Preparando ambiente da CLI do Tello..."
    & (Join-Path $repoRoot "scripts\setup_tello_cli_env.ps1")
} elseif (-not $SkipSetup) {
    Write-Host "Validando ambiente da CLI do Tello..."
    & $pythonPath (Join-Path $repoRoot "scripts\check_tello_cli_env.py")
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Ambiente invalido. Recriando/verificando dependencias..."
        & (Join-Path $repoRoot "scripts\setup_tello_cli_env.ps1")
    }
}

Test-TelloUdpPortsAvailable
Test-TelloNetworkProfile

Write-Host ""
Write-Host "Abrindo CLI do Tello. Comandos uteis:"
Write-Host "  command"
Write-Host "  battery?"
Write-Host "  streamon"
Write-Host "  streamoff"
Write-Host "  end"
Write-Host ""

& $pythonPath -m src.visao_computacional.drone
