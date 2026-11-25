#!/usr/bin/env python3
"""Redraw the whole profile (build_lab.py) and stamp every image URL with its content hash."""
import re
import subprocess
import sys
from pathlib import Path

from notebook import README, ROOT, stamp

LAB = Path(__file__).resolve().parent


def stamp_static_urls():
    """Append/refresh ?v=<sha1> on every local SVG URL in README so GitHub's CDN busts immediately."""
    text = README.read_text(encoding="utf-8")

    def sub(m):
        attr, rel = m.group(1), m.group(2)
        path = ROOT / rel
        if not path.is_file():
            return m.group(0)
        return f'{attr}="{rel}?v={stamp(path.read_text(encoding="utf-8"))}"'

    new = re.sub(r'(srcset|src)="(assets/[^"?]+\.svg)(?:\?v=[0-9a-f]+)?"', sub, text)
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("stamped static SVG URLs in README")


def main():
    for script in ("build_lab.py",):
        subprocess.run([sys.executable, str(LAB / script)], check=True, cwd=LAB.parent)
    stamp_static_urls()


if __name__ == "__main__":
    main()
