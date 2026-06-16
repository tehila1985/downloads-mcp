from __future__ import annotations
from src.application.base_sort_use_case import BaseSortUseCase
from src.domain.strategies import DateSortStrategy, ExtensionSortStrategy
from src.infrastructure.file_repository import BaseFileRepository


class SmartSortUseCase(BaseSortUseCase):
    def __init__(self, repo: BaseFileRepository) -> None:
        super().__init__(repo, ExtensionSortStrategy())


class DateSortUseCase(BaseSortUseCase):
    def __init__(self, repo: BaseFileRepository) -> None:
        super().__init__(repo, DateSortStrategy())
