"""Typesafe async read-only SDK for the kaloricketabulky.cz internal API."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("kaloricketabulky-sdk")
except PackageNotFoundError:  # pragma: no cover - only hit when running from a non-installed tree
    __version__ = "0.0.0"

__all__ = ["__version__"]
