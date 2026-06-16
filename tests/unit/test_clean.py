from __future__ import annotations
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.application.clean_use_case import ClearInstallersUseCase, FindLargeFilesUseCase
from src.domain.exceptions import FolderNotFoundError
from src.infrastructure.file_repository import BaseFileRepository


def _mock_repo(files: list[Path] | None = None, exists: bool = True) -> BaseFileRepository:
    repo = MagicMock(spec=BaseFileRepository)
    repo.exists.return_value = exists
    repo.list_files.return_value = files or []
    return repo


class TestClearInstallersUseCase:
    def test_raises_when_folder_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FolderNotFoundError):
            ClearInstallersUseCase(_mock_repo(exists=False)).execute(tmp_path)

    def test_old_installer_is_flagged(self, tmp_path: Path) -> None:
        f = tmp_path / "setup.exe"
        f.touch()
        old_mtime = time.time() - (60 * 86_400)  # 60 days ago
        import os; os.utime(f, (old_mtime, old_mtime))
        repo = _mock_repo(files=[f])
        result = ClearInstallersUseCase(repo).execute(tmp_path, days_old=30, dry_run=True)
        assert result["removed_count"] == 1

    def test_recent_installer_is_not_flagged(self, tmp_path: Path) -> None:
        f = tmp_path / "setup.exe"
        f.touch()  # mtime = now
        repo = _mock_repo(files=[f])
        result = ClearInstallersUseCase(repo).execute(tmp_path, days_old=30, dry_run=True)
        assert result["removed_count"] == 0

    def test_dry_run_does_not_delete(self, tmp_path: Path) -> None:
        f = tmp_path / "old.exe"
        f.touch()
        import os; os.utime(f, (0, 0))
        repo = _mock_repo(files=[f])
        ClearInstallersUseCase(repo).execute(tmp_path, days_old=1, dry_run=True)
        repo.delete_file.assert_not_called()


class TestFindLargeFilesUseCase:
    def test_raises_when_folder_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FolderNotFoundError):
            FindLargeFilesUseCase(_mock_repo(exists=False)).execute(tmp_path)

    def test_file_above_threshold_included(self, tmp_path: Path) -> None:
        f = tmp_path / "big.iso"
        f.write_bytes(b"x" * (600 * 1024 * 1024))  # 600 MB
        repo = _mock_repo(files=[f])
        result = FindLargeFilesUseCase(repo).execute(tmp_path, min_size_mb=500)
        assert result["count"] == 1

    def test_file_below_threshold_excluded(self, tmp_path: Path) -> None:
        f = tmp_path / "small.pdf"
        f.write_bytes(b"x" * 100)
        repo = _mock_repo(files=[f])
        result = FindLargeFilesUseCase(repo).execute(tmp_path, min_size_mb=500)
        assert result["count"] == 0

    def test_results_sorted_descending(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.iso"
        f2 = tmp_path / "b.iso"
        f1.write_bytes(b"x" * (1024 * 1024 * 1024))   # 1 GB
        f2.write_bytes(b"x" * (600 * 1024 * 1024))    # 600 MB
        repo = _mock_repo(files=[f1, f2])
        result = FindLargeFilesUseCase(repo).execute(tmp_path, min_size_mb=100)
        sizes = [item["size_mb"] for item in result["files"]]
        assert sizes == sorted(sizes, reverse=True)
