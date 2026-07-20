#!/usr/bin/env python3
"""
Build the IRONMAN 70.3 Tracker.

Pipeline:
  1. Run src/build_data.py  -> regenerates src/plan_data.json (the 77-week plan).
  2. Inject that JSON into the /*PLAN_DATA*/ placeholder in src/app_template.html.
  3. Write the result to ./index.html (the file GitHub Pages serves).
  4. Copy index.html + PWA assets into ios-app/www/ for the native build.

Usage:
  python3 build.py

No third-party packages required (standard library only).
"""
import os, re, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
TPL = os.path.join(SRC, "app_template.html")
DATA = os.path.join(SRC, "plan_data.json")
OUT = os.path.join(ROOT, "index.html")
PLACEHOLDER = "/*PLAN_DATA*/"

PWA_ASSETS = [
    "manifest.webmanifest", "sw.js",
    "icon-192.png", "icon-512.png", "icon-512-maskable.png",
    "apple-touch-icon.png", "favicon-32.png",
]


def main():
    # 1. regenerate the plan data
    print("→ generating plan data ...")
    subprocess.run([sys.executable, os.path.join(SRC, "build_data.py")], check=True)

    # 2 + 3. inject into the template
    tpl = open(TPL, encoding="utf-8").read()
    if PLACEHOLDER not in tpl:
        sys.exit(f"ERROR: placeholder {PLACEHOLDER!r} not found in {TPL}")
    data = open(DATA, encoding="utf-8").read()
    html = tpl.replace(PLACEHOLDER, data)
    open(OUT, "w", encoding="utf-8").write(html)
    print(f"→ wrote {OUT} ({len(html):,} bytes)")

    # 4. sync the native iOS wrapper's web assets
    www = os.path.join(ROOT, "ios-app", "www")
    if os.path.isdir(os.path.dirname(www)):
        os.makedirs(www, exist_ok=True)
        shutil.copy(OUT, os.path.join(www, "index.html"))
        for a in PWA_ASSETS:
            ap = os.path.join(ROOT, a)
            if os.path.exists(ap):
                shutil.copy(ap, os.path.join(www, a))
        print("→ synced ios-app/www/")

    print("✓ build complete")


if __name__ == "__main__":
    main()
