"""Copy the pre-drawn front page into the output directory.

The picture itself is drawn at build time by draw_front.py, which
produces entry.png next to this file. This module does no drawing at
all and needs no third-party packages: it only copies that finished
PNG into the output folder, so running it twice yields byte-identical
files and it works in a bare Python image.
"""

import os
import shutil
import sys


def output_directory():
    """Pick the destination folder from the environment, or /output."""
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if chosen:
        return chosen
    return "/output"


def run():
    """Copy entry.png beside this file into the output directory."""
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    target_dir = output_directory()
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "entry.png")
    shutil.copyfile(source, target)
    wanted = os.path.getsize(source)
    got = os.path.getsize(target)
    if got != wanted:
        print("error: copied file is %d bytes, expected %d"
              % (got, wanted), file=sys.stderr)
        return 1
    print("wrote %s (%d bytes)" % (target, got))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
