import json
from typing import Any, Dict, Optional
import core.compat  # noqa: F401
from core.json_polyfill import EXTENDSCRIPT_JSON_POLYFILL
import win32com.client


class IllustratorBridge:
    """Adobe Illustrator COM Bridge & ExtendScript Runner."""

    def __init__(self):
        self.app = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to or launch Adobe Illustrator."""
        try:
            self.app = win32com.client.Dispatch("Illustrator.Application")
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
        return int(self.app.Documents.Count)

    def execute_jsx(self, jsx_code: str) -> Dict[str, Any]:
        """Execute ExtendScript (JSX) in Illustrator and return structured output."""
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

    def create_document(self, width_pt: float = 800.0, height_pt: float = 600.0, name: str = "Untitled-AI") -> Dict[str, Any]:
        """Create a new document with specified dimensions (in points)."""
        jsx = f"""
var doc = app.documents.add(DocumentColorSpace.RGB, {width_pt}, {height_pt});
return JSON.stringify({{"success": true, "name": doc.name, "width": doc.width, "height": doc.height}});
"""
        return self.execute_jsx(jsx)
