"""Voice optimizer — summaries, freshness, follow-up suggestions."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.models.common import VoiceContext

logger = logging.getLogger(__name__)


class VoiceOptimizer:
    def build_voice_context(self, data: List[Dict[str, Any]],
                            source: str, total: int, returned: int) -> VoiceContext:
        return VoiceContext(
            summary=self._summarize(data, source),
            freshness=self._freshness(data),
            suggestion=self._suggest(source, total, returned),
        )

    def _summarize(self, records, source):
        n = len(records)
        if n == 0:
            return f"No {source} records found."
        method = {"crm": self._crm, "support": self._support,
                  "analytics": self._analytics}.get(source)
        return method(records) if method else f"Found {n} {source} records."

    def _crm(self, records):
        active = sum(1 for r in records if r.get("status") == "active")
        return f"Found {len(records)} customers, {active} active and {len(records)-active} inactive."

    def _support(self, records):
        open_t = sum(1 for r in records if r.get("status") == "open")
        high = sum(1 for r in records if r.get("priority") == "high")
        return f"Found {len(records)} tickets, {open_t} open, {high} high-priority."

    def _analytics(self, records):
        values = [r.get("value", 0) for r in records if "value" in r]
        if not values:
            return f"Found {len(records)} analytics records."
        return f"Found {len(records)} data points, average value {sum(values)/len(values):.1f}."

    def _freshness(self, records):
        now = datetime.now(timezone.utc)
        stamp = now.strftime("%Y-%m-%d %H:%M UTC")
        if not records:
            return f"Data as of {stamp}"
        dates = []
        for r in records:
            for key in ("created_at", "date", "timestamp"):
                if key in r:
                    try:
                        dates.append(datetime.fromisoformat(str(r[key]).replace("Z", "+00:00")))
                    except (ValueError, TypeError):
                        pass
                    break
        if not dates:
            return f"Data as of {stamp}"
        newest = max(dates)
        if newest.tzinfo is None:
            newest = newest.replace(tzinfo=timezone.utc)
        delta = (now - newest).days
        if delta == 0: return f"Data as of {stamp} (updated today)"
        if delta == 1: return f"Data as of {stamp} (updated yesterday)"
        return f"Data as of {stamp} (updated {delta} days ago)"

    def _suggest(self, source, total, returned):
        if total == 0:
            return f"Try broadening your {source} search filters."
        if total > returned:
            return "Say 'next page' to see more results."
        return {"crm": "Say 'show active customers' or 'search customer by name'.",
                "support": "Say 'show high priority tickets' or 'show open tickets'.",
                "analytics": "Say 'show last 7 days' or 'show metrics for today'."}.get(source)
