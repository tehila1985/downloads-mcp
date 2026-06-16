from __future__ import annotations
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.application.extract_use_case import ExtractAndCleanupUseCase
from src.domain.exceptions import ExtractionError, FolderNotFoundError
from src.infrastructure.file_repository import BaseFileRepository


def _mock_repo(files: list[Path] | None = None, exists: bool = True) -> BaseFileRepository:
    repo = MagicMock(spec=BaseFileRepository)
    repo.exists.return_value = exists
    repo.list_files.return_value = files or []
    return repo


class TestExtractAndCleanupUseCase:
    def test_raises_when_folder_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FolderNotFoundError):
            ExtractAndCleanupUseCase(_mock_repo(exists=False)).execute(tmp_path)

    def test_zip_file_is_extracted(self, tmp_path: Path) -> None:
        f = tmp_path / "archive.zip"
        repo = _mock_repo(files=[f])
        result = ExtractAndCleanupUseCase(repo).execute(tmp_path, dry_run=False)
        repo.extract_zip.assert_called_once_with(f, tmp_path / "archive")
        assert result["extracted_count"] == 1

    def test_non_zip_file_is_ignored(self, tmp_path: Path) -> None:
        f = tmp_path / "document.pdf"
        repo = _mock_repo(files=[f])
        result = ExtractAndCleanupUseCase(repo).execute(tmp_path, dry_run=False)
        repo.extract_zip.assert_not_called()
        assert result["extracted_count"] == 0

    def test_dry_run_does_not_extract_or_delete(self, tmp_path: Path) -> None:
        f = tmp_path / "archive.zip"
        repo = _mock_repo(files=[f])
        ExtractAndCleanupUseCase(repo).execute(tmp_path, dry_run=True)
        repo.extract_zip.assert_not_called()
        repo.delete_file.assert_not_called()

    def test_extraction_error_captured_in_errors_list(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.zip"
        repo = _mock_repo(files=[f])
        repo.extract_zip.side_effect = ExtractionError(str(f), Exception("corrupt"))
        result = ExtractAndCleanupUseCase(repo).execute(tmp_path, dry_run=False)
        assert result["extracted_count"] == 0
        assert len(result["errors"]) == 1

    def test_archive_deleted_after_extraction(self, tmp_path: Path) -> None:
        f = tmp_path / "archive.zip"
        repo = _mock_repo(files=[f])
        ExtractAndCleanupUseCase(repo).execute(tmp_path, dry_run=False)
        repo.delete_file.assert_called_once_with(f)
