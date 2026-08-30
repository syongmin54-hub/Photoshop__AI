import os
import re
from pathlib import Path
from typing import Optional

TEMP_IMG_DIR = Path.cwd() / "temp_images"
TEMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


class StockImageManager:
    """Safe, Non-blocking Local & Pre-downloaded Image Resolver."""

    @staticmethod
    def resolve_image(prompt_or_path: str) -> Optional[str]:
        """Fast local image path resolver without blocking network calls."""
        # 1. Direct local path (e.g., D:\Photos\img.jpg or C:/...)
        path_matches = re.findall(r'[A-Za-z]:[\\/][^\s"\']+', prompt_or_path)
        for pm in path_matches:
            p = Path(pm.strip("\"'"))
            if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".psd"]:
                return str(p.resolve()).replace("\\", "/")
            elif p.is_dir():
                for img in p.iterdir():
                    if img.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                        return str(img.resolve()).replace("\\", "/")

        # 2. Check if already exists in temp_images
        for f in TEMP_IMG_DIR.glob("*.*"):
            if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                return str(f.resolve()).replace("\\", "/")

        return None
