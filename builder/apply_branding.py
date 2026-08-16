#!/usr/bin/env python3
from pathlib import Path
import base64, html, sys
root=Path(sys.argv[1]); icon=Path(sys.argv[2])
p=root/'assets/param.json.template'; s=p.read_text(); old='"titleName": "WebKit Autoloader v[[VERSION_PLACEHOLDER]]"'; new='"titleName": "Playstore WebKit v[[VERSION_PLACEHOLDER]]"'
if old not in s: raise SystemExit('param title anchor missing')
p.write_text(s.replace(old,new,1))
brand='PLAYSTORE | Telegram: Myplaystore_ir | Instagram: Myplaystore.ir | Tel: 0936 041 7330'
for rel in ['frontend/autoloader/index.html','frontend/installer-page/index.html']:
    p=root/rel; s=p.read_text(); marker='This project is free and open source: github.com/itsPLK/ps5-webkit-autoloader'
    if marker not in s: raise SystemExit(f'footer anchor missing in {rel}')
    p.write_text(s.replace(marker, marker+'<br />'+html.escape(brand),1))
(root/'assets/icon0.png').write_bytes(icon.read_bytes())
b64=base64.b64encode(icon.read_bytes()).decode('ascii')
svg=('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n  <image width="512" height="512" href="data:image/png;base64,'+b64+'"/>\n</svg>\n')
for rel in ['frontend/autoloader/logo.svg','frontend/installer-page/logo.svg','frontend/autoloader/favicon.svg','frontend/installer-page/favicon.svg']:
    p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(svg)
