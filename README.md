# PulseIQ — Healthcare GenAI Analytics Copilot

PulseIQ is a production-grade, enterprise analytics copilot for pharmaceutical and healthcare commercial teams. It connects governed sales data, prescriber networks, and compliance knowledge into a single natural-language interface powered by a multi-agent LangGraph pipeline.

---

## Architecture Overview

```mermaid
flowchart TD
    User([User - Field Rep / Manager / Analyst])
    UI[Next.js Frontend\nChat + Dashboard]

    User -->|Natural language question| UI
    UI -->|POST /api/v1/chat| API

    subgraph Backend [FastAPI Backend - LangGraph Pipeline]
        direction TB
        API[Chat API\nbackend/api/v1/chat.py]
        Intent[Intent Agent\nClassifies: analytics / graph / knowledge / hybrid]
        Planner[Query Planner\nBuilds execution plan]
        SQL[SQL Agent\nLLM-powered Cube.js query builder]
        Graph[Graph Agent\nNeo4j Cypher query executor]
        RAG[RAG Agent\nChromaDB semantic retrieval]
        Validation[Validation Agent\nGuardrails - schema + injection check]
        Response[Response Agent\nStructured executive summary synthesis]

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

    subgraph DataLayer [Data Layer]
        Cube[Cube.js Semantic Layer\nPre-aggregations + governed metrics]
        PG[(PostgreSQL\ndim + fact schemas\n1,000 HCPs / 125K rows)]
        Neo4j[(Neo4j Graph DB\nReferral networks\nHCP influence maps)]
        Chroma[(ChromaDB\nRAG knowledge base\nPolicies + glossary)]
        LLM[Cerebras LLM API\n5-key rotation pool\nllama-3.3-70b]
    end

    SQL -->|Cube REST API| Cube
    Cube --> PG
    Graph -->|Bolt protocol| Neo4j
    RAG -->|Embedding search| Chroma
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
cp .env.example .env
# Edit .env and add your CEREBRAS_API_KEYS (comma-separated pool)
```

### 2. Start infrastructure

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

### 3. Load data

```bash
cd data/seed
python generate_synthetic_data.py
python load_to_postgres.py

cd ../neo4j
python load_graph.py
```

### 4. Ingest RAG knowledge

```bash
python -c "
import sys; sys.path.insert(0, '.')
from backend.rag.chroma_client import chroma_rag
chroma_rag.ingest_all(force=True)
"
```

### 5. Start Cube.js

```bash
cd cube
npm install
npm run dev
```

### 6. Start backend

```bash
pip install -r backend/requirements.txt
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
