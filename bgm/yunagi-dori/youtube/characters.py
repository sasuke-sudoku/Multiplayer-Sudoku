"""動画に登場する猫と自転車の人（夕日を背にしたシルエット）。

猫:
  * 歩き方は「ラテラル・シーケンス」（左後→左前→右後→右前の順に足を出す）の歩行。
    着地中の足は地面に固定し（足が滑らない）、膝・肘の角度は足の位置から逆算（2 関節 IK）する。
  * 速さを落とすと脚の動きも自然に遅くなる（脚の位相は移動距離で決まる）。
  * 座るときは減速 → 背中を向けて腰を下ろす → 海を眺める（耳・頭・しっぽの先が時々動く）
    → 振り返って立ち、加速して歩き去る。
自転車の人:
  * 道の奥行きに合わせた遠近（遠ざかるほど小さく、消失点へ）。ペダルをこぐ脚と車体の揺れ。
  * 日本は左側通行なので、遠ざかる人は画面の左寄り、近づく人は右寄りを走る。
どちらも上側・横の縁が夕日で光り、影は手前（カメラ側）に長く伸びる。
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

TAU = 2 * math.pi
SS = 4                       # 4 倍の解像度で描いてから縮小
DARK = (32, 22, 25, 255)
RIM = (255, 158, 82, 255)


def smoothstep(a, b, x):
    x = min(1.0, max(0.0, (x - a) / (b - a)))
    return x * x * (3 - 2 * x)


class Canvas:
    """シルエットを 1 色のマスクとして描く小さな画用紙。原点 (ox, oy) は足元、1 単位 = SS px"""

    def __init__(self, w, h, ox, oy):
        self.size = (w * SS, h * SS)
        self.ox, self.oy = ox * SS, oy * SS
        self.m = Image.new("L", self.size, 0)
        self.d = ImageDraw.Draw(self.m)

    def P(self, x, y):
        return (self.ox + x * SS, self.oy + y * SS)

    def ell(self, cx, cy, rx, ry, rot=0.0):
        c, s = math.cos(rot), math.sin(rot)
        pts = [self.P(cx + rx * math.cos(u) * c - ry * math.sin(u) * s, cy + rx * math.cos(u) * s + ry * math.sin(u) * c)
               for u in np.linspace(0, TAU, 32)]
        self.d.polygon(pts, fill=255)

    def poly(self, pts):
        self.d.polygon([self.P(x, y) for x, y in pts], fill=255)

    def limb(self, pts, w0, w1=None):
        """太さが w0 → w1 に変わる関節つきの線（丸い関節）"""
        w1 = w0 if w1 is None else w1
        for i in range(len(pts) - 1):
            wa = w0 + (w1 - w0) * i / max(1, len(pts) - 1)
            wb = w0 + (w1 - w0) * (i + 1) / max(1, len(pts) - 1)
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            ang = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
            ca, sa = math.cos(ang), math.sin(ang)
            self.poly([(x0 + ca * wa / 2, y0 + sa * wa / 2), (x1 + ca * wb / 2, y1 + sa * wb / 2),
                       (x1 - ca * wb / 2, y1 - sa * wb / 2), (x0 - ca * wa / 2, y0 - sa * wa / 2)])
            self.ell(x0, y0, wa / 2, wa / 2)
        self.ell(*pts[-1], w1 / 2, w1 / 2)

    def curve(self, pts, w0, w1):
        self.limb(pts, w0, w1)


def finish(body_mask, rim_shifts, scale, flip=False, rotate=0.0, origin=None):
    """マスクから「暗い本体＋夕日の縁」の RGBA スプライトを作り、縮小する"""
    rim = Image.new("L", body_mask.size, 0)
    for dx, dy in rim_shifts:
        rim = ImageChops.lighter(rim, ImageChops.offset(body_mask, int(dx * SS), int(dy * SS)))
    rim = ImageChops.subtract(rim, body_mask)
    im = Image.new("RGBA", body_mask.size, DARK[:3] + (0,))
    im.paste(Image.new("RGBA", body_mask.size, DARK), (0, 0), body_mask)
    im.paste(Image.new("RGBA", body_mask.size, RIM), (0, 0), rim.filter(ImageFilter.GaussianBlur(SS * 0.3)))
    if rotate:
        im = im.rotate(rotate, resample=Image.BICUBIC, center=origin)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    w, h = body_mask.size
    return im.convert("RGBa").resize((max(1, round(w / SS * scale)), max(1, round(h / SS * scale))), Image.LANCZOS).convert("RGBA")


def two_bone(j, f, l1, l2, bend):
    """関節 j から足先 f へ、長さ l1, l2 の 2 本の骨。bend=+1 で関節が後ろ（-x）に曲がる"""
    dx, dy = f[0] - j[0], f[1] - j[1]
    d = min(math.hypot(dx, dy), l1 + l2 - 1e-3)
    a = math.atan2(dy, dx)
    cos_k = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    k = math.acos(max(-1.0, min(1.0, cos_k)))
    ang = a + k * bend
    return (j[0] + l1 * math.cos(ang), j[1] + l1 * math.sin(ang))


# ================================================================ 猫
STRIDE = 26.0      # 1 歩行周期で進む距離（単位）
DUTY = 0.62        # 足が地面に着いている割合
GAIT = {"LH": 0.0, "LF": 0.25, "RH": 0.5, "RF": 0.75}


def _foot(u, joint_x, reach):
    if u < DUTY:                                     # 着地中: 体が進む分だけ後ろへ（地面に対して静止）
        return joint_x + reach + STRIDE * DUTY * (0.5 - u / DUTY), -0.6
    v = (u - DUTY) / (1 - DUTY)                      # 振り出し: 弧を描いて前へ
    return joint_x + reach + STRIDE * DUTY * (-0.5 + v), -0.6 - 3.2 * math.sin(math.pi * v) ** 0.8


def cat_side_mask(dist, t, stand=0.0):
    """横向き（右向き）の歩く猫。dist=移動距離（脚の位相）、stand=1 で四つ足で静止"""
    c = Canvas(84, 52, 42, 46)
    cyc = dist / STRIDE
    bob = 0.45 * math.cos(TAU * 2 * cyc) * (1 - stand)
    sh = (8.5, -12.5 + bob)                          # 肩
    hp = (-9.5, -12.0 - bob * 0.6)                   # 腰
    legs = []
    for name, off in GAIT.items():
        u = (cyc + off) % 1.0
        front = name[1] == "F"
        jx, jy = sh if front else hp
        fx, fy = _foot(u, jx, 1.2 if front else -0.8)
        if stand:
            fx = fx * (1 - stand) + (jx + (1.2 if front else -0.8) + (1.5 if name[0] == "L" else -1.5)) * stand
            fy = fy * (1 - stand) - 0.6 * stand
        legs.append((name, front, (jx, jy), (fx, fy)))
    # 奥の脚（右側）を先に、少し細く描く
    for name, front, j, f in sorted(legs, key=lambda L: L[0][0] != "R"):
        far = name[0] == "R"
        w = 0.88 if far else 1.0
        if front:
            knee = two_bone(j, f, 6.4, 6.4, +1)                      # 肘は後ろへ
            c.limb([j, knee, f], 4.4 * w, 2.9 * w)
        else:
            knee = two_bone(j, (f[0] - 2.2, f[1] - 4.5), 6.0, 4.8, -1)  # 膝は前、かかと（飛節）は後ろ
            hock = (f[0] - 2.2, f[1] - 4.5)
            c.limb([j, knee, hock, f], 5.6 * w, 2.8 * w)
    # 胴（胸が少し高く、腹がわずかに垂れる）
    c.ell(-0.5, -15.0 + bob * 0.4, 14.5, 7.6, 0.02)
    c.ell(hp[0] - 0.5, hp[1] - 2.8, 7.4, 7.2)
    c.ell(sh[0] + 0.5, sh[1] - 3.2, 6.8, 7.0)
    c.ell(0, -12.5, 11, 4.5)                         # 腹
    # 首と頭（頭は背中とほぼ同じ高さで、歩みに合わせてわずかに上下）
    hb = 0.35 * math.sin(TAU * 2 * cyc + 0.6) * (1 - stand)
    hx, hy = 19.0, -21.5 + hb
    c.poly([(sh[0] + 1, sh[1] - 9), (hx - 2.5, hy - 5), (hx + 1, hy + 4.5), (sh[0] + 5, sh[1] - 0.5)])
    c.ell(hx, hy, 6.0, 5.4)
    c.ell(hx + 4.6, hy + 1.6, 2.6, 2.1)              # 鼻先
    c.poly([(hx - 4.6, hy - 2.4), (hx - 3.4, hy - 10.0), (hx - 0.2, hy - 4.6)])   # 耳
    c.poly([(hx + 0.4, hy - 4.8), (hx + 2.6, hy - 10.2), (hx + 4.6, hy - 2.6)])
    # しっぽ: 付け根から上に立ち、先が少し前に曲がる（ゆっくり揺れる）
    sway = math.sin(TAU * t / 2.3)
    base = (hp[0] - 5.5, hp[1] - 6.0)
    pts = []
    for u in np.linspace(0, 1, 14):
        ang = math.radians(150 - 75 * u ** 1.3 + 10 * sway * u)
        r = 19 * u
        pts.append((base[0] + r * math.cos(ang) * 0.75 - 1.5 * u, base[1] - r * math.sin(ang)))
    tip = pts[-1]
    pts.append((tip[0] + 2.2 + 1.2 * sway, tip[1] - 0.8))
    c.curve(pts, 3.6, 2.4)
    return c.m


def cat_back_mask(t, k=1.0, look=0.0):
    """背中を向けた猫。k=0 で立っている（後ろ脚が見え、しっぽが立つ）→ k=1 で座る。look=-1..1 で頭を左右に"""
    c = Canvas(60, 52, 30, 46)
    L = lambda a, b: a + (b - a) * k  # noqa: E731
    breathe = 1 + 0.012 * math.sin(TAU * t / 3.2) * k
    if k < 0.98:                                                        # 後ろ脚（座ると隠れる）
        for side in (-1, 1):
            c.limb([(side * L(4.2, 6.0), L(-11.0, -5.0)), (side * L(4.6, 7.0), L(-4.5, -2.0)), (side * L(4.4, 7.0), -0.6)], 4.4, 3.0)
    c.ell(0, L(-13.5, -6.0), L(8.4, 12.5), L(7.4, 6.5))                  # 腰
    c.ell(0, L(-17.0, -13.0) * breathe, L(7.0, 9.8), L(6.5, 11.5) * breathe)  # 胴
    c.ell(0, L(-20.0, -21.5), L(6.2, 7.4), L(4.6, 6.0))                  # 肩
    hx = 1.6 * look
    hy = L(-25.5, -29.0)
    c.ell(hx, hy, 7.0 - 0.6 * abs(look), 6.2)                           # 頭（横を向くと少し細く）
    flick = max(0.0, math.sin(TAU * t / 5.3)) ** 30 * k                 # ときどき耳がぴくっと動く
    le = (-4.8 + hx - 0.8 * look, hy - 2.5)
    re = (4.8 + hx - 0.8 * look, hy - 2.5)
    c.poly([(le[0] - 1.8, le[1] + 0.5), (le[0] - 0.6 - 1.5 * flick, le[1] - 8.0 + 1.2 * flick), (le[0] + 2.4, le[1] - 1.2)])
    c.poly([(re[0] - 2.4, re[1] - 1.2), (re[0] + 0.6 + 0.5 * look, re[1] - 8.0), (re[0] + 1.8, re[1] + 0.5)])
    # しっぽ: 立っているときは真上に立ち、座ると地面に沿って体の前へ回り込む
    tw = math.sin(TAU * t / 1.4) * (0.5 + 0.5 * math.sin(TAU * t / 9.0))
    up = [(0.8 * math.sin(u * 2.2) + 2.2 * u ** 3 + 0.8 * math.sin(TAU * t / 2.3) * u, -15.0 - 18.0 * u) for u in np.linspace(0, 1, 14)]
    down = [(8.5 + 12 * math.sin(u * 1.9), -2.0 - 2.5 * math.sin(math.pi * u) - (3.5 * tw) * u ** 5) for u in np.linspace(0, 1, 14)]
    c.curve([(L(a[0], b[0]), L(a[1], b[1])) for a, b in zip(up, down)], 3.4, 2.6)
    return c.m


# 猫の出番: 区間ごとに (開始, 終了, 動き, 始点, 終点)。y は足元
CAT_SCENES = [
    dict(scale=1.1, segs=[(16.0, 44.0, "walk", (-60, 652), (1345, 668))]),
    dict(scale=0.85, segs=[(90.0, 104.0, "walk_stop", (1345, 607), (735, 616)),
                           (104.0, 105.6, "to_sit", (735, 616), (735, 616)),
                           (105.6, 119.0, "sit", (735, 616), (735, 616)),
                           (119.0, 120.4, "to_walk", (735, 616), (735, 616)),
                           (120.4, 135.0, "walk_start", (735, 616), (-60, 610))]),
    dict(scale=1.25, segs=[(167.0, 193.0, "walk", (1345, 690), (-60, 678))]),
]


def _seg_pos(seg, t):
    t0, t1, kind, p0, p1 = seg
    u = (t - t0) / (t1 - t0)
    if kind == "walk_stop":     # 最後の 3 割でゆっくり止まる
        e = u / 0.7 * 0.85 if u < 0.7 else 0.85 + 0.15 * (1 - (1 - (u - 0.7) / 0.3) ** 2)
    elif kind == "walk_start":  # 最初の 2 割で歩き出す
        e = 0.1 * (u / 0.2) ** 2 if u < 0.2 else 0.1 + 0.9 * (u - 0.2) / 0.8
    else:
        e = u
    return p0[0] + (p1[0] - p0[0]) * e, p0[1] + (p1[1] - p0[1]) * e


def draw_cat(frame, t):
    for sc in CAT_SCENES:
        segs = sc["segs"]
        if not segs[0][0] <= t < segs[-1][1]:
            continue
        s = sc["scale"]
        dist = 0.0                                   # この場面での累積移動距離（単位）
        for seg in segs:
            t0, t1, kind, p0, p1 = seg
            if t >= t1:
                dist += math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / s
                continue
            x, y = _seg_pos(seg, t)
            dist += math.hypot(x - p0[0], y - p0[1]) / s
            facing = 1 if (p1[0] - p0[0]) > 0 else -1
            if kind in ("to_sit", "sit", "to_walk"):
                facing = -1
            u = (t - t0) / (t1 - t0)
            sprites = []
            if kind in ("walk", "walk_stop", "walk_start"):
                sprites.append((cat_side_mask(dist, t), 1.0, (42, 46), facing == -1, 0.0))
            elif kind == "sit":
                look = 0.0
                for lc in (108.5, 114.0):            # ときどき左右を見回す
                    look += math.sin(math.pi * smoothstep(lc, lc + 2.4, t)) * (1 if lc < 110 else -0.8)
                sprites.append((cat_back_mask(t, 1.0, look), 1.0, (30, 46), False, 0.0))
            else:
                # 座る: 背中を向ける（0.25 秒で横向き→後ろ向き）→ 腰を下ろす。立つときはその逆
                dur = t1 - t0
                turn = 0.25 / dur
                v = u if kind == "to_sit" else 1 - u
                swap = smoothstep(0, turn, v)                              # 横向き → 後ろ向き
                k = smoothstep(turn, 1.0, v)                               # 立ち → 座り
                if swap < 1:
                    sprites.append((cat_side_mask(dist, t, stand=1.0), 1 - swap, (42, 46), True, 0.0))
                if swap > 0:
                    sprites.append((cat_back_mask(t, k), swap, (30, 46), False, 0.0))
            # 影（夕日を背にしているので手前に伸びる）
            sh = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).polygon([(x - 16 * s, y - 1), (x + 16 * s, y - 1), (x + 22 * s, y + 13 * s), (x - 20 * s, y + 13 * s)],
                                       fill=(20, 8, 12, 70))
            frame.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3 * s)))
            for mask, alpha, (ox, oy), flip, rot in sprites:
                if alpha <= 0.01:
                    continue
                spr = finish(mask, [(0, -1.0), (-0.5, -0.6), (0.5, -0.6)], s, flip=flip)
                if alpha < 1:
                    spr.putalpha(spr.getchannel("A").point(lambda v, a=alpha: int(v * a)))
                w = spr.width
                px = x - ((w - ox * s) if flip else ox * s)
                frame.alpha_composite(spr, (int(round(px)), int(round(y - oy * s))))
            return


# ================================================================ 自転車の人
VP = (708.0, 552.0)        # 道の消失点（海へ下りていく坂の先）


def rider_mask(crank, t):
    """後ろ（または前）から見た自転車の人。逆光なので前後どちらから見ても同じシルエット"""
    c = Canvas(40, 80, 20, 76)
    c.ell(0, -14.5, 2.0, 14.5)                       # 後輪（縦に細く見える）
    c.ell(0.6, -16.5, 1.6, 12.5)                     # 前輪（奥に少しずれて見える）
    c.poly([(-3.4, -31), (3.4, -31), (3.0, -27.5), (-3.0, -27.5)])   # 荷台
    c.limb([(-11.5, -42.5), (-4, -41), (4, -41), (11.5, -42.5)], 1.4)  # ハンドル
    c.ell(0, -31.5, 4.2, 1.7)                        # サドル
    for side in (-1, 1):                             # 脚: クランクの回転に合わせて上下
        a = crank + (0 if side < 0 else math.pi)
        pedal = (side * 4.6, -14.0 + 6.2 * math.sin(a))
        hip = (side * 3.2, -33.0)
        knee = ((hip[0] + pedal[0]) / 2 + side * (1.6 + 0.9 * (1 + math.sin(a))), (hip[1] + pedal[1]) / 2 - 2.0)
        c.limb([hip, knee, pedal], 4.6, 2.9)
        c.ell(pedal[0], pedal[1] + 0.6, 2.2, 1.1)    # 靴
    c.poly([(-5.2, -33.5), (5.2, -33.5), (7.6, -51.5), (-7.6, -51.5)])   # 胴（少し前かがみ）
    c.ell(0, -51.5, 8.0, 3.0)                        # 肩
    for side in (-1, 1):                             # 腕: 肩からハンドルへ
        c.limb([(side * 7.0, -51.0), (side * 10.6, -46.0), (side * 11.0, -42.0)], 2.9, 2.4)
    c.ell(0, -54.2, 2.2, 2.0)                        # 首
    c.ell(0, -60.0, 4.6, 5.2)                        # 頭
    c.ell(0, -63.6, 5.8, 1.7)                        # 学生帽のつば
    c.ell(0, -64.6, 4.6, 2.2)
    return c.m


# (開始, 終了, 遠近 z の始点, 終点, 車線の横位置 x0)。z=1 が画面の手前、z が大きいほど遠い
RIDES = [
    dict(t0=40.0, t1=60.0, z0=0.9, z1=7.5, x0=605.0, cadence=1.05),   # 坂を下って遠ざかる（左側通行）
    dict(t0=139.0, t1=162.0, z0=7.5, z1=0.8, x0=815.0, cadence=0.8),   # 坂を上って近づいてくる
    dict(t0=196.0, t1=214.0, z0=0.9, z1=7.5, x0=600.0, cadence=1.0),
]


def draw_rider(frame, t):
    for r in RIDES:
        if not r["t0"] <= t < r["t1"]:
            continue
        u = (t - r["t0"]) / (r["t1"] - r["t0"])
        z = r["z0"] + (r["z1"] - r["z0"]) * u          # 等速で進む（奥行き z が時間に比例）
        x = VP[0] + (r["x0"] - VP[0]) / z
        y = VP[1] + 280.0 / z
        s = 2.4 / z
        fade = 1 - smoothstep(5.5, 7.5, z)           # 遠くでかすんで消える
        if s < 0.12 or fade <= 0:
            return
        crank = TAU * r["cadence"] * t
        roll = 2.6 * math.sin(crank)                  # ペダルを踏むたびに車体がわずかに傾く
        x += 0.8 * s * math.sin(crank)
        # 影: 夕日を背にしているので手前へ長く伸びる
        sh = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        L = 72 * s
        ImageDraw.Draw(sh).polygon([(x - 3 * s, y), (x + 3 * s, y), (x + 9 * s, y + L), (x - 5 * s, y + L)],
                                   fill=(20, 8, 12, int(75 * fade)))
        frame.alpha_composite(sh.filter(ImageFilter.GaussianBlur(max(1, 2.5 * s))))
        mask = rider_mask(crank, t)
        spr = finish(mask, [(0, -1.1), (-0.8, -0.4), (0.8, -0.4)], s, rotate=roll, origin=(20 * SS, 76 * SS))
        if fade < 1:
            spr.putalpha(spr.getchannel("A").point(lambda v: int(v * fade)))
        frame.alpha_composite(spr, (int(round(x - 20 * s)), int(round(y - 76 * s))))
        return
