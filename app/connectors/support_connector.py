"""Support ticket connector — filtering by status/priority/customer_id."""

import logging
from typing import Any, Dict, List
from app.connectors.base import BaseConnector
from app.models.common import DataType

logger = logging.getLogger(__name__)

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


class SupportConnector(BaseConnector):
    source_name = "support"
    description = "Retrieve support tickets with optional filters."
    data_type = DataType.TABULAR

    def fetch(self, **filters) -> List[Dict[str, Any]]:
        records = self._load_json("support_tickets.json")

        if status := filters.get("status"):
            records = [r for r in records if r.get("status", "").lower() == status.lower()]

        if priority := filters.get("priority"):
            records = [r for r in records if r.get("priority", "").lower() == priority.lower()]

        if cid := filters.get("customer_id"):
            records = [r for r in records if str(r.get("customer_id")) == str(cid)]

        sort_field = filters.get("sort_by", "priority")
        sort_order = filters.get("sort_order", "desc")

        if sort_field == "priority":
            records.sort(key=lambda r: PRIORITY_ORDER.get(r.get("priority", "low"), 99),
                         reverse=(sort_order == "desc"))
        else:
            records.sort(key=lambda r: r.get(sort_field, ""), reverse=(sort_order == "desc"))

        logger.info("Support fetch: %d results (filters=%s)", len(records), filters)
        return records

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "status": {"type": "string", "description": "Filter by status", "enum": ["open", "closed"]},
            "priority": {"type": "string", "description": "Filter by priority", "enum": ["high", "medium", "low"]},
            "customer_id": {"type": "integer", "description": "Filter by customer ID"},
            "sort_by": {"type": "string", "description": "Sort field", "default": "priority"},
            "sort_order": {"type": "string", "description": "Sort direction", "enum": ["asc", "desc"]},
        }
