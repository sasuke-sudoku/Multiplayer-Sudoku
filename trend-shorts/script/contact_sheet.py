"""Tile check stills into one image: python3 script/contact_sheet.py <dir> <out.png> [columns]"""
import pathlib, sys
from PIL import Image

files = sorted(pathlib.Path(sys.argv[1]).glob("*.png"))
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 7
w, h = Image.open(files[0]).size
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols, h * rows), "#888888")
for i, f in enumerate(files):
    sheet.paste(Image.open(f).convert("RGB"), ((i % cols) * w, (i // cols) * h))
sheet.save(sys.argv[2])
