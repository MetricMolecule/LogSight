# FDD-001 — Log Ingestion API

## Goal

Accept structured log events from clients.

---

## Endpoint

POST /logs

---

## Input

{
    service,
    level,
    message,
    timestamp,
    metadata
}

---

## Validation

- service -> string
- level -> enum
- message -> string
- timestamp -> datetime
- metadata -> JSON object

---

## Output

202 Accepted

{
    status: accepted
}

---

## Future Work

Instead of returning immediately,
publish the log into Redis Streams.