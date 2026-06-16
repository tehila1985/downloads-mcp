from __future__ import annotations
import zipfile
from pathlib import Path

import pytest

from src.application.clean_use_case import ClearInstallersUseCase, FindLargeFilesUseCase
from src.application.deduplicate_use_case import DeduplicateFilesUseCase
from src.application.extract_use_case import ExtractAndCleanupUseCase
from src.application.scan_use_case import ScanUseCase
from src.application.sort_use_case import SmartSortUseCase
from src.infrastructure.file_repository import LocalFileRepository

REPO = LocalFileRepository()


@pytest.fixture
def populated(tmp_path: Path) -> Path:
    (tmp_path / "invoice.pdf").write_bytes(b"pdf")
    (tmp_path / "setup.exe").write_bytes(b"exe")
    (tmp_path / "photo.jpg").write_bytes(b"jpg")
    (tmp_path / "script.py").write_bytes(b"py")
    (tmp_path / "data.zip").write_bytes(b"zip")
    return tmp_path


class TestScanIntegration:
    def test_counts_all_files(self, populated: Path) -> None:
        result = ScanUseCase(REPO).execute(populated)
        assert result["total_files"] == 5

    def test_categorises_correctly(self, populated: Path) -> None:
        result = ScanUseCase(REPO).execute(populated)
        assert result["by_category"]["Documents"] == 1
        assert result["by_category"]["Installers"] == 1
        assert result["by_category"]["Media"] == 1
        assert result["by_category"]["Code"] == 1
        assert result["by_category"]["Archives"] == 1


class TestSmartSortIntegration:
    def test_files_moved_to_correct_subfolders(self, populated: Path) -> None:
        SmartSortUseCase(REPO).execute(populated, dry_run=False)
        assert (populated / "Documents" / "invoice.pdf").exists()
        assert (populated / "Installers" / "setup.exe").exists()
        assert (populated / "Media" / "photo.jpg").exists()
        assert (populated / "Code" / "script.py").exists()
        assert (populated / "Archives" / "data.zip").exists()

    def test_dry_run_does_not_move(self, populated: Path) -> None:
        SmartSortUseCase(REPO).execute(populated, dry_run=True)
        assert (populated / "invoice.pdf").exists()


class TestDeduplicateIntegration:
    def test_duplicate_is_removed(self, tmp_path: Path) -> None:
        f1 = tmp_path / "original.txt"
        f2 = tmp_path / "copy.txt"
        f1.write_bytes(b"identical content")
        f2.write_bytes(b"identical content")
        result = DeduplicateFilesUseCase(REPO).execute(tmp_path, dry_run=False)
        assert result["removed_count"] == 1
        remaining = list(tmp_path.iterdir())
        assert len(remaining) == 1

    def test_unique_files_untouched(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_bytes(b"aaa")
        (tmp_path / "b.txt").write_bytes(b"bbb")
        result = DeduplicateFilesUseCase(REPO).execute(tmp_path, dry_run=False)
        assert result["removed_count"] == 0


class TestExtractIntegration:
    def test_zip_extracted_and_deleted(self, tmp_path: Path) -> None:
        archive = tmp_path / "bundle.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("hello.txt", "hello world")
        result = ExtractAndCleanupUseCase(REPO).execute(tmp_path, dry_run=False)
        assert result["extracted_count"] == 1
        assert not archive.exists()
        assert (tmp_path / "bundle" / "hello.txt").exists()


class TestCleanIntegration:
    def test_find_large_files_returns_correct_count(self, tmp_path: Path) -> None:
        (tmp_path / "big.bin").write_bytes(b"x" * (600 * 1024 * 1024))
        (tmp_path / "small.txt").write_bytes(b"tiny")
        result = FindLargeFilesUseCase(REPO).execute(tmp_path, min_size_mb=500)
        assert result["count"] == 1
        assert result["files"][0]["size_mb"] == pytest.approx(600.0, abs=1.0)
