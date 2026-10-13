#!/usr/bin/env python3
"""風のアニメーション（make_wind_video.py の 24 秒ループ）に、曲全体を通した“出来事”を重ねた動画を作る。

ループの背景（揺れる木・はためく日よけ・舞う木の葉 など）の上に、時間とともに変わるものを描く:
  * 猫 ………… 3 回通りを横切る。2 回目は途中で座って海を眺め、しっぽを揺らしてから歩き去る
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

W, H, FPS = wind.W, wind.H, wind.FPS
TAU = 2 * math.pi
rng = np.random.default_rng(1964)
FRAMES_DIR = os.path.join(HERE, "_wind_frames")


def smoothstep(a, b, x):
    x = min(1.0, max(0.0, (x - a) / (b - a)))
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- 猫
SS = 4  # 猫は 4 倍の解像度で描いてから縮小（輪郭をなめらかに）
CAT_DARK = (34, 24, 26, 255)
CAT_RIM = (255, 156, 80, 255)  # 夕日を背にした縁の光


def _cat_shapes(d, phase, pose, tail_ph, color, dy=0.0):
    """猫の形を描く。座標は足元中心が原点、右向き、1 単位 = 1px（SS 倍して描く）"""
    def P(x, y):
        return (OX + x * SS, OY + (y + dy) * SS)

    def ell(cx, cy, rx, ry, rot=0.0, n=28):
        c, s = math.cos(rot), math.sin(rot)
        return [P(cx + rx * math.cos(u) * c - ry * math.sin(u) * s, cy + rx * math.cos(u) * s + ry * math.sin(u) * c)
                for u in np.linspace(0, TAU, n)]

    def limb(x0, y0, x1, y1, w):
        d.line([P(x0, y0), P(x1, y1)], fill=color, width=int(w * SS))
        r = w * SS / 2
        for x, y in ((x0, y0), (x1, y1)):
            px, py = P(x, y)
            d.ellipse([px - r, py - r, px + r, py + r], fill=color)

    if pose == "walk":
        bob = 0.8 * math.sin(2 * phase)
        legs = ((10, 0.0), (10, math.pi), (-10, math.pi), (-10, 0.0))
        for hx, off in legs:                                           # 脚（対角の脚が同時に出る、短め）
            a = 0.55 * math.sin(phase + off)
            lift = 1.6 * max(0.0, math.sin(phase + off + 1.4))
            limb(hx, -10 + bob, hx + 4 * math.sin(a), -5 + bob - lift * 0.5, 3.8)
            limb(hx + 4 * math.sin(a), -5 + bob - lift * 0.5, hx + 8 * math.sin(a), -1.2 - lift, 3.2)
        d.polygon(ell(0, -14 + bob, 16, 9.5, 0.02), fill=color)       # 胴（丸め）
        d.polygon(ell(9, -18 + bob, 8, 7, -0.5), fill=color)           # 胸〜首
        hx, hy = 18, -23 + bob * 0.6
        d.polygon(ell(hx, hy, 7.6, 6.8), fill=color)                   # 頭（大きめ）
        d.polygon([P(hx - 6, hy - 2.5), P(hx - 4.5, hy - 11.5), P(hx - 0.5, hy - 5.5)], fill=color)  # 耳
        d.polygon([P(hx + 0.5, hy - 5.5), P(hx + 3.5, hy - 11.5), P(hx + 6.2, hy - 2.5)], fill=color)
        d.polygon(ell(hx + 6, hy + 1.6, 2.4, 2.0), fill=color)         # 鼻先
        sway = math.sin(tail_ph)
        tail = [(-14 - 7 * u - 2 * math.sin(math.pi * u) + 3 * sway * u * u, -17 - 18 * u + 5 * u * u) for u in np.linspace(0, 0.85, 10)]
        tail += [(tail[-1][0] + 2.5 + 2 * sway, tail[-1][1] - 2.5)]   # 先がくるんと曲がる
    else:  # 座って海を眺める
        d.polygon(ell(-3, -13, 9.5, 12, -0.35), fill=color)           # 胴（縦長）
        d.polygon(ell(-8, -6, 9, 6), fill=color)                       # 腰
        limb(3, -14, 4, -0.5, 3.2)                                     # 前脚
        limb(6, -14, 7.5, -0.5, 3.2)
        hx, hy = 4, -30
        d.polygon(ell(hx, hy, 7, 6.3), fill=color)
        d.polygon([P(hx - 5, hy - 3), P(hx - 3.5, hy - 12), P(hx + 0.5, hy - 5)], fill=color)
        d.polygon([P(hx + 1, hy - 5), P(hx + 4.5, hy - 12), P(hx + 6, hy - 2.5)], fill=color)
        d.polygon(ell(hx + 6, hy + 1.8, 2.6, 2.1), fill=color)
        flick = math.sin(tail_ph)
        tail = [(-14 + 26 * u, -1.5 - 3 * math.sin(math.pi * u) - (2.5 + 2.5 * flick) * u ** 4) for u in np.linspace(0, 1, 12)]
    d.line([P(x, y) for x, y in tail], fill=color, width=int(3.6 * SS), joint="curve")
    tx, ty = P(*tail[-1])
    d.ellipse([tx - 1.6 * SS, ty - 1.6 * SS, tx + 1.6 * SS, ty + 1.6 * SS], fill=color)


OX, OY = 50 * SS, 48 * SS  # スプライト内の足元の位置


def cat_sprite(phase, pose, tail_ph, facing, scale):
    size = (100 * SS, 56 * SS)
    body = Image.new("L", size, 0)
    _cat_shapes(ImageDraw.Draw(body), phase, pose, tail_ph, 255, dy=0.0)
    up = Image.new("L", size, 0)
    _cat_shapes(ImageDraw.Draw(up), phase, pose, tail_ph, 255, dy=-1.0)
    rim = ImageChops.subtract(up, body)                               # 上側の縁だけ（夕日の逆光）
    im = Image.new("RGBA", size, CAT_DARK[:3] + (0,))
    im.paste(Image.new("RGBA", size, CAT_DARK), (0, 0), body)
    im.paste(Image.new("RGBA", size, CAT_RIM), (0, 0), rim)
    if facing < 0:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.convert("RGBa").resize((max(1, int(100 * scale)), max(1, int(56 * scale))), Image.LANCZOS)  # 乗算済みαで縮小（縁のにじみ防止）
    return im.convert("RGBA")


CAT_SCENES = [  # (開始, 終了, [(区間の終わりの時刻, x, 動き)...], 向き, y, 大きさ)
    dict(t0=18, x0=-80, y=662, s=1.15, facing=1, keys=[(36, 1360, "walk")]),
    dict(t0=92, x0=1360, y=602, s=0.85, facing=-1, keys=[(104, 720, "walk"), (113, 720, "sit"), (121, -80, "walk")]),
    dict(t0=165, x0=-80, y=672, s=1.2, facing=1, keys=[(183, 1360, "walk")]),
]


def cat_state(t):
    for sc in CAT_SCENES:
        if not sc["t0"] <= t < sc["keys"][-1][0]:
            continue
        ts, xs = sc["t0"], sc["x0"]
        dist = 0.0
        for te, xe, mode in sc["keys"]:
            if t < te:
                u = (t - ts) / (te - ts)
                x = xs + (xe - xs) * u if mode == "walk" else xs
                dist += abs(x - xs)
                facing = sc["facing"] if mode == "sit" or xe == xs else (1 if xe > xs else -1)
                return dict(x=x, y=sc["y"], s=sc["s"], pose=mode, facing=facing, dist=dist, t=t)
            dist += abs(xe - xs)
            ts, xs = te, xe
    return None


def draw_cat(layer, t):
    st = cat_state(t)
    if st is None:
        return
    s = st["s"]
    phase = TAU * st["dist"] / (34 * s)                                  # 歩幅に合わせて脚を動かす
    tail_ph = TAU * t / (2.4 if st["pose"] == "sit" else 1.6)
    spr = cat_sprite(phase, st["pose"], tail_ph, st["facing"], s)
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))                # 夕日を背にした影は手前に伸びる
    ImageDraw.Draw(shadow).ellipse([st["x"] - 24 * s, st["y"] - 2 * s, st["x"] + 24 * s, st["y"] + 9 * s], fill=(20, 8, 10, 80))
    layer.alpha_composite(shadow)
    layer.alpha_composite(spr, (int(st["x"] - OX / SS * s), int(st["y"] - OY / SS * s)))


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
    draw_cat(frame, t)
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
        for t in (24.0, 60.0, 108.0, 200.0):
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
