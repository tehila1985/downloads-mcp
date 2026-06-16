from __future__ import annotations
import time
from pathlib import Path

from src.domain.config import APP_CONFIG
from src.domain.events import FileDeleted, bus
from src.domain.exceptions import FolderNotFoundError
from src.infrastructure.file_repository import BaseFileRepository


class ClearInstallersUseCase:
    def __init__(self, repo: BaseFileRepository) -> None:
        self._repo = repo

    def execute(
        self,
        root: Path,
        days_old: int = APP_CONFIG.DEFAULT_DAYS_OLD,
        dry_run: bool = False,
    ) -> dict[str, object]:
        if not self._repo.exists(root):
            raise FolderNotFoundError(str(root))

        cutoff = time.time() - (days_old * 86_400)
        removed: list[str] = []

        for file in self._repo.list_files(root, recursive=True):
            if (
                file.suffix.lower() in APP_CONFIG.INSTALLER_EXTENSIONS
                and file.stat().st_mtime < cutoff
            ):
                if not dry_run:
                    self._repo.delete_file(file)
                    bus.publish(FileDeleted(path=file, reason=f"installer_older_than_{days_old}d"))
                removed.append(str(file))

        return {"removed_count": len(removed), "removed_files": removed}


class FindLargeFilesUseCase:
    def __init__(self, repo: BaseFileRepository) -> None:
        self._repo = repo

    def execute(
        self,
        root: Path,
        min_size_mb: int = APP_CONFIG.DEFAULT_MIN_SIZE_MB,
    ) -> dict[str, object]:
        if not self._repo.exists(root):
            raise FolderNotFoundError(str(root))

        min_bytes = min_size_mb * 1024 * 1024
        large_files = [
            {"path": str(f), "size_mb": round(f.stat().st_size / (1024 * 1024), 2)}
            for f in self._repo.list_files(root, recursive=True)
            if f.stat().st_size >= min_bytes
        ]
        large_files.sort(key=lambda x: x["size_mb"], reverse=True)  # type: ignore[arg-type]
        return {"count": len(large_files), "files": large_files}
