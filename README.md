
# Universal Data Connector

A production-quality **Universal Data Connector** built with FastAPI that provides a unified interface for an LLM to access different data sources through function calling. Responses are optimised for voice conversations with automatic pagination, business-rule filtering, and contextual summaries.

---

<img width="1597" height="660" alt="image" src="https://github.com/user-attachments/assets/c6f22d41-e4df-4f40-8cd6-c8388c59affe" />


## Features

- **3 Data Connectors** — CRM customers, support tickets, and analytics metrics
- **Intelligent Filtering** — per-source query parameters (status, priority, search, date range)
- **Business Rules Engine** — voice-friendly pagination, result limiting, context messages
- **Voice Optimization** — summaries, freshness indicators, follow-up suggestions
- **LLM Function-Calling Schemas** — `GET /schema/functions` returns tool definitions compatible with OpenAI/Anthropic
- **Auto-generated Docs** — Swagger UI at `/docs`, ReDoc at `/redoc`
- **Comprehensive Tests** — connectors, services, and full API integration tests
- **Docker Ready** — single-command deployment

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Local Development

```bash
# 1. Clone the repository
git clone <repo-url>
cd universal-data-connector

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment config (optional)
copy .env.example .env

# 5. Run the server
uvicorn app.main:app --reload
```

Visit: **http://localhost:8000/docs** for the interactive API documentation.

### Docker

```bash
docker-compose up --build
```

Visit: **http://localhost:8000/docs**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check with uptime, version, data source status |
| `GET` | `/data/sources` | List all available data sources |
| `GET` | `/data/{source}` | Query a data source with filters and pagination |
| `GET` | `/schema/functions` | LLM function-calling tool definitions |
| `GET` | `/docs` | Swagger UI (auto-generated) |
| `GET` | `/redoc` | ReDoc documentation |

### Query Parameters for `/data/{source}`

| Parameter | Type | Description | Sources |
|-----------|------|-------------|---------|
| `voice_mode` | bool | Enable voice-optimised responses (default: true) | All |
| `page` | int | Page number, 1-based (default: 1) | All |
| `page_size` | int | Items per page, 1-100 (default: 10) | All |
| `sort_by` | string | Field to sort by | All |
| `sort_order` | string | `asc` or `desc` (default: desc) | All |
| `status` | string | `active`/`inactive` (CRM) or `open`/`closed` (Support) | CRM, Support |
| `customer_id` | int | Filter by customer ID | CRM, Support |
| `search` | string | Free-text search on name/email | CRM |
| `priority` | string | `high`, `medium`, or `low` | Support |
| `metric` | string | Metric name (e.g. `daily_active_users`) | Analytics |
| `date_from` | string | Start date YYYY-MM-DD (inclusive) | Analytics |
| `date_to` | string | End date YYYY-MM-DD (inclusive) | Analytics |

---

## Example Queries

```bash
# Health check
curl http://localhost:8000/health

# List sources
curl http://localhost:8000/data/sources

# CRM – active customers (voice mode)
curl "http://localhost:8000/data/crm?status=active&voice_mode=true"

# Support – open high-priority tickets
curl "http://localhost:8000/data/support?status=open&priority=high"

# Analytics – last 7 days
curl "http://localhost:8000/data/analytics?date_from=2026-02-10&date_to=2026-02-16"

# Pagination
curl "http://localhost:8000/data/crm?page=2&page_size=5"

# LLM function schemas
curl http://localhost:8000/schema/functions
```

---

## Architecture

```
universal-data-connector/
├── app/
│   ├── main.py                 # FastAPI entry point (CORS, lifespan, error handler)
│   ├── config.py               # Pydantic-settings configuration
│   ├── models/
│   │   ├── common.py           # DataResponse envelope, Metadata, DataType enum
│   │   ├── crm.py              # Customer model
│   │   ├── support.py          # SupportTicket model
│   │   └── analytics.py        # AnalyticsMetric / AnalyticsSummary models
│   ├── connectors/
│   │   ├── base.py             # Abstract BaseConnector with schema generation
│   │   ├── crm_connector.py    # CRM filtering: status, customer_id, search
│   │   ├── support_connector.py# Support filtering: status, priority, customer_id
│   │   └── analytics_connector.py # Analytics filtering: metric, date range
│   ├── services/
│   │   ├── data_identifier.py  # Heuristic data-type classifier
│   │   ├── business_rules.py   # Pagination, voice limits, context messages
│   │   └── voice_optimizer.py  # Summaries, freshness, follow-up suggestions
│   ├── routers/
│   │   ├── health.py           # Rich health check endpoint
│   │   └── data.py             # /data/{source}, /data/sources, /schema/functions
│   └── utils/
│       ├── logging.py          # Structured logging configuration
│       └── mock_data.py        # Random data generators with CLI
├── tests/
│   ├── test_connectors.py      # Connector unit tests
│   ├── test_business_rules.py  # Service unit tests
│   └── test_api.py             # API integration tests
├── data/
│   ├── customers.json          # 50 CRM customer records
│   ├── support_tickets.json    # 50 support tickets
│   └── analytics.json          # 30 days of DAU metrics
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── SUMMARY.md
└── README.md
```

---

## Running Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

---

## Generating Mock Data

```bash
python -m app.utils.mock_data             # default: 50 records
python -m app.utils.mock_data --count 100 # custom count
```

---

## Configuration

All settings can be overridden via environment variables or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Universal Data Connector | Application name |
| `APP_VERSION` | 1.0.0 | Displayed in health check |
| `DEBUG` | false | Show detailed errors |
| `DATA_DIR` | `./data` | Path to JSON data files |
| `MAX_RESULTS` | 10 | Max items per page (voice mode) |
| `DEFAULT_PAGE_SIZE` | 10 | Default page size |
| `DEFAULT_VOICE_MODE` | true | Voice mode on by default |
| `LOG_LEVEL` | INFO | Logging verbosity |

---

## Design Decisions

1. **Connector abstraction** — `BaseConnector` enforces a consistent interface so adding a new data source requires only one new class.
2. **Voice-first defaults** — Results are capped at 10 and include spoken summaries because the primary consumer is a voice AI assistant.
3. **LLM schema endpoint** — `/schema/functions` returns tool definitions that LLMs can use for function calling without any custom integration code.
4. **Business rules as a service** — Pagination and limiting logic lives in `BusinessRulesEngine`, separate from connectors, so rules can evolve independently.
5. **Consistent response envelope** — Every endpoint returns a `DataResponse` with `success`, `data`, and `metadata` so the LLM never has to guess the shape.
