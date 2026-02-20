"""Tests for data-source connectors."""

from app.connectors.crm_connector import CRMConnector
from app.connectors.support_connector import SupportConnector
from app.connectors.analytics_connector import AnalyticsConnector


class TestCRMConnector:
    def setup_method(self):
        self.connector = CRMConnector()

    def test_fetch_returns_data(self):
        data = self.connector.fetch()
        assert isinstance(data, list) and len(data) > 0

    def test_filter_by_status(self):
        data = self.connector.fetch(status="active")
        assert all(r["status"] == "active" for r in data)

    def test_filter_by_customer_id(self):
        data = self.connector.fetch(customer_id=1)
        assert len(data) == 1 and data[0]["customer_id"] == 1

    def test_sort_ascending(self):
        data = self.connector.fetch(sort_by="customer_id", sort_order="asc")
        ids = [r["customer_id"] for r in data]
        assert ids == sorted(ids)

    def test_schema(self):
        schema = self.connector.get_schema()
        assert schema["name"] == "query_crm"
        assert "parameters" in schema


class TestSupportConnector:
    def setup_method(self):
        self.connector = SupportConnector()

    def test_fetch_returns_data(self):
        data = self.connector.fetch()
        assert isinstance(data, list) and len(data) > 0

    def test_filter_by_status(self):
        data = self.connector.fetch(status="open")
        assert all(r["status"] == "open" for r in data)

    def test_filter_by_priority(self):
        data = self.connector.fetch(priority="high")
        assert all(r["priority"] == "high" for r in data)

    def test_filter_by_customer_id(self):
        all_data = self.connector.fetch()
        cid = all_data[0]["customer_id"]
        data = self.connector.fetch(customer_id=cid)
        assert all(r["customer_id"] == cid for r in data)

    def test_combined_filters(self):
        data = self.connector.fetch(status="open", priority="high")
        for r in data:
            assert r["status"] == "open" and r["priority"] == "high"

    def test_schema(self):
        schema = self.connector.get_schema()
        assert schema["name"] == "query_support"


class TestAnalyticsConnector:
    def setup_method(self):
        self.connector = AnalyticsConnector()

    def test_fetch_returns_data(self):
        data = self.connector.fetch()
        assert isinstance(data, list) and len(data) > 0

    def test_filter_by_metric(self):
        data = self.connector.fetch(metric="daily_active_users")
        assert all(r["metric"] == "daily_active_users" for r in data)

    def test_filter_by_date_range(self):
        data = self.connector.fetch(date_from="2026-02-01", date_to="2026-02-10")
        for r in data:
            assert "2026-02-01" <= r["date"] <= "2026-02-10"

    def test_sort_by_value(self):
        data = self.connector.fetch(sort_by="value", sort_order="asc")
        values = [r["value"] for r in data]
        assert values == sorted(values)

    def test_schema(self):
        schema = self.connector.get_schema()
        assert schema["name"] == "query_analytics"
