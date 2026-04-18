# AMZN Stock Tracker

A responsive, real-time stock dashboard focused on **Amazon (AMZN)**—built so you can open it on your **phone or desktop** and check your largest holding whenever you want. The UI surfaces live price, intraday charting, and configurable alerts, backed by a **FastAPI** service and **WebSocket** streaming.

---

## Why this project

Amazon is my most invested position. I wanted a **single-purpose web app** I could trust for a quick read on price, daily change, and context—without wading through a full brokerage UI.

Along the way I focused on three learning goals:

1. **Deploy a Python API** to a server (container-friendly FastAPI, long-lived WebSocket connections, scheduled polling).
2. **Ship the frontend on Vercel** (Next.js, environment-based API URLs, HTTPS).
3. **Use WebSockets end-to-end** for push-style updates after an initial REST load.

---

## What it does

- **Live dashboard** — Current price, open, daily % change, volume; market cap and P/E when Yahoo’s quote API returns them (cloud IPs can be rate-limited; the UI falls back to intraday-derived figures when needed).
- **Intraday chart** — Recharts area chart with the same interval as the backend (`5m` by default).
- **Alerts** — Optional absolute price and % move-from-open thresholds; surfaced in-app and over the socket (once per day per alert type).
- **Health & docs** — `GET /health` for uptime checks; FastAPI auto-docs at `/docs`.

---

## Architecture

```text
┌─────────────┐     HTTPS / WSS      ┌──────────────────┐
│   Browser   │ ◄──────────────────► │  FastAPI (API)   │
│  (Vercel)   │   REST + WebSocket   │  APScheduler     │
└─────────────┘                      │  yfinance        │
       │                             └────────┬─────────┘
       │                                      │
       └──────── Next.js static / SSR ─────────┘
                 (NEXT_PUBLIC_* → your API host)
```

- **Backend** polls Yahoo Finance via **yfinance** on a schedule, broadcasts **quotes** and **alerts** to connected WebSocket clients, and serves **REST** for initial load and tooling.
- **Frontend** hydrates from `/metrics` and `/history`, then stays in sync over **`/ws`**.

---

## Tech stack

| Layer | Technologies |
|--------|----------------|
| **Frontend** | [Next.js](https://nextjs.org/) 16, [React](https://react.dev/) 19, [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/) v4, [Recharts](https://recharts.org/), [Zustand](https://github.com/pmndrs/zustand) |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [APScheduler](https://apscheduler.readthedocs.io/), [Pydantic](https://docs.pydantic.dev/) v2, [yfinance](https://github.com/ranaroussi/yfinance), [tenacity](https://tenacity.readthedocs.io/) (retries) |
| **Real-time** | Native WebSockets (`/ws`), broadcast from scheduled poll cycle |
| **Packaging** | Backend: [uv](https://docs.astral.sh/uv/) + `pyproject.toml`; Frontend: `npm` |
| **Containers** | [Docker](https://www.docker.com/) Compose for local full-stack runs |

---

## Prerequisites

- **Python** 3.12+ with [uv](https://docs.astral.sh/uv/)
- **Node.js** 22+
- **Optional:** Docker + Docker Compose for a one-command stack

---

## Local development

**1. Backend** (terminal 1):

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**2. Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** in the browser.  
Use **localhost**, not the container hostname printed in Docker logs.

### Docker (full stack)

```bash
docker compose up --build
```

Same URLs: app at port **3000**, API at **8000**.

---

## Deployment notes

**Frontend (Vercel)**  
Set environment variables for **production** builds (they are inlined at build time):

| Variable | Example | Purpose |
|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | `https://api.yourdomain.com` | REST base URL (**https**) |
| `NEXT_PUBLIC_WS_URL` | `wss://api.yourdomain.com/ws` | WebSocket (**wss** on HTTPS sites) |

Redeploy after changing `NEXT_PUBLIC_*` values.

**Backend (your server)**  
Run the FastAPI app behind a process manager or container; terminate TLS at a reverse proxy if needed. Update **`CORS_ORIGINS`** in `backend/.env` to include your Vercel URL (e.g. `https://your-app.vercel.app`). Ensure the host running yfinance can reach Yahoo (some cloud IPs see stricter rate limits—`/history` may succeed when full quote metadata is throttled).

---

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service metadata and pointers to UI/docs |
| `/metrics` | GET | Latest quote (price, change, fundamentals when available) |
| `/history` | GET | Intraday series (`?interval=5m&period=1d`) |
| `/ws` | WebSocket | Streaming quotes and alerts |
| `/health` | GET | Liveness check |
| `/docs` | GET | OpenAPI (Swagger UI) |

---

## Configuration

**`backend/.env`**

| Variable | Default | Description |
|----------|---------|-------------|
| `TICKER` | `AMZN` | Symbol to track |
| `POLL_INTERVAL_SECONDS` | `60` | Poll + broadcast interval |
| `DATA_INTERVAL` | `5m` | Intraday bar size for history |
| `ALERT_PRICE_THRESHOLD` | `267.00` | Absolute price alert |
| `ALERT_MOVE_THRESHOLD_PCT` | `3.0` | % move from daily open |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |

**`frontend/.env.local`** (local overrides)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend REST origin |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000/ws` | WebSocket URL |

---

## Disclaimer

Market data is provided via **yfinance** (Yahoo) for educational and personal use only. This is **not** financial advice.
