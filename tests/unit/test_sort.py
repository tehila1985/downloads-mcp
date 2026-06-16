from __future__ import annotations
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from src.application.sort_use_case import DateSortUseCase, SmartSortUseCase
from src.domain.exceptions import CollisionError, FolderNotFoundError
from src.infrastructure.file_repository import BaseFileRepository


def _mock_repo(files: list[Path], root_exists: bool = True) -> BaseFileRepository:
    """Build a mock repo where the root exists but all target paths are free."""
    repo = MagicMock(spec=BaseFileRepository)
    # First call to exists() validates the root; subsequent calls are collision checks
    # on target paths which should be free so sorting proceeds without collision.
    _calls: list[int] = [0]
    def _exists(p: Path) -> bool:
        _calls[0] += 1
        return root_exists if _calls[0] == 1 else False
    repo.exists.side_effect = _exists
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
        repo = _mock_repo([f])  # root exists, target is free
        SmartSortUseCase(repo).execute(tmp_path, dry_run=False)
        repo.move.assert_called_once()

    # ── Collision tests ───────────────────────────────────────────────────────

    def test_collision_produces_numbered_suffix(self, tmp_path: Path) -> None:
        """When target already exists, the first free _N slot is used."""
        f = tmp_path / "report.pdf"
        repo = _mock_repo([f])
        # Override: root=True (call 1), plain target taken (call 2), _1 slot free (call 3+)
        _calls: list[int] = [0]
        def exists_side(p: Path) -> bool:
            _calls[0] += 1
            return _calls[0] <= 2  # call1=root True, call2=plain target True, rest=False
        repo.exists.side_effect = exists_side
        SmartSortUseCase(repo).execute(tmp_path, dry_run=False)
        dst = repo.move.call_args[0][1]
        assert dst.name == "report_1.pdf"

    def test_collision_uses_timestamp_after_counter_exhausted(self, tmp_path: Path) -> None:
        """After _COUNTER_LIMIT sequential slots are all taken, fall back to timestamp name."""
        import re
        from src.application.base_sort_use_case import BaseSortUseCase
        f = tmp_path / "report.pdf"
        repo = _mock_repo([f])
        # exists() call sequence (total 101 when all slots taken):
        #   call 1      : root validation
        #   call 2      : plain target (report.pdf)
        #   calls 3-100 : report_1.pdf .. report_98.pdf  (98 counter checks)
        #   call 101    : timestamp slot  → False (free) → use it
        total_taken = 100  # calls 1-100 return True; call 101 (timestamp) returns False
        _calls: list[int] = [0]
        def exists_side(p: Path) -> bool:
            _calls[0] += 1
            return _calls[0] <= total_taken
        repo.exists.side_effect = exists_side
        SmartSortUseCase(repo).execute(tmp_path, dry_run=False)
        dst = repo.move.call_args[0][1]
        assert re.match(r"report_\d{8}_\d{6}_\d{6}\.pdf", dst.name), dst.name

    def test_collision_raises_when_all_slots_taken(self, tmp_path: Path) -> None:
        """CollisionError is raised when every candidate path is occupied."""
        f = tmp_path / "report.pdf"
        repo = _mock_repo([f])
        # Clear side_effect so return_value takes effect for every call
        repo.exists.side_effect = None
        repo.exists.return_value = True
        with pytest.raises(CollisionError):
            SmartSortUseCase(repo).execute(tmp_path, dry_run=False)


class TestDateSortUseCase:
    def test_dry_run_returns_year_month_folder(self, tmp_path: Path) -> None:
        f = tmp_path / "old.pdf"
        f.touch()  # real file needed for stat().st_mtime in DateSortStrategy
        repo = _mock_repo([f])
        result = DateSortUseCase(repo).execute(tmp_path, dry_run=True)
        folder = result["details"][str(f)]
        import re
        assert re.match(r"Would move to \d{4}-\d{2}", folder)
