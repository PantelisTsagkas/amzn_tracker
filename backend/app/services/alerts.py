import logging
from datetime import datetime, timezone

from app.core.config import Settings
from app.models.schemas import AlertEvent, AlertType, StockQuote

logger = logging.getLogger(__name__)


class AlertService:
    """Stateful alert checker. Each condition fires at most once per day."""

    def __init__(self) -> None:
        self._triggered: set[str] = set()

    def reset_daily(self) -> None:
        logger.info("Resetting daily alert state (%d alerts were triggered)", len(self._triggered))
        self._triggered.clear()

    def check(self, quote: StockQuote, config: Settings) -> list[AlertEvent]:
        alerts: list[AlertEvent] = []
        now = datetime.now(timezone.utc)

        pct_key = f"{quote.ticker}:pct_move"
        if pct_key not in self._triggered and abs(quote.change_pct) >= config.alert_move_threshold_pct:
            event = AlertEvent(
                alert_type=AlertType.PCT_MOVE,
                message=(
                    f"{quote.ticker} moved {quote.change_pct:+.2f}% from daily open "
                    f"(threshold: {config.alert_move_threshold_pct}%)"
                ),
                price=quote.price,
                ticker=quote.ticker,
                triggered_at=now,
            )
            self._triggered.add(pct_key)
            alerts.append(event)
            logger.warning("ALERT: %s", event.message)

        price_key = f"{quote.ticker}:price_threshold"
        if price_key not in self._triggered and quote.price >= config.alert_price_threshold:
            event = AlertEvent(
                alert_type=AlertType.PRICE_THRESHOLD,
                message=(
                    f"{quote.ticker} reached ${quote.price:.2f} "
                    f"(threshold: ${config.alert_price_threshold:.2f})"
                ),
                price=quote.price,
                ticker=quote.ticker,
                triggered_at=now,
            )
            self._triggered.add(price_key)
            alerts.append(event)
            logger.warning("ALERT: %s", event.message)

        return alerts
