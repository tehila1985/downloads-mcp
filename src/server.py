from __future__ import annotations
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from src.container import (
    clear,
    date_sort,
    default_root,
    dedup_files,
    dedup_folders,
    extract,
    find_large,
    scan,
    smart_sort,
)

mcp = FastMCP("Downloads Warden", version="3.0.2")


def _root(folder_path: Optional[str]) -> Path:
    return Path(folder_path) if folder_path else default_root()


@mcp.tool()
def scan_downloads_tool(folder_path: Optional[str] = None) -> dict:
    """Analyze Downloads folder structure and return statistics about files."""
    return scan.execute(_root(folder_path))


@mcp.tool()
def smart_sort_files_tool(folder_path: Optional[str] = None, dry_run: bool = True) -> dict:
    """Sort files into categories: Documents, Media, Installers, Code, Archives, Other."""
    return smart_sort.execute(_root(folder_path), dry_run=dry_run)


@mcp.tool()
def sort_by_date_tool(folder_path: Optional[str] = None, dry_run: bool = True) -> dict:
    """Sort files into folders by year-month (YYYY-MM) based on modification date."""
    return date_sort.execute(_root(folder_path), dry_run=dry_run)


@mcp.tool()
def deduplicate_by_hash_tool(folder_path: Optional[str] = None, dry_run: bool = True) -> dict:
    """Remove duplicate files using SHA-256 hash comparison."""
    return dedup_files.execute(_root(folder_path), dry_run=dry_run)


@mcp.tool()
def deduplicate_folders_tool(folder_path: Optional[str] = None, dry_run: bool = True) -> dict:
    """Identify and remove folders with identical content."""
    return dedup_folders.execute(_root(folder_path), dry_run=dry_run)


@mcp.tool()
def auto_extract_and_cleanup_tool(folder_path: Optional[str] = None, dry_run: bool = True) -> dict:
    """Extract ZIP archives and delete them after successful extraction."""
    return extract.execute(_root(folder_path), dry_run=dry_run)


@mcp.tool()
def clear_installers_tool(
    folder_path: Optional[str] = None,
    days_old: int = 30,
    dry_run: bool = True,
) -> dict:
    """Remove old installer files (.exe, .msi, .dmg) older than specified days."""
    return clear.execute(_root(folder_path), days_old=days_old, dry_run=dry_run)


@mcp.tool()
def find_large_files_tool(
    folder_path: Optional[str] = None,
    min_size_mb: int = 500,
) -> dict:
    """Find files larger than specified size in MB (default 500 MB)."""
    return find_large.execute(_root(folder_path), min_size_mb=min_size_mb)


if __name__ == "__main__":
    mcp.run()
