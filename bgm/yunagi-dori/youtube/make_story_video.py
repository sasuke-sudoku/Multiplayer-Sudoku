#!/usr/bin/env python3
"""風のアニメーション（make_wind_video.py の 24 秒ループ）に、曲全体を通した“出来事”を重ねた動画を作る。

ループの背景（揺れる木・はためく日よけ・舞う木の葉 など）の上に、時間とともに変わるものを描く:
  * 猫 ………… 3 回通りを横切る。2 回目は途中で止まり、背中を向けて座って海を眺めてから歩き去る（characters.py）
  * 自転車の人 …… 坂を下って遠ざかる／上って近づいてくる（遠近つき、characters.py）
  * カモメ …… 時々、群れで空を横切る
  * 小舟 ……… 海の上をゆっくり進む
  * 夕暮れの進行 …… 曲が進むにつれて空が暮れ、店の窓明かりが強まり、終盤は星がまたたく
出力: yunagi-dori_story_youtube.mp4（1920x1080, 30fps）
使い方: python3 make_story_video.py   （ループの背景フレームが無ければ先に作る）
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_video_street as street  # noqa: E402
import make_wind_video as wind  # noqa: E402
import characters  # noqa: E402  猫と自転車の人

W, H, FPS = wind.W, wind.H, wind.FPS
TAU = 2 * math.pi
rng = np.random.default_rng(1964)
FRAMES_DIR = os.path.join(HERE, "_wind_frames")


def smoothstep(a, b, x):
    x = min(1.0, max(0.0, (x - a) / (b - a)))
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- カモメ・小舟・星
BIRD_FLIGHTS = [10, 55, 128, 196]           # 群れが現れる時刻
BIRDS = [(rng.uniform(-40, 80), rng.uniform(-25, 25), rng.uniform(0, TAU), rng.uniform(0.8, 1.2)) for _ in range(5)]
STARS = [(rng.uniform(560, 1280), rng.uniform(5, 260), rng.uniform(0.6, 1.6), rng.uniform(0, TAU), rng.uniform(1.5, 4)) for _ in range(80)]


def draw_birds(d, t):
    for t0 in BIRD_FLIGHTS:
        u = (t - t0) / 16
        if not 0 <= u <= 1:
            continue
        cx = 1350 - u * 1450
        cy = 170 - 60 * u + 15 * math.sin(u * 5)
        for ox, oy, ph, sc in BIRDS:
            x, y = cx + ox, cy + oy
            flap = math.sin(TAU * 2.2 * t + ph)
            span = 9 * sc
            pts = [(x - span, y - 3 * flap - 1), (x - span * 0.45, y - 2.5 * flap - 2.5), (x, y),
                   (x + span * 0.45, y - 2.5 * flap - 2.5), (x + span, y - 3 * flap - 1)]
            d.line(pts, fill=(45, 30, 45, 230), width=2, joint="curve")


def draw_boat(d, t, dur):
    x = 655 + 200 * t / dur
    y = 447 + 0.6 * math.sin(TAU * t / 3.1)
    d.polygon([(x - 7, y), (x + 7, y), (x + 5, y + 2.5), (x - 5, y + 2.5)], fill=(40, 25, 30, 235))
    d.polygon([(x - 1, y - 1), (x - 1, y - 11), (x + 5, y - 1)], fill=(60, 40, 45, 225))


def draw_stars(d, t, dur):
    k = smoothstep(dur * 0.62, dur * 0.9, t)
    if k <= 0:
        return
    for x, y, r, ph, sp in STARS:
        a = k * (0.55 + 0.45 * math.sin(TAU * t / sp + ph))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 245, 220, int(200 * a)))


# ---------------------------------------------------------------- 合成
def window_mask(img):
    hsv = np.asarray(Image.fromarray((img * 255).astype(np.uint8)).convert("HSV")).astype(np.float32) / 255
    lum = img @ np.array([0.299, 0.587, 0.114], np.float32)
    warm = (hsv[..., 0] * 360 > 18) & (hsv[..., 0] * 360 < 55) & (hsv[..., 1] > 0.35) & (lum > 0.45)
    zone = np.maximum(wind.region((0, 0, 560, 640), 20), wind.region((1080, 300, 1280, 450), 20))
    return wind.blur(warm.astype(np.float32) * zone, 4)


def compose(f, base, t, dur, win, sky_dark):
    p = smoothstep(0, dur, t)                                           # 曲の進行（0→1）
    a = np.asarray(base).astype(np.float32) / 255
    flicker = 1 + 0.06 * math.sin(TAU * t / 1.7) * math.sin(TAU * t / 0.53)
    a = a + (win * (0.06 + 0.22 * p) * flicker)[..., None] * np.array([1.0, 0.7, 0.35], np.float32)   # 窓明かりが強まる
    dusk = 0.17 * p
    a = a * (1 - dusk * sky_dark)[..., None] + (dusk * sky_dark * 0.25)[..., None] * np.array([0.35, 0.25, 0.6], np.float32)
    frame = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    draw_stars(d, t, dur)
    draw_birds(d, t)
    draw_boat(d, t, dur)
    frame.alpha_composite(over)
    characters.draw_rider(frame, t)
    characters.draw_cat(frame, t)
    return frame.convert("RGB")


def ensure_loop_frames():
    if os.path.isdir(FRAMES_DIR) and len(os.listdir(FRAMES_DIR)) == wind.N:
        return
    subprocess.run([sys.executable, os.path.join(HERE, "make_wind_video.py"), "--frames-only"], check=True)


def main():
    if "--preview" in sys.argv:          # 猫・カモメなどの確認用に数枚だけ書き出す
        img = np.asarray(Image.open(os.path.join(HERE, "canva", "sunset_street2_mystic.jpg")).convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
        win = window_mask(img)
        sky_dark = 0.5 + 0.5 * np.clip(1 - np.mgrid[0:H, 0:W][0] / 420, 0, 1)
        base = Image.fromarray((img * 255).astype(np.uint8))
        out = sys.argv[sys.argv.index("--preview") + 1]
        for t in [float(v) for v in os.environ.get('PREVIEW_TIMES', '24,60,108,200').split(',')]:
            compose(0, base, t, 217.2, win, sky_dark).save(os.path.join(out, f"story_{int(t)}.png"))
        return

    ensure_loop_frames()
    img = np.asarray(Image.open(os.path.join(HERE, "canva", "sunset_street2_mystic.jpg")).convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    win = window_mask(img)
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
    sky_dark = 0.5 + 0.5 * np.clip(1 - yy / 420, 0, 1)                  # 空ほど暮れる

    audio = os.path.join(HERE, "..", "yunagi-dori_full.wav")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio]).decode())
    total = int(dur * FPS)
    txt_path = os.path.join(HERE, "_story_text.png")
    street.text_layer().save(txt_path)
    out = os.path.join(HERE, "yunagi-dori_story_youtube.mp4")
    vf = (f"[0:v]scale=1920:1080:flags=lanczos,unsharp=5:5:0.4[bg];[bg][1:v]overlay=0:0,"
          f"fade=t=in:st=0:d=1.5,fade=t=out:st={dur - 3:.2f}:d=3,format=yuv420p[v]")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", txt_path, "-i", audio, "-filter_complex", vf,
                           "-map", "[v]", "-map", "2:a", "-t", f"{dur:.3f}",
                           "-c:v", "libx264", "-preset", "medium", "-b:v", "3200k", "-maxrate", "4800k", "-bufsize", "9600k",
                           "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for f in range(total):
        base = Image.open(os.path.join(FRAMES_DIR, f"{f % wind.N:04d}.png")).convert("RGB")
        ff.stdin.write(compose(f, base, f / FPS, dur, win, sky_dark).tobytes())
        if f % 300 == 0:
            print(f"frame {f}/{total}", flush=True)
    ff.stdin.close()
    ff.wait()
    os.remove(txt_path)
    print("wrote", out)


if __name__ == "__main__":
    main()
