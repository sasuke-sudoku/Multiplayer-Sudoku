#!/usr/bin/env python3
"""参考画像（文字なし版）からサムネイル背景を作る: くっきり＋幻想的な仕上げ。
使い方:
  python3 make_mystic_bg.py 参考画像 出力.jpg [--crop x0,y0,x1,y1] [--sun x,y] [--text x,y]
  --crop 元画像から使う範囲（省略時は 1 枚目のスクショ右下の画像）
  --sun  出力画像（1280x720）での夕日の位置
  --text 出力画像でのタイトル文字の中心（この周りを暗いもやで囲む）"""
import argparse

import numpy as np
from PIL import Image, ImageFilter

W, H = 1280, 720
rng = np.random.default_rng(7)


def to_np(im):
    return np.asarray(im).astype(np.float32) / 255


def to_im(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def screen(a, b):
    return 1 - (1 - a) * (1 - b)


def main(src_path, out_path, crop, SUN, TEXT, gap=200):
    src = Image.open(src_path).convert("RGB")
    c = src.crop(crop)
    w, h = c.size
    nh = round(w * 9 / 16)
    top = max(0, (h - nh) // 2) if h - nh < 40 else 20
    c = c.crop((0, top, w, top + nh))

    # --- くっきり: 段階的に拡大し、ノイズを抑えてから細部と局所コントラストを強調
    if W / c.width > 1.5:  # 大きく拡大するときだけノイズを抑えて 2 段階で拡大
        c = c.filter(ImageFilter.MedianFilter(3))
        c = c.resize((c.width * 3 // 2, c.height * 3 // 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 80, 2))
    c = c.resize((W, H), Image.LANCZOS)
    c = c.filter(ImageFilter.UnsharpMask(radius=2.0, percent=110, threshold=3))     # 輪郭
    c = c.filter(ImageFilter.UnsharpMask(radius=24, percent=35, threshold=0))       # 局所コントラスト（霞を晴らす）
    a = to_np(c)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)

    # --- 幻想的な色調: 影を青紫、明部を金色に
    shadow = np.clip(1 - lum / 0.45, 0, 1)[..., None]
    high = np.clip((lum - 0.55) / 0.45, 0, 1)[..., None]
    a = a + shadow * np.array([0.02, -0.01, 0.07]) * 0.9 + high * np.array([0.05, 0.025, -0.03])
    a = np.clip((a - 0.5) * 1.14 + 0.5, 0, 1) * 0.94                                # コントラストを上げ、少し暗めに
    g = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    a = np.clip(g + (a - g) * 1.18, 0, 1)                                            # 彩度を上げる

    # --- ブルーム: 明るい部分をにじませて光らせる
    bright = np.clip((lum - 0.74) / 0.26, 0, 1)[..., None] * a
    bloom = to_np(to_im(bright).filter(ImageFilter.GaussianBlur(18))) * 0.35 + to_np(to_im(bright).filter(ImageFilter.GaussianBlur(60))) * 0.25
    a = screen(a, bloom)

    # --- 夕日からの光芒（放射状の光の筋）
    ang = np.arctan2(yy - SUN[1], xx - SUN[0])
    dist = np.hypot(xx - SUN[0], yy - SUN[1])
    rays = 0.5 + 0.5 * np.sin(ang * 23 + 1.3) * np.sin(ang * 9 + 0.4)
    rays = np.clip(rays, 0, 1) ** 3 * np.exp(-dist / 520)
    rays_img = to_np(to_im(np.repeat(rays[..., None], 3, 2)).filter(ImageFilter.GaussianBlur(6)))
    a = screen(a, rays_img * np.array([1.0, 0.75, 0.4]) * 0.3)
    halo = np.exp(-(dist / 170) ** 2)[..., None] * np.array([1.0, 0.82, 0.55]) * 0.18
    a = screen(a, halo)

    # --- 光の粒（舞い上がる蛍・光の粉）
    sp = np.zeros((H, W), np.float32)
    for _ in range(140):
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.95)
        r = rng.choice([1.2, 1.8, 2.6, 4.0], p=[0.45, 0.3, 0.17, 0.08])
        k = rng.uniform(0.4, 1.0)
        x0, x1, y0, y1 = int(max(0, x - r * 6)), int(min(W, x + r * 6)), int(max(0, y - r * 6)), int(min(H, y + r * 6))
        gx, gy = np.meshgrid(np.arange(x0, x1), np.arange(y0, y1))
        sp[y0:y1, x0:x1] += k * np.exp(-((gx - x) ** 2 + (gy - y) ** 2) / (2 * r * r))
    sp_img = np.clip(sp, 0, 1)[..., None] * np.array([1.0, 0.88, 0.6])
    sp_glow = to_np(to_im(sp_img).filter(ImageFilter.GaussianBlur(5)))
    a = screen(a, sp_img * 0.85 + sp_glow * 0.9)

    # --- タイトルの後ろの深い茜〜紫のもや（白文字を浮かせる）
    mask = np.zeros((H, W), np.float32)
    tx, ty = TEXT
    mask += 0.55 * np.exp(-(((xx - tx) / 430) ** 2 + ((yy - ty) / 150) ** 2))
    mask += 0.5 * np.exp(-(((xx - tx) / 520) ** 2 + ((yy - ty - gap) / 45) ** 2))
    mask = np.clip(mask, 0, 0.6)[..., None]
    a = a * (1 - mask) + np.array([0.30, 0.10, 0.12]) * mask

    # --- 周辺減光
    v = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    a = a * (1 - 0.32 * np.clip(v - 0.55, 0, 1) ** 1.4)[..., None]

    to_im(a).save(out_path, quality=94)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--crop", default="673,329,1365,785")
    ap.add_argument("--sun", default="942,313")
    ap.add_argument("--text", default="640,230")
    ap.add_argument("--subtitle-gap", type=int, default=200)
    ar = ap.parse_args()
    nums = lambda s: tuple(int(v) for v in s.split(","))  # noqa: E731
    main(ar.src, ar.out, nums(ar.crop), nums(ar.sun), nums(ar.text), ar.subtitle_gap)
