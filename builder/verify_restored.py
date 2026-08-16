#!/usr/bin/env python3
import sys, zipfile
from pathlib import Path
zip_path=Path(sys.argv[1]); root=Path('/data/ps5_autoloader')
with zipfile.ZipFile(zip_path) as z:
    for n in z.namelist():
        if n.endswith('/'): continue
        rel=n.split('/',1)[1]
        got=(root/rel).read_bytes(); exp=z.read(n)
        if got != exp: raise SystemExit(f'mismatch: {rel}')
print('restore byte-for-byte verification: PASS')
