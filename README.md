# PulseIQ — Healthcare GenAI Analytics Copilot

PulseIQ is a production-grade, enterprise analytics copilot for pharmaceutical and healthcare commercial teams. It connects governed sales data, prescriber networks, and compliance knowledge into a single natural-language interface powered by a multi-agent LangGraph pipeline.

---

## Architecture Overview

```mermaid
flowchart TD
    User(["User\nField Rep / Manager / Analyst / Med Affairs"])
    UI["Next.js 14 Frontend\nChat Interface + Live Dashboard\nRole-based views + Recharts"]

    User -->|"Natural language question"| UI
    UI -->|"POST /api/v1/chat\nJSON body: question + role"| API

    subgraph Backend ["FastAPI Backend — LangGraph Multi-Agent Pipeline"]
        direction TB
        API["Chat API\nbackend/api/v1/chat.py\nRequest validation + session routing"]
        Intent["Intent Agent\nClassifies: analytics / graph / knowledge / hybrid\nExtracts: city, specialty, tier, hcp_name, metric, limit"]
        Planner["Query Planner\nBuilds ordered execution plan\nRoutes to one or more agent nodes"]

        subgraph Agents ["Parallel Agent Nodes"]
            direction LR
            SQL["SQL Agent\nLLM builds Cube.js JSON query"]
            Graph["Graph Agent\nNeo4j Cypher executor"]
            RAG["RAG Agent\nChromaDB cosine search"]
            Catalog["Catalog Agent\nMetadata and schema search"]
        end

        Aggregator["Result Aggregator\nMerges parallel outputs safely"]
        Validation["Validation Agent\nCube schema guardrails"]
        Visualization["Visualization Agent\nDetermines React chart types"]
        Response["Response Agent\nGemini 1.5 Flash synthesis\nExecutive Summary format"]
        Evaluation["Evaluation Agent\nLLM-as-a-judge scoring"]

        API --> Intent
        Intent --> Planner
        Planner --> SQL
        Planner --> Graph
        Planner --> RAG
        Planner --> Catalog
        SQL --> Aggregator
        Graph --> Aggregator
        RAG --> Aggregator
        Catalog --> Aggregator
        Aggregator --> Validation
        Validation --> Visualization
        Visualization --> Response
        Response --> Evaluation
    end

    subgraph DataLayer ["Data Layer"]
        direction LR
        Cube["Cube.js v0.35\nSemantic Layer\nPre-aggregations"]
        PG[("PostgreSQL 15\n22 Payer360 Tables\nPSU Claims, Sales, LAAD\nMCO Profiles & Formularies")]
        Neo4j[("Neo4j 5.x\nMCO Hierarchies\nSubsidiary mappings")]
        Chroma[("ChromaDB\nPayer360 Data Dictionary\nGlossary, Rules, FAQs")]
        LLM["Google Gemini API\ngemini-1.5-flash\nDirect API integration"]
    end

    SQL -->|"Cube REST API\n/cubejs-api/v1/load"| Cube
    Cube --> PG
    Graph -->|"Bolt bolt://localhost:7687"| Neo4j
    RAG -->|"Cosine similarity search"| Chroma
    Catalog -->|"Semantic match"| Chroma
    Response -->|"LLM synthesis"| LLM

    Response --> API
    API -->|JSON answer + sources| UI
```

---

## System Components

| Component | Technology | Purpose |
|---|---|---|
| Frontend | Next.js 14, Recharts, Framer Motion | Chat interface, live dashboard, role-based views |
| API Layer | FastAPI, LangGraph | Multi-agent orchestration pipeline |
| Semantic Layer | Cube.js | Governed metrics, pre-aggregations, REST API |
| Analytical DB | PostgreSQL | 22 Payer360 tables: PSU Claims, Sales, LAAD, Formulary |
| Graph DB | Neo4j | MCO Hierarchies, parent/child mapping |
| Vector DB | ChromaDB | RAG knowledge retrieval: Data Dictionary schemas and rules |
| LLM | Google Gemini API | Intent classification, query generation, response synthesis |

---

## Agent Pipeline

