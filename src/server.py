from fastmcp import FastMCP
from typing import Optional
from .services.scanner import scan_downloads
from .services.sorter import smart_sort_files
from .services.deduplicator import deduplicate_by_hash, deduplicate_folders
from .services.extractor import auto_extract_and_cleanup
from .services.cleaner import clear_installers, find_large_files

mcp = FastMCP("Downloads Warden")

@mcp.tool()
def scan_downloads_tool(folder_path: Optional[str] = None) -> dict:
    """Analyze Downloads folder structure and return statistics about files."""
    return scan_downloads(folder_path)

@mcp.tool()
def smart_sort_files_tool(folder_path: Optional[str] = None, dry_run: bool = False) -> dict:
    """Sort files into categories: Documents, Media, Installers, Code, Archives, Other."""
    return smart_sort_files(folder_path, dry_run)

@mcp.tool()
def deduplicate_by_hash_tool(folder_path: Optional[str] = None, dry_run: bool = False) -> dict:
    """Remove duplicate files using SHA-256 hash comparison."""
    return deduplicate_by_hash(folder_path, dry_run)

@mcp.tool()
def deduplicate_folders_tool(folder_path: Optional[str] = None, dry_run: bool = False) -> dict:
    """Identify and remove folders with identical content."""
    return deduplicate_folders(folder_path, dry_run)

@mcp.tool()
def auto_extract_and_cleanup_tool(folder_path: Optional[str] = None, dry_run: bool = False) -> dict:
    """Extract ZIP archives and delete them after successful extraction."""
    return auto_extract_and_cleanup(folder_path, dry_run)

@mcp.tool()
def clear_installers_tool(folder_path: Optional[str] = None, days_old: int = 30, dry_run: bool = False) -> dict:
    """Remove old installer files (.exe, .msi, .dmg) older than specified days."""
    return clear_installers(folder_path, days_old, dry_run)

@mcp.tool()
def find_large_files_tool(folder_path: Optional[str] = None, min_size_mb: int = 500) -> dict:
    """Find files larger than specified size in MB (default 500MB)."""
    return find_large_files(folder_path, min_size_mb)

if __name__ == "__main__":
    mcp.run()
