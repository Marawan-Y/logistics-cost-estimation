# pyi_hooks/rth_fix_streamlit_metadata.py
# Purpose: ensure importlib.metadata can resolve "streamlit" in PyInstaller onefile.

import sys

# PyInstaller ensures stdlib importlib.metadata exists on 3.8+.
try:
    import importlib.metadata as _im
except Exception:  # extremely old Python — not your case, but be safe
    _im = None

if _im:
    try:
        # If this doesn't raise, metadata is discoverable — nothing to do.
        _im.version("streamlit")
    except Exception:
        # Fallback: import streamlit first, then synthesize a Distribution stub.
        # Streamlit exposes __version__ in its package.
        try:
            import streamlit  # noqa
            _ver = getattr(streamlit, "__version__", None)
        except Exception:
            _ver = None

        if _ver:
            # Minimal shim: register a synthetic distribution so version() works.
            class _FakeDist(_im.Distribution):  # type: ignore[attr-defined]
                def __init__(self, name, version):
                    self._name = name
                    self._version = version

                @property
                def metadata(self):
                    from email.message import Message
                    m = Message()
                    m["Name"] = self._name
                    m["Version"] = self._version
                    return m

            class _Finder:
                @classmethod
                def find_distributions(cls, context=_im.DistributionFinder.Context()):
                    name = getattr(context, "name", None)
                    if name and name.lower().replace("-", "_") == "streamlit":
                        yield _FakeDist("streamlit", _ver)

            # PEP 451-style finder registration
            _im.distribution  # attribute exists
            try:
                _im.DistributionFinder  # type: ignore[attr-defined]
                sys.meta_path.append(_Finder())  # last resort
            except Exception:
                # On newer CPython, importlib.metadata reads entry_points of
                # installed distributions; we simply short-circuit later calls
                # to version("streamlit") by monkeypatching.
                _orig_version = _im.version

                def _version(name: str):
                    if name.lower().replace("-", "_") == "streamlit":
                        return _ver
                    return _orig_version(name)

                _im.version = _version  # type: ignore[assignment]
