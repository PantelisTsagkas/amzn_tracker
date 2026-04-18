import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.models.schemas import WSMessage, WSMessageType
from app.routes.metrics import router as metrics_router
from app.routes.websocket import manager, router as ws_router
from app.services.alerts import AlertService
from app.services import stock

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

alert_service = AlertService()


async def poll_and_broadcast() -> None:
    """Scheduled job: fetch latest quote, check alerts, broadcast to WS clients."""
    try:
        quote = await stock.fetch_quote(settings.ticker)
        logger.info(
            "%s  $%.2f  %+.2f%%  [%d clients]",
            quote.ticker, quote.price, quote.change_pct, manager.client_count,
        )

        await manager.broadcast(WSMessage(type=WSMessageType.QUOTE, payload=quote))

        alerts = alert_service.check(quote, settings)
        for alert in alerts:
            await manager.broadcast(WSMessage(type=WSMessageType.ALERT, payload=alert))

    except Exception:
        logger.exception("Error during poll cycle")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fire one poll immediately so REST + first WS clients have data
    await poll_and_broadcast()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        poll_and_broadcast,
        "interval",
        seconds=settings.poll_interval_seconds,
        id="stock_poll",
        max_instances=1,
    )
    scheduler.start()
    logger.info(
        "Scheduler started — polling %s every %ds",
        settings.ticker, settings.poll_interval_seconds,
    )
    yield
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")


app = FastAPI(
    title="AMZN Stock Tracker",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    """Avoid a bare 404 when someone opens the API base URL (e.g. after `docker compose up`)."""
    return {
        "service": "amzn-tracker-api",
        "ui": "http://localhost:3000",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
