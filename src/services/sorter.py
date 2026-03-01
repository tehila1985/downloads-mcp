from pathlib import Path
import shutil
from ..utils import get_downloads_folder

def smart_sort_files(folder_path: str = None, dry_run: bool = False) -> dict:
    downloads = Path(folder_path) if folder_path else get_downloads_folder()
    
    if not downloads.exists():
        raise FileNotFoundError(f"Downloads folder not found: {downloads}")
    
    categories = {
        'Documents': {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx', '.odt', '.rtf'},
        'Media': {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mp3', '.avi', '.mov', '.mkv', '.wav', '.flac'},
        'Installers': {'.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.apk'},
        'Code': {'.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.json', '.xml', '.yaml', '.yml'},
        'Archives': {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'},
    }
    
    moved = {}
    
    for item in downloads.iterdir():
        if item.is_file():
            ext = item.suffix.lower()
            category = 'Other'
            
            for cat, exts in categories.items():
                if ext in exts:
                    category = cat
                    break
            
            target_dir = downloads / category
            if not dry_run:
                target_dir.mkdir(exist_ok=True)
                target_path = target_dir / item.name
                counter = 1
                while target_path.exists():
                    target_path = target_dir / f"{item.stem}_{counter}{item.suffix}"
                    counter += 1
                shutil.move(str(item), str(target_path))
            
            moved[str(item)] = str(target_dir / item.name) if not dry_run else f"Would move to {category}"
    
    return {"moved_files": len(moved), "details": moved}
