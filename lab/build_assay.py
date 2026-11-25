#!/usr/bin/env python3
"""picoGym progress as the tube rack on the lab console, from lab/data/picoctf.json.

picoCTF has no public API, so update that file after solving; the rack redraws
assets/live/picogym-*.svg and refills the ASSAY block.

    python lab/build_assay.py
"""
import console


def main():
    changed = console.write_live("picogym")
    print(f"picogym: README {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
