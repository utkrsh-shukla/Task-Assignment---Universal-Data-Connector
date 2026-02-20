"""Tests for business rules engine and voice optimizer."""

from app.services.business_rules import BusinessRulesEngine
from app.services.voice_optimizer import VoiceOptimizer
from app.services.data_identifier import identify_data_type
from app.models.common import DataType


class TestDataIdentifier:
    def test_empty(self):
        assert identify_data_type([]) == DataType.EMPTY

    def test_time_series(self):
        assert identify_data_type([{"date": "2026-01-01", "value": 42}]) == DataType.TIME_SERIES

    def test_tabular(self):
        data = [{"customer_id": 1, "name": "Alice", "email": "a@b.com", "status": "active"}]
        assert identify_data_type(data) == DataType.TABULAR

    def test_key_value(self):
        assert identify_data_type([{"key": "setting", "val": "on"}]) == DataType.KEY_VALUE


class TestBusinessRulesEngine:
    def setup_method(self):
        self.engine = BusinessRulesEngine()
        self.data = [{"id": i} for i in range(25)]

    def test_voice_mode_limits(self):
        page_data, pag, _ = self.engine.apply(self.data, voice_mode=True)
        assert len(page_data) == 10 and pag.current_page == 1

    def test_page_2(self):
        page_data, pag, _ = self.engine.apply(self.data, page=2, page_size=10, voice_mode=True)
        assert pag.current_page == 2 and pag.has_previous is True

    def test_custom_page_size(self):
        page_data, pag, _ = self.engine.apply(self.data, page=1, page_size=5, voice_mode=False)
        assert len(page_data) == 5 and pag.total_pages == 5

    def test_empty(self):
        page_data, _, msg = self.engine.apply([], voice_mode=True)
        assert page_data == [] and "No results" in msg

    def test_context_all(self):
        _, _, msg = self.engine.apply([{"id": i} for i in range(3)], page_size=10, voice_mode=True)
        assert "all 3" in msg

    def test_context_partial(self):
        _, _, msg = self.engine.apply(self.data, page_size=10, voice_mode=True)
        assert "10 of" in msg


class TestVoiceOptimizer:
    def setup_method(self):
        self.opt = VoiceOptimizer()

    def test_crm_summary(self):
        data = [{"status": "active"}, {"status": "active"}, {"status": "inactive"}]
        ctx = self.opt.build_voice_context(data, "crm", 3, 3)
        assert "2 active" in ctx.summary and "1 inactive" in ctx.summary

    def test_support_summary(self):
        data = [{"status": "open", "priority": "high"},
                {"status": "open", "priority": "low"},
                {"status": "closed", "priority": "medium"}]
        ctx = self.opt.build_voice_context(data, "support", 3, 3)
        assert "2 open" in ctx.summary and "1 high-priority" in ctx.summary

    def test_analytics_summary(self):
        data = [{"value": 100}, {"value": 200}, {"value": 300}]
        ctx = self.opt.build_voice_context(data, "analytics", 3, 3)
        assert "200" in ctx.summary

    def test_freshness(self):
        ctx = self.opt.build_voice_context([], "crm", 0, 0)
        assert "Data as of" in ctx.freshness

    def test_suggestion_paginated(self):
        ctx = self.opt.build_voice_context([], "crm", 50, 10)
        assert ctx.suggestion is not None and "next page" in ctx.suggestion.lower()
