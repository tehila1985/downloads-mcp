from __future__ import annotations
import hashlib
import shutil
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

from src.domain.config import APP_CONFIG
from src.domain.exceptions import ExtractionError, FileOperationError, HashComputationError


class BaseFileRepository(ABC):
    """Abstract boundary for all file-system operations."""

    @abstractmethod
    def list_files(self, root: Path, recursive: bool = False) -> list[Path]: ...

    @abstractmethod
    def list_dirs(self, root: Path) -> list[Path]: ...

    @abstractmethod
    def move(self, src: Path, dst: Path) -> None: ...

    @abstractmethod
    def delete_file(self, path: Path) -> None: ...

    @abstractmethod
    def delete_dir(self, path: Path) -> None: ...

    @abstractmethod
    def mkdir(self, path: Path) -> None: ...

    @abstractmethod
    def compute_hash(self, path: Path) -> str: ...

    @abstractmethod
    def extract_zip(self, archive: Path, destination: Path) -> None: ...

    @abstractmethod
    def exists(self, path: Path) -> bool: ...


class LocalFileRepository(BaseFileRepository):
    """Concrete implementation backed by the real local file system."""

    def list_files(self, root: Path, recursive: bool = False) -> list[Path]:
        iterator = root.rglob("*") if recursive else root.iterdir()
        return [p for p in iterator if p.is_file()]

    def list_dirs(self, root: Path) -> list[Path]:
        return [p for p in root.iterdir() if p.is_dir()]

    def move(self, src: Path, dst: Path) -> None:
        try:
            shutil.move(str(src), str(dst))
        except OSError as exc:
            raise FileOperationError(str(src), exc) from exc

    def delete_file(self, path: Path) -> None:
        try:
            path.unlink()
        except OSError as exc:
            raise FileOperationError(str(path), exc) from exc

    def delete_dir(self, path: Path) -> None:
        try:
            shutil.rmtree(path)
        except OSError as exc:
            raise FileOperationError(str(path), exc) from exc

    def mkdir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def compute_hash(self, path: Path) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(path, "rb") as fh:
                for chunk in iter(lambda: fh.read(APP_CONFIG.HASH_CHUNK_SIZE), b""):
                    sha256.update(chunk)
        except OSError as exc:
            raise HashComputationError(str(path), exc) from exc
        return sha256.hexdigest()

    def extract_zip(self, archive: Path, destination: Path) -> None:
        try:
            with zipfile.ZipFile(archive, "r") as zf:
                zf.extractall(destination)
        except (zipfile.BadZipFile, OSError) as exc:
            raise ExtractionError(str(archive), exc) from exc

    def exists(self, path: Path) -> bool:
        return path.exists()
