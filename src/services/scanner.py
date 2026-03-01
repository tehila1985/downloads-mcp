from pathlib import Path
from collections import defaultdict
from ..models import ScanResult
from ..utils import get_downloads_folder

def scan_downloads(folder_path: str = None) -> dict:
    downloads = Path(folder_path) if folder_path else get_downloads_folder()
    
    if not downloads.exists():
        raise FileNotFoundError(f"Downloads folder not found: {downloads}")
    
    total_files = 0
    total_size = 0
    by_category = defaultdict(int)
    by_extension = defaultdict(int)
    
    categories = {
        'Documents': {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx', '.odt'},
        'Media': {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3', '.avi', '.mov', '.mkv'},
        'Installers': {'.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm'},
        'Code': {'.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.json', '.xml'},
        'Archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'},
    }
    
    for item in downloads.rglob('*'):
        if item.is_file():
            total_files += 1
            size = item.stat().st_size
            total_size += size
            ext = item.suffix.lower()
            by_extension[ext] += 1
            
            category = 'Other'
            for cat, exts in categories.items():
                if ext in exts:
                    category = cat
                    break
            by_category[category] += 1
    
    return ScanResult(
        total_files=total_files,
        total_size=total_size,
        by_category=dict(by_category),
        by_extension=dict(by_extension)
    ).model_dump()
