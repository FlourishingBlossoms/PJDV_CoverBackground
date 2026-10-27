#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_from_images.py — 把任意图片批量做成 MM+ 静态背景 USM（DarkMV 用）。

用法:
    python build_from_images.py --images <图片目录> --wannacri <WannaCri 工具目录> --out <输出目录>
        [--size 1920x1080] [--frames 6] [--crf 16] [--brightness 100]
        [--gray] [--dim 1.0] [--title-csv titles.csv] [--workers 1]

图片命名:
    pv_12345.png / pv_12345.jpg   -> 输出 pv_12345.usm
    其它名字                      -> 用 --map 指定的 CSV 映射（name,pv）或按序号输出 pv_<stem>.usm

标题文字（可选）:
    --title-csv 指向 CSV：第一列 pv 编号（如 12345 或 pv_12345），第二列标题，第三列署名（可空）
    会在图片底部居中绘制白字标题（需 Pillow + 字体）

依赖:
    Python 3.9+、Pillow、ffmpeg、WannaCri GUI（https://github.com/hiki8man/Wannacri_GUI）
"""
import argparse
import csv
import os
import shutil
import subprocess
import sys
import tempfile

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None


def run(cmd, cwd=None, timeout=None):
    return subprocess.run(cmd, cwd=cwd, timeout=timeout,
                          stdin=subprocess.DEVNULL,
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def find_ffmpeg(wannacri_dir):
    p = os.path.join(wannacri_dir, "ffmpeg", "ffmpeg.exe")
    if os.path.exists(p):
        return p
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    raise SystemExit("找不到 ffmpeg：请放到 <wannacri>/ffmpeg/ffmpeg.exe 或加入 PATH")


def load_titles(csv_path):
    titles = {}
    if not csv_path or not os.path.exists(csv_path):
        return titles
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 2:
                continue
            pv = row[0].strip()
            pv = pv[3:] if pv.lower().startswith("pv_") else pv
            if pv.isdigit():
                titles[pv] = (row[1].strip(), row[2].strip() if len(row) > 2 else "")
    return titles


def process_image(img_path, pv, args, ffmpeg, workdir):
    """图片 -> 6 帧静音 mp4"""
    tmp_png = os.path.join(workdir, "frame.png")
    img = Image.open(img_path).convert("RGB")
    w, h = args.size
    # 等比铺满 + 居中裁切
    scale = max(w / img.width, h / img.height)
    nw, nh = int(img.width * scale + 0.5), int(img.height * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS).crop(((nw - w) // 2, (nh - h) // 2,
                                                   (nw - w) // 2 + w, (nh - h) // 2 + h))
    if args.gray:
        img = img.convert("L").convert("RGB")
    if args.dim != 1.0:
        img = img.point(lambda v: min(255, int(v * args.dim)))
    # 标题
    title, credit = args.titles.get(pv, ("", ""))
    if title and args.font and os.path.exists(args.font):
        d = ImageDraw.Draw(img)
        try:
            f1 = ImageFont.truetype(args.font, 64)
            f2 = ImageFont.truetype(args.font, 32)
        except Exception:
            f1 = f2 = ImageFont.load_default()
        for text, font, y in ((title, f1, int(h * 0.42)), (credit, f2, int(h * 0.42) + 84)):
            if not text:
                continue
            box = d.textbbox((0, 0), text, font=font)
            tw_, th_ = box[2] - box[0], box[3] - box[1]
            x = (w - tw_) // 2
            d.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0))
            d.text((x, y), text, font=font, fill=(255, 255, 255))
    img.save(tmp_png, "PNG")

    mp4 = os.path.join(workdir, f"{pv}.mp4")
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
           "-loop", "1", "-i", tmp_png,
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-frames:v", str(args.frames), "-r", "30", "-shortest",
           "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", mp4]
    run(cmd)
    return mp4 if os.path.exists(mp4) else None


def convert(wannacri_dir, mp4, outdir):
    exe = os.path.join(wannacri_dir, "convert_GUI.exe")
    if not os.path.exists(exe):
        raise SystemExit(f"找不到 {exe}")
    # 必须从工具目录启动：它按相对路径找 ffmpeg
    run([exe, mp4, "-vp9", "-vol", "60", "-crf", "16", "-brightness", "100",
         "-output", outdir], cwd=wannacri_dir, timeout=600)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", required=True, help="图片目录")
    ap.add_argument("--wannacri", required=True, help="WannaCri GUI 工具目录（含 convert_GUI.exe）")
    ap.add_argument("--out", required=True, help="输出目录（DarkMV/rom/movie）")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--frames", type=int, default=6)
    ap.add_argument("--gray", action="store_true", help="转灰度")
    ap.add_argument("--dim", type=float, default=1.0, help="整体压暗系数，如 0.75")
    ap.add_argument("--font", default="", help="TTF/TTC 字体路径（画标题用）")
    ap.add_argument("--title-csv", default="", help="pv,标题,署名 的 CSV")
    ap.add_argument("--map", default="", help="图片名,pv编号 的 CSV（图片名不是 pv_xxx 时用）")
    args = ap.parse_args()

    if Image is None:
        raise SystemExit("需要 Pillow：pip install pillow")
    args.size = tuple(int(x) for x in args.size.lower().split("x"))
    args.titles = load_titles(args.title_csv)

    mapping = {}
    if args.map and os.path.exists(args.map):
        with open(args.map, encoding="utf-8-sig", newline="") as f:
            for row in csv.reader(f):
                if len(row) >= 2 and row[1].strip().isdigit():
                    mapping[row[0].strip()] = row[1].strip()

    ffmpeg = find_ffmpeg(args.wannacri)
    os.makedirs(args.out, exist_ok=True)
    workdir = tempfile.mkdtemp(prefix="diva_bg_")

    files = sorted(f for f in os.listdir(args.images)
                   if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")))
    if not files:
        raise SystemExit("图片目录为空")
    print(f"待处理 {len(files)} 张图")

    ok = fail = 0
    for name in files:
        stem = os.path.splitext(name)[0]
        pv = stem[3:] if stem.lower().startswith("pv_") else mapping.get(name) or mapping.get(stem)
        if not pv:
            print(f"[skip] {name} 无法确定 pv 编号（可用 --map 指定）")
            fail += 1
            continue
        src = os.path.join(args.images, name)
        try:
            mp4 = process_image(src, pv, args, ffmpeg, workdir)
            if not mp4:
                print(f"[fail] {name} 生成视频失败")
                fail += 1
                continue
            # 清空输出目录里的旧产物，避免残留
            for f in os.listdir(args.out):
                try:
                    os.remove(os.path.join(args.out, f))
                except OSError:
                    pass
            convert(args.wannacri, mp4, args.out)
            usm = os.path.join(args.out, f"{pv}.usm")
            if os.path.exists(usm) and os.path.getsize(usm) > 2000:
                os.replace(usm, os.path.join(args.out, f"pv_{pv}.usm"))
                ok += 1
                print(f"[ok] {name} -> pv_{pv}.usm")
            else:
                fail += 1
                print(f"[fail] {name} 转换失败")
        except Exception as e:
            fail += 1
            print(f"[err] {name}: {e}")

    print(f"完成：成功 {ok}，失败 {fail}；输出目录 {args.out}")


if __name__ == "__main__":
    main()
