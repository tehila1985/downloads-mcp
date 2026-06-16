from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from .config import EXTENSION_REGISTRY


class SortStrategy(ABC):
    """Determines the target sub-folder name for a given file."""

    @abstractmethod
    def get_target_folder(self, file: Path) -> str: ...


class ExtensionSortStrategy(SortStrategy):
    """Routes files to category folders based on a registry map."""

    def __init__(self, registry: dict[str, str] = EXTENSION_REGISTRY) -> None:
        self._registry = registry

    def get_target_folder(self, file: Path) -> str:
        return self._registry.get(file.suffix.lower(), "Other")


class DateSortStrategy(SortStrategy):
    """Routes files to YYYY-MM folders based on modification date."""

    def get_target_folder(self, file: Path) -> str:
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        return mtime.strftime("%Y-%m")


class StrategyFactory:
    """Registry-based factory — adding a new strategy is one line."""

    _registry: dict[str, type[SortStrategy]] = {
        "extension": ExtensionSortStrategy,
        "date": DateSortStrategy,
    }

    @classmethod
    def create(cls, name: str) -> SortStrategy:
        try:
            return cls._registry[name]()
        except KeyError:
            raise ValueError(f"Unknown strategy '{name}'. Available: {list(cls._registry)}")

    @classmethod
    def register(cls, name: str, strategy_cls: type[SortStrategy]) -> None:
        cls._registry[name] = strategy_cls
