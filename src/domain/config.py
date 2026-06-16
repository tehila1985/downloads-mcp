from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CategoryRules:
    CATEGORIES: dict[str, frozenset[str]] = field(default_factory=lambda: {
        "Documents": frozenset({
            ".pdf", ".doc", ".docx", ".txt", ".xlsx", ".xls",
            ".pptx", ".ppt", ".odt", ".rtf", ".csv",
        }),
        "Media": frozenset({
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg",
            ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv",
            ".mp3", ".wav", ".flac", ".aac", ".ogg",
        }),
        "Installers": frozenset({
            ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".apk",
        }),
        "Code": frozenset({
            ".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".cs",
            ".html", ".css", ".json", ".xml", ".yaml", ".yml",
            ".sh", ".bat", ".ps1", ".rb", ".go", ".rs", ".php",
        }),
        "Archives": frozenset({
            ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
        }),
    })


@dataclass(frozen=True)
class AppConfig:
    DEFAULT_DAYS_OLD: int = 30
    DEFAULT_MIN_SIZE_MB: int = 500
    HASH_CHUNK_SIZE: int = 8192
    INSTALLER_EXTENSIONS: frozenset[str] = field(
        default_factory=lambda: frozenset({".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"})
    )


CATEGORY_RULES = CategoryRules()
APP_CONFIG = AppConfig()

# Flat reverse-lookup: ".pdf" -> "Documents"
EXTENSION_REGISTRY: dict[str, str] = {
    ext: cat
    for cat, exts in CATEGORY_RULES.CATEGORIES.items()
    for ext in exts
}
