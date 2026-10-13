#!/usr/bin/env python3
"""海へ続く商店街（幻想版）の背景 + タイトル文字 + 曲 で YouTube 用動画を作る。
- 背景: canva/sunset_street2_mystic.jpg（make_mystic_bg.py で作成）
- 文字: しっぽり明朝（SIL OFL, fonts/OFL.txt）、白文字＋オレンジの光
- 動き: 背景がゆっくりズーム（Ken Burns）、頭はフェードイン
出力: yunagi-dori_street_youtube.mp4（1920x1080, 30fps）と thumbnail_street.png（1280x720）"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1920, 1080
S = W / 1280  # Canva 版（1280x720）のレイアウトからの倍率
FONT_XB = os.path.join(HERE, "fonts", "ShipporiMincho_800ExtraBold.ttf")
FONT_B = os.path.join(HERE, "fonts", "ShipporiMincho_700Bold.ttf")
CX = 720 * S  # 文字のまとまりの中心（空の部分、画面のやや右）

LINES = [  # (文字, フォント, 大きさ, 中心 y, 字間)
    ("― オリジナル曲 ―", FONT_B, 40, 100, 6),
    ("夕凪通り", FONT_XB, 168, 212, 10),
    ("昭和ノスタルジー風フィールドBGM", FONT_B, 46, 330, 2),
]


def draw_spaced(d, cx, cy, text, font, spacing, fill):
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    asc, desc = font.getmetrics()
    y = cy - (asc + desc) / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill)
        x += w + spacing


def text_layer():
    """白文字 + 外側のオレンジの光 + 下の濃い影 を透過 PNG で作る"""
    shapes = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(shapes)
    for text, path, size, cy, sp in LINES:
        draw_spaced(d, CX, cy * S, text, ImageFont.truetype(path, int(size * S)), sp * S, 255)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = shapes.filter(ImageFilter.GaussianBlur(8 * S))
    layer.paste(Image.new("RGBA", (W, H), (60, 15, 0, 255)), (int(3 * S), int(5 * S)), shadow.point(lambda v: int(v * 0.85)))
    for radius, color, k in ((40, (255, 120, 20), 0.75), (14, (255, 170, 60), 0.9)):
        glow = shapes.filter(ImageFilter.GaussianBlur(radius * S)).point(lambda v, k=k: min(255, int(v * k * 1.6)))
        layer = Image.alpha_composite(layer, Image.merge("RGBA", (*Image.new("RGB", (W, H), color).split(), glow)))
    white = Image.merge("RGBA", (*Image.new("RGB", (W, H), (255, 252, 244)).split(), shapes))
    return Image.alpha_composite(layer, white)


def main():
    bg = Image.open(os.path.join(HERE, "canva", "sunset_street2_mystic.jpg")).convert("RGB").resize((W, H), Image.LANCZOS)
    bg = bg.filter(ImageFilter.UnsharpMask(1.5, 50, 2))
    bg_path = os.path.join(HERE, "street_bg_1080.png")
    bg.save(bg_path)
    txt = text_layer()
    txt_path = os.path.join(HERE, "street_text_1080.png")
    txt.save(txt_path)
    thumb = Image.alpha_composite(bg.convert("RGBA"), txt).convert("RGB").resize((1280, 720), Image.LANCZOS)
    thumb.save(os.path.join(HERE, "thumbnail_street.png"))

    audio = os.path.join(HERE, "..", "yunagi-dori_full.wav")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", audio]).decode())
    frames = int(dur * 30) + 1
    # 背景は 2 倍に拡大してからズームすると、ゆっくりした動きでもガタつかない
    vf = (f"[0:v]scale={W * 2}:{H * 2},zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d=1:s={W}x{H}:fps=30[bg];[bg][1:v]overlay=0:0,fade=t=in:st=0:d=1.5,format=yuv420p[v]")
    out = os.path.join(HERE, "yunagi-dori_street_youtube.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stats", "-loop", "1", "-framerate", "30", "-t", f"{dur:.3f}", "-i", bg_path,
                    "-i", txt_path, "-i", audio, "-filter_complex", vf, "-map", "[v]", "-map", "2:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", "30",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(bg_path)
    os.remove(txt_path)
    print("wrote", out)


if __name__ == "__main__":
    main()
