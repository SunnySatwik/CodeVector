# CodeVector — Product Catalog API

A backend API for browsing a product catalog with cursor-based pagination and snapshot consistency, built with FastAPI and PostgreSQL.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?style=flat&logo=postgresql&logoColor=white)](https://supabase.com/)

---

## Overview

CodeVector is a REST API that lets users browse a catalog of around 50,000 products stored in PostgreSQL. The main design challenge was: **how do you paginate reliably through data that might change while someone is browsing?**

Standard `OFFSET` pagination breaks down when rows are added or removed between requests — users can end up seeing duplicates or skipping products entirely. This project solves that with two design choices:

1. **Cursor-based pagination** — each page returns a cursor pointing to the last item, so the next query continues from that exact position rather than a row count.
2. **Snapshot consistency** — a timestamp is captured on the first request and reused for all subsequent pages, so the user always sees the data as it was when they started browsing.

---
## Live API

Base URL:
https://codevector-uoaj.onrender.com

Interactive API Documentation:
https://codevector-uoaj.onrender.com/docs

## Features

- Cursor-based (keyset) pagination that stays correct even when data changes
- Snapshot timestamps to give users a consistent view across pages
- Category filtering
- ~50,000 seeded products for pagination testing
- Auto-generated Swagger docs at `/docs`

---

## Architecture

| Layer | Technology | Role |
|---|---|---|
| **API Framework** | FastAPI | Handles routing, request validation, and auto-generates OpenAPI docs |
| **Database** | PostgreSQL on Supabase | Stores the product catalog |
| **ORM** | SQLAlchemy | Defines models and builds queries |
| **Driver** | psycopg2-binary | Connects Python to PostgreSQL |
| **Pagination** | Keyset / Cursor | Stable page traversal over large datasets |
| **Consistency** | Snapshot Timestamp | Filters data to a fixed point in time per session |

---

## Project Structure

```
CodeVector/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLAlchemy engine, session, and Base
│   ├── models.py                # Product model and database indexes
│   ├── schemas.py               # Pydantic response schemas
│   ├── routes/
│   │   └── products.py          # GET /products endpoint
│   ├── services/
│   │   └── pagination.py        # Cursor encode/decode helpers
│   ├── seed/
│   │   └── generate_products.py # Script to seed the database
│   └── utils/                   # Reserved for shared utilities
├── requirements.txt
├── .env                         # Not committed — see Environment Variables
├── .gitignore
└── README.md
```

---

## API Endpoints

### `GET /products`

Returns a page of products with optional category filtering and cursor-based pagination.

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | `integer` | `50` | Number of products per page |
| `category` | `string` | — | Filter by category |
| `cursor` | `string` | — | Cursor from the previous page's `next_cursor` field |
| `snapshot` | `string` | — | ISO 8601 timestamp from the first response. Pass this on every subsequent request. |

**Available categories:** `electronics`, `clothing`, `books`, `sports`, `home`, `beauty`, `toys`

---

#### Example Requests

**First page:**
```http
GET /products?limit=50
```

**First page with category filter:**
```http
GET /products?limit=50&category=electronics
```

**Next page (passing cursor and snapshot from the previous response):**
```http
GET /products?limit=50&cursor=eyJ1cGRhdGVkX2F0IjogIjIwMjYtMDYtMjNUMDU6MzM6MzQuNDQyMzk1IiwgImlkIjogMjI4Mzd9&snapshot=2026-06-23T06%3A48%3A12.346808
```

---

#### Example Response

```json
{
  "items": [
    {
      "id": 22837,
      "name": "Product 4312",
      "category": "electronics",
      "price": 4299.99,
      "created_at": "2026-01-15T10:22:00",
      "updated_at": "2026-06-23T05:33:34.442395"
    },
    {
      "id": 19504,
      "name": "Product 891",
      "category": "electronics",
      "price": 149.50,
      "created_at": "2025-12-01T08:11:00",
      "updated_at": "2026-06-23T05:31:19.001234"
    }
  ],
  "next_cursor": "eyJ1cGRhdGVkX2F0IjogIjIwMjYtMDYtMjNUMDU6MzE6MTkuMDAxMjM0IiwgImlkIjogMTk1MDR9",
  "snapshot": "2026-06-23T06:48:12.346808"
}
```

| Field | Description |
|---|---|
| `items` | Products on this page |
| `next_cursor` | Pass as `cursor` on the next request. `null` means no more pages. |
| `snapshot` | Pass as `snapshot` on every subsequent request |

---

### `GET /`

Health check.

```json
{ "message": "Backend Running" }
```

---

## Local Setup

### Prerequisites

- Python 3.11+
- Git
- A PostgreSQL database (local or Supabase)

### 1. Clone the Repository

```bash
git clone https://github.com/SunnySatwik/CodeVector.git
cd CodeVector
```

### 2. Create and Activate a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate — Windows (PowerShell)
venv\Scripts\Activate.ps1

# Activate — macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` File

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

See [Environment Variables](#environment-variables) below for details.

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### 6. Open the Swagger Docs

Go to `http://127.0.0.1:8000/docs` to explore and test the API interactively.

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Full PostgreSQL connection string — e.g. `postgresql://user:password@host:5432/dbname` |

The app uses `python-dotenv` to load this from `.env` automatically. The `.env` file is in `.gitignore` and should never be committed.

If you're using Supabase, copy the connection string from:  
*Dashboard → Project → Settings → Database → Connection String (URI mode)*

---

## Database Setup

The `products` table is created automatically when the app starts, via SQLAlchemy's `Base.metadata.create_all()`.

```sql
CREATE TABLE products (
    id         BIGSERIAL PRIMARY KEY,
    name       VARCHAR   NOT NULL,
    category   VARCHAR   NOT NULL,
    price      NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### Seeding the Database

To populate the database with ~50,000 products for testing:

```bash
python -m app.seed.generate_products
```

This inserts products in batches with randomised categories, prices, and timestamps.

---

## How Pagination Works

### The Problem with OFFSET

`OFFSET`-based pagination skips a fixed number of rows before returning results. If rows are inserted or deleted while a user is browsing, the offset shifts — products get duplicated across pages or disappear entirely. This becomes more noticeable with larger datasets and concurrent writes.

### Cursor Pagination

Instead of an offset, each page response includes a `next_cursor` — a Base64-encoded token containing the `updated_at` and `id` of the last product on that page.

```python
# Cursor payload (before encoding)
{
  "updated_at": "2026-06-23T05:33:34.442395",
  "id": 22837
}
```

The next query uses this to fetch products that come strictly after that position in the sort order `(updated_at DESC, id DESC)`:

```sql
WHERE (updated_at, id) < ('2026-06-23T05:33:34.442395', 22837)
ORDER BY updated_at DESC, id DESC
LIMIT 50
```

This is stable regardless of what's been inserted or deleted elsewhere in the table.

### Snapshot Consistency

Cursor pagination still has a subtle problem: if a product is updated after the user starts browsing, its `updated_at` changes and it could shift into a position the user has already passed — causing it to show up again on a later page.

The snapshot timestamp prevents this. On the first request (no `snapshot` param), the server captures the current UTC time and returns it in the response. Every query filters `updated_at <= snapshot`, so only products that existed before the session started are included. The user passes this same timestamp on every subsequent request.

```
Page 1: GET /products
        ← returns items + next_cursor + snapshot

Page 2: GET /products?cursor=<next_cursor>&snapshot=<snapshot>
        ← same snapshot, stable dataset

Page N: GET /products?cursor=<next_cursor>&snapshot=<snapshot>
```

---

## Design Decisions

**Why not OFFSET pagination?**  
It's simple to implement but unreliable with live data. Products can appear twice or get skipped when rows are inserted or deleted between requests. For a catalog that could change at any time, this isn't acceptable.

**Why cursor (keyset) pagination?**  
The cursor encodes a position in the sort order, not a row count. New inserts or deletes elsewhere in the table don't affect it. The queries also use `(updated_at, id)` as the sort key, which means the database can use an index to find the next page directly rather than scanning from the start.

**Why add snapshot consistency on top?**  
Cursor pagination alone doesn't account for rows that change their sort position mid-session (i.e. rows whose `updated_at` gets updated). The snapshot timestamp locks in the visible dataset at session start, so even if a product is re-indexed in the background, it won't affect the current browsing session.

---

## Future Improvements

- [ ] Async database sessions using `asyncpg` for better concurrency
- [ ] Full-text product search
- [ ] Rate limiting middleware
- [ ] Response caching for common queries
- [ ] Automatic snapshot expiry after a configurable time-to-live
- [ ] Docker Compose setup for easier local development

---

## Technologies Used

| Technology | Purpose |
|---|---|
| [Python 3.11+](https://www.python.org/) | Core language |
| [FastAPI](https://fastapi.tiangolo.com/) | API framework |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ORM and query builder |
| [PostgreSQL](https://www.postgresql.org/) | Database |
| [Supabase](https://supabase.com/) | Hosted PostgreSQL |
| [psycopg2-binary](https://pypi.org/project/psycopg2-binary/) | PostgreSQL driver |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server |
| [Faker](https://faker.readthedocs.io/) | Synthetic data for seeding |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | `.env` file loading |
