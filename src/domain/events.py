from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Generic, TypeVar

E = TypeVar("E")


@dataclass(frozen=True)
class FileMoved:
    src: Path
    dst: Path
    category: str


@dataclass(frozen=True)
class FileDeleted:
    path: Path
    reason: str


@dataclass(frozen=True)
class FileExtracted:
    archive: Path
    destination: Path


@dataclass(frozen=True)
class ScanCompleted:
    total_files: int
    total_size: int


class EventBus(Generic[E]):
    def __init__(self) -> None:
        self._handlers: list[Callable[[E], None]] = []

    def subscribe(self, handler: Callable[[E], None]) -> None:
        self._handlers.append(handler)

    def publish(self, event: E) -> None:
        for handler in self._handlers:
            handler(event)


# Shared application-wide bus (typed as object to accept any event)
bus: EventBus[object] = EventBus()
