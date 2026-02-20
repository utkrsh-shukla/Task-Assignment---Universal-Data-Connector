"""Health check router."""

import time, logging
from fastapi import APIRouter
from app.config import settings
from app.connectors import CRMConnector, SupportConnector, AnalyticsConnector

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)
_start_time = time.time()

CONNECTORS = {
    "crm": CRMConnector(),
    "support": SupportConnector(),
    "analytics": AnalyticsConnector(),
}


@router.get("/health")
async def health_check():
    uptime = time.time() - _start_time
    sources = {}
    for name, conn in CONNECTORS.items():
        try:
            count = conn.get_record_count()
            sources[name] = {"available": True, "record_count": count}
        except Exception:
            sources[name] = {"available": False, "record_count": 0}

    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "uptime_seconds": round(uptime, 2),
        "data_sources": sources,
    }