```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant I as Intent Agent
    participant P as Planner
    participant S as SQL Agent
    participant Agg as Aggregator
    participant Res as Response Agent
    participant LLM as Gemini LLM

    U->>A: "What is the market share by patient counts?"
    A->>I: classify intent + extract entities
    I->>LLM: intent classification prompt
    LLM-->>I: analytics, {metric: market share}
    I->>P: intent=analytics, entities
    P->>S: build Cube query
    S->>LLM: Cube schema + question
    LLM-->>S: valid Cube JSON query
    S->>Cube.js: execute query
    Cube.js-->>S: Rows of PSU Claims data
    S->>Agg: query_results
    Agg->>Res: merged state with results
    Res->>LLM: executive summary prompt + data
    LLM-->>Res: structured answer
    Res-->>A: final_answer + sources + confidence
    A-->>U: Executive Summary response
```

---

## Data Model

```mermaid
erDiagram
    MCO_PROFILE {
        string mdm_mco_id PK
        string mdm_mco_name
        string mdm_book_of_business
    }
    FORMULARY_ROLLUP {
        string payer_360_hashkey PK
        string mdm_mco_id FK
        string product_brand_name
        string access_position
    }
    PSU_CLAIMS {
        string psu_claim_id PK
        string mdm_mco_id FK
        int patient_count
    }
    SALES {
        string sale_id PK
        string mdm_mco_id FK
        float sale_amount_usd
    }

    MCO_PROFILE ||--o{ FORMULARY_ROLLUP : "determines access"
    MCO_PROFILE ||--o{ PSU_CLAIMS : "covers patients in"
    MCO_PROFILE ||--o{ SALES : "drives sales via"
```

---

## RAG Knowledge Base

Documents ingested into ChromaDB at startup:

| Collection | Document | Coverage |
|---|---|---|
| glossary | payer360_glossary.md | 1300+ Column definitions |
| glossary | payer360_faq.md | 14 Q&A pairs from data dictionary |
| glossary | payer360_tables.md | 29 Tables defined |
| compliance | payer360_business_rules.md | Core logic for LAAD, Sales, etc. |
| compliance | payer360_things_to_know.md | 1000+ caveats and rules |
| catalog | payer360_catalog.md | Semantic column search |

---

## Setup

### Prerequisites

- Docker Desktop
- Python 3.12
- Node.js 20
- PostgreSQL (via Docker)
- Neo4j (via Docker)

### 1. Environment

```bash
copy .env.example .env
# Edit .env — add GEMINI_API_KEY with your Google Gemini key
```

### 2. Start Docker (Postgres, Cube, Redis, Neo4j)

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

### 3. Generate and load data

```bash
python scripts\generate_full_synthetic_db.py
python scripts\load_payer360_to_postgres.py
```

### 4. Verify Cube

```bash
cd ..\..
python scripts\test_cube.py
```

### 5. Load Neo4j graph

```bash
cd data\neo4j
pip install -r requirements.txt
python load_graph.py
```

### 6. Start backend

```bash
pip install -r backend\requirements.txt
$env:PYTHONPATH = "C:\Users\YourUser\rags"
python scripts\extract_payer360_rag.py
uvicorn backend.main:app --reload --port 8000
```

### 7. Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## Endpoints

| URL | Purpose |
|---|---|
| http://localhost:4000 | Cube Playground |
| http://localhost:8000/docs | FastAPI interactive docs |
| http://localhost:8000/api/v1/health/cube | Cube health check |
| http://localhost:8000/api/v1/health/neo4j | Neo4j health check |
| http://localhost:8000/api/v1/health/rag | ChromaDB RAG health check |
| POST /api/v1/chat | Full LangGraph agent pipeline |

### Sample chat request

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Show top 10 cardiologists in Bangalore by prescription volume", "role": "sales_rep"}'
```

---

## Project Structure

```
rags/
  backend/
    agents/          LangGraph agent nodes (intent, sql, graph, rag, response, validation)
    api/             FastAPI routers
    prompts/         LLM system prompts
    rag/             ChromaDB client and chunker
    semantic/        Cube.js client and metric registry
    utils/           LLM key rotation client, config
  cube/
    model/           Cube.js schema files (SalesFact, HcpMaster, etc.)
  data/
    rag/glossary/    Knowledge base markdown documents
    seed/            Synthetic data generator and PostgreSQL loader
    neo4j/           Neo4j graph loader
  frontend/
    app/             Next.js pages (dashboard, chat, landing)
    components/      UI components (charts, chat, dashboard)
    lib/             API client, role definitions
  infrastructure/
    docker/          docker-compose.yml
```

---

## License

MIT
