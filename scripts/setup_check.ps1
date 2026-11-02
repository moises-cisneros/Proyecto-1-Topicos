<#
.SYNOPSIS
    Script de verificacion del entorno de desarrollo para SMS Sentinel.
.DESCRIPTION
    Comprueba si la maquina local cuenta con las herramientas necesarias para el stack:
    Git, Python 3.10+, Node.js 20+, pnpm, Docker y Docker Compose.
#>

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Verificacion del Entorno de Desarrollo - SMS Sentinel  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

function Check-Tool {
    param (
        [string]$Name,
        [scriptblock]$CheckCmd,
        [bool]$Mandatory = $true
    )

    Write-Host -NoNewline "Verificando $Name... "
    try {
        $output = & $CheckCmd 2>&1
        if ($LASTEXITCODE -eq 0 -or $output) {
            Write-Host "[OK] -> $output" -ForegroundColor Green
            return $true
        } else {
            throw "Comando no respondio correctamente"
        }
    } catch {
        if ($Mandatory) {
            Write-Host "[NO INSTALADO / ERROR] (Obligatorio)" -ForegroundColor Red
        } else {
            Write-Host "[NO ENCONTRADO] (Opcional pero recomendado)" -ForegroundColor Yellow
        }
        return $false
    }
}

$AllOk = $true

# 1. Git
$ok = Check-Tool -Name "Git" -CheckCmd { git --version }
$AllOk = $AllOk -and $ok

# 2. Python
$ok = Check-Tool -Name "Python" -CheckCmd { python --version }
$AllOk = $AllOk -and $ok

# 3. Node.js
$ok = Check-Tool -Name "Node.js" -CheckCmd { node --version }
$AllOk = $AllOk -and $ok

# 4. pnpm
$ok = Check-Tool -Name "pnpm" -CheckCmd { pnpm --version } -Mandatory $false
if (-not $ok) {
    Write-Host "   -> Puede instalar pnpm mediante: npm install -g pnpm" -ForegroundColor DarkCyan
}

# 5. Docker
$ok = Check-Tool -Name "Docker" -CheckCmd { docker --version } -Mandatory $false
if (-not $ok) {
    Write-Host "   -> Docker Desktop es requerido para ejecutar contenedores en puertos 3090, 8090 y 5439." -ForegroundColor DarkCyan
}

# 6. Docker Compose
$ok = Check-Tool -Name "Docker Compose" -CheckCmd { docker compose version } -Mandatory $false

Write-Host "----------------------------------------------------------" -ForegroundColor Cyan
if ($AllOk) {
    Write-Host "Entorno base verificado exitosamente." -ForegroundColor Green
} else {
    Write-Host "Faltan herramientas esenciales en el sistema." -ForegroundColor Red
}
Write-Host "==========================================================" -ForegroundColor Cyan

