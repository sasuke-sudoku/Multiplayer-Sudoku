#!/usr/bin/env python3
"""YouTube 用の静止画動画（1920x1080 MP4）とサムネイル（1280x720 PNG）を作る。
先に ../make_bgm.py を実行して yunagi-dori_full.wav を作っておくこと。"""
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
W, H = 1920, 1080
rng = np.random.default_rng(1960)


def sky():
    """夕焼けのグラデーション（上: 群青 → 中: 茜 → 地平線: 橙）"""
    y = np.linspace(0, 1, H)[:, None]
    stops = [(0.0, (38, 40, 92)), (0.45, (170, 80, 110)), (0.72, (240, 140, 80)), (1.0, (255, 200, 120))]
    img = np.zeros((H, W, 3))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        t = np.clip((y - p0) / (p1 - p0), 0, 1)
        mask = (y >= p0) & (y <= p1)
        for i in range(3):
            img[..., i] = np.where(mask, c0[i] + (c1[i] - c0[i]) * t, img[..., i])
    return Image.fromarray(img.astype(np.uint8))


def town(draw):
    """昭和の街並みのシルエット: 瓦屋根の家、電柱と電線、遠くの山"""
    base = int(H * 0.80)
    dark = (40, 26, 44)
    far = (95, 55, 85)
    # 遠くの山
    pts = [(0, base - 120)] + [(x, base - 120 - int(60 * np.sin(x / 260) + 30 * np.sin(x / 90))) for x in range(0, W + 1, 20)] + [(W, base)]
    draw.polygon([(0, base)] + pts + [(W, base)], fill=far)
    # 家並み
    x = -40
    while x < W:
        w = int(rng.integers(140, 260))
        h = int(rng.integers(90, 170))
        draw.rectangle([x, base - h, x + w, H], fill=dark)
        draw.polygon([(x - 18, base - h), (x + w // 2, base - h - int(w * 0.32)), (x + w + 18, base - h)], fill=dark)
        for _ in range(int(rng.integers(0, 3))):  # 灯りのともった窓
            wx = x + int(rng.integers(15, max(16, w - 45)))
            wy = base - h + int(rng.integers(20, max(21, h - 40)))
            draw.rectangle([wx, wy, wx + 26, wy + 20], fill=(255, 196, 110))
        x += w + int(rng.integers(0, 30))
    draw.rectangle([0, base, W, H], fill=(30, 20, 34))
    # 電柱と電線
    poles = [180, 820, 1460]
    for px in poles:
        draw.rectangle([px - 7, base - 430, px + 7, H], fill=(25, 16, 28))
        for dy in (0, 40):
            draw.rectangle([px - 60, base - 410 + dy, px + 60, base - 402 + dy], fill=(25, 16, 28))
    for dy in (-6, 34, 74):
        for a, b in zip([-500] + poles, poles + [W + 500]):
            xs = np.linspace(a, b, 60)
            sag = 50 * np.sin(np.pi * (xs - a) / (b - a))
            pts = [(float(xx), float(base - 404 + dy + s)) for xx, s in zip(xs, sag)]
            draw.line(pts, fill=(25, 16, 28), width=3)


def title(img, scale=1.0):
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, int(150 * scale))
    small = ImageFont.truetype(FONT, int(46 * scale))
    w, h = img.size
    for text, font, y in (("夕凪通り", big, 0.11), ("昭和ノスタルジー風 フィールドBGM（オリジナル曲）", small, 0.29)):
        tw = d.textlength(text, font=font)
        pos = ((w - tw) / 2, h * y)
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).text((pos[0] + 4, pos[1] + 4), text, font=font, fill=(30, 10, 30, 170))
        img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)))
        d.text(pos, text, font=font, fill=(255, 246, 228))
    return img


def main():
    img = sky()
    # 夕日
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W * 0.62, H * 0.52, W * 0.62 + 260, H * 0.52 + 260], fill=(255, 225, 160, 255))
    img = Image.alpha_composite(img.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(18)))
    town(ImageDraw.Draw(img))
    img = title(img)
    frame = os.path.join(HERE, "frame.png")
    img.convert("RGB").save(frame)
    img.convert("RGB").resize((1280, 720), Image.LANCZOS).save(os.path.join(HERE, "thumbnail.png"))

    audio = os.path.join(HERE, "..", "yunagi-dori_full.wav")
    out = os.path.join(HERE, "yunagi-dori_youtube.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "1", "-i", frame, "-i", audio,
                    "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "1",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out],
                   check=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
