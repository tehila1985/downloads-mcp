from pathlib import Path
import time
from ..utils import get_downloads_folder

def clear_installers(folder_path: str = None, days_old: int = 30, dry_run: bool = False) -> dict:
    downloads = Path(folder_path) if folder_path else get_downloads_folder()
    
    if not downloads.exists():
        raise FileNotFoundError(f"Downloads folder not found: {downloads}")
    
    installer_exts = {'.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'}
    removed = []
    cutoff_time = time.time() - (days_old * 86400)
    
    for item in downloads.rglob('*'):
        if item.is_file() and item.suffix.lower() in installer_exts:
            if item.stat().st_mtime < cutoff_time:
                if not dry_run:
                    item.unlink()
                removed.append(str(item))
    
    return {"removed_count": len(removed), "removed_files": removed}

def find_large_files(folder_path: str = None, min_size_mb: int = 500) -> dict:
    downloads = Path(folder_path) if folder_path else get_downloads_folder()
    
    if not downloads.exists():
        raise FileNotFoundError(f"Downloads folder not found: {downloads}")
    
    min_size_bytes = min_size_mb * 1024 * 1024
    large_files = []
    
    for item in downloads.rglob('*'):
        if item.is_file():
            size = item.stat().st_size
            if size >= min_size_bytes:
                large_files.append({
                    "path": str(item),
                    "size_mb": round(size / (1024 * 1024), 2)
                })
    
    large_files.sort(key=lambda x: x['size_mb'], reverse=True)
    return {"count": len(large_files), "files": large_files}
