#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""usm_to_images.py — 把 DarkMV 里已有的静态 USM 反向导出成 PNG（方便二次修改）。

用法:
    python usm_to_images.py --usm <DarkMV/rom/movie 目录> --out <PNG 输出目录>

依赖: ffmpeg（放在 PATH，或用 --ffmpeg 指定）
说明: 只解关键帧；P 帧依赖前序帧，单独解码会失败，属正常现象。
"""
import argparse
import os
import struct
import subprocess


def parse_first_frame(path):
    d = open(path, "rb").read()
    # 大块布局：帧区从 0xBB0 开始（模板 874576 字节）
    if len(d) == 874576:
        sz = struct.unpack_from("<I", d, 0xBB0)[0]
        if 0 < sz <= len(d) - 0xBBC:
            return 1920, 1080, d[0xBBC:0xBBC + sz]
    # 通用：逐帧 chunk（@SFV tag + size BE + body；首帧 chunk 含 IVF 头）
    off = 0
    first = True
    while off + 8 <= len(d):
        tag = d[off:off + 4]
        if tag not in (b"CRID", b"@SFV", b"@SFD", b"@SFH", b"@ALP"):
            break
        size = struct.unpack_from(">I", d, off + 4)[0]
        body = d[off + 8:off + 8 + size]
        if tag == b"@SFV" and len(body) > 64:
            # 找 DKIF
            idx = body.find(b"DKIF")
            if idx >= 0 and idx + 32 <= len(body):
                w, h = struct.unpack_from("<HH", body, idx + 12)
                pos = idx + 32
                while pos + 12 <= len(body):
                    fsz, _pts = struct.unpack_from("<IQ", body, pos)
                    if 0 < fsz and pos + 12 + fsz <= len(body):
                        return w, h, body[pos + 12:pos + 12 + fsz]
                    break
        off += 8 + size
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--usm", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    n = 0
    for f in sorted(os.listdir(args.usm)):
        if not f.lower().endswith(".usm"):
            continue
        p = os.path.join(args.usm, f)
        fr = parse_first_frame(p)
        if not fr:
            print(f"[skip] {f} 解析失败")
            continue
        w, h, data = fr
        ivf = os.path.join(args.out, "_tmp.ivf")
        png = os.path.join(args.out, os.path.splitext(f)[0] + ".png")
        hdr = (b"DKIF" + struct.pack("<HH", 0, 32) + b"VP90" +
               struct.pack("<HH", w, h) + struct.pack("<IIII", 30, 1, 1, 0))
        with open(ivf, "wb") as fh:
            fh.write(hdr + struct.pack("<IQ", len(data), 0) + data)
        subprocess.run([args.ffmpeg, "-y", "-loglevel", "error", "-i", ivf,
                        "-frames:v", "1", png], capture_output=True)
        os.remove(ivf)
        if os.path.exists(png):
            n += 1
    print(f"导出 {n} 张 PNG 到 {args.out}")


if __name__ == "__main__":
    main()
