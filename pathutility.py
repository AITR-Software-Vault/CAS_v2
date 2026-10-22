from pathlib import Path
import sys
from PIL import Image

def get_application_dir() -> Path:
    """
    Returns the directory containing the application assets.
    Works both during normal Python execution and inside a PyInstaller bundled executable.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent

APP_DIR = get_application_dir()

IMAGE_DIR = APP_DIR / "images"
ASSET_DIR = APP_DIR / "assets"
ICON_DIR = ASSET_DIR / "icons"
FONT_DIR = ASSET_DIR / "fonts"

def image_path(filename: str) -> Path:
    return IMAGE_DIR / filename

def icon_path(filename: str) -> Path:
    return ICON_DIR / filename

def font_path(filename: str) -> Path:
    return FONT_DIR / filename

def get_output_dir() -> Path:
    try:
        # Try true Windows API to get the real Documents folder (handles OneDrive/Localization)
        import ctypes.wintypes
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        if buf.value:
            output_dir = Path(buf.value) / "AutoCAS Reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            return output_dir
    except Exception:
        pass
        
    try:
        output_dir = Path.home() / "Documents" / "AutoCAS Reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    except Exception:
        # Fallback to the User's root home directory
        output_dir = Path.home() / "AutoCAS Reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

def validate_rgba_transparency(path: Path):
    try:
        image = Image.open(path).convert("RGBA")
        alpha = image.getchannel("A")
        if alpha.getextrema() == (255, 255):
            raise ValueError(f"Logo is fully opaque and has no transparency: {path}")
    except Exception as e:
        raise ValueError(f"Failed to validate transparency for {path}: {e}")

def validate_required_assets() -> None:
    required_assets = [
        image_path("acropolis_logo_transparent.png"),
        image_path("footer_logo_transparent.png"),
        icon_path("sleep.png"),
        icon_path("movement.png"),
        icon_path("people.png"),
        icon_path("workload.png"),
        icon_path("conversation.png"),
        icon_path("reach_out.png"),
    ]

    missing_assets = [str(path) for path in required_assets if not path.is_file()]

    if missing_assets:
        raise FileNotFoundError(
            "Required PDF assets are missing:\n" + "\n".join(missing_assets)
        )
        
    # validate_rgba_transparency(image_path("acropolis_logo_transparent.png"))
    # validate_rgba_transparency(image_path("footer_logo_transparent.png"))
