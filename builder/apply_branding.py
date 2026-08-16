#!/usr/bin/env python3
from pathlib import Path
import base64, sys

root = Path(sys.argv[1])
icon = Path(sys.argv[2])
bg = Path(sys.argv[3])

# Home-screen title only. Keep Title ID/category/deeplink and runtime logic upstream.
p = root / 'assets/param.json.template'
s = p.read_text()
old = '"titleName": "WebKit Autoloader v[[VERSION_PLACEHOLDER]]"'
new = '"titleName": "Playstore WebKit v[[VERSION_PLACEHOLDER]]"'
if old not in s:
    raise SystemExit('param title anchor missing')
p.write_text(s.replace(old, new, 1))

# Keep the supplied logo as the PS5 home-screen icon.
(root / 'assets/icon0.png').write_bytes(icon.read_bytes())

# Use the same artwork for page logo/favicons. No contact text is added below the icon.
b64 = base64.b64encode(icon.read_bytes()).decode('ascii')
svg = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
    f'  <image width="512" height="512" href="data:image/png;base64,{b64}"/>\n'
    '</svg>\n'
)
for rel in [
    'frontend/autoloader/logo.svg',
    'frontend/installer-page/logo.svg',
    'frontend/autoloader/favicon.svg',
    'frontend/installer-page/favicon.svg',
]:
    q = root / rel
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(svg)

# Branding of document titles only.
for rel, old_title, new_title in [
    (
        'frontend/autoloader/index.html',
        '<title>WebKit Autoloader v[[VERSION_PLACEHOLDER]] by PLK (built [[BUILD_TIME_PLACEHOLDER]])</title>',
        '<title>Playstore WebKit v[[VERSION_PLACEHOLDER]] by PLK (built [[BUILD_TIME_PLACEHOLDER]])</title>',
    ),
    (
        'frontend/installer-page/index.html',
        '<title>WebKit Autoloader Installer v[[VERSION_PLACEHOLDER]] by PLK (built [[BUILD_TIME_PLACEHOLDER]])</title>',
        '<title>Playstore WebKit Installer v[[VERSION_PLACEHOLDER]] by PLK (built [[BUILD_TIME_PLACEHOLDER]])</title>',
    ),
]:
    q = root / rel
    text = q.read_text()
    if old_title not in text:
        raise SystemExit(f'title anchor missing in {rel}')
    q.write_text(text.replace(old_title, new_title, 1))

# Fullscreen background for the actual Autoloader page.
bg_dest = root / 'frontend/autoloader/playstore-bg.jpg'
bg_dest.write_bytes(bg.read_bytes())

css_path = root / 'frontend/autoloader/style.css'
css = css_path.read_text()
css += r'''

/* PLAYSTORE BRANDING ONLY: full-screen artwork; runtime/layout logic untouched. */
body,
#splash,
#loader {
  background-color: #05070d !important;
  background-image: url("playstore-bg.jpg") !important;
  background-position: center center !important;
  background-repeat: no-repeat !important;
  -webkit-background-size: cover !important;
  background-size: cover !important;
}

/* The full-screen artwork already contains the center logo and labels. */
#splash .logo,
#splash h1,
#footer {
  display: none !important;
}
'''
css_path.write_text(css)
