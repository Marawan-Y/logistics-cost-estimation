# pyi_hooks/rth_streamlit_version_shim.py
# Runtime hook: ensure importlib.metadata can report a Streamlit version
# even when .dist-info metadata isn't present in the frozen app.

import os

try:
    import importlib.metadata as _md  # Py3.8+
except Exception:  # pragma: no cover
    _md = None

_VER = os.environ.get("STREAMLIT_BUNDLED_VERSION")

if _md and _VER:
    # Wrap importlib.metadata.version / distribution so that asking for
    # "streamlit" never raises PackageNotFoundError inside the EXE.
    _real_version = _md.version
    _real_distribution = _md.distribution

    def _safe_version(name: str):
        if name == "streamlit":
            return _VER
        return _real_version(name)

    def _safe_distribution(name: str):
        if name == "streamlit":
            # Provide a tiny shim object with the .metadata mapping used by Streamlit.
            class _DistShim:
                def __init__(self, n, v):
                    self._name = n
                    self.metadata = {"Name": n, "Version": v}
            return _DistShim("streamlit", _VER)
        return _real_distribution(name)

    _md.version = _safe_version
    _md.distribution = _safe_distribution
