# LogSight

### Distributed Log Ingestion & Observability Platform

LogSight is a lightweight, self-hosted log ingestion and observability platform built to demonstrate a production-style asynchronous backend pipeline.

It accepts application logs over HTTP, buffers them in Redis Streams, processes them with a background worker, persists them in PostgreSQL, and pushes newly processed logs to connected dashboards over WebSockets.

**Live demo:** https://logsight-rnjc.onrender.com/  
**API documentation:** https://logsight-rnjc.onrender.com/docs

---

## What LogSight demonstrates

LogSight is intentionally built around a decoupled ingestion pipeline rather than writing directly to the database inside the HTTP request.

```text
                    ┌──────────────────────┐
                    │   Application /      │
                    │   Log Producer       │
                    └──────────┬───────────┘
                               │ HTTP POST
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │   Ingestion API      │
                    └──────────┬───────────┘
                               │ XADD
                               ▼
                    ┌──────────────────────┐
                    │   Redis Streams      │
                    │   Durable Buffer     │
                    └──────────┬───────────┘
                               │ consume
                               ▼
                    ┌──────────────────────┐
                    │   Background Worker  │
                    │   Processing Layer   │
                    └──────────┬───────────┘
                               │ persist
                               ▼
                    ┌──────────────────────┐
                    │     PostgreSQL       │
                    │ Persistent Log Store │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐         ┌──────────────────┐
        │ REST Analytics  │         │ Redis Pub/Sub    │
        │ & Log Queries   │         │ Live Events      │
        └────────┬────────┘         └────────┬─────────┘
                 │                           │
                 └─────────────┬─────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ WebSocket Dashboard  │
                    │ Live Logs + Charts   │
                    └──────────────────────┘
```

### Why this architecture?

The important design decision is **decoupling ingestion from persistence**.

A producer does not need to wait for PostgreSQL to finish writing a log. FastAPI places the event into Redis Streams and returns an accepted response. A worker consumes the stream and performs the database write separately.

This creates a clear separation between:

- **Ingestion** — FastAPI
- **Buffering / decoupling** — Redis Streams
- **Background processing** — Worker
- **Durable storage** — PostgreSQL
- **Querying / analytics** — FastAPI + PostgreSQL
- **Real-time delivery** — Redis Pub/Sub + WebSockets
- **Presentation** — Browser dashboard

---

## Features

### Log ingestion

- HTTP `POST /logs` ingestion API
- Structured log payloads
- Timestamp, service, level, message, request ID and user ID
- Redis Stream based asynchronous ingestion
- HTTP `202 Accepted` response after queueing

### Background processing

- Dedicated worker process
- Redis Stream consumption
- Database persistence outside the request path
- Separation between API availability and database processing

### Querying

- Paginated log retrieval
- Service filtering
- Log-level filtering
- Timestamp range filtering
- Ascending / descending timestamp ordering

### Real-time dashboard

- Live log updates through WebSockets
- Automatic dashboard statistics refresh
- Live log-level distribution
- Service distribution
- Hourly log volume
- Recent log table

### Analytics API

Currently exposed analytics include:

- Total logs
- Error count
- Warning count
- Number of services
- Log counts by level
- Log counts by service
- Hourly error statistics
- Hourly log volume
- Error rate
- Top services

### Deployment

- Dockerized application
- Environment-variable based configuration
- PostgreSQL-compatible deployment
- Redis-compatible deployment
- Production deployment on Render
- External PostgreSQL and Redis services

---

## Technology Stack

| Layer | Technology | Responsibility |
|---|---|---|
| API | FastAPI | HTTP ingestion, querying and analytics |
| Validation | Pydantic | Request/response schemas |
| Queue / Buffer | Redis Streams | Asynchronous log buffering |
| Worker | Python | Background log processing |
| Database | PostgreSQL | Persistent log storage |
| Real-time | Redis Pub/Sub + WebSockets | Live dashboard updates |
| Frontend | HTML, CSS, JavaScript | Dashboard UI |
| Charts | Chart.js | Analytics visualization |
| ORM | SQLAlchemy | Database access |
| Runtime | Uvicorn | ASGI application server |
| Containers | Docker / Docker Compose | Local reproducible environment |
| Deployment | Render | Public deployment |

---

## API

### Health

```http
GET /health
```

Returns:

```json
{
  "status": "ok"
}
```

### Ingest a log

```http
POST /logs
Content-Type: application/json
```

Example:

```json
{
  "timestamp": "2026-10-06T08:30:00Z",
  "service": "payment-service",
  "level": "ERROR",
  "message": "Payment gateway timeout",
  "request_id": "demo-001",
  "user_id": "user-demo",
  "metadata": {
    "gateway": "stripe",
    "retry": 2
  }
}
```

The endpoint queues the event into Redis Streams and returns:

```json
{
  "status": "accepted"
}
```

### Query logs

```http
GET /logs
```

Supported query parameters:

```text
service
level
start_time
end_time
page
limit
sort
```

Example:

```text
GET /logs?service=payment-service&level=ERROR&page=1&limit=20&sort=desc
```

### Analytics

```text
GET /analytics/levels
GET /analytics/services
GET /analytics/errors/hourly
GET /analytics/summary
GET /analytics/error-rate
GET /analytics/top-services
GET /analytics/logs/hourly
```

### WebSocket

```text
/ws/logs
```

Connected dashboards receive newly processed logs in real time.

Full interactive documentation is available at:

**https://logsight-rnjc.onrender.com/docs**

---

## Local Development

### 1. Clone

```bash
git clone https://github.com/MetricMolecule/LogSight.git
cd LogSight
```

### 2. Start the infrastructure

```bash
docker compose up -d
```

This starts:

- PostgreSQL
- Redis
- FastAPI API
- Background worker

