#!/usr/bin/env python3
"""ui-verify reference alignment loop: pixel diff + heatmap between the
implemented page's screenshot and the reference screenshot.

Usage:
    python diff.py <impl-screenshot> <ref-screenshot> [-o heatmap-out-path] [--threshold 24]

Output: overall difference ratio + top-to-bottom 10-band hotspot distribution
+ heatmap (differing pixels overlaid in red). The ratio is a locator aid, not a
pass gate (see the alignment-loop boundary in ui-verify SKILL.md).
"""
import argparse
import os
import sys

from PIL import Image, ImageChops

BANDS = 10


def main():
    p = argparse.ArgumentParser(description="screenshot pixel diff (ui-verify reference alignment loop)")
    p.add_argument("impl", help="implemented page screenshot")
    p.add_argument("ref", help="reference screenshot")
    p.add_argument("-o", "--out", default=None, help="heatmap output path (default <impl>.diff.png)")
    p.add_argument("--threshold", type=int, default=24,
                   help="grayscale diff threshold per pixel, default 24 (tolerates JPEG noise / anti-aliasing)")
    a = p.parse_args()

    impl = Image.open(a.impl).convert("RGB")
    ref = Image.open(a.ref).convert("RGB")
    if impl.size != ref.size:
        print(f"[warn] size mismatch impl={impl.size} ref={ref.size}; "
              f"ref was resized to impl's size — resizing cannot fix breakpoint misalignment; "
              f"same-structure replication tasks should re-shoot both at a unified viewport first")
        ref = ref.resize(impl.size)

    d = ImageChops.difference(impl, ref).convert("L")
    w, h = d.size
    hist = d.histogram()
    total = w * h
    changed = sum(hist[a.threshold + 1:])
    ratio = changed / total

    print(f"impl: {impl.size}  ref: {ref.size}  threshold: {a.threshold}")
    print(f"overall difference: {ratio:.2%}  (locator aid, not a pass gate)")
    print("hotspot bands (top to bottom, pixel range : in-band difference):")
    for i in range(BANDS):
        top, bottom = h * i // BANDS, h * (i + 1) // BANDS
        bhist = d.crop((0, top, w, bottom)).histogram()
        bratio = sum(bhist[a.threshold + 1:]) / (w * (bottom - top))
        bar = "#" * int(bratio * 50)
        print(f"  {i:>2}  {top:>5}-{bottom:<5}  {bratio:6.2%}  {bar}")

    out = a.out or os.path.splitext(a.impl)[0] + ".diff.png"
    mask = d.point(lambda v: 140 if v > a.threshold else 0)
    heat = Image.composite(Image.new("RGB", impl.size, (255, 32, 32)), impl, mask)
    heat.save(out)
    print(f"heatmap: {os.path.abspath(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
