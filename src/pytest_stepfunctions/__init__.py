try:
    from ._version import version
    __version__ = version
except ImportError:
    __version__ = "unknown"


def add(a: int, b: int) -> int:
    return a + b
