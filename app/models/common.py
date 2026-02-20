"""Shared response models — envelope, metadata, pagination, voice context."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DataType(str, Enum):
    TABULAR = "tabular"
    TIME_SERIES = "time_series"
    KEY_VALUE = "key_value"
    EMPTY = "empty"
    UNKNOWN = "unknown"


class PaginationInfo(BaseModel):
    current_page: int = Field(..., description="Current page (1-based)")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total pages")
    has_next: bool = Field(..., description="Next page exists")
    has_previous: bool = Field(..., description="Previous page exists")


class VoiceContext(BaseModel):
    summary: str = Field(..., description="One-line spoken summary")
    freshness: str = Field(..., description="Data freshness indicator")
    suggestion: Optional[str] = Field(None, description="Follow-up suggestion")


class DataSourceInfo(BaseModel):
    name: str = Field(..., description="Source identifier")
    description: str = Field(..., description="Human-readable description")
    record_count: int = Field(..., description="Total records in source")


class Metadata(BaseModel):
    total_results: int
    returned_results: int
    data_type: DataType
    data_freshness: str
    source: DataSourceInfo
    pagination: PaginationInfo
    voice_context: Optional[VoiceContext] = None
    filters_applied: Dict[str, Any] = Field(default_factory=dict)


class DataResponse(BaseModel):
    success: bool = Field(True)
    data: List[Any] = Field(...)
    metadata: Metadata = Field(...)
