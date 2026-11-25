"""Make the web version: copy the desktop UI into site/app/ and plug in the browser engine.

The desktop app and the web app share presetpicker/ui/ (index.html, app.css, app.js); only the
backend differs: site/app/webapi.js stands in for the Python API. Run before publishing the site
(the Pages workflow does this).
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from presetpicker import __version__  # noqa: E402

UI, OUT = ROOT / "presetpicker" / "ui", ROOT / "site" / "app"

for name in ("app.css", "app.js"):
    shutil.copy2(UI / name, OUT / name)
shutil.copytree(UI / "fonts", OUT / "fonts", dirs_exist_ok=True)

html = (UI / "index.html").read_text()
html = html.replace('<html lang="en">', f'<html lang="en" data-version="{__version__} (web)">', 1)
html = html.replace("<title>Preset Picker</title>", "<title>Preset Picker · Web · Grain &amp; Glow</title>\n"
                    '<meta name="robots" content="noindex">\n<link rel="icon" href="../favicon.png">', 1)
engine = ('<script src="https://cdn.jsdelivr.net/npm/exifr@7.1.3/dist/full.umd.js"></script>\n'
          '<script src="engine.js"></script>\n<script src="webapi.js"></script>\n')
html, n = re.subn(r'<script src="app.js"></script>', engine + '<script src="app.js"></script>', html)
assert n == 1, "app.js script tag not found"
(OUT / "index.html").write_text(html)
print("web app written to", OUT)
