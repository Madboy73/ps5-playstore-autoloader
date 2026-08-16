#!/usr/bin/env python3
import argparse, binascii, re, zipfile, zlib

def ident(name):
    x = re.sub(r'[^A-Za-z0-9_]', '_', name)
    if not x or x[0].isdigit(): x = '_' + x
    return x

def c_array(data, cols=12):
    return '\n'.join('    ' + ', '.join(f'0x{b:02x}' for b in data[i:i+cols]) + ',' for i in range(0,len(data),cols))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('zip'); ap.add_argument('--out-c',required=True); ap.add_argument('--out-h',required=True); args=ap.parse_args()
    with zipfile.ZipFile(args.zip,'r') as z:
        names=[n for n in z.namelist() if not n.endswith('/')]; prefix='ps5_autoloader/'
        bad=[n for n in names if not n.startswith(prefix) or '/' in n[len(prefix):]]
        if bad: raise SystemExit(f'Unexpected archive layout: {bad}')
        rel=[n[len(prefix):] for n in names]
        if 'autoload.txt' not in rel: raise SystemExit('autoload.txt missing')
        ordered=[n for n in rel if n!='autoload.txt']+['autoload.txt']; entries=[]
        for name in ordered:
            raw=z.read(prefix+name); co=zlib.compressobj(level=9,wbits=-15); comp=co.compress(raw)+co.flush()
            entries.append((name,raw,comp,binascii.crc32(raw)&0xffffffff,name=='autoload.txt'))
    h='''#pragma once\n#include <stddef.h>\n#include <stdint.h>\n\ntypedef struct {\n    const char *name;\n    const unsigned char *compressed_data;\n    size_t compressed_size;\n    size_t original_size;\n    uint32_t crc32;\n    int is_config;\n} playstore_pack_entry_t;\n\nextern const playstore_pack_entry_t g_playstore_default_pack[];\nextern const size_t g_playstore_default_pack_count;\n'''
    open(args.out_h,'w',newline='\n').write(h); lines=['#include "playstore_default_pack.h"','']
    for idx,(name,raw,comp,crc,is_config) in enumerate(entries):
        sym=f'pack_{idx}_{ident(name)}'; lines += [f'static const unsigned char {sym}[] = {{',c_array(comp),'};','']
    lines += ['const playstore_pack_entry_t g_playstore_default_pack[] = {']
    for idx,(name,raw,comp,crc,is_config) in enumerate(entries):
        sym=f'pack_{idx}_{ident(name)}'; esc=name.replace('\\','\\\\').replace('"','\\"')
        lines.append(f'    {{"{esc}", {sym}, sizeof({sym}), {len(raw)}u, 0x{crc:08x}u, {1 if is_config else 0}}},')
    lines += ['};','const size_t g_playstore_default_pack_count = sizeof(g_playstore_default_pack) / sizeof(g_playstore_default_pack[0]);','']
    open(args.out_c,'w',newline='\n').write('\n'.join(lines))
    print(f'Generated {len(entries)} entries: raw={sum(len(x[1]) for x in entries)} compressed={sum(len(x[2]) for x in entries)}')
if __name__=='__main__': main()
