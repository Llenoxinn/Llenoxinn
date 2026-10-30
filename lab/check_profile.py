#!/usr/bin/env python3
"""Check the GitHub profile's local links, generated blocks and image assets.

Run after rebuilding the lab: python lab/check_profile.py
No network, token or third-party dependencies are needed.
"""
import re
import tempfile
import xml.etree.ElementTree as ET
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from notebook import ROOT, picture, replace_block

MARKERS = {"STACK", "PROJECTS", "CONTRIBUTIONS", "LEETCODE", "ASSAY"}


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.anchors = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.anchors.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.anchors.add(attrs["name"])
        for name in ("href", "src"):
            if attrs.get(name):
                self.targets.append(attrs[name])
        if attrs.get("srcset"):
            self.targets.extend(part.strip().split()[0] for part in attrs["srcset"].split(","))
        if tag == "img":
            assert attrs.get("alt", "").strip(), "Image is missing useful alt text"


def check_helpers():
    """Marker updates must preserve neighbouring content and remain idempotent."""
    with tempfile.TemporaryDirectory(prefix="check-profile-", dir=ROOT / "lab") as folder:
        path = Path(folder) / "README.md"
        path.write_text("before\n<!-- TEST:START -->old<!-- TEST:END -->\nafter\n", encoding="utf-8")
        assert replace_block("TEST", "new", path)
        assert path.read_text(encoding="utf-8") == "before\n<!-- TEST:START -->\nnew\n<!-- TEST:END -->\nafter\n"
        assert not replace_block("TEST", "new", path)
        try:
            replace_block("MISSING", "new", path)
        except SystemExit:
            pass
        else:
            raise AssertionError("Missing block markers must reject an update")
    paired = picture("example", "An example", width="100%", ext="webp", query="v=1")
    assert 'srcset="assets/example-dark.webp?v=1"' in paired
    assert 'src="assets/example-light.webp?v=1"' in paired


def main():
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    size = len(text.encode("utf-8"))
    assert size < 500 * 1024, f"README is {size:,} bytes; GitHub truncates above 500 KiB"
    blocks = re.findall(r"<!-- ([A-Z]+):(START|END) -->", text)
    assert {name for name, _ in blocks} == MARKERS, "Generated block names changed"
    for name in MARKERS:
        start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
        assert text.count(start) == text.count(end) == 1, f"{name} markers must occur exactly once"
        assert text.index(start) < text.index(end), f"{name} markers are reversed"
    stls = list(re.finditer(r"^```stl\s*$", text, re.M))
    assert len(stls) <= 1, "GitHub supports only one reliable inline STL viewer here"
    assert not re.search(r"^#{1,6}\s", text, re.M), "Section headers are drawn; Markdown headings add GitHub's rule lines"

    prose = re.sub(r"^```[^\n]*\n.*?^```\s*$", "", text, flags=re.M | re.S)
    refs = References()
    refs.feed(prose)
    refs.targets.extend(re.findall(r"!?\[[^\]]*\]\(<?([^\s)>]+)>?\)", prose))
    for title in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", prose, re.M):
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        refs.anchors.add(slug)

    files = set()
    for raw in refs.targets:
        target = urlsplit(unescape(raw))
        if target.scheme:
            assert target.scheme in {"https", "http", "mailto"}, f"Unsupported link scheme: {raw}"
            assert target.netloc if target.scheme != "mailto" else "@" in target.path, f"Malformed link: {raw}"
            continue
        assert not target.netloc, f"Protocol-relative URL: {raw}"
        if not target.path:
            assert not target.fragment or unquote(target.fragment) in refs.anchors, f"Missing section anchor: {raw}"
            continue
        path = (ROOT / unquote(target.path)).resolve()
        assert path.is_relative_to(ROOT.resolve()), f"Local link leaves the repository: {raw}"
        assert path.exists(), f"Missing local target: {raw}"
        if path.is_file():
            files.add(path)
        theme = re.search(r"-(dark|light)(\.[^.]+)$", path.name)
        if theme:
            other = "light" if theme[1] == "dark" else "dark"
            pair = path.with_name(path.name[:theme.start()] + "-" + other + theme[2])
            assert pair.is_file(), f"Missing theme counterpart: {pair.relative_to(ROOT)}"
    for path in files:
        if path.suffix == ".svg":
            svg = ET.parse(path).getroot()
            assert svg.tag == "{http://www.w3.org/2000/svg}svg", f"Invalid SVG root: {path.name}"
            assert svg.get("viewBox"), f"SVG has no responsive viewBox: {path.name}"
            assert not svg.findall(".//{http://www.w3.org/2000/svg}script"), f"SVG scripts do not run in GitHub images: {path.name}"
    check_helpers()
    print(f"Profile checks passed: {size:,} bytes, {len(MARKERS)} generated blocks, {len(files)} local files, {len(stls)} inline STL viewer(s).")


if __name__ == "__main__":
    main()
