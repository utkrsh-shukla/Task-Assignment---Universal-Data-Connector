"""Analytics metric models."""

from pydantic import BaseModel, Field


class AnalyticsMetric(BaseModel):
    metric: str = Field(..., description="Metric name")
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    value: float = Field(..., description="Metric value")


class AnalyticsSummary(BaseModel):
    metric: str
    period: str
    average: float
    minimum: float
    maximum: float
    total: float
    count: int
    trend: str = Field(..., description="'increasing', 'decreasing', or 'stable'")
