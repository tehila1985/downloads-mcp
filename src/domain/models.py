from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class FileMetadata:
    path: Path
    name: str
    size: int
    extension: str
    hash: Optional[str] = None


@dataclass(frozen=True)
class ScanResult:
    total_files: int
    total_size: int
    by_category: dict[str, int]
    by_extension: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return {
            "total_files": self.total_files,
            "total_size_bytes": self.total_size,
            "total_size_mb": round(self.total_size / (1024 * 1024), 2),
            "by_category": self.by_category,
            "by_extension": self.by_extension,
        }


@dataclass(frozen=True)
class OperationResult:
    action: str
    count: int
    items: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {"action": self.action, "count": self.count, "items": list(self.items)}
