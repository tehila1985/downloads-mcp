from __future__ import annotations
from abc import ABC
from pathlib import Path

from src.domain.events import FileMoved, bus
from src.domain.exceptions import FolderNotFoundError
from src.domain.strategies import SortStrategy
from src.infrastructure.file_repository import BaseFileRepository


class BaseSortUseCase(ABC):
    """
    Template Method: validate → list → categorise → resolve collision → move.
    Subclasses only need to provide the concrete SortStrategy.
    """

    MAX_COLLISION_RETRIES: int = 9999

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
        target = target_dir / file.name
        counter = 1
        while self._repo.exists(target) and counter <= self.MAX_COLLISION_RETRIES:
            target = target_dir / f"{file.stem}_{counter}{file.suffix}"
            counter += 1
        return target
