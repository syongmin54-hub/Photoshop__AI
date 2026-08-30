import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import core.compat  # noqa: F401
from core.json_polyfill import EXTENDSCRIPT_JSON_POLYFILL
import win32com.client


class IllustratorBridge:
    """Adobe Illustrator COM Bridge & High-Performance Decomposed ExtendScript Runner."""

    def __init__(self):
        self.app = None
        self._connected = False
        self.temp_img_dir = (Path.cwd() / "temp_images").resolve()
        self.temp_img_dir.mkdir(parents=True, exist_ok=True)
        self.temp_snapshot_path = self.temp_img_dir / "canvas_snapshot.png"

    def connect(self) -> bool:
        """Connect to or launch Adobe Illustrator."""
        try:
            self.app = win32com.client.Dispatch("Illustrator.Application")
            try:
                self.app.UserInteractionLevel = -1  # DONTDISPLAYALERTS
            except Exception:
                pass
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise RuntimeError(f"Illustrator COM 연결 실패: {e}")

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
        try:
            return int(self.app.Documents.Count)
        except Exception:
            return 0

    def execute_jsx(self, jsx_code: str) -> Dict[str, Any]:
        """Execute ExtendScript (JSX) in Illustrator with performance wrapper."""
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
app.redraw();
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

    def capture_canvas_snapshot(self, scale_percent: float = 20.0) -> Optional[str]:
        """Fast export active canvas to lightweight PNG for Vision AI."""
        if not self.is_connected or self.document_count == 0:
            return None

        clean_path = str(self.temp_snapshot_path).replace("\\", "/")
        export_jsx = f"""
try {{
    var doc = app.activeDocument;
    var f = new File("{clean_path}");
    var opt = new ExportOptionsPNG24();
    opt.antiAliasing = false;
    opt.transparency = false;
    opt.artBoardClipping = true;
    opt.horizontalScale = {scale_percent};
    opt.verticalScale = {scale_percent};
    doc.exportFile(f, ExportType.PNG24, opt);
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

    def capture_all_artboards_snapshots(self, scale_percent: float = 20.0) -> List[Dict[str, Any]]:
        """Decomposed Multi-page Vision: Export each Artboard/Page as an individual visual snapshot."""
        if not self.is_connected or self.document_count == 0:
            return []

        clean_dir = str(self.temp_img_dir).replace("\\", "/")
        export_all_jsx = f"""
try {{
    var doc = app.activeDocument;
    var list = [];
    var opt = new ExportOptionsPNG24();
    opt.antiAliasing = false;
    opt.transparency = false;
    opt.artBoardClipping = true;
    opt.horizontalScale = {scale_percent};
    opt.verticalScale = {scale_percent};

    for (var a = 0; a < doc.artboards.length; a++) {{
        doc.artboards.setActiveArtboardIndex(a);
        var ab = doc.artboards[a];
        var outPath = "{clean_dir}/page_" + a + ".png";
        var f = new File(outPath);
        doc.exportFile(f, ExportType.PNG24, opt);
        list.push({{"index": a, "name": ab.name, "path": f.fsName}});
    }}
    return JSON.stringify({{"success": true, "pages": list}});
}} catch(e) {{
    return JSON.stringify({{"success": false, "error": e.message}});
}}
"""
        res = self.execute_jsx(export_all_jsx)
        pages_b64 = []
        if res.get("success") and "pages" in res.get("result", {}):
            for p in res["result"]["pages"]:
                p_file = Path(p["path"])
                if p_file.exists():
                    try:
                        b64 = base64.b64encode(p_file.read_bytes()).decode("utf-8")
                        pages_b64.append({
                            "index": p["index"],
                            "name": p["name"],
                            "base64": b64
                        })
                    except Exception:
                        pass
        return pages_b64

    def create_document(self, width_pt: float = 800.0, height_pt: float = 600.0, name: str = "Untitled-AI") -> Dict[str, Any]:
        """Create a new document with specified dimensions (in points)."""
        jsx = f"""
var doc = app.documents.add(DocumentColorSpace.RGB, {width_pt}, {height_pt});
return JSON.stringify({{"success": true, "name": doc.name, "width": doc.width, "height": doc.height}});
"""
        return self.execute_jsx(jsx)
