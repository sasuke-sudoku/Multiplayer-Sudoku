#!/usr/bin/env python3
"""「海へ続く商店街」の背景に“風”のアニメーションを付けた YouTube 用動画を作る。

1 枚絵の各部分を領域ごとに動かし、風の強弱（突風）に合わせて反応させる:
  * 木・生け垣・鉢植え …… 風下へしなりながら細かく揺れる
  * 店の日よけ（赤白の庇） …… 波打つようにはためく
  * 吊り看板「みまのや」 …… 振り子のように揺れる
  * 電線 ……………………… 上下にたわんで揺れる
  * 雲 ………………………… ゆっくり流れてうねる
  * 海の照り返し …………… きらめく
  * 舞う木の葉・光の粒・風の筋 …… 風速に合わせて画面を横切る
24 秒で継ぎ目なくループする映像を作り、曲の長さまで繰り返して音を付ける。
文字（タイトル）は make_video_street.py と同じものを上に重ねる（風では動かない）。

出力: yunagi-dori_wind_youtube.mp4（1920x1080, 30fps）
使い方: python3 make_wind_video.py
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_video_street as street  # noqa: E402  文字レイヤーを共有

W, H = 1280, 720          # 動きの計算はこの解像度で行い、最後に 1920x1080 へ拡大
FPS = 30
LOOP = 24.0               # ループの長さ（秒）。周期的な動きはすべてこの長さで一周する
N = int(LOOP * FPS)
rng = np.random.default_rng(2026)
TAU = 2 * math.pi


def per(k):
    """ループ長で k 周期になる角周波数（ループの継ぎ目で動きが一致する）"""
    return TAU * k / LOOP


# ---------------------------------------------------------------- 風の強さ
def wind(t):
    """0.3（そよ風）〜 1.0（突風）。t=5 秒と 15.5 秒あたりで突風が来る"""
    g = 0.3
    for c, w, a in ((5.0, 1.6, 0.7), (15.5, 2.2, 0.55)):
        d = (t - c + LOOP / 2) % LOOP - LOOP / 2           # ループをまたいでも滑らか
        g += a * math.exp(-(d / w) ** 2)
    return g + 0.04 * math.sin(per(7) * t)


# 葉や粒の移動量を決めるため、風の強さの積分（ループ 1 周で正規化）を前計算
_ts = np.arange(N) / FPS
_wind = np.array([wind(t) for t in _ts])
_cum = np.concatenate([[0], np.cumsum(_wind)[:-1]]) / _wind.sum()   # 0 → 1 に増える


# ---------------------------------------------------------------- 補助
def smooth_noise(shape, cells, seed):
    r = np.random.default_rng(seed)
    small = Image.fromarray((r.random((cells[1], cells[0])) * 255).astype(np.uint8))
    return np.asarray(small.resize((shape[1], shape[0]), Image.BICUBIC)).astype(np.float32) / 255 * 2 - 1


def region(box, feather=18, shape="rect"):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    (d.ellipse if shape == "ellipse" else d.rectangle)(box, fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(feather))).astype(np.float32) / 255


def blur(m, r):
    return np.asarray(Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255


def sample(img, x, y):
    """双一次補間で img を座標 (x, y) から読む"""
    x = np.clip(x, 0, W - 1.001)
    y = np.clip(y, 0, H - 1.001)
    x0 = x.astype(np.int32)
    y0 = y.astype(np.int32)
    fx = (x - x0)[..., None]
    fy = (y - y0)[..., None]
    a = img[y0, x0]
    b = img[y0, x0 + 1]
    c = img[y0 + 1, x0]
    d = img[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


# ---------------------------------------------------------------- 準備: 領域マスク
def build_masks(img):
    hsv = np.asarray(Image.fromarray((img * 255).astype(np.uint8)).convert("HSV")).astype(np.float32) / 255
    hue, sat, val = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    lum = img @ np.array([0.299, 0.587, 0.114], np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    greenish = blur(((hue > 45) & (hue < 175) & (sat > 0.12)).astype(np.float32), 3)
    foliage_zone = np.maximum.reduce([
        region((990, 410, 1280, 580), 25),           # 右の生け垣
        region((880, 320, 1010, 470), 20, "ellipse"),  # 右奥の木
        region((480, 260, 620, 470), 22, "ellipse"),   # 中央の木
        region((0, 420, 130, 610), 20),              # 左手前の植え込み
        region((150, 580, 240, 660), 12),            # 鉢植えの花
        region((290, 420, 430, 530), 16),            # 店先の鉢植え
    ])
    foliage = np.clip(foliage_zone * (0.35 + 0.65 * greenish), 0, 1)

    reddish = (((hue < 25) | (hue > 330)) & (sat > 0.35) & (val > 0.3)).astype(np.float32)
    awning_zone = np.maximum(region((115, 195, 345, 365), 10), region((395, 280, 535, 395), 10))
    awning = blur(np.clip(awning_zone * (0.4 + 0.6 * blur(reddish, 4)), 0, 1), 3)

    sign = region((258, 128, 314, 262), 4)               # 吊り看板「みまのや」
    sign2 = region((474, 240, 510, 322), 3)

    sky_zone = (yy < 400).astype(np.float32) * np.clip((xx - 540) / 80, 0, 1)
    dark_line = (lum < 0.30).astype(np.float32)          # 電線・電柱・家の輪郭は動かさない
    sky = blur(sky_zone * (1 - blur(dark_line, 2) * 1.6).clip(0, 1) * (lum > 0.3), 6)
    sky *= 1 - region((1090, 200, 1280, 420), 20)        # 右の家の屋根を除く
    sky *= 1 - region((860, 300, 1010, 430), 15)

    thin_dark = np.clip(blur(lum, 3) - lum - 0.05, 0, 1) * 6   # 周囲より暗い細い線 = 電線
    wires = np.clip(thin_dark, 0, 1) * np.maximum(region((430, 0, 680, 340), 10), region((990, 90, 1280, 330), 10))
    wires *= blur(blur((lum > 0.35).astype(np.float32), 5) > 0.7, 2)   # 周りが空のところだけ（屋根の線は除く）
    wires = blur(wires, 2.5) * 1.8

    sea = region((630, 405, 900, 512), 12) * (1 - foliage_zone)
    glint = np.clip((lum - 0.55) / 0.35, 0, 1) * sea

    return dict(foliage=foliage, awning=awning, sign=sign, sign2=sign2, sky=np.clip(sky, 0, 1),
                wires=np.clip(wires, 0, 1), glint=glint)


# ---------------------------------------------------------------- 粒子（木の葉・光の粒・風の筋）
class Leaf:
    def __init__(self, i):
        self.laps = int(rng.integers(1, 3))              # ループ中に画面を何回横切るか（整数 → 継ぎ目なし）
        self.x0 = rng.uniform(0, 1)
        self.y = rng.uniform(80, 650)
        self.amp = rng.uniform(15, 45)
        self.ph = rng.uniform(0, TAU)
        self.k = int(rng.integers(2, 6))
        self.size = rng.uniform(8, 15)
        self.spin = int(rng.integers(3, 9)) * rng.choice([-1, 1])
        self.color = [(214, 120, 40), (190, 80, 30), (230, 170, 60), (120, 140, 50), (240, 140, 90)][i % 5]

    def pos(self, f):
        span = W + 120
        x = ((self.x0 + self.laps * _cum[f]) % 1) * span - 60
        y = self.y + self.amp * math.sin(per(self.k) * _ts[f] + self.ph) + 25 * (_wind[f] - 0.3)
        return x, y


class Mote:
    def __init__(self):
        self.x0 = rng.uniform(0, 1)
        self.y = rng.uniform(40, 600)
        self.laps = 1
        self.amp = rng.uniform(5, 20)
        self.k = int(rng.integers(1, 4))
        self.ph = rng.uniform(0, TAU)
        self.r = rng.uniform(1.2, 3.2)
        self.tw = int(rng.integers(4, 12))

    def pos(self, f):
        x = ((self.x0 + self.laps * _cum[f]) % 1) * (W + 40) - 20
        y = self.y + self.amp * math.sin(per(self.k) * _ts[f] + self.ph)
        return x, y


def draw_particles(f, leaves, motes):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    g = ImageDraw.Draw(glow)
    t = _ts[f]
    # 風の筋（突風のときだけ現れる、アニメ風の白い線）
    strength = max(0.0, (_wind[f] - 0.55) / 0.45)
    if strength > 0:
        for j in range(7):
            yb = 120 + j * 70 + 20 * math.sin(j * 1.7)
            xs = ((j * 0.37 + 3 * _cum[f]) % 1) * (W + 600) - 300
            pts = [(xs + u * 260, yb + 14 * math.sin(u * 3 + j)) for u in np.linspace(0, 1, 14)]
            g.line(pts, fill=(255, 245, 225, int(120 * strength)), width=3)
    # 光の粒
    for m in motes:
        x, y = m.pos(f)
        a = 0.55 + 0.45 * math.sin(per(m.tw) * t + m.ph)
        g.ellipse([x - m.r * 2.5, y - m.r * 2.5, x + m.r * 2.5, y + m.r * 2.5], fill=(255, 210, 140, int(90 * a)))
        d.ellipse([x - m.r, y - m.r, x + m.r, y + m.r], fill=(255, 240, 200, int(230 * a)))
    # 木の葉（回転しながら飛ぶ、楕円の葉＋葉脈）
    for lf in leaves:
        x, y = lf.pos(f)
        ang = per(lf.spin) * t + lf.ph
        flip = abs(math.cos(per(lf.spin) * t * 0.5 + lf.ph))       # 裏返り（幅が縮む）
        L, Wd = lf.size, lf.size * 0.45 * (0.25 + 0.75 * flip)
        pts = []
        for u in np.linspace(0, TAU, 14):
            px, py = L * math.cos(u), Wd * math.sin(u) * (1 - 0.3 * math.cos(u))
            pts.append((x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)))
        shade = 0.75 + 0.25 * flip
        col = tuple(int(c * shade) for c in lf.color) + (235,)
        d.polygon(pts, fill=col)
        d.line([(x - L * math.cos(ang), y - L * math.sin(ang)), (x + L * math.cos(ang), y + L * math.sin(ang))],
               fill=(90, 50, 20, 160), width=1)
    glow = glow.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(glow, layer)


# ---------------------------------------------------------------- 1 フレームの描画
def render_frame(f, img, M, fields, leaves, motes):
    t = _ts[f]
    w = _wind[f]
    yy, xx = fields["grid"]
    dx = np.zeros((H, W), np.float32)
    dy = np.zeros((H, W), np.float32)

    # 木・植え込み: 風下（右）へしなる + 葉ごとに位相のずれた細かい揺れ
    lean = 4.5 * w
    flutter = (1.5 + 3.0 * w) * np.sin(per(19) * t + fields["ph_fol"]) + 0.8 * w * np.sin(per(41) * t + 2 * fields["ph_fol"])
    dx -= M["foliage"] * (lean + flutter) * (0.6 + 0.4 * fields["n_fol"])
    dy -= M["foliage"] * 0.9 * w * np.sin(per(23) * t + fields["ph_fol"] * 1.3)

    # 日よけ: 左から右へ波が走るようにはためく
    wave = np.sin(xx / 22 - per(29) * t) + 0.5 * np.sin(xx / 9 - per(53) * t)
    dy -= M["awning"] * (0.6 + 2.0 * w) * wave
    dx -= M["awning"] * 0.8 * w

    # 吊り看板: 上端を支点に振り子のように揺れる
    for key, (px, py, length) in (("sign", (286, 128, 134)), ("sign2", (492, 240, 82))):
        theta = (0.010 + 0.05 * w) * math.sin(per(11) * t + (0 if key == "sign" else 1.3)) + 0.025 * (w - 0.3)
        rel_y = np.clip(yy - py, 0, length)
        dx -= M[key] * rel_y * theta
        dy -= M[key] * (xx - px) * (-theta) * 0.2

    # 電線: たわみの振動（位置によって位相が進む）
    dy -= M["wires"] * (0.6 + 2.2 * w) * np.sin(per(13) * t - xx / 140)

    # 雲: 風で流れながらゆっくりうねる
    dx -= M["sky"] * (6 * np.sin(per(1) * t + yy / 120) + 2.5 * w * fields["n_sky"] * np.sin(per(3) * t + xx / 200))
    dy -= M["sky"] * 1.5 * np.sin(per(2) * t + xx / 160)

    out = sample(img, xx + dx, yy + dy)

    # 海のきらめき
    sparkle = np.clip(np.sin(xx / 3.1 + per(37) * t + fields["ph_sea"]) * np.sin(yy / 1.7 - per(29) * t), 0, 1) ** 6
    out = out + (M["glint"] * (0.25 + 0.5 * sparkle))[..., None] * np.array([1.0, 0.85, 0.55], np.float32) * 0.6

    # 突風のときは画面全体がわずかに明るくなり、木漏れ日がちらつく
    out = out * (1 + 0.025 * (w - 0.3))

    frame = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    frame = Image.alpha_composite(frame, draw_particles(f, leaves, motes))
    return frame.convert("RGB")


def main():
    img = np.asarray(Image.open(os.path.join(HERE, "canva", "sunset_street2_mystic.jpg")).convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    M = build_masks(img)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fields = dict(grid=(yy, xx),
                  ph_fol=(smooth_noise((H, W), (40, 24), 1) * math.pi).astype(np.float32),
                  n_fol=smooth_noise((H, W), (20, 12), 2),
                  n_sky=smooth_noise((H, W), (8, 5), 3),
                  ph_sea=(smooth_noise((H, W), (30, 10), 4) * 3).astype(np.float32))
    leaves = [Leaf(i) for i in range(26)]
    motes = [Mote() for _ in range(70)]

    frames_dir = os.path.join(HERE, "_wind_frames")
    os.makedirs(frames_dir, exist_ok=True)
    preview = "--preview" in sys.argv
    todo = range(int(4 * FPS), int(6 * FPS), 6) if preview else range(N)
    for f in todo:
        render_frame(f, img, M, fields, leaves, motes).save(os.path.join(frames_dir, f"{f:04d}.png"), compress_level=1)
        if f % 60 == 0:
            print(f"frame {f}/{N}", flush=True)
    if preview or "--frames-only" in sys.argv:   # --frames-only: ループの各フレームだけ残す（make_story_video.py 用）
        return

    # テキストレイヤー（1920x1080）
    txt_path = os.path.join(HERE, "_wind_text.png")
    street.text_layer().save(txt_path)
    loop_mp4 = os.path.join(HERE, "_wind_loop.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(frames_dir, "%04d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv444p", loop_mp4], check=True)
    audio = os.path.join(HERE, "..", "yunagi-dori_full.wav")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio]).decode())
    out = os.path.join(HERE, "yunagi-dori_wind_youtube.mp4")
    vf = (f"[0:v]scale=1920:1080:flags=lanczos,unsharp=5:5:0.4[bg];[bg][1:v]overlay=0:0,"
          f"fade=t=in:st=0:d=1.5,fade=t=out:st={dur - 3:.2f}:d=3,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stats", "-stream_loop", "-1", "-i", loop_mp4, "-i", txt_path, "-i", audio,
                    "-filter_complex", vf, "-map", "[v]", "-map", "2:a", "-t", f"{dur:.3f}",
                    "-c:v", "libx264", "-preset", "medium", "-b:v", "3000k", "-maxrate", "4500k", "-bufsize", "9000k", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
    for p in os.listdir(frames_dir):
        os.remove(os.path.join(frames_dir, p))
    os.rmdir(frames_dir)
    os.remove(txt_path)
    os.remove(loop_mp4)
    print("wrote", out)


if __name__ == "__main__":
    main()
