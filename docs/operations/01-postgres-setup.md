# Operation: PostgreSQL Setup

## Purpose
Initialize the PostgreSQL data warehouse that replaces Snowflake in this platform.

## Prerequisites
- Docker Desktop installed
- Port 5432 available

## Step-by-step

1. Start PostgreSQL:
   ```powershell
   docker compose -f infrastructure/docker/docker-compose.yml up -d postgres
   ```

2. Verify connection:
   ```powershell
   docker exec hc-postgres pg_isready -U postgres -d healthcare_analytics
   ```

3. Schemas created automatically via init scripts in `data/ddl/`.

## Inputs / Outputs
- **Input**: DDL scripts in `data/ddl/`
- **Output**: Database `healthcare_analytics` with schemas `dim`, `fact`, `staging`, `audit`, `meta`

## Failure Modes
- Port conflict: change `5432:5432` in docker-compose.yml
- Init script error: check `docker logs hc-postgres`
