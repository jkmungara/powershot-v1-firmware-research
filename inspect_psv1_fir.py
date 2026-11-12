#!/usr/bin/env python3
from pathlib import Path
import argparse, collections, hashlib, math, struct

def entropy(data):
    c=collections.Counter(data); n=len(data)
    return -sum((v/n)*math.log2(v/n) for v in c.values()) if n else 0

def main():
    ap=argparse.ArgumentParser(description='Read-only Canon FIR header inspector')
    ap.add_argument('firmware', type=Path)
    args=ap.parse_args(); data=args.firmware.read_bytes()
    print('file:', args.firmware)
    print('size:', len(data), f'(0x{len(data):x})')
    print('sha256:', hashlib.sha256(data).hexdigest())
    print('model_id:', f'0x{struct.unpack_from("<I",data,0)[0]:08x}')
    print('version:', data[0x10:0x20].split(b'\0')[0].decode('ascii','replace'))
    for name,off in [('stored_checksum',0x20),('updater_header',0x24),('updater_payload',0x28),('second_updater',0x2c),('firmware_header',0x30),('file_size_field',0x38)]:
        v=struct.unpack_from('<I',data,off)[0]
        print(f'{name}: 0x{v:08x} ({v})')
    print('window_entropy:')
    for off in range(0,len(data),1024*1024):
        b=data[off:off+65536]
        print(f'  0x{off:08x}: {entropy(b):.5f}')
if __name__=='__main__': main()
