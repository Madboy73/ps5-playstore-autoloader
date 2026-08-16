#!/usr/bin/env python3
from pathlib import Path
import base64, sys

root = Path(sys.argv[1])
icon = Path(sys.argv[2])
bg = Path(sys.argv[3])

# Home-screen label only. Keep titleId/category/deeplink exactly upstream.
p = root / 'assets/param.json.template'
s = p.read_text()
old = '"titleName": "WebKit Autoloader v[[VERSION_PLACEHOLDER]]"'
new = '"titleName": "Playstore WebKit v[[VERSION_PLACEHOLDER]]"'
if old not in s:
    raise SystemExit('param title anchor missing')
p.write_text(s.replace(old, new, 1))

# Exact supplied 512x512 artwork as the PS5 homescreen icon.
(root / 'assets/icon0.png').write_bytes(icon.read_bytes())

# Small icon wrapper for favicon + installer-page logo.
icon_b64 = base64.b64encode(icon.read_bytes()).decode('ascii')
icon_svg = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n'
    f'  <image width="512" height="512" href="data:image/png;base64,{icon_b64}"/>\n'
    '</svg>\n'
)
for rel in [
    'frontend/autoloader/favicon.svg',
    'frontend/installer-page/logo.svg',
    'frontend/installer-page/favicon.svg',
]:
    q = root / rel
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(icon_svg)

# IMPORTANT: reuse the upstream autoloader logo.svg route for the full-screen
# artwork. This route already exists in the official registry/AppCache, so no
# new runtime route/file-registration logic is required.
bg_b64 = base64.b64encode(bg.read_bytes()).decode('ascii')
bg_svg = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" '
    'preserveAspectRatio="xMidYMid slice">\n'
    f'  <image width="1920" height="1080" preserveAspectRatio="xMidYMid slice" '
    f'href="data:image/jpeg;base64,{bg_b64}"/>\n'
    '</svg>\n'
)
(root / 'frontend/autoloader/logo.svg').write_text(bg_svg)

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

# Full-screen background on the real Autoloader page. The artwork itself
# contains the center logo/contact/instructions, so hide duplicate splash text.
css_path = root / 'frontend/autoloader/style.css'
css = css_path.read_text()
css += r'''

/* PLAYSTORE BRANDING ONLY. No exploit/autoloader runtime logic is changed. */
body,
#splash,
#loader {
  background-color: #05070d !important;
  background-image: url("logo.svg") !important;
  background-position: center center !important;
  background-repeat: no-repeat !important;
  -webkit-background-size: cover !important;
  background-size: cover !important;
}

#splash .logo,
#splash h1,
#footer {
  display: none !important;
}
'''
css_path.write_text(css)
