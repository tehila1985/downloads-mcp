from __future__ import annotations
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.application.scan_use_case import ScanUseCase
from src.domain.exceptions import FolderNotFoundError
from src.infrastructure.file_repository import BaseFileRepository


def _mock_repo(files: list[Path], exists: bool = True) -> BaseFileRepository:
    repo = MagicMock(spec=BaseFileRepository)
    repo.exists.return_value = exists
    repo.list_files.return_value = files
    return repo


class TestScanUseCase:
    def test_raises_when_folder_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FolderNotFoundError):
            ScanUseCase(_mock_repo([], exists=False)).execute(tmp_path)

    def test_empty_folder_returns_zeros(self, tmp_path: Path) -> None:
        result = ScanUseCase(_mock_repo([])).execute(tmp_path)
        assert result["total_files"] == 0
        assert result["total_size_bytes"] == 0

    def test_counts_files_correctly(self, tmp_path: Path) -> None:
        files = []
        for name in ("a.pdf", "b.jpg", "c.exe"):
            f = tmp_path / name
            f.write_bytes(b"x" * 100)
            files.append(f)
        result = ScanUseCase(_mock_repo(files)).execute(tmp_path)
        assert result["total_files"] == 3

    def test_categorises_pdf_as_documents(self, tmp_path: Path) -> None:
        f = tmp_path / "report.pdf"
        f.write_bytes(b"x")
        result = ScanUseCase(_mock_repo([f])).execute(tmp_path)
        assert result["by_category"]["Documents"] == 1

    def test_result_contains_required_keys(self, tmp_path: Path) -> None:
        result = ScanUseCase(_mock_repo([])).execute(tmp_path)
        for key in ("total_files", "total_size_bytes", "total_size_mb", "by_category", "by_extension"):
            assert key in result
