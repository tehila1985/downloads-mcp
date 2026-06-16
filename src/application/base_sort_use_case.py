from __future__ import annotations
from abc import ABC
from datetime import datetime
from pathlib import Path

from src.domain.events import FileMoved, bus
from src.domain.exceptions import CollisionError, FolderNotFoundError
from src.domain.strategies import SortStrategy
from src.infrastructure.file_repository import BaseFileRepository


class BaseSortUseCase(ABC):
    """
    Template Method: validate → list → categorise → resolve collision → move.
    Subclasses only need to provide the concrete SortStrategy.

    Collision strategy (in order):
      1. document.pdf already exists  →  document_1.pdf, document_2.pdf … document_99.pdf
      2. Still taken after 99 tries   →  document_20250101_153045_123456.pdf  (timestamp)
      3. Timestamp slot also taken    →  raise CollisionError (extremely unlikely)
    """

    _COUNTER_LIMIT: int = 99

    def __init__(self, repo: BaseFileRepository, strategy: SortStrategy) -> None:
        self._repo = repo
        self._strategy = strategy

    def execute(self, root: Path, dry_run: bool = False) -> dict[str, object]:
        if not self._repo.exists(root):
            raise FolderNotFoundError(str(root))

        moved: dict[str, str] = {}

        for file in self._repo.list_files(root, recursive=False):
            folder_name = self._strategy.get_target_folder(file)
            target_dir = root / folder_name
            target = self._resolve_collision(target_dir, file)

            if not dry_run:
                self._repo.mkdir(target_dir)
                self._repo.move(file, target)
                bus.publish(FileMoved(src=file, dst=target, category=folder_name))

            moved[str(file)] = str(target) if not dry_run else f"Would move to {folder_name}"

        return {"moved_files": len(moved), "details": moved}

    def _resolve_collision(self, target_dir: Path, file: Path) -> Path:
        # Phase 1: sequential counter  →  stem_1.ext … stem_99.ext
        target = target_dir / file.name
        for counter in range(1, self._COUNTER_LIMIT + 1):
            if not self._repo.exists(target):
                return target
            target = target_dir / f"{file.stem}_{counter}{file.suffix}"

        # Phase 2: microsecond timestamp  →  stem_20250101_153045_123456.ext
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        target = target_dir / f"{file.stem}_{ts}{file.suffix}"
        if not self._repo.exists(target):
            return target

        raise CollisionError(str(file), str(target))
