"""Heuristic data-type classifier for connector output."""

from typing import Any, Dict, List
from app.models.common import DataType


def identify_data_type(records: List[Dict[str, Any]]) -> DataType:
    if not records:
        return DataType.EMPTY
    sample = records[0]
    date_keys = {"date", "timestamp", "created_at", "time"}
    metric_keys = {"value", "count", "metric", "amount"}
    if date_keys & set(sample.keys()) and metric_keys & set(sample.keys()):
        return DataType.TIME_SERIES
    if len(sample) <= 3:
        return DataType.KEY_VALUE
    return DataType.TABULAR
