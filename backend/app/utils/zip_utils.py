# backend/app/utils/zip_utils.py

import zipfile
from typing import List
import os

def zip_files(file_paths: List[str], zip_path: str):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for path in file_paths:
            zipf.write(path, arcname=os.path.basename(path))
