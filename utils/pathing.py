# utils/pathing.py
from pathlib import Path
import sys

def app_path(*relative_parts: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base.joinpath(*relative_parts)
