from __future__ import annotations
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from src.application.deduplicate_use_case import DeduplicateFilesUseCase, DeduplicateFoldersUseCase
from src.domain.exceptions import FolderNotFoundError
from src.infrastructure.file_repository import BaseFileRepository


def _mock_repo(
    files: list[Path] | None = None,
    dirs: list[Path] | None = None,
    hash_map: dict[str, str] | None = None,
    exists: bool = True,
) -> BaseFileRepository:
    repo = MagicMock(spec=BaseFileRepository)
    repo.exists.return_value = exists
    repo.list_files.return_value = files or []
    repo.list_dirs.return_value = dirs or []
    if hash_map:
        repo.compute_hash.side_effect = lambda p: hash_map[str(p)]
    return repo


class TestDeduplicateFilesUseCase:
    def test_raises_when_folder_missing(self, tmp_path: Path) -> None:
        with pytest.raises(FolderNotFoundError):
            DeduplicateFilesUseCase(_mock_repo(exists=False)).execute(tmp_path)

    def test_no_duplicates_removes_nothing(self, tmp_path: Path) -> None:
        f1, f2 = tmp_path / "a.pdf", tmp_path / "b.pdf"
        for f in (f1, f2):
            f.touch()
        repo = _mock_repo(files=[f1, f2], hash_map={str(f1): "aaa", str(f2): "bbb"})
        result = DeduplicateFilesUseCase(repo).execute(tmp_path, dry_run=True)
        assert result["removed_count"] == 0

    def test_duplicate_pair_removes_newer(self, tmp_path: Path) -> None:
        f1, f2 = tmp_path / "a.pdf", tmp_path / "a_copy.pdf"
        f1.write_bytes(b"same")
        f2.write_bytes(b"same")
        repo = _mock_repo(files=[f1, f2], hash_map={str(f1): "abc", str(f2): "abc"})
        result = DeduplicateFilesUseCase(repo).execute(tmp_path, dry_run=True)
        assert result["removed_count"] == 1

    def test_dry_run_does_not_delete(self, tmp_path: Path) -> None:
        f1, f2 = tmp_path / "x.txt", tmp_path / "x2.txt"
        for f in (f1, f2):
            f.touch()
        repo = _mock_repo(files=[f1, f2], hash_map={str(f1): "xyz", str(f2): "xyz"})
        DeduplicateFilesUseCase(repo).execute(tmp_path, dry_run=True)
        repo.delete_file.assert_not_called()

    def test_hash_error_is_recorded_not_raised(self, tmp_path: Path) -> None:
        """A file that cannot be hashed is skipped; the error is captured in 'errors'."""
        from src.domain.exceptions import HashComputationError
        f = tmp_path / "locked.bin"
        repo = _mock_repo(files=[f])
        repo.compute_hash.side_effect = HashComputationError(str(f), OSError("permission denied"))
        result = DeduplicateFilesUseCase(repo).execute(tmp_path, dry_run=True)
        assert result["removed_count"] == 0
        assert len(result["errors"]) == 1
        assert "locked.bin" in result["errors"][0]


class TestDeduplicateFoldersUseCase:
    def test_identical_folders_removes_newer(self, tmp_path: Path) -> None:
        d1, d2 = tmp_path / "folderA", tmp_path / "folderB"
        d1.mkdir(); d2.mkdir()
        f1, f2 = d1 / "x.txt", d2 / "x.txt"
        f1.write_bytes(b"hi"); f2.write_bytes(b"hi")

        def list_files_side_effect(root: Path, recursive: bool = False) -> list[Path]:
            if root == d1: return [f1]
            if root == d2: return [f2]
            return []

        repo = MagicMock(spec=BaseFileRepository)
        repo.exists.return_value = True
        repo.list_dirs.return_value = [d1, d2]
        repo.list_files.side_effect = list_files_side_effect
        repo.compute_hash.side_effect = lambda p: "samehash"

        result = DeduplicateFoldersUseCase(repo).execute(tmp_path, dry_run=True)
        assert result["removed_count"] == 1

    def test_folder_hash_error_is_recorded_not_raised(self, tmp_path: Path) -> None:
        """A folder whose files cannot be hashed is skipped; error goes into 'errors'."""
        from src.domain.exceptions import HashComputationError
        d = tmp_path / "bad_folder"
        d.mkdir()
        f = d / "file.bin"

        repo = MagicMock(spec=BaseFileRepository)
        repo.exists.return_value = True
        repo.list_dirs.return_value = [d]
        repo.list_files.return_value = [f]
        repo.compute_hash.side_effect = HashComputationError(str(f), OSError("locked"))

        result = DeduplicateFoldersUseCase(repo).execute(tmp_path, dry_run=True)
        assert result["removed_count"] == 0
        assert len(result["errors"]) == 1
