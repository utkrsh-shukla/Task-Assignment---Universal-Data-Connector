# Pydantic models for all data sources
from app.models.common import DataResponse, Metadata, DataType, PaginationInfo, VoiceContext
from app.models.crm import Customer
from app.models.support import SupportTicket
from app.models.analytics import AnalyticsMetric, AnalyticsSummary
