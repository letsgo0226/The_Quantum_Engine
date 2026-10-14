#!/usr/bin/env python3
"""ATGC metalinguistic codec and bounded v42 runner (no hashes)."""
import argparse, json, subprocess, sys
from pathlib import Path
def encode(data):
    return "".join("C" if b >> i & 1 else "A" for b in data for i in range(7,-1,-1))
def decode(seq):
    if len(seq)%8 or set(seq)-set("AC"): raise ValueError("Invalid ATGC bit sequence")
    return bytes(int(seq[i:i+8].replace("A","0").replace("C","1"),2) for i in range(0,len(seq),8))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("encode","decode","selftest","solve"))
    p.add_argument("file",nargs="?")
    a=p.parse_args()
    if a.mode=="selftest":
        data=Path(__file__).with_name("v42.sh").read_bytes()
        assert decode(encode(data))==data
        print(json.dumps({"self_ATGC_roundtrip":True,"self_bytes":len(data),"sha_used":False}))
    elif a.mode=="solve":
        data=Path(a.file).read_bytes() if a.file else sys.stdin.buffer.read()
        r=subprocess.run(["sh",str(Path(__file__).with_name("v42.sh"))],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        sys.stdout.buffer.write(r.stdout);sys.stderr.buffer.write(r.stderr);sys.exit(r.returncode)
    elif a.mode=="encode":
        data=Path(a.file).read_bytes() if a.file else sys.stdin.buffer.read()
        print(encode(data))
    else:
        data=Path(a.file).read_text().strip() if a.file else sys.stdin.read().strip()
        sys.stdout.buffer.write(decode(data))
if __name__=="__main__": main()