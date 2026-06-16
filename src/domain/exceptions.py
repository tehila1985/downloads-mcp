from __future__ import annotations


class WardenError(Exception):
    """Base exception for all Downloads Warden errors."""


class FolderNotFoundError(WardenError):
    def __init__(self, path: str) -> None:
        super().__init__(f"Folder not found: {path}")


class FileOperationError(WardenError):
    def __init__(self, path: str, cause: Exception) -> None:
        super().__init__(f"File operation failed for '{path}': {cause}")
        self.__cause__ = cause


class HashComputationError(WardenError):
    def __init__(self, path: str, cause: Exception) -> None:
        super().__init__(f"Cannot compute hash for '{path}': {cause}")
        self.__cause__ = cause


class ExtractionError(WardenError):
    def __init__(self, path: str, cause: Exception) -> None:
        super().__init__(f"Failed to extract '{path}': {cause}")
        self.__cause__ = cause


class CollisionError(WardenError):
    def __init__(self, src: str, dst: str) -> None:
        super().__init__(f"Cannot resolve collision: '{src}' -> '{dst}'")
