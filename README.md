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
            SQL["SQL Agent\nLLM builds Cube.js JSON query\nFalls back to keyword rules\nFixes date ranges automatically"]
            Graph["Graph Agent\nNeo4j Cypher executor\nReferral network traversal\nKOL influence scoring"]
            RAG["RAG Agent\nChromaDB cosine search\nPolicy + glossary retrieval\nTop-3 chunk context"]
        end

        Validation["Validation Agent\nCube schema guardrails\nPrompt injection detection\nAPI error passthrough"]
        Response["Response Agent\nCerebras gpt-oss-120b synthesis\nExecutive Summary format\nSource attribution + confidence"]

        API --> Intent
        Intent --> Planner
        Planner --> SQL
        Planner --> Graph
        Planner --> RAG
        SQL --> Validation
        Graph --> Validation
        RAG --> Validation
        Validation --> Response
    end

    subgraph DataLayer ["Data Layer"]
        direction LR
        Cube["Cube.js v0.35\nSemantic Layer\nPre-aggregations\nGoverned metrics registry"]
        PG[("PostgreSQL 15\ndim schema: HCP, Product, Territory\nfact schema: Sales, Rx, Interactions\n1,000 HCPs / 125K fact rows")]
        Neo4j[("Neo4j 5.x\nHCP referral graph\nSalesRep visit graph\nProduct prescription graph")]
        Chroma[("ChromaDB\nRAG collections: glossary / compliance / segmentation\n7 policy documents / 60+ chunks")]
        LLM["Cerebras API\ngpt-oss-120b\n5-key rotation pool\nExponential backoff on 429"]
    end

    SQL -->|"Cube REST API\n/cubejs-api/v1/load"| Cube
    Cube --> PG
    Graph -->|"Bolt bolt://localhost:7687"| Neo4j
    RAG -->|"Cosine similarity search"| Chroma
    Response -->|"LLM synthesis"| LLM
    Response -->|LLM synthesis| LLM

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
| Analytical DB | PostgreSQL | Star schema: HCPs, sales, prescriptions, territories |
| Graph DB | Neo4j | HCP referral networks, influence mapping |
| Vector DB | ChromaDB | RAG knowledge retrieval: policies, glossary, FAQ |
| LLM | Cerebras API | Intent classification, query generation, response synthesis |

---

## Agent Pipeline

```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant I as Intent Agent
    participant P as Planner
    participant S as SQL Agent
    participant G as Graph Agent
    participant R as RAG Agent
    participant V as Validation
    participant Res as Response Agent
    participant LLM as Cerebras LLM

    U->>A: "Show top cardiologists in Bangalore by Rx"
    A->>I: classify intent + extract entities
    I->>LLM: intent classification prompt
    LLM-->>I: analytics, {specialty: Cardiology, city: Bangalore}
    I->>P: intent=analytics, entities
    P->>S: build Cube query
    S->>LLM: Cube schema + question
    LLM-->>S: valid Cube JSON query
    S->>Cube.js: execute query
    Cube.js-->>S: 10 rows of HCP performance data
    S->>V: query_results
    V-->>V: schema validation pass
    V->>Res: state with results
    Res->>LLM: executive summary prompt + data
    LLM-->>Res: structured answer
    Res-->>A: final_answer + sources + confidence
    A-->>U: Executive Summary response
```

---

## Data Model

```mermaid
erDiagram
    HCP_MASTER {
        string hcp_id PK
        string specialty
        string tier
        float segmentation_score
        boolean is_kol
        int referral_count
        string city
    }
    PRODUCT_MASTER {
        string product_id PK
        string product_name
        string therapeutic_area
    }
    TERRITORY_MASTER {
        string territory_id PK
        string territory_name
        string region
    }
    SALES_FACT {
        date sale_date
        string hcp_id FK
        string product_id FK
        string territory_id FK
        float net_sales
        int units_sold
    }
    PRESCRIPTION_FACT {
        date rx_date
        string hcp_id FK
        string product_id FK
        int rx_count
        int new_rx_count
    }

    HCP_MASTER ||--o{ SALES_FACT : "attributed to"
    HCP_MASTER ||--o{ PRESCRIPTION_FACT : "written by"
    PRODUCT_MASTER ||--o{ SALES_FACT : "sold as"
    PRODUCT_MASTER ||--o{ PRESCRIPTION_FACT : "prescribed as"
    TERRITORY_MASTER ||--o{ SALES_FACT : "sold in"
```

---

## RAG Knowledge Base

Documents ingested into ChromaDB at startup:

| Collection | Document | Coverage |
|---|---|---|
| glossary | business_glossary.md | KPIs, tier definitions, metric formulas |
| glossary | faq.md | General platform Q&A |
| glossary | analytics_definitions.md | All Cube measures and dimensions explained |
| glossary | common_business_questions.md | 30+ canonical Q&A pairs with real data |
| compliance | pharma_compliance_policy.md | Off-label, SOPs, promotional rules |
| compliance | hcp_tier_rules.md | Gold/Silver/Bronze classification criteria |
| segmentation | call_planning_sop.md | Visit frequency, priority logic |

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
# Edit .env — add CEREBRAS_API_KEYS as a comma-separated pool of gpt-oss-120b keys
```

### 2. Start Docker (Postgres, Cube, Redis, Neo4j)

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

### 3. Generate and load data

```bash
cd data\seed
pip install -r requirements.txt
python generate_synthetic_data.py
python load_to_postgres.py
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
cd ..\..
pip install -r backend\requirements.txt
$env:PYTHONPATH = "C:\Users\YourUser\rags"
python backend\scripts\ingest_rag.py
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
