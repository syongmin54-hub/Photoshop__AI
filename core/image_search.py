import os
import re
import urllib.parse
from pathlib import Path
from typing import Optional
import requests

TEMP_IMG_DIR = Path.cwd() / "temp_images"
TEMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


class StockImageManager:
    """Finds and downloads royalty-free commercial-safe stock images (Unsplash/Wikimedia) or resolves local files."""

    @staticmethod
    def search_and_download_stock(keyword: str, width: int = 1200, height: int = 800) -> Optional[str]:
        """Search and download a high-res royalty-free commercial image by keyword."""
        clean_kw = re.sub(r"[^\w\s-]", "", keyword).strip().replace(" ", ",")
        encoded_kw = urllib.parse.quote(clean_kw)
        
        # Safe Unsplash high-res direct source URL
        img_url = f"https://images.unsplash.com/photo-1500000000000?auto=format&fit=crop&w={width}&h={height}&q=85"
        # Search via Unsplash Source endpoint or fallback direct keyword query
        search_url = f"https://source.unsplash.com/{width}x{height}/?{encoded_kw}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Try direct fetch with redirect resolution
        try:
            # First try Wikimedia Commons public search API for authentic royalty-free images
            wiki_api = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_kw}&gsrlimit=1&prop=imageinfo&iiprop=url&format=json"
            wiki_resp = requests.get(wiki_api, headers=headers, timeout=5)
            if wiki_resp.status_code == 200:
                data = wiki_resp.json()
                pages = data.get("query", {}).get("pages", {})
                if pages:
                    first_page = next(iter(pages.values()))
                    image_url = first_page.get("imageinfo", [{}])[0].get("url")
                    if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                        down_resp = requests.get(image_url, headers=headers, timeout=10)
                        if down_resp.status_code == 200:
                            file_name = f"stock_{re.sub(r'[^a-zA-Z0-9]', '_', clean_kw)[:20]}.jpg"
                            save_path = TEMP_IMG_DIR / file_name
                            save_path.write_bytes(down_resp.content)
                            return str(save_path.resolve()).replace("\\", "/")

            # Fallback to Unsplash / LoremFlickr free stock
            fallback_url = f"https://loremflickr.com/{width}/{height}/{clean_kw}/all"
            f_resp = requests.get(fallback_url, headers=headers, timeout=10, allow_redirects=True)
            if f_resp.status_code == 200 and len(f_resp.content) > 5000:
                file_name = f"stock_{re.sub(r'[^a-zA-Z0-9]', '_', clean_kw)[:20]}.jpg"
                save_path = TEMP_IMG_DIR / file_name
                save_path.write_bytes(f_resp.content)
                return str(save_path.resolve()).replace("\\", "/")

        except Exception as e:
            print(f"[StockImageManager Warning] 이미지 검색 실패 ({keyword}): {e}")

        return None

    @staticmethod
    def resolve_local_image(file_or_dir_path: str) -> Optional[str]:
        """Validate and return absolute path of a local image file."""
        p = Path(file_or_dir_path.strip("\"'"))
        if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".psd"]:
            return str(p.resolve()).replace("\\", "/")
        elif p.is_dir():
            # Pick first valid image in dir
            for img in p.iterdir():
                if img.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    return str(img.resolve()).replace("\\", "/")
        return None
