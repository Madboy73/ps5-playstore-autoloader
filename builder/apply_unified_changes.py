#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]); main=root/'src/main.c'; mk=root/'Makefile'
s=main.read_text(); needle='#include "sync.h"\n'
if needle not in s: raise SystemExit('main include anchor missing')
s=s.replace(needle, needle+'#include "playstore_restore.h"\n',1)
anchor='''    /* Step 4: locate autoload.txt */\n    char config_path[512];\n'''
insert='''    /* Playstore additions only: keep the upstream lookup/parser/fallback unchanged.\n       1) Ensure lowercase /data/homebrew exists, without touching existing content.\n       2) If /data/ps5_autoloader/autoload.txt is absent, restore the bundled\n          default package. A restore failure is non-fatal here: upstream's\n          original config lookup and embedded Payload Manager fallback remain. */\n    if (playstore_ensure_homebrew_dir() != 0)\n        autoloader_notify("WARNING: could not create /data/homebrew");\n\n    if (playstore_ensure_default_autoloader() != 0)\n        autoloader_notify("WARNING: Playstore autoloader restore failed");\n\n    /* Step 4: locate autoload.txt */\n    char config_path[512];\n'''
if anchor not in s: raise SystemExit('main step4 anchor missing')
main.write_text(s.replace(anchor,insert,1))
s=mk.read_text(); old='SRCS     := src/main.c src/launcher.c src/app_killer.c src/notification.c src/sync.c\n'; new='SRCS     := src/main.c src/launcher.c src/app_killer.c src/notification.c src/sync.c src/playstore_restore.c src/playstore_default_pack.c src/inflate.c\n'
if old not in s: raise SystemExit('Makefile SRCS anchor missing')
mk.write_text(s.replace(old,new,1))
