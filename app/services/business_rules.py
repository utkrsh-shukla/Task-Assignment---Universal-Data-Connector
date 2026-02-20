"""Business rules engine — pagination, limiting, context messages."""

import math, logging
from typing import Any, Dict, List, Tuple

from app.config import settings
from app.models.common import PaginationInfo

logger = logging.getLogger(__name__)


class BusinessRulesEngine:
    def __init__(self, max_results: int = None, default_page_size: int = None):
        self.max_results = max_results or settings.MAX_RESULTS
        self.default_page_size = default_page_size or settings.DEFAULT_PAGE_SIZE

    def apply(self, records: List[Dict[str, Any]], page: int = 1,
              page_size: int = None, voice_mode: bool = True
              ) -> Tuple[List[Dict[str, Any]], PaginationInfo, str]:
        page_size = min(page_size or self.default_page_size, self.max_results)
        total = len(records)
        total_pages = max(1, math.ceil(total / page_size))
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        page_records = records[start:start + page_size]

        pagination = PaginationInfo(
            current_page=page, page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages, has_previous=page > 1,
        )

        if total == 0:
            msg = "No results found."
        elif len(page_records) == total:
            msg = f"Showing all {total} results."
        else:
            msg = f"Showing {len(page_records)} of {total} results (page {page}/{total_pages})."

        return page_records, pagination, msg
