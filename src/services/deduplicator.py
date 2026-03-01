from pathlib import Path
from collections import defaultdict
from ..utils import get_downloads_folder, get_file_hash

def deduplicate_by_hash(folder_path: str = None, dry_run: bool = False) -> dict:
    downloads = Path(folder_path) if folder_path else get_downloads_folder()
    
    if not downloads.exists():
        raise FileNotFoundError(f"Downloads folder not found: {downloads}")
    
    hash_map = defaultdict(list)
    
    for item in downloads.rglob('*'):
        if item.is_file():
            try:
                file_hash = get_file_hash(item)
                hash_map[file_hash].append(item)
            except Exception:
                continue
    
    duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
    removed = []
    
    for file_hash, files in duplicates.items():
        files.sort(key=lambda x: x.stat().st_mtime)
        for duplicate in files[1:]:
            if not dry_run:
                duplicate.unlink()
            removed.append(str(duplicate))
    
    return {"removed_count": len(removed), "removed_files": removed}

def deduplicate_folders(folder_path: str = None, dry_run: bool = False) -> dict:
    downloads = Path(folder_path) if folder_path else get_downloads_folder()
    
    if not downloads.exists():
        raise FileNotFoundError(f"Downloads folder not found: {downloads}")
    
    def get_folder_hash(folder: Path) -> str:
        hashes = []
        for item in sorted(folder.rglob('*')):
            if item.is_file():
                try:
                    hashes.append(get_file_hash(item))
                except Exception:
                    continue
        return ''.join(hashes)
    
    folder_map = defaultdict(list)
    
    for item in downloads.iterdir():
        if item.is_dir():
            try:
                folder_hash = get_folder_hash(item)
                folder_map[folder_hash].append(item)
            except Exception:
                continue
    
    duplicates = {h: folders for h, folders in folder_map.items() if len(folders) > 1}
    removed = []
    
    for folder_hash, folders in duplicates.items():
        folders.sort(key=lambda x: x.stat().st_mtime)
        for duplicate in folders[1:]:
            if not dry_run:
                import shutil
                shutil.rmtree(duplicate)
            removed.append(str(duplicate))
    
    return {"removed_count": len(removed), "removed_folders": removed}
