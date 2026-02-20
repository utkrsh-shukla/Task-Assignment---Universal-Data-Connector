"""API integration tests."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealth:
    def test_returns_200(self):
        assert client.get("/health").status_code == 200

    def test_status_healthy(self):
        assert client.get("/health").json()["status"] == "healthy"

    def test_includes_version(self):
        assert "version" in client.get("/health").json()

    def test_includes_sources(self):
        body = client.get("/health").json()
        for src in ("crm", "support", "analytics"):
            assert src in body["data_sources"]


class TestDataSources:
    def test_list(self):
        body = client.get("/data/sources").json()
        names = [s["name"] for s in body["sources"]]
        assert "crm" in names and "support" in names and "analytics" in names


class TestCRM:
    def test_returns_data(self):
        body = client.get("/data/crm").json()
        assert body["success"] is True and len(body["data"]) > 0

    def test_metadata_structure(self):
        meta = client.get("/data/crm").json()["metadata"]
        for key in ("total_results", "returned_results", "data_type", "pagination", "source"):
            assert key in meta

    def test_voice_on(self):
        assert client.get("/data/crm?voice_mode=true").json()["metadata"]["voice_context"] is not None

    def test_voice_off(self):
        assert client.get("/data/crm?voice_mode=false").json()["metadata"]["voice_context"] is None

    def test_filter_status(self):
        for r in client.get("/data/crm?status=active").json()["data"]:
            assert r["status"] == "active"

    def test_pagination(self):
        body = client.get("/data/crm?page=1&page_size=3").json()
        assert len(body["data"]) == 3
        pag = body["metadata"]["pagination"]
        assert pag["current_page"] == 1 and pag["has_next"] is True


class TestSupport:
    def test_returns_data(self):
        assert client.get("/data/support").json()["success"] is True

    def test_filter_open_high(self):
        for r in client.get("/data/support?status=open&priority=high").json()["data"]:
            assert r["status"] == "open" and r["priority"] == "high"


class TestAnalytics:
    def test_returns_data(self):
        assert client.get("/data/analytics").json()["success"] is True

    def test_date_range(self):
        for r in client.get("/data/analytics?date_from=2026-02-01&date_to=2026-02-10").json()["data"]:
            assert "2026-02-01" <= r["date"] <= "2026-02-10"


class TestErrors:
    def test_unknown_source_404(self):
        resp = client.get("/data/invalid_source")
        assert resp.status_code == 404 and "Unknown" in resp.json()["detail"]

    def test_invalid_page_422(self):
        assert client.get("/data/crm?page=0").status_code == 422


class TestSchema:
    def test_returns_functions(self):
        body = client.get("/schema/functions").json()
        assert len(body["functions"]) == 3

    def test_structure(self):
        for f in client.get("/schema/functions").json()["functions"]:
            assert "name" in f and "description" in f and "parameters" in f

    def test_names(self):
        names = {f["name"] for f in client.get("/schema/functions").json()["functions"]}
        assert names == {"query_crm", "query_support", "query_analytics"}
