#!/usr/bin/env python3
"""Rebuild the profile's deterministic artwork with the active lab theme."""
import subprocess
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent


def main():
    for script in ("build_banner.py", "build_headers.py", "build_shelf.py", "build_projects.py"):
        subprocess.run([sys.executable, str(LAB / script)], check=True, cwd=LAB.parent)


if __name__ == "__main__":
    main()
