from __future__ import annotations
from collections import defaultdict
from pathlib import Path

from src.domain.events import FileDeleted, bus
from src.domain.exceptions import FolderNotFoundError, HashComputationError
from src.infrastructure.file_repository import BaseFileRepository


class DeduplicateFilesUseCase:
    def __init__(self, repo: BaseFileRepository) -> None:
        self._repo = repo

    def execute(self, root: Path, dry_run: bool = False) -> dict[str, object]:
        if not self._repo.exists(root):
            raise FolderNotFoundError(str(root))

        hash_map: dict[str, list[Path]] = defaultdict(list)
        errors: list[str] = []

        for file in self._repo.list_files(root, recursive=True):
            try:
                hash_map[self._repo.compute_hash(file)].append(file)
            except HashComputationError as exc:
                errors.append(str(exc))

        removed: list[str] = []
        for files in hash_map.values():
            if len(files) < 2:
                continue
            files.sort(key=lambda f: f.stat().st_mtime)
            for duplicate in files[1:]:
                if not dry_run:
                    self._repo.delete_file(duplicate)
                    bus.publish(FileDeleted(path=duplicate, reason="duplicate"))
                removed.append(str(duplicate))

        return {"removed_count": len(removed), "removed_files": removed, "errors": errors}


class DeduplicateFoldersUseCase:
    def __init__(self, repo: BaseFileRepository) -> None:
        self._repo = repo

    def execute(self, root: Path, dry_run: bool = False) -> dict[str, object]:
        if not self._repo.exists(root):
            raise FolderNotFoundError(str(root))

        folder_hashes: dict[str, list[Path]] = defaultdict(list)
        errors: list[str] = []

        for folder in self._repo.list_dirs(root):
            try:
                folder_hashes[self._compute_folder_hash(folder)].append(folder)
            except HashComputationError as exc:
                errors.append(str(exc))

        removed: list[str] = []
        for folders in folder_hashes.values():
            if len(folders) < 2:
                continue
            folders.sort(key=lambda f: f.stat().st_mtime)
            for duplicate in folders[1:]:
                if not dry_run:
                    self._repo.delete_dir(duplicate)
                    bus.publish(FileDeleted(path=duplicate, reason="duplicate_folder"))
                removed.append(str(duplicate))

        return {"removed_count": len(removed), "removed_folders": removed, "errors": errors}

    def _compute_folder_hash(self, folder: Path) -> str:
        hashes: list[str] = []
        for file in sorted(self._repo.list_files(folder, recursive=True)):
            hashes.append(self._repo.compute_hash(file))
        return "".join(hashes)
