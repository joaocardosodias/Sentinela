[CmdletBinding()]
param(
    [string]$VenvPath = ".venv",
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$venvFullPath = Join-Path $repoRoot $VenvPath
$pythonPath = Join-Path $venvFullPath "Scripts\python.exe"

function Assert-VenvPath {
    param(
        [string]$PathToCheck
    )

    $repoRootFull = [System.IO.Path]::GetFullPath($repoRoot.Path).TrimEnd('\')
    $venvFull = [System.IO.Path]::GetFullPath($PathToCheck).TrimEnd('\')
    $expectedPrefix = "$repoRootFull\"

    if (-not $venvFull.StartsWith($expectedPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Caminho da venv fora do repositorio: $venvFull"
    }

    if ((Split-Path -Leaf $venvFull) -ne ".venv") {
        throw "Por seguranca, este script so remove uma pasta chamada .venv. Caminho recebido: $venvFull"
    }

    return $venvFull
}

function Remove-LocalVenv {
    if (Test-Path -LiteralPath $venvFullPath) {
        $safeVenvPath = Assert-VenvPath -PathToCheck $venvFullPath
        Write-Host "Removendo ambiente Python local quebrado: $safeVenvPath"

        $removed = $false
        for ($attempt = 1; $attempt -le 8; $attempt++) {
            try {
                Remove-Item -LiteralPath $safeVenvPath -Recurse -Force -ErrorAction Stop
                $removed = $true
                break
            } catch {
                if ($attempt -eq 8) {
                    throw
                }

                Write-Warning "Tentativa $attempt de remover .venv falhou: $($_.Exception.Message)"
                Start-Sleep -Seconds 2
            }
        }

        if (-not $removed) {
            throw "Nao foi possivel remover a .venv."
        }
    }
}

function New-LocalVenv {
    Write-Host "Criando .venv limpa"
    python -m venv --clear --without-pip $venvFullPath
    if ($LASTEXITCODE -ne 0) {
        throw "python -m venv falhou ao criar a .venv."
    }

    & $pythonPath -m ensurepip --upgrade
    if ($LASTEXITCODE -ne 0) {
        throw "ensurepip falhou ao instalar o pip da .venv."
    }
}

function Test-VenvPip {
    if (-not (Test-Path -LiteralPath $pythonPath)) {
        return $false
    }

    & $pythonPath -c "import pip; import pip._internal.index.collector" *> $null
    return $LASTEXITCODE -eq 0
}

function Invoke-CheckedCommand {
    param(
        [string]$Description,
        [scriptblock]$Command
    )

    Write-Host $Description
    & $Command

    if ($LASTEXITCODE -ne 0) {
        throw "$Description falhou com codigo $LASTEXITCODE."
    }
}

if ($Recreate) {
    Remove-LocalVenv
}

if (-not (Test-Path -LiteralPath $pythonPath)) {
    New-LocalVenv
}

if (-not (Test-VenvPip)) {
    Write-Host "pip da .venv indisponivel ou corrompido. Recriando .venv..."
    Remove-LocalVenv
    New-LocalVenv
}

Invoke-CheckedCommand "Atualizando pip" {
    & $pythonPath -m pip install --upgrade pip
}

$requirementsPath = Join-Path $repoRoot "requirements.txt"
$requirements = Get-Content -Path $requirementsPath |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") }

foreach ($requirement in $requirements) {
    $package = $requirement

    if ($package -eq "ultralytics") {
        # O cache local de wheels do torch pode ficar corrompido no Windows.
        # Baixar sem cache antes do ultralytics evita falhas silenciosas no install.
        Invoke-CheckedCommand "Instalando torch/torchvision sem cache" {
            & $pythonPath -m pip install --no-cache-dir torch torchvision
        }
    }

    Invoke-CheckedCommand "Instalando $package" {
        & $pythonPath -m pip install $package
    }
}

Invoke-CheckedCommand "Garantindo numpy para OpenCV" {
    & $pythonPath -m pip install "numpy>=2"
}

# easyocr depends on opencv-python-headless. The drone UI uses cv2.imshow,
# so we reinstall the GUI build after the dependency resolver finishes.
Invoke-CheckedCommand "Reinstalando OpenCV com suporte a GUI" {
    & $pythonPath -m pip install --force-reinstall --no-deps "opencv-python>=4.8.0"
}

& $pythonPath (Join-Path $repoRoot "scripts\check_tello_cli_env.py")
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao validar o ambiente Python da CLI do Tello."
}

Write-Host ""
Write-Host "Para abrir a CLI:"
Write-Host "$pythonPath -m src.visao_computacional.drone"
