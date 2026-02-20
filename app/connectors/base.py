"""Abstract base connector for all data sources."""

import json, logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.models.common import DataType

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    source_name: str = ""
    description: str = ""
    data_type: DataType = DataType.UNKNOWN

    def _load_json(self, filename: str) -> List[Dict[str, Any]]:
        path = Path(settings.DATA_DIR) / filename
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Loaded %d records from %s", len(data), filename)
            return data
        except FileNotFoundError:
            logger.error("Data file not found: %s", path)
            return []
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in %s: %s", path, e)
            return []

    @abstractmethod
    def fetch(self, **filters) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        ...

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": f"query_{self.source_name}",
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self._get_parameters(),
                "required": [],
            },
        }

    def get_record_count(self) -> int:
        return len(self.fetch())
