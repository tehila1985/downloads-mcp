from __future__ import annotations
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.application.sort_use_case import DateSortUseCase, SmartSortUseCase
from src.domain.exceptions import FolderNotFoundError
from src.infrastructure.file_repository import BaseFileRepository


def _mock_repo(files: list[Path], root_exists: bool = True) -> BaseFileRepository:
    repo = MagicMock(spec=BaseFileRepository)
    repo.exists.return_value = root_exists
    repo.list_files.return_value = files
    return repo


class TestSmartSortUseCase:
    def test_pdf_routed_to_documents(self, tmp_path: Path) -> None:
        f = tmp_path / "report.pdf"
        use_case = SmartSortUseCase(_mock_repo([f]))
        result = use_case.execute(tmp_path, dry_run=True)
        assert result["details"][str(f)] == "Would move to Documents"

    def test_exe_routed_to_installers(self, tmp_path: Path) -> None:
        f = tmp_path / "setup.exe"
        use_case = SmartSortUseCase(_mock_repo([f]))
        result = use_case.execute(tmp_path, dry_run=True)
        assert result["details"][str(f)] == "Would move to Installers"

    def test_jpg_routed_to_media(self, tmp_path: Path) -> None:
        f = tmp_path / "photo.jpg"
        use_case = SmartSortUseCase(_mock_repo([f]))
        result = use_case.execute(tmp_path, dry_run=True)
        assert result["details"][str(f)] == "Would move to Media"

    def test_unknown_extension_routed_to_other(self, tmp_path: Path) -> None:
        f = tmp_path / "mystery.xyz"
        use_case = SmartSortUseCase(_mock_repo([f]))
        result = use_case.execute(tmp_path, dry_run=True)
        assert result["details"][str(f)] == "Would move to Other"

    def test_raises_when_folder_not_found(self, tmp_path: Path) -> None:
        use_case = SmartSortUseCase(_mock_repo([], root_exists=False))
        with pytest.raises(FolderNotFoundError):
            use_case.execute(tmp_path)

    def test_moved_count_matches_files(self, tmp_path: Path) -> None:
        files = [tmp_path / f"f{i}.pdf" for i in range(5)]
        use_case = SmartSortUseCase(_mock_repo(files))
        result = use_case.execute(tmp_path, dry_run=True)
        assert result["moved_files"] == 5

    def test_dry_run_does_not_call_move(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.pdf"
        repo = _mock_repo([f])
        SmartSortUseCase(repo).execute(tmp_path, dry_run=True)
        repo.move.assert_not_called()

    def test_real_run_calls_move(self, tmp_path: Path) -> None:
        f = tmp_path / "doc.pdf"
        repo = _mock_repo([f])
        repo.exists.side_effect = lambda p: True  # collision check also returns True for root
        SmartSortUseCase(repo).execute(tmp_path, dry_run=False)
        repo.move.assert_called_once()


class TestDateSortUseCase:
    def test_dry_run_returns_year_month_folder(self, tmp_path: Path) -> None:
        f = tmp_path / "old.pdf"
        f.touch()  # real file needed for stat().st_mtime in DateSortStrategy
        repo = _mock_repo([f])
        result = DateSortUseCase(repo).execute(tmp_path, dry_run=True)
        folder = result["details"][str(f)]
        import re
        assert re.match(r"Would move to \d{4}-\d{2}", folder)
