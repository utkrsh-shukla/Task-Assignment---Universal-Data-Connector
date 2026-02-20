"""CRM data connector — customers with status/search/customer_id filtering."""

import logging
from typing import Any, Dict, List
from app.connectors.base import BaseConnector
from app.models.common import DataType

logger = logging.getLogger(__name__)


class CRMConnector(BaseConnector):
    source_name = "crm"
    description = "Retrieve CRM customer data with optional filters."
    data_type = DataType.TABULAR

    def fetch(self, **filters) -> List[Dict[str, Any]]:
        records = self._load_json("customers.json")

        if status := filters.get("status"):
            records = [r for r in records if r.get("status", "").lower() == status.lower()]

        if cid := filters.get("customer_id"):
            records = [r for r in records if str(r.get("customer_id")) == str(cid)]

        if search := filters.get("search"):
            term = search.lower()
            records = [r for r in records
                       if term in r.get("name", "").lower()
                       or term in r.get("email", "").lower()]

        # Sort by created_at desc
        sort_field = filters.get("sort_by", "created_at")
        sort_order = filters.get("sort_order", "desc")
        records.sort(key=lambda r: r.get(sort_field, ""), reverse=(sort_order == "desc"))

        logger.info("CRM fetch: %d results (filters=%s)", len(records), filters)
        return records

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "status": {"type": "string", "description": "Filter by status", "enum": ["active", "inactive"]},
            "customer_id": {"type": "integer", "description": "Filter by customer ID"},
            "search": {"type": "string", "description": "Search name or email"},
            "sort_by": {"type": "string", "description": "Sort field", "default": "created_at"},
            "sort_order": {"type": "string", "description": "Sort direction", "enum": ["asc", "desc"]},
        }
