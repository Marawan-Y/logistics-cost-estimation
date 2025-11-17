# pyi_hooks/hook-streamlit.py
# Enhanced PyInstaller hook for Streamlit to ensure all static assets are bundled

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_submodules,
    copy_metadata,
    get_package_paths
)
import os

# Collect metadata
datas = copy_metadata("streamlit")

# Collect all submodules
hiddenimports = collect_submodules("streamlit")

# Get the streamlit package directory
pkg_base, pkg_dir = get_package_paths("streamlit")

# Explicitly add static and template directories
static_dir = os.path.join(pkg_dir, "static")
templates_dir = os.path.join(pkg_dir, "web", "server", "templates")

if os.path.exists(static_dir):
    # Add entire static directory
    datas.append((static_dir, "streamlit/static"))
    print(f"[hook-streamlit] Added static dir: {static_dir}")
else:
    print(f"[hook-streamlit] WARNING: static dir not found at {static_dir}")

if os.path.exists(templates_dir):
    # Add templates directory
    datas.append((templates_dir, "streamlit/web/server/templates"))
    print(f"[hook-streamlit] Added templates dir: {templates_dir}")
else:
    print(f"[hook-streamlit] WARNING: templates dir not found at {templates_dir}")

# Collect all data files from streamlit package
datas += collect_data_files("streamlit", include_py_files=False)

# Ensure these critical modules are imported
hiddenimports += [
    "streamlit.runtime",
    "streamlit.runtime.scriptrunner",
    "streamlit.runtime.state",
    "streamlit.web.bootstrap",
    "streamlit.web.cli",
    "streamlit.web.server",
    "streamlit.web.server.server",
    "streamlit.web.server.routes",
]

print(f"[hook-streamlit] Total data entries: {len(datas)}")
print(f"[hook-streamlit] Total hidden imports: {len(hiddenimports)}")