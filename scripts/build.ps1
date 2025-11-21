param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

switch ($Command.ToLower()) {
    "build" {
        Write-Host "Building .exe..." -ForegroundColor Green
        poetry run pyinstaller src/main.py --clean
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Build ready: dist\ObjectDetector.exe" -ForegroundColor Green
        } else {
            Write-Host "Build failed" -ForegroundColor Red
        }
    }

    "clean" {
        Write-Host "Cleaning..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
        Get-ChildItem -Filter "*.spec" | Where-Object { $_.Name -ne "build.spec" } | Remove-Item -Force
        Write-Host "Cleaned!" -ForegroundColor Green
    }

    default {
        Write-Host "Uses:" -ForegroundColor Cyan
        Write-Host "  .\scripts\build.ps1 build"
        Write-Host "  .\scripts\build.ps1 clean"
    }
}
