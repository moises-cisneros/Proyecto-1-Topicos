<#
.SYNOPSIS
    Script de verificacion previa a la realizacion de commits para SMS Sentinel.
.DESCRIPTION
    Ejecuta validaciones tecnicas de integridad de software:
    1. Verifica que la identidad del desarrollador este configurada en Git (user.name y user.email).
    2. Comprueba que los archivos fundamentales del repositorio publico existan.
    3. Valida la sintaxis de todos los archivos Python en el proyecto.
#>

$ErrorActionPreference = "Stop"
Write-Host "==> [Pre-Commit Check] Ejecutando validaciones de calidad..." -ForegroundColor Cyan

# 1. Comprobar configuracion de identidad de Git
$GitName = git config user.name
$GitEmail = git config user.email

if (-not $GitName -or -not $GitEmail) {
    Write-Host "[ERROR] Falta configurar user.name o user.email en Git." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Identidad de Git: $GitName <$GitEmail>" -ForegroundColor Green

# 2. Comprobar que los archivos esenciales publicos del repositorio existan
$CoreDocs = @("README.md", "LICENSE", "CONTRIBUTING.md", "ARCHITECTURE.md", "DESIGN.md")
foreach ($doc in $CoreDocs) {
    if (-not (Test-Path $doc)) {
        Write-Host "[ERROR] Archivo esencial no encontrado: $doc" -ForegroundColor Red
        exit 1
    }
}
Write-Host "[OK] Archivos fundamentales de repositorio presentes." -ForegroundColor Green

# 3. Comprobar sintaxis Python en archivos .py (excluyendo entornos virtuales)
$PythonFiles = Get-ChildItem -Path . -Recurse -Filter *.py -Exclude ".venv","venv","node_modules",".git",".agents"
if ($PythonFiles.Count -gt 0) {
    Write-Host "==> Verificando sintaxis de $($PythonFiles.Count) archivos Python..." -ForegroundColor Green
    foreach ($file in $PythonFiles) {
        $result = python -m py_compile "$($file.FullName)" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Error de sintaxis en: $($file.FullName)" -ForegroundColor Red
            Write-Host $result -ForegroundColor Red
            exit 1
        }
    }
    Write-Host "[OK] Sintaxis Python correcta en todos los modulos." -ForegroundColor Green
}

# 4. Validar formato e integridad de CONTRIBUCIONES.md
if (Test-Path "scripts/verify_contributions.py") {
    Write-Host "==> Verificando integridad de CONTRIBUCIONES.md..." -ForegroundColor Cyan
    $contributionsCheck = python scripts/verify_contributions.py 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Inconsistencias detectadas en CONTRIBUCIONES.md:" -ForegroundColor Red
        Write-Host $contributionsCheck -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] CONTRIBUCIONES.md verificado correctamente." -ForegroundColor Green
}

Write-Host "==> [Pre-Commit Check] Todas las validaciones de calidad pasaron exitosamente." -ForegroundColor Green
exit 0

