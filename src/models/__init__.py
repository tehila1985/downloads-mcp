from pydantic import BaseModel
from typing import Optional

class FileInfo(BaseModel):
    path: str
    name: str
    size: int
    extension: str
    hash: Optional[str] = None

class ScanResult(BaseModel):
    total_files: int
    total_size: int
    by_category: dict[str, int]
    by_extension: dict[str, int]