### 3. Check service health

```bash
docker compose ps
```

Then:

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

### 4. Open the dashboard

```text
http://localhost:8000/
```

### 5. Open API documentation

```text
http://localhost:8000/docs
```

### Stop the stack

```bash
docker compose down
```

To remove the local PostgreSQL volume as well:

```bash
docker compose down -v
```

---

## Environment Variables

LogSight reads its infrastructure configuration from environment variables.

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
REDIS_URL=redis://HOST:6379/0
```

For hosted Redis providers using TLS, the Redis URL may use:

```text
rediss://...
```

See `.env.example` for the expected configuration shape.

---

## Project Structure

```text
LogSight/
├── app/
│   ├── core/
│   │   ├── database.py
│   │   ├── redis.py
│   │   ├── websocket_manager.py
│   │   └── ws_manager.py
│   │
│   ├── routers/
│   │   ├── analytics.py
│   │   ├── dashboard.py
│   │   ├── logs.py
│   │   └── ws.py
│   │
│   ├── services/
│   │   ├── analytics_service.py
│   │   ├── dashboard_service.py
│   │   └── log_service.py
│   │
│   ├── workers/
│   │   └── consumer.py
│   │
│   ├── static/
│   │   ├── app.js
│   │   ├── index.html
│   │   └── style.css
│   │
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── docs/
│   ├── architecture.md
│   ├── roadmap.md
│   └── feature_designs/
│
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Design Decisions

### Why Redis Streams?

Redis Streams provide a lightweight event-streaming mechanism without introducing the operational overhead of Kafka for a project of this size.

They allow the API to hand work to a consumer rather than coupling every ingestion request directly to PostgreSQL.

For a much larger deployment, Kafka or another distributed streaming platform would be a natural evolution.

### Why PostgreSQL?

Logs have structured fields such as service, level and timestamp, while SQL aggregation is useful for dashboard analytics.

PostgreSQL provides durable storage and straightforward filtering and aggregation.

For very high-volume log search, a dedicated system such as OpenSearch, Elasticsearch or ClickHouse could be introduced.

### Why WebSockets?

Polling the API repeatedly is wasteful for a live dashboard.

WebSockets allow the server to push newly processed logs to connected clients as events arrive.

### Why Redis Pub/Sub as well as Redis Streams?

The two Redis features have different responsibilities:

- **Redis Streams** → reliable processing pipeline
- **Redis Pub/Sub** → real-time notification to connected dashboard clients

This keeps the ingestion path and presentation path logically separate.

---

## Failure and Scaling Considerations

LogSight is intentionally a portfolio-scale system rather than a claim of Datadog-scale infrastructure.

The current architecture provides a foundation for scaling:

```text
                  Current
                    │
                    ▼
          ┌──────────────────┐
          │ FastAPI replicas │
          └────────┬─────────┘
                   ▼
            Redis Streams
                   │
          ┌────────┴────────┐
          ▼                 ▼
      Worker 1           Worker 2
          │                 │
          └────────┬────────┘
                   ▼
              PostgreSQL
```

At significantly higher volumes, the next steps would include:

- Multiple worker consumers
- Stream partitioning / Kafka
- Bulk database inserts
- Connection pooling
- PostgreSQL partitioning
- Dedicated log-search storage
- Retention policies
- Backpressure controls
- Retry and dead-letter handling
- Horizontal API scaling
- Metrics and infrastructure monitoring

The important point is that the current separation makes these future changes possible without rewriting the entire ingestion API.

---

## Testing the Pipeline

A simple test sequence is:

### 1. Send a log

```bash
curl -X POST "http://localhost:8000/logs" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-10-06T08:30:00Z",
    "service": "payment-service",
    "level": "ERROR",
    "message": "Payment gateway timeout",
    "request_id": "demo-001",
    "user_id": "user-demo",
    "metadata": {
      "gateway": "stripe",
      "retry": 2
    }
  }'
```

### 2. Query the database through the API

```bash
curl "http://localhost:8000/logs?limit=5"
```

### 3. Check analytics

```bash
curl "http://localhost:8000/analytics/summary"
```

### 4. Open the dashboard

```text
http://localhost:8000/
```

A newly processed log should appear in the dashboard through the WebSocket connection.

---

## Production Demo

The deployed version demonstrates the complete flow:

```text
POST /logs
     ↓
FastAPI
     ↓
Redis Stream
     ↓
Background Worker
     ↓
PostgreSQL
     ↓
Redis Pub/Sub
     ↓
WebSocket
     ↓
Live Dashboard
```

Live deployment:

**https://logsight-rnjc.onrender.com/**

Swagger:

**https://logsight-rnjc.onrender.com/docs**

---

## Current Scope

Implemented:

- [x] FastAPI ingestion API
- [x] Redis Stream buffering
- [x] Background worker
- [x] PostgreSQL persistence
- [x] Log querying
- [x] Filtering
- [x] Pagination
- [x] Analytics endpoints
- [x] WebSocket live updates
- [x] Dashboard charts
- [x] Docker Compose local environment
- [x] Production deployment
- [x] Health endpoint


---

## Engineering Takeaways

The project focuses on a few practical backend engineering concepts:

1. **Decoupling** — ingestion does not directly depend on database writes.
2. **Asynchronous processing** — workers handle persistence independently.
3. **Event-driven updates** — WebSockets deliver processed events to the UI.
4. **Separation of concerns** — routers, services, workers and infrastructure are separated.
5. **Containerization** — the full local stack can be reproduced with Docker Compose.
6. **Scalability thinking** — the architecture identifies clear bottlenecks and upgrade paths.

LogSight is designed to show not only that a dashboard can be built, but that the backend behind it has been structured as a small distributed system.
