from __future__ import annotations
from pathlib import Path

from src.domain.events import FileExtracted, bus
from src.domain.exceptions import ExtractionError, FolderNotFoundError
from src.infrastructure.file_repository import BaseFileRepository


class ExtractAndCleanupUseCase:
    def __init__(self, repo: BaseFileRepository) -> None:
        self._repo = repo

    def execute(self, root: Path, dry_run: bool = False) -> dict[str, object]:
        if not self._repo.exists(root):
            raise FolderNotFoundError(str(root))

        extracted: list[str] = []
        errors: list[str] = []

        for archive in self._repo.list_files(root, recursive=True):
            if archive.suffix.lower() != ".zip":
                continue
            destination = archive.parent / archive.stem
            try:
                if not dry_run:
                    self._repo.extract_zip(archive, destination)
                    self._repo.delete_file(archive)
                    bus.publish(FileExtracted(archive=archive, destination=destination))
                extracted.append(str(archive))
            except ExtractionError as exc:
                errors.append(str(exc))

        return {"extracted_count": len(extracted), "extracted_files": extracted, "errors": errors}
