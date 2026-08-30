import os
import sys
from pathlib import Path

def get_base_dir() -> Path:
    """Get base directory whether running from script or frozen PyInstaller executable."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent

def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    base_path = get_base_dir()
    candidate = base_path / relative_path
    if candidate.exists():
        return candidate
    # Fallback to current working directory
    return Path.cwd() / relative_path

def ensure_win32():
    """Ensure pywin32 DLLs and modules are properly in sys.path and DLL search directories."""
    try:
        import win32com.client
        return
    except (ImportError, ModuleNotFoundError):
        pass

    for p in sys.path:
        sp_path = Path(p)
        if (sp_path / "pywin32_system32").exists():
            sys32 = sp_path / "pywin32_system32"
            try:
                os.add_dll_directory(str(sys32))
            except Exception:
                pass
            os.environ["PATH"] = str(sys32) + os.pathsep + os.environ.get("PATH", "")
            
            for extra in [sys32, sp_path / "win32", sp_path / "win32" / "lib", sp_path]:
                if str(extra) not in sys.path:
                    sys.path.insert(0, str(extra))
            break

ensure_win32()
