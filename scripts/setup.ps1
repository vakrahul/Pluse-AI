# Healthcare Analytics Copilot - Setup Script (Windows PowerShell)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "=== Step 1: Start Docker services ===" -ForegroundColor Cyan
docker compose -f infrastructure/docker/docker-compose.yml up -d postgres
Write-Host "Waiting for PostgreSQL..."
Start-Sleep -Seconds 8

Write-Host "=== Step 2: Generate synthetic data ===" -ForegroundColor Cyan
Set-Location "$Root\data\seed"
pip install -q -r requirements.txt
python generate_synthetic_data.py

Write-Host "=== Step 3: Load data into PostgreSQL ===" -ForegroundColor Cyan
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_DB = "healthcare_analytics"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "postgres"
python load_to_postgres.py

Write-Host "=== Step 4: Start Cube ===" -ForegroundColor Cyan
Set-Location $Root
docker compose -f infrastructure/docker/docker-compose.yml up -d cube

Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "PostgreSQL: localhost:5432"
Write-Host "Cube Playground: http://localhost:4000"
Write-Host "Cube API: http://localhost:4000/cubejs-api/v1"
