from __future__ import annotations
import logging
from pathlib import Path

from src.application.clean_use_case import ClearInstallersUseCase, FindLargeFilesUseCase
from src.application.deduplicate_use_case import DeduplicateFilesUseCase, DeduplicateFoldersUseCase
from src.application.extract_use_case import ExtractAndCleanupUseCase
from src.application.scan_use_case import ScanUseCase
from src.application.sort_use_case import DateSortUseCase, SmartSortUseCase
from src.domain.events import bus
from src.infrastructure.file_repository import LocalFileRepository

logger = logging.getLogger("downloads_warden")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# ── Wire observers ────────────────────────────────────────────────────────────
def _on_any(event: object) -> None:
    logger.info(event)

bus.subscribe(_on_any)  # type: ignore[arg-type]

# ── Build all use-cases with a shared repository ──────────────────────────────
_repo = LocalFileRepository()

scan          = ScanUseCase(_repo)
smart_sort    = SmartSortUseCase(_repo)
date_sort     = DateSortUseCase(_repo)
dedup_files   = DeduplicateFilesUseCase(_repo)
dedup_folders = DeduplicateFoldersUseCase(_repo)
extract       = ExtractAndCleanupUseCase(_repo)
clear         = ClearInstallersUseCase(_repo)
find_large    = FindLargeFilesUseCase(_repo)


def default_root() -> Path:
    return Path.home() / "Downloads"
