"""Command-line entry point for the kaloricketabulky package."""

import sys

from kaloricketabulky import __version__


def main() -> int:
    """Run the command-line interface.

    Returns the process exit code.
    """
    sys.stdout.write(f"kaloricketabulky-sdk {__version__}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
