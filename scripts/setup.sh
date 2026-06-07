#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Step 1: Start Docker services ==="
docker compose -f infrastructure/docker/docker-compose.yml up -d postgres
echo "Waiting for PostgreSQL..."
sleep 10

echo "=== Step 2: Generate synthetic data ==="
cd data/seed
pip install -r requirements.txt
python generate_synthetic_data.py

echo "=== Step 3: Load data into PostgreSQL ==="
export POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_DB=healthcare_analytics
export POSTGRES_USER=postgres POSTGRES_PASSWORD=postgres
python load_to_postgres.py

echo "=== Step 4: Start Cube ==="
cd "$ROOT"
docker compose -f infrastructure/docker/docker-compose.yml up -d cube
sleep 15

echo "=== Step 5: Test Cube ==="
python scripts/test_cube.py

echo "=== Setup complete ==="
echo "Cube Playground: http://localhost:4000"
echo "API: uvicorn backend.main:app --reload --port 8000"
