from __future__ import annotations
from collections import defaultdict
from pathlib import Path

from src.domain.config import CATEGORY_RULES
from src.domain.events import ScanCompleted, bus
from src.domain.exceptions import FolderNotFoundError
from src.domain.models import ScanResult
from src.infrastructure.file_repository import BaseFileRepository


class ScanUseCase:
    def __init__(self, repo: BaseFileRepository) -> None:
        self._repo = repo

    def execute(self, root: Path) -> dict[str, object]:
        if not self._repo.exists(root):
            raise FolderNotFoundError(str(root))

        total_size = 0
        by_category: dict[str, int] = defaultdict(int)
        by_extension: dict[str, int] = defaultdict(int)

        for file in self._repo.list_files(root, recursive=True):
            size = file.stat().st_size
            total_size += size
            ext = file.suffix.lower()
            by_extension[ext] += 1
            by_category[self._resolve_category(ext)] += 1

        result = ScanResult(
            total_files=sum(by_extension.values()),
            total_size=total_size,
            by_category=dict(by_category),
            by_extension=dict(by_extension),
        )
        bus.publish(ScanCompleted(total_files=result.total_files, total_size=total_size))
        return result.to_dict()

    @staticmethod
    def _resolve_category(ext: str) -> str:
        for cat, exts in CATEGORY_RULES.CATEGORIES.items():
            if ext in exts:
                return cat
        return "Other"
