"""Analytics connector — daily metrics with date range filtering."""

import logging
from typing import Any, Dict, List
from app.connectors.base import BaseConnector
from app.models.common import DataType

logger = logging.getLogger(__name__)


class AnalyticsConnector(BaseConnector):
    source_name = "analytics"
    description = "Retrieve analytics time-series data with optional filters."
    data_type = DataType.TIME_SERIES

    def fetch(self, **filters) -> List[Dict[str, Any]]:
        records = self._load_json("analytics.json")

        if metric := filters.get("metric"):
            records = [r for r in records if r.get("metric", "").lower() == metric.lower()]

        if date_from := filters.get("date_from"):
            records = [r for r in records if r.get("date", "") >= date_from]

        if date_to := filters.get("date_to"):
            records = [r for r in records if r.get("date", "") <= date_to]

        sort_field = filters.get("sort_by", "date")
        sort_order = filters.get("sort_order", "desc")
        records.sort(key=lambda r: r.get(sort_field, ""), reverse=(sort_order == "desc"))

        logger.info("Analytics fetch: %d results (filters=%s)", len(records), filters)
        return records

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "metric": {"type": "string", "description": "Filter by metric name"},
            "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
            "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"},
            "sort_by": {"type": "string", "description": "Sort field", "default": "date"},
            "sort_order": {"type": "string", "description": "Sort direction", "enum": ["asc", "desc"]},
        }
