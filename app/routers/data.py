"""Data router — /data/{source}, /data/sources, /schema/functions."""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.connectors.crm_connector import CRMConnector
from app.connectors.support_connector import SupportConnector
from app.connectors.analytics_connector import AnalyticsConnector
from app.models.common import DataResponse, DataSourceInfo, Metadata
from app.services.business_rules import BusinessRulesEngine
from app.services.data_identifier import identify_data_type
from app.services.voice_optimizer import VoiceOptimizer
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Data"])

_rules = BusinessRulesEngine()
_voice = VoiceOptimizer()

_CONNECTOR_MAP = {
    "crm": CRMConnector,
    "support": SupportConnector,
    "analytics": AnalyticsConnector,
}


@router.get("/data/sources", summary="List available data sources")
def list_sources():
    sources = []
    for cls in _CONNECTOR_MAP.values():
        conn = cls()
        sources.append({"name": conn.source_name, "description": conn.description,
                        "data_type": conn.data_type.value})
    return {"sources": sources}


@router.get("/data/{source}", response_model=DataResponse, summary="Query a data source",
            responses={404: {"description": "Unknown data source"}})
def get_data(
    source: str,
    voice_mode: bool = Query(True, description="Enable voice-optimised responses"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction"),
    status: Optional[str] = Query(None, description="Status filter (CRM/Support)"),
    customer_id: Optional[int] = Query(None, description="Customer ID filter"),
    search: Optional[str] = Query(None, description="CRM text search"),
    priority: Optional[str] = Query(None, description="Support priority filter"),
    metric: Optional[str] = Query(None, description="Analytics metric filter"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
):
    connector_cls = _CONNECTOR_MAP.get(source)
    if not connector_cls:
        raise HTTPException(404, f"Unknown source '{source}'. Available: {', '.join(_CONNECTOR_MAP)}")

    connector = connector_cls()
    fetch_kwargs = _build_fetch_kwargs(
        source=source, status=status, customer_id=customer_id, search=search,
        priority=priority, metric=metric, date_from=date_from, date_to=date_to,
        sort_by=sort_by, sort_order=sort_order,
    )

    raw_data = connector.fetch(**fetch_kwargs)
    total = len(raw_data)
    data_type = identify_data_type(raw_data)

    page_data, pagination, _ = _rules.apply(
        raw_data, page=page, page_size=page_size, voice_mode=voice_mode)

    voice_context = None
    if voice_mode:
        voice_context = _voice.build_voice_context(
            data=page_data, source=source, total=total, returned=len(page_data))

    filters_applied = {k: v for k, v in fetch_kwargs.items()
                       if v is not None and k not in ("sort_by", "sort_order")}

    metadata = Metadata(
        total_results=total,
        returned_results=len(page_data),
        data_type=data_type,
        data_freshness=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        source=DataSourceInfo(name=connector.source_name, description=connector.description,
                              record_count=total),
        pagination=pagination,
        voice_context=voice_context,
        filters_applied=filters_applied,
    )
    return DataResponse(success=True, data=page_data, metadata=metadata)


@router.get("/schema/functions", summary="LLM function-calling schemas")
def get_function_schemas():
    functions = [cls().get_schema() for cls in _CONNECTOR_MAP.values()]
    return {"functions": functions}


def _build_fetch_kwargs(source: str, **params) -> dict:
    source_params = {
        "crm": {"status", "customer_id", "search", "sort_by", "sort_order"},
        "support": {"status", "priority", "customer_id", "sort_by", "sort_order"},
        "analytics": {"metric", "date_from", "date_to", "sort_by", "sort_order"},
    }
    allowed = source_params.get(source, set())
    return {k: v for k, v in params.items() if k in allowed and v is not None}
