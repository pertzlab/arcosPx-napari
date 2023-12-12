try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
from ._widget import remove_background, track_events

__all__ = ("remove_background", "track_events")
