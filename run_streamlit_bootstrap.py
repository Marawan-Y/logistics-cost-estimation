import os, sys, time, socket, threading, webbrowser
from pathlib import Path
from datetime import datetime

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

# --- Resolve important locations ---
FROZEN = getattr(sys, "frozen", False)
EXE_PATH = Path(sys.executable).resolve() if FROZEN else Path(__file__).resolve()
EXE_DIR  = EXE_PATH.parent
# In onefile, PyInstaller extracts into _MEIPASS; in onedir there is no _MEIPASS.
BASE = Path(getattr(sys, "_MEIPASS", EXE_DIR))

# Candidate roots to search for Overview.py and app folders:
candidates = [
    BASE,                          # _MEIPASS (onefile)
    EXE_DIR,                       # dist\logistics_app (onedir) or dist\ (onefile exe dir)
    EXE_DIR.parent,                # dist\
    Path.cwd(),                    # current working directory (if launched via shell)
    EXE_DIR / "logistics_app_content",  # companion content folder we may ship
]

log(f"BASE={BASE}")
log(f"EXE_DIR={EXE_DIR}")
log(".env loaded (if present)")

# Optional: load .env if present in any candidate
try:
    from dotenv import load_dotenv
    for root in candidates:
        envp = root / ".env"
        if envp.exists():
            load_dotenv(envp)
            break
except Exception:
    pass

# --- Streamlit env (quiet + headless inside EXE) ---
os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "0")
os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "1")

# Choose port (env override supported)
PORT = int(os.environ.get("STREAMLIT_SERVER_PORT", "8501"))
HOST = os.environ.get("STREAMLIT_SERVER_ADDRESS", "127.0.0.1")
URL  = f"http://{HOST}:{PORT}"

def _port_is_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False

def _open_when_ready(url: str, host: str, port: int, max_wait_s: int = 45):
    start = time.time()
    while time.time() - start < max_wait_s:
        if _port_is_open(host, port):
            time.sleep(0.5)
            try:
                webbrowser.open(url, new=1, autoraise=True)
            except Exception:
                pass
            return
        time.sleep(0.4)
    # Fallback open anyway
    try:
        webbrowser.open(url, new=1, autoraise=True)
    except Exception:
        pass

# Pick the app root (where Overview.py is)
APP_ROOT = None
for root in candidates:
    if (root / "Overview.py").exists():
        APP_ROOT = root
        break

if APP_ROOT is None:
    log("ERROR: Overview.py not found in any of these locations:")
    for root in candidates:
        log(f"  - {root}")
    # Small diagnostic: list contents of BASE & EXE_DIR
    try:
        log(f"DIR {BASE}: " + ", ".join(sorted(p.name for p in BASE.glob("*"))))
    except Exception:
        pass
    try:
        log(f"DIR {EXE_DIR}: " + ", ".join(sorted(p.name for p in EXE_DIR.glob("*"))))
    except Exception:
        pass
    sys.exit(2)

# Switch to the app root
os.chdir(APP_ROOT)
log(f"APP_ROOT={APP_ROOT}")

# Fire the waiter thread first (so it’s ready as server starts)
threading.Thread(target=_open_when_ready, args=(URL, HOST, PORT), daemon=True).start()

# Import streamlit and print versions for certainty
log("About to import streamlit...")
try:
    import streamlit
    from importlib import metadata as im
    v1 = getattr(streamlit, "__version__", "unknown")
    v2 = "unknown"
    try:
        v2 = im.version("streamlit")
    except Exception:
        pass
    log(f"streamlit import OK. __version__={v1} ; metadata.version={v2}")
except Exception as e:
    log("streamlit import FAILED:")
    import traceback; traceback.print_exc()
    sys.exit(3)

# Run Streamlit (blocks)
import streamlit.web.cli as stcli
sys.argv = [
    "streamlit",
    "run",
    "Overview.py",
    f"--server.address={HOST}",
    f"--server.port={PORT}",
    "--server.headless=true",
    "--browser.gatherUsageStats=false",
]
sys.exit(stcli.main())
