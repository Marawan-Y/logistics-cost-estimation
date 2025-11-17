#!/bin/bash

# -----------------------------------------------------------------------------
#  build_executable_mac.sh
#
#  Compile the multipage Streamlit application into a self‑contained macOS
#  executable using PyInstaller.  This script installs PyInstaller (if
#  necessary), cleans previous build artefacts, and bundles the application
#  code along with the resource directories (pages, utils, .streamlit) and
#  the default data file (logistics_data.json).  The resulting binary will
#  reside in the `release` directory.
#
#  To create a .app bundle or a .dmg distribution, additional tooling
#  (e.g. create‑dmg) can be used after this step; the produced binary can be
#  wrapped accordingly.
# -----------------------------------------------------------------------------

set -e

# Ensure Python 3 is available
if ! command -v python3 > /dev/null 2>&1; then
  echo "Python3 is required but was not found on your PATH. Please install Python 3.8+ and try again." >&2
  exit 1
fi

echo "Installing/updating PyInstaller..."
python3 -m pip install --upgrade pip > /dev/null
python3 -m pip install --upgrade pyinstaller > /dev/null

# Remove previous artefacts
rm -rf build dist logistics_app.spec

echo "Building standalone executable..."
pyinstaller --noconsole --onefile \
  --add-data "pages:pages" \
  --add-data "utils:utils" \
  --add-data ".streamlit:.streamlit" \
  --add-data "logistics_data.json:." \
  --name logistics_app \
  Overview.py

# Organise output
mkdir -p release
if [ -f dist/logistics_app ]; then
  mv dist/logistics_app release/
fi

echo "Build complete! The binary is located in the release directory (release/logistics_app)."