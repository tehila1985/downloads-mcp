from pathlib import Path
import zipfile
import shutil
from ..utils import get_downloads_folder

def auto_extract_and_cleanup(folder_path: str = None, dry_run: bool = False) -> dict:
    downloads = Path(folder_path) if folder_path else get_downloads_folder()
    
    if not downloads.exists():
        raise FileNotFoundError(f"Downloads folder not found: {downloads}")
    
    extracted = []
    
    for item in downloads.rglob('*.zip'):
        if item.is_file():
            try:
                extract_dir = item.parent / item.stem
                if not dry_run:
                    with zipfile.ZipFile(item, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    item.unlink()
                extracted.append(str(item))
            except Exception as e:
                continue
    
    return {"extracted_count": len(extracted), "extracted_files": extracted}
