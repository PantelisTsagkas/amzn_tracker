# AMZN Stock Tracker

Real-time Amazon stock monitoring dashboard with FastAPI backend and Next.js frontend.

## Architecture

- **Backend**: FastAPI + WebSocket streaming + APScheduler (60s polling) + yfinance
- **Frontend**: Next.js 16 + React 19 + Recharts + Zustand + Tailwind CSS v4
- **Alerting**: Price threshold ($267) and % move (3%) alerts, fired once per day

## Quick Start

### Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 22+
- Or: Docker + Docker Compose

### Local Development

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

Open [http://localhost:3000](http://localhost:3000).

### Docker

```bash
docker compose up --build
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/metrics` | GET | Latest price, open, % change, market cap, P/E |
| `/history` | GET | Intraday time series (`?interval=5m&period=1d`) |
| `/ws` | WS | Live price + alert streaming |
| `/health` | GET | Health check |

## Configuration

Backend config via `backend/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `TICKER` | `AMZN` | Stock ticker symbol |
| `POLL_INTERVAL_SECONDS` | `60` | Polling frequency |
| `DATA_INTERVAL` | `5m` | yfinance intraday interval |
| `ALERT_PRICE_THRESHOLD` | `267.00` | Absolute price alert |
| `ALERT_MOVE_THRESHOLD_PCT` | `3.0` | % move from daily open |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed origins |

Frontend config via `frontend/.env.local`:

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000/ws` | WebSocket URL |
