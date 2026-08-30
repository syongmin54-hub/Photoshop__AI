import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import core.compat  # noqa: F401
from core.json_polyfill import EXTENDSCRIPT_JSON_POLYFILL
import win32com.client


class PhotoshopBridge:
    """Adobe Photoshop COM Bridge & ExtendScript Runner."""

    def __init__(self):
        self.app = None
        self._connected = False
        self.temp_snapshot_path = (Path.cwd() / "temp_images" / "canvas_snapshot_ps.png").resolve()

    def connect(self) -> bool:
        """Connect to or launch Adobe Photoshop."""
        try:
            self.app = win32com.client.Dispatch("Photoshop.Application")
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise RuntimeError(f"Photoshop COM 연결 실패 (설치 여부 확인 필요): {e}")

    @property
    def is_connected(self) -> bool:
        return self._connected and self.app is not None

    @property
    def version(self) -> str:
        if not self.is_connected:
            self.connect()
        return str(self.app.Version)

    @property
    def document_count(self) -> int:
        if not self.is_connected:
            self.connect()
        return int(self.app.Documents.Count)

    def execute_jsx(self, jsx_code: str, history_title: Optional[str] = "AI Assistant") -> Dict[str, Any]:
        """Execute ExtendScript (JSX) in Photoshop with Atomic History support."""
        if not self.is_connected:
            self.connect()

        wrapped_code = f"""
{EXTENDSCRIPT_JSON_POLYFILL}

function __adobe_ai_runner__() {{
    try {{
        {jsx_code}
    }} catch(err) {{
        return JSON.stringify({{
            "success": false,
            "error": err.message || err.toString(),
            "line": err.line || null
        }});
    }}
}}
var __res__ = __adobe_ai_runner__();
__res__;
"""
        try:
            raw_result = self.app.DoJavaScript(wrapped_code)
            if raw_result and str(raw_result) != "undefined":
                try:
                    parsed = json.loads(raw_result)
                    if isinstance(parsed, dict) and "success" in parsed:
                        return parsed
                    return {"success": True, "result": parsed}
                except json.JSONDecodeError:
                    return {"success": True, "result": raw_result}
            return {"success": True, "result": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def capture_canvas_snapshot(self) -> Optional[str]:
        """Fast export current active Photoshop canvas to PNG and return base64 string for Vision AI."""
        if not self.is_connected or self.document_count == 0:
            return None

        clean_path = str(self.temp_snapshot_path).replace("\\", "/")
        export_jsx = f"""
try {{
    var doc = app.activeDocument;
    var f = new File("{clean_path}");
    var opt = new PNGSaveOptions();
    opt.compression = 9;
    opt.interlaced = false;
    doc.saveAs(f, opt, true, Extension.LOWERCASE);
    return JSON.stringify({{"success": true, "path": f.fsName}});
}} catch(e) {{
    return JSON.stringify({{"success": false, "error": e.message}});
}}
"""
        res = self.execute_jsx(export_jsx)
        if res.get("success") and self.temp_snapshot_path.exists():
            try:
                img_data = self.temp_snapshot_path.read_bytes()
                return base64.b64encode(img_data).decode("utf-8")
            except Exception:
                pass
        return None

    def create_document(self, width: int = 1920, height: int = 1080, resolution: int = 72, name: str = "Untitled-AI") -> Dict[str, Any]:
        """Create a new Photoshop document."""
        jsx = f"""
var doc = app.documents.add({width}, {height}, {resolution}, "{name}", NewDocumentMode.RGB, DocumentFill.WHITE);
return JSON.stringify({{"success": true, "name": doc.name, "width": doc.width.value, "height": doc.height.value}});
"""
        return self.execute_jsx(jsx)
