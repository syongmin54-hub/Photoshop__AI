import json
import os
import re
import urllib.parse
from pathlib import Path
from typing import Optional
import requests

TEMP_IMG_DIR = Path.cwd() / "temp_images"
TEMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


class StockImageManager:
    """Finds and downloads images from multiple sources (Pinterest, Unsplash, Wikimedia, Pixabay, Local)."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    @classmethod
    def resolve_pinterest_pin(cls, pin_url: str) -> Optional[str]:
        """Extract original high-res image from a Pinterest Pin URL."""
        try:
            resp = requests.get(pin_url, headers=cls.HEADERS, timeout=10)
            if resp.status_code == 200:
                # Find high-res pinimg URL (e.g., https://i.pinimg.com/originals/... or /736x/...)
                matches = re.findall(r'https://i\.pinimg\.com/[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
                if matches:
                    # Prefer originals or highest resolution
                    best_match = matches[0]
                    for m in matches:
                        if "/originals/" in m or "/736x/" in m:
                            best_match = m
                            break
                    
                    down_resp = requests.get(best_match, headers=cls.HEADERS, timeout=10)
                    if down_resp.status_code == 200:
                        file_name = f"pinterest_{abs(hash(pin_url)) % 100000}.jpg"
                        save_path = TEMP_IMG_DIR / file_name
                        save_path.write_bytes(down_resp.content)
                        return str(save_path.resolve()).replace("\\", "/")
        except Exception as e:
            print(f"[Pinterest Resolver Warning] 핀 추출 실패 ({pin_url}): {e}")
        return None

    @classmethod
    def search_pinterest_images(cls, keyword: str) -> Optional[str]:
        """Search Pinterest visual database for aesthetics and extract high-res image."""
        try:
            encoded_kw = urllib.parse.quote(keyword)
            # Use DuckDuckGo / Pinterest public image search proxy
            ddg_url = f"https://html.duckduckgo.com/html/?q=site:pinterest.com+{encoded_kw}"
            resp = requests.get(ddg_url, headers=cls.HEADERS, timeout=10)
            if resp.status_code == 200:
                pin_urls = re.findall(r'https?://(?:[a-z]{2}\.)?pinterest\.com/pin/[0-9]+', resp.text)
                if pin_urls:
                    first_pin = pin_urls[0]
                    res = cls.resolve_pinterest_pin(first_pin)
                    if res:
                        return res

            # Fallback to direct pinimg regex search
            img_matches = re.findall(r'https://i\.pinimg\.com/[^"\'\s]+\.(?:jpg|jpeg|png)', resp.text)
            if img_matches:
                down_resp = requests.get(img_matches[0], headers=cls.HEADERS, timeout=10)
                if down_resp.status_code == 200:
                    file_name = f"pinterest_search_{abs(hash(keyword)) % 100000}.jpg"
                    save_path = TEMP_IMG_DIR / file_name
                    save_path.write_bytes(down_resp.content)
                    return str(save_path.resolve()).replace("\\", "/")
        except Exception as e:
            print(f"[Pinterest Search Warning] 핀터레스트 검색 실패 ({keyword}): {e}")

        # Fallback to standard stock
        return cls.search_and_download_stock(keyword)

    @classmethod
    def search_and_download_stock(cls, keyword: str, width: int = 1200, height: int = 800) -> Optional[str]:
        """Search and download a high-res royalty-free commercial image by keyword."""
        clean_kw = re.sub(r"[^\w\s-]", "", keyword).strip().replace(" ", ",")
        encoded_kw = urllib.parse.quote(clean_kw)

        # 1. Wikimedia Commons public search
        try:
            wiki_api = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded_kw}&gsrlimit=1&prop=imageinfo&iiprop=url&format=json"
            wiki_resp = requests.get(wiki_api, headers=cls.HEADERS, timeout=5)
            if wiki_resp.status_code == 200:
                data = wiki_resp.json()
                pages = data.get("query", {}).get("pages", {})
                if pages:
                    first_page = next(iter(pages.values()))
                    image_url = first_page.get("imageinfo", [{}])[0].get("url")
                    if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                        down_resp = requests.get(image_url, headers=cls.HEADERS, timeout=10)
                        if down_resp.status_code == 200:
                            file_name = f"stock_{re.sub(r'[^a-zA-Z0-9]', '_', clean_kw)[:20]}.jpg"
                            save_path = TEMP_IMG_DIR / file_name
                            save_path.write_bytes(down_resp.content)
                            return str(save_path.resolve()).replace("\\", "/")
        except Exception:
            pass

        # 2. Fallback to Unsplash / LoremFlickr
        try:
            fallback_url = f"https://loremflickr.com/{width}/{height}/{clean_kw}/all"
            f_resp = requests.get(fallback_url, headers=cls.HEADERS, timeout=10, allow_redirects=True)
            if f_resp.status_code == 200 and len(f_resp.content) > 5000:
                file_name = f"stock_{re.sub(r'[^a-zA-Z0-9]', '_', clean_kw)[:20]}.jpg"
                save_path = TEMP_IMG_DIR / file_name
                save_path.write_bytes(f_resp.content)
                return str(save_path.resolve()).replace("\\", "/")
        except Exception:
            pass

        return None

    @classmethod
    def resolve_image(cls, prompt_or_path: str) -> Optional[str]:
        """Auto-route image resolution: Pinterest URL/Search, Local Path, or Stock Search."""
        # A. Pinterest URL in prompt
        pin_match = re.search(r'https?://(?:[a-z]{2}\.)?pinterest\.com/pin/[^\s"\']+', prompt_or_path)
        if pin_match:
            return cls.resolve_pinterest_pin(pin_match.group(0))

        # B. Direct local path
        path_matches = re.findall(r'[A-Za-z]:[\\/][^\s"\']+', prompt_or_path)
        for pm in path_matches:
            local_res = cls.resolve_local_image(pm)
            if local_res:
                return local_res

        # C. Pinterest explicitly requested
        if "핀터레스트" in prompt_or_path or "pinterest" in prompt_or_path.lower():
            clean_kw = prompt_or_path.replace("핀터레스트", "").replace("pinterest", "").replace("에서", "").replace("검색", "").replace("찾아", "").strip()
            return cls.search_pinterest_images(clean_kw)

        # D. General stock search
        return cls.search_and_download_stock(prompt_or_path)

    @staticmethod
    def resolve_local_image(file_or_dir_path: str) -> Optional[str]:
        """Validate and return absolute path of a local image file."""
        p = Path(file_or_dir_path.strip("\"'"))
        if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".psd"]:
            return str(p.resolve()).replace("\\", "/")
        elif p.is_dir():
            for img in p.iterdir():
                if img.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                    return str(img.resolve()).replace("\\", "/")
        return None
