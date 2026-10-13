#!/usr/bin/env python3
"""「夕凪通り」— 妖怪ウォッチ2「桜町」を参考にした、オリジナルの昭和ノスタルジー系フィールドBGM。

原曲のメロディーは一切使っていません。参考にしたのは「設計思想」だけです:
  * アルトリコーダー風のリード（素朴な息の音＋タンギングの“チフ”）で学校・昭和の時代感を出す
  * C メジャー中心、F → C/E → Dm7 → C のベース順次下降
  * Fm / Fm6 / A♭ などの同主短調からの借用和音で「明るさの中の一瞬の陰り」
  * ヨナ抜き（ド・レ・ミ・ソ・ラ）中心の口ずさめる旋律
  * 78 BPM、密度の低い伴奏で、探索中に長時間聴いても疲れない
  * 曲全体が継ぎ目なくループする

依存: numpy のみ（MP3/OGG 変換に ffmpeg があれば使用）
使い方: python3 make_bgm.py [出力ディレクトリ]
"""
import os
import struct
import subprocess
import sys
import wave

import numpy as np

SR = 44100
BPM = 78
BEAT = 60.0 / BPM
BAR = 4
rng = np.random.default_rng(1960)

# ---------------------------------------------------------------- 音名ユーティリティ
_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    """'C5', 'Ab4', 'C#5' -> MIDI ノート番号 (C4 = 60)"""
    pc = _PC[name[0]]
    i = 1
    while name[i] in "#b":
        pc += 1 if name[i] == "#" else -1
        i += 1
    return pc + 12 * (int(name[i:]) + 1)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- 楽曲データ
# コード: (ベース, ギター/アコーディオンのボイシング)
CHORDS = {
    "F": ("F2", ["A3", "C4", "F4", "A4"]),
    "C/E": ("E2", ["G3", "C4", "E4", "G4"]),
    "Dm7": ("D2", ["A3", "C4", "D4", "F4"]),
    "C": ("C2", ["G3", "C4", "E4", "G4"]),
    "Fm": ("F2", ["Ab3", "C4", "F4", "Ab4"]),
    "Fm6": ("F2", ["Ab3", "C4", "D4", "F4"]),
    "Am": ("A2", ["A3", "C4", "E4", "A4"]),
    "Am7": ("A2", ["G3", "C4", "E4", "A4"]),
    "G7": ("G2", ["G3", "B3", "D4", "F4"]),
    "G7sus": ("G2", ["G3", "C4", "D4", "F4"]),
    "Em/G": ("G2", ["G3", "B3", "E4", "G4"]),
    "Em7": ("E2", ["G3", "B3", "D4", "E4"]),
    "A7": ("A2", ["G3", "C#4", "E4", "A4"]),
    "Abmaj7": ("Ab2", ["G3", "C4", "Eb4", "Ab4"]),
}

# 各小節: [(コード, 拍数), ...]
A = [[("F", 4)], [("C/E", 4)], [("Dm7", 4)], [("C", 4)],
     [("F", 4)], [("Fm", 4)], [("C/E", 2), ("Am7", 2)], [("Dm7", 2), ("G7", 2)]]
A2 = [[("F", 4)], [("C/E", 4)], [("Dm7", 4)], [("G7sus", 2), ("G7", 2)],
      [("Am7", 4)], [("Dm7", 2), ("G7", 2)], [("F", 2), ("Fm6", 2)], [("C", 4)]]
B = [[("Am", 4)], [("Em/G", 4)], [("F", 4)], [("C/E", 4)],
     [("Dm7", 4)], [("Em7", 2), ("A7", 2)], [("Dm7", 2), ("Fm6", 2)], [("G7sus", 2), ("G7", 2)]]

# 旋律 (音名 or 'r', 拍数) — ヨナ抜き中心のオリジナル旋律
MEL_A = [
    ("C5", 1), ("D5", .5), ("E5", .5), ("G5", 1.5), ("E5", .5),
    ("D5", 1), ("C5", .5), ("A4", .5), ("C5", 2),
    ("r", .5), ("A4", .5), ("C5", .5), ("D5", .5), ("F5", 1), ("E5", .5), ("D5", .5),
    ("E5", 3), ("r", 1),
    ("C5", 1), ("D5", .5), ("E5", .5), ("G5", 1.5), ("A5", .5),
    ("C6", 1.5), ("Ab5", .5), ("G5", 2),                       # Fm 上の A♭ = 借用和音の陰り
    ("E5", 1), ("G5", .5), ("E5", .5), ("D5", 1), ("C5", 1),
    ("D5", 2.5), ("r", 1.5),
]
MEL_A2 = [
    ("C5", 1), ("D5", .5), ("E5", .5), ("G5", 1.5), ("E5", .5),
    ("A5", 1), ("G5", .5), ("E5", .5), ("G5", 2),
    ("r", .5), ("F5", .5), ("E5", .5), ("D5", .5), ("C5", 1), ("A4", .5), ("C5", .5),
    ("D5", 3), ("r", 1),
    ("r", .5), ("C5", .5), ("E5", .5), ("G5", .5), ("A5", 1.5), ("G5", .5),
    ("F5", 1), ("E5", .5), ("D5", .5), ("G5", 1), ("F5", 1),
    ("E5", 1.5), ("D5", .5), ("C5", 1.5), ("D5", .5),          # Fm6 上の D
    ("C5", 3), ("r", 1),
]
MEL_B = [
    ("E5", 1), ("A5", 1.5), ("G5", .5), ("E5", 1),
    ("G5", 1.5), ("E5", .5), ("D5", 1), ("B4", 1),
    ("C5", 1), ("D5", .5), ("E5", .5), ("A5", 2),
    ("G5", 2.5), ("E5", .5), ("r", 1),
    ("F5", 1), ("E5", .5), ("D5", .5), ("A5", 1.5), ("F5", .5),
    ("G5", 1), ("E5", 1), ("C#5", 1), ("E5", 1),
    ("D5", 1.5), ("F5", .5), ("Ab5", 1.5), ("G5", .5),         # Fm6 上の A♭
    ("G5", 2), ("F5", .5), ("D5", .5), ("B4", 1),
]
# 最後の A'' 用: 後半 4 小節で音域を上げて曲の頂点（E6）を作る
MEL_A3 = MEL_A2[:16] + [
    ("D5", 2), ("G5", .5), ("A5", .5), ("B5", 1),              # G7 で駆け上がる
    ("C6", 1.5), ("A5", .5), ("E6", 1.5), ("D6", .5),          # 頂点
    ("C6", 1), ("A5", .5), ("F5", .5), ("B5", 1), ("D6", 1),
    ("C6", 1.5), ("A5", .5), ("Ab5", 1.5), ("F5", .5),         # Fm6 で A→A♭ と半音下降
    ("C6", 3), ("r", 1),                                       # 高いドで着地
]

SECTIONS = [  # (名前, 小節, 旋律, 編成の強さ)
    ("A", A, MEL_A, 1),          # イントロなしで、いきなり A メロから
    ("A'", A2, MEL_A2, 2),
    ("B", B, MEL_B, 3),
    ("A''", A2, MEL_A3, 4),      # 盛り上がり（サビ相当）
]
TOTAL_BEATS = sum(len(s[1]) * BAR for s in SECTIONS)
LOOP_SEC = TOTAL_BEATS * BEAT

# ---------------------------------------------------------------- 音源（すべて加算合成）


def adsr(n, a, r, sus_decay=0.0):
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / max(a, 1e-4))
    if sus_decay:
        env *= np.exp(-np.maximum(0, t - a) * sus_decay)
    rn = min(int(r * SR), n)
    if rn > 0:
        env[-rn:] *= np.linspace(1, 0, rn) ** 1.5
    return env


def harmonica(m, dur, vel=0.8):
    """複音ハーモニカ風: 2枚のリード（±7セント）のうなり + 息の雑音 + 遅れて掛かるビブラート"""
    n = int((dur + 0.08) * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    scoop = -30 * np.exp(-t / 0.045)                              # 吹き始めのわずかな音程の持ち上がり
    vib = 12 * np.clip((t - 0.28) / 0.35, 0, 1) * np.sin(2 * np.pi * 5.2 * t + rng.uniform(0, 6))
    env = adsr(n, 0.035, 0.09, sus_decay=0.12)
    env *= 1 + 0.06 * np.sin(2 * np.pi * 0.9 * t)                 # 息圧のゆらぎ
    out = np.zeros(n)
    for detune in (-7.0, 7.0):
        f = f0 * 2 ** ((scoop + vib + detune) / 1200)
        ph = 2 * np.pi * np.cumsum(f) / SR + rng.uniform(0, 6)
        k = 1
        while k * f0 < 9000:
            fk = k * f0
            # 鼻にかかった中域（~1.3k / 2.8k）を持ち上げ、高域は息の強さで開く
            form = 1 + 1.6 * np.exp(-((np.log2(fk / 1300)) ** 2) / 0.25) + 0.8 * np.exp(-((np.log2(fk / 2800)) ** 2) / 0.2)
            amp = form / k ** 1.15 * (0.7 if k % 2 == 0 else 1.0)
            out += amp * env ** (1 + 0.07 * k) * np.sin(k * ph)
            k += 1
    breath = shaped_noise(n, 1200, 4500)
    out += 0.12 * breath * env * (0.3 + 1.2 * np.exp(-t / 0.05))
    return vel * out / 14


def guitar(m, dur, vel=0.5):
    """ナイロン弦ギター風のはじき（倍音ごとに減衰時間を変える）"""
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    out = np.zeros(n)
    for k in range(1, 16):
        if k * f0 > 7000:
            break
        amp = abs(np.sin(np.pi * k * 0.18)) / k
        tau = 1.6 / (1 + 0.25 * k ** 1.3)
        out += amp * np.exp(-t / tau) * np.sin(2 * np.pi * k * f0 * 1.0007 ** (k - 1) * t)
    out *= np.minimum(1, t / 0.004)
    rel = int(0.12 * SR)
    end = int(dur * SR)
    if end + rel < n:
        out[end:end + rel] *= np.linspace(1, 0, rel)
        out[end + rel:] = 0
    return vel * out / 2.2


def bass(m, dur, vel=0.8):
    """ウッドベース風"""
    n = int((dur + 0.25) * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    out = np.zeros(n)
    for k, a in zip(range(1, 7), (1, 0.55, 0.25, 0.12, 0.06, 0.03)):
        out += a * np.exp(-t / (0.9 / k ** 0.8)) * np.sin(2 * np.pi * k * f0 * t)
    out += 0.25 * np.exp(-t / 0.015) * rng.standard_normal(n) * 0.3   # 指が弦に当たる音
    return vel * out * adsr(n, 0.006, 0.12) / 1.6


def recorder(m, dur, vel=0.8):
    """アルトリコーダー風: 基音中心の柔らかい音 + 発音時のチフ（息の雑音）+ ごく浅いビブラート"""
    n = int((dur + 0.06) * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    cents = 14 * np.exp(-t / 0.025)                               # 吹き始めにわずかに上ずる
    cents += 6 * np.clip((t - 0.4) / 0.4, 0, 1) * np.sin(2 * np.pi * 4.8 * t + rng.uniform(0, 6))
    ph = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200)) / SR
    env = adsr(n, 0.03, 0.05, sus_decay=0.05)
    out = np.zeros(n)
    for k, a in ((1, 1.0), (2, 0.10), (3, 0.16), (4, 0.03), (5, 0.04), (7, 0.01)):
        if k * f0 < 12000:
            out += a * env ** (1 + 0.15 * k) * np.sin(k * ph)
    chiff = shaped_noise(n, 2 * f0, 7000) * np.exp(-t / 0.018)
    air = shaped_noise(n, 1500, 6000) * env
    out += 0.22 * chiff + 0.025 * air
    return vel * out / 5.5


def accordion(m, dur, vel=0.3):
    """アコーディオン風の持続和音（2列リードのミュゼット・チューニング）"""
    n = int((dur + 0.2) * SR)
    t = np.arange(n) / SR
    env = adsr(n, 0.18, 0.2) * (1 + 0.05 * np.sin(2 * np.pi * 0.5 * t))
    out = np.zeros(n)
    for detune in (0.0, 9.0):
        f0 = hz(m) * 2 ** (detune / 1200)
        for k in range(1, 8):
            if k * f0 > 4000:
                break
            out += (1 / k ** 1.9) * np.sin(2 * np.pi * k * f0 * t + rng.uniform(0, 6))
    return vel * env * out / 3


def glock(m, dur, vel=0.4):
    """鉄琴（非整数倍音）"""
    n = int(max(dur, 0.5) * SR + 1.5 * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    out = np.zeros(n)
    for r, a, tau in ((1, 1, 1.2), (2.76, 0.35, 0.35), (5.40, 0.15, 0.12), (8.93, 0.08, 0.05)):
        if r * f0 < 16000:
            out += a * np.exp(-t / tau) * np.sin(2 * np.pi * r * f0 * t)
    return vel * out * np.minimum(1, t / 0.002) / 2


def shaped_noise(n, lo, hi):
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec *= (f > lo) & (f < hi)
    x = np.fft.irfft(spec, n)
    return x / (np.abs(x).max() + 1e-9)


def shaker(vel):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    return vel * shaped_noise(n, 5000, 14000) * np.minimum(1, t / 0.012) * np.exp(-t / 0.025)


def brush(vel):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    return vel * shaped_noise(n, 1500, 9000) * np.minimum(1, t / 0.03) * np.exp(-t / 0.09)


def woodblock(vel):
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    return vel * (np.sin(2 * np.pi * 1180 * t) + 0.4 * np.sin(2 * np.pi * 2650 * t)) * np.exp(-t / 0.03)


def strings(m, dur, vel=0.2):
    """弦楽アンサンブル: 3人分のわずかに音程・ビブラートがずれた弓の持続音"""
    n = int((dur + 0.5) * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    env = adsr(n, 0.28, 0.45)
    out = np.zeros(n)
    for detune in (-8.0, 0.0, 7.0):
        vib = 8 * np.sin(2 * np.pi * rng.uniform(5.0, 6.0) * t + rng.uniform(0, 6)) * np.clip(t / 0.5, 0, 1)
        ph = 2 * np.pi * np.cumsum(f0 * 2 ** ((detune + vib) / 1200)) / SR + rng.uniform(0, 6)
        k = 1
        while k * f0 < 5000 and k <= 10:
            out += np.exp(-k * f0 / 2200) / k * np.sin(k * ph)
            k += 1
    return vel * env * out / 2.2


def piano(m, dur, vel=0.3):
    """アップライトピアノ風（弦の非調和性と2段階の減衰）"""
    n = int((dur + 1.0) * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    out = np.zeros(n)
    for k in range(1, 13):
        fk = k * f0 * np.sqrt(1 + 0.0004 * k * k)
        if fk > 9000:
            break
        decay = 0.6 * np.exp(-t / (0.35 / k ** 0.5)) + 0.4 * np.exp(-t / (2.8 / (1 + 0.3 * k)))
        out += (1 / k ** 1.25) * decay * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6))
    out += 0.15 * shaped_noise(n, 800, 5000) * np.exp(-t / 0.008)       # ハンマーの打鍵音
    out *= np.minimum(1, t / 0.003)
    rel = int(0.15 * SR)
    end = int(dur * SR)
    out[end:end + rel] *= np.linspace(1, 0, len(out[end:end + rel]))
    out[end + rel:] = 0
    return vel * out / 2


def clarinet(m, dur, vel=0.5):
    """クラリネット風（奇数倍音が強い、柔らかなハモり担当）"""
    n = int((dur + 0.08) * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    cents = 4 * np.clip((t - 0.4) / 0.4, 0, 1) * np.sin(2 * np.pi * 5 * t)
    ph = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200)) / SR
    env = adsr(n, 0.05, 0.08, sus_decay=0.08)
    out = np.zeros(n)
    for k, a in ((1, 1), (2, 0.04), (3, 0.42), (4, 0.03), (5, 0.22), (7, 0.1), (9, 0.05)):
        if k * f0 < 9000:
            out += a * env ** (1 + 0.1 * k) * np.sin(k * ph)
    out += 0.02 * shaped_noise(n, 1000, 5000) * env
    return vel * out / 4


def horn(m, dur, vel=0.3):
    """ホルン風: 柔らかく丸い金管の持続音（A'' の厚み担当）"""
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    f0 = hz(m)
    env = adsr(n, 0.12, 0.25)
    ph = 2 * np.pi * f0 * t + 2 * np.pi * f0 * 0.002 * np.sin(2 * np.pi * 4.5 * t) / 4.5
    out = np.zeros(n)
    for k in range(1, 10):
        if k * f0 > 3000:
            break
        out += np.exp(-k * f0 / 900) * env ** (1 + 0.25 * k) * np.sin(k * ph)
    return vel * out / 1.5


def snare(vel):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    return vel * (shaped_noise(n, 1200, 9000) * np.exp(-t / 0.09)
                  + 0.6 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04))


def crash(vel, reverse=False):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    metal = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (3150, 4420, 5870, 7330, 8990))
    x = (shaped_noise(n, 3000, 16000) + 0.15 * metal) * np.exp(-t / 0.45) * np.minimum(1, t / 0.002)
    return vel * (x[::-1] if reverse else x)


def kick(vel):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    f = 48 + 45 * np.exp(-t / 0.03)
    return vel * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)


def tambourine(vel):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    jingle = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (5300, 7100, 9400, 11800))
    return vel * (shaped_noise(n, 6000, 15000) + 0.3 * jingle) * np.minimum(1, t / 0.004) * np.exp(-t / 0.07)


# ---------------------------------------------------------------- 配置
TRACKS = {k: np.zeros(int((LOOP_SEC + 4) * SR)) for k in
          ("lead", "harmony", "guitar", "piano", "bass", "strings", "violin", "horn", "accordion",
           "glock", "shaker", "brush", "wood", "kick", "tamb", "snare", "crash")}
MIDI_EVENTS = {k: [] for k in ("lead", "harmony", "guitar", "piano", "bass", "strings", "violin",
                                "horn", "accordion", "glock", "drums")}


def place(track, beat, sig):
    i = int(round(beat * BEAT * SR))
    if i < 0:  # 揺らぎで 0 秒より前にはみ出した分は切り捨てる
        sig, i = sig[-i:], 0
    end = min(len(TRACKS[track]), i + len(sig))
    TRACKS[track][i:end] += sig[:end - i]


def human(ms=8):
    return rng.uniform(-ms, ms) / 1000 / BEAT


def note(track, beat, m, dur, vel, gen):
    b = beat + human(6 if track != "bass" else 3)
    place(track, b, gen(m, dur * BEAT, vel))
    MIDI_EVENTS[track].append((max(0, b), dur, m, vel))


SCALE = {0, 2, 4, 5, 7, 9, 11}


def approach(cur, nxt):
    if nxt == cur:
        return cur + 7 if cur + 7 < midi("D3") else cur - 5
    step = -1 if nxt > cur else 1
    a = nxt + step
    return a if a % 12 in SCALE else nxt + 2 * step


def harmony_note(m, chord):
    """旋律の 3〜9 半音下にあるコード構成音のうち最も近いもの（3度・6度のハモり）"""
    bass_nm, voicing = CHORDS[chord]
    pcs = {midi(bass_nm) % 12} | {midi(x) % 12 for x in voicing}
    for d in range(3, 10):
        if (m - d) % 12 in pcs:
            return m - d
    return None


def arrange():
    beat = 0.0
    all_chords = []
    for name, bars, mel, lvl in SECTIONS:
        for bar in bars:
            pos = 0
            for ch, ln in bar:
                all_chords.append((beat + pos, ln, ch, lvl, name))
                pos += ln
            beat += BAR
    # ループ先頭（A の F）に向かうアプローチも計算できるよう、先頭を末尾に複製
    roots = [midi(CHORDS[c[2]][0]) for c in all_chords] + [midi(CHORDS[all_chords[0][2]][0])]

    for i, (b, ln, ch, lvl, sec) in enumerate(all_chords):
        root = roots[i]
        voicing = [midi(x) for x in CHORDS[ch][1]]
        # --- ギター: 8分音符のアルペジオ
        pattern = [0, 2, 1, 3, 2, 1, 3, 2]
        gvel = 0.42
        for s in range(int(ln * 2)):
            idx = pattern[s % 8] if s else 0
            acc = 1.0 if s % 2 == 0 else 0.75
            note("guitar", b + s * 0.5, voicing[idx], 0.9, gvel * acc, guitar)
        # --- ベース: ルート → 5度 → 次のルートへの経過音（F→E→D→C の順次下降を活かす）
        if ln == 4:
            note("bass", b, root, 1.8, 0.85, bass)
            note("bass", b + 2, root + 7 if root + 7 <= midi("D3") else root - 5, 0.9, 0.6, bass)
            note("bass", b + 3, approach(root, roots[i + 1]), 0.9, 0.55, bass)
        else:
            note("bass", b, root, 1.4, 0.85, bass)
            note("bass", b + 1.5, root + 7 if root + 7 <= midi("D3") else root - 5, 0.45, 0.5, bass)
        # --- アコーディオン: A' 以降に薄く
        if lvl >= 2:
            av = {2: 0.10, 3: 0.14, 4: 0.12}[lvl]
            for v in voicing[1:]:
                note("accordion", b, v, ln * 0.97, av, accordion)
        # --- 弦楽: 全編で和音を支え、セクションごとに厚くする（チェロ → ヴァイオリンの順に追加）
        sv = (0.16, 0.14, 0.18, 0.24, 0.26)[lvl]
        for v in voicing:
            note("strings", b, v, ln * 0.98, sv, strings)
        if lvl >= 2:
            note("strings", b, root + 12, ln * 0.98, sv * 0.9, strings)        # チェロ
        if lvl >= 3:
            note("violin", b, voicing[-1] + 12, ln * 0.98, sv * 0.8, strings)  # 高音のヴァイオリン
        # --- ピアノ: 2・4 拍目の裏打ち（ベースとで“ズン・チャッ”）。A'' は 1 拍目にオクターブ上も足す
        for off in ((1, 3) if ln == 4 else (1,)):
            for v in voicing[1:]:
                note("piano", b + off, v, 0.6, 0.22 if lvl < 4 else 0.26, piano)
        if lvl == 4:
            for v in voicing[1:]:
                note("piano", b, v + 12, 0.9, 0.16, piano)
            # --- ホルン: 中音域の和音で厚みを足す
            for v in voicing[1:3]:
                note("horn", b, v, ln * 0.97, 0.3, horn)
        # --- 打楽器
        if lvl >= 1:
            for off in ((0, 2) if lvl >= 3 and ln == 4 else (0, 1.5) if lvl == 4 else (0,)):
                place("kick", b + off, kick(0.55))
                MIDI_EVENTS["drums"].append((b + off, 0.25, 36, 0.5))
        for s in range(int(ln * 2)):
            bb = b + s * 0.5
            if lvl >= 1:
                place("shaker", bb + human(4), shaker(0.05 if s % 2 == 0 else 0.09))
                MIDI_EVENTS["drums"].append((bb, 0.25, 70, 0.4))
            if lvl >= 2 and s % 4 == 2:  # 2拍目・4拍目
                place("brush", bb + human(4), brush(0.10))
                MIDI_EVENTS["drums"].append((bb, 0.5, 40, 0.4))
                if lvl >= 3:
                    place("tamb", bb + human(4), tambourine(0.08))
                    MIDI_EVENTS["drums"].append((bb, 0.25, 54, 0.4))
                if lvl == 4:  # A'' はスネアのバックビート
                    place("snare", bb + human(3), snare(0.22))
                    MIDI_EVENTS["drums"].append((bb, 0.25, 38, 0.5))
            if lvl == 4 and s % 2 == 1:  # A'' はタンバリンを 8 分の裏にも
                place("tamb", bb + human(4), tambourine(0.05))
                MIDI_EVENTS["drums"].append((bb, 0.25, 54, 0.3))
        if lvl == 3 and ln == 4:
            place("wood", b + 3.5, woodblock(0.10))
            MIDI_EVENTS["drums"].append((b + 3.5, 0.25, 76, 0.4))
        # --- 鉄琴: B は各小節頭にコードの3度を高音で
        if lvl == 3 and ln == 4:
            note("glock", b, voicing[2] + 24 if voicing[2] + 24 < 100 else voicing[2] + 12, 2, 0.25, glock)

    # --- 盛り上がりへの橋渡し: B の最後 2 拍でスネアのクレッシェンド＋逆再生シンバル、A'' 頭でクラッシュ
    sec_start, b_end = {}, 0.0
    for name, bars, _, _ in SECTIONS:
        sec_start[name] = b_end
        b_end += len(bars) * BAR
    top = sec_start["A''"]
    for j in range(8):
        bb = top - 2 + j * 0.25
        place("snare", bb, snare(0.08 + 0.05 * j))
        MIDI_EVENTS["drums"].append((bb, 0.2, 38, 0.3 + 0.08 * j))
    swell = crash(0.25, reverse=True)
    place("crash", top - len(swell) / SR / BEAT, swell)
    for bb in (top, top + 4 * BAR):
        place("crash", bb, crash(0.35 if bb == top else 0.22))
        MIDI_EVENTS["drums"].append((bb, 2, 49, 0.6))

    def chord_at(pos):
        for cb, cln, ch, _, _ in all_chords:
            if cb <= pos + 1e-9 < cb + cln:
                return ch
        return all_chords[-1][2]

    # --- 旋律
    beat = 0.0
    for name, bars, mel, lvl in SECTIONS:
        if mel:
            pos = beat
            for nm, ln in mel:
                if nm != "r":
                    m = midi(nm)
                    vel = 0.8 + 0.1 * (ln >= 1.5) + 0.08 * (lvl == 4)
                    note("lead", pos, m, ln * 0.92, vel, recorder)  # ハーモニカに戻す場合は harmonica
                    # クラリネットのハモり: A' は長い音だけ、B と A'' は全部
                    if lvl >= 3 or (lvl == 2 and ln >= 1):
                        h = harmony_note(m, chord_at(pos))
                        if h is not None:
                            note("harmony", pos, h, ln * 0.92, 0.55, clarinet)
                    if lvl == 4:   # A'' は弦楽が旋律をオクターブ下で、鉄琴が長い音をオクターブ上で重ねる
                        note("violin", pos, m - 12, ln * 0.98, 0.22, strings)
                        if ln >= 1:
                            note("glock", pos, m + 12, ln, 0.16, glock)
                pos += ln
            assert abs(pos - beat - len(bars) * BAR) < 1e-9, (name, pos - beat)
        beat += len(bars) * BAR


# ---------------------------------------------------------------- ミックス
def reverb_ir(sec=2.2):
    n = int(sec * SR)
    t = np.arange(n) / SR
    ir = shaped_noise(n, 200, 7000) * np.exp(-t / 0.42)
    ir[: int(0.012 * SR)] = 0                          # プリディレイ
    for d, g in ((0.017, 0.5), (0.029, 0.35), (0.041, 0.28), (0.063, 0.2)):
        ir[int(d * SR)] += g * 8
    return ir / np.sqrt(np.sum(ir ** 2))


def fft_conv(x, h):
    n = len(x) + len(h) - 1
    size = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(h, size), size)[:n]


def pan(x, p):  # p: -1 (左) .. +1 (右)
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)])


def mix():
    mixdef = {  # 音量, 定位, リバーブ送り
        "lead": (1.15, 0.05, 0.30),
        "harmony": (0.70, -0.20, 0.30),
        "guitar": (0.50, -0.45, 0.25),
        "piano": (0.45, 0.25, 0.30),
        "bass": (0.42, 0.0, 0.05),
        "strings": (0.26, -0.30, 0.50),
        "violin": (0.50, 0.40, 0.50),
        "kick": (0.26, 0.0, 0.05),
        "tamb": (0.60, 0.45, 0.20),
        "accordion": (0.28, 0.40, 0.35),
        "glock": (0.80, 0.30, 0.45),
        "shaker": (1.80, -0.50, 0.10),
        "brush": (1.40, 0.20, 0.15),
        "wood": (0.80, -0.25, 0.30),
        "horn": (0.40, 0.15, 0.45),
        "snare": (0.55, 0.10, 0.25),
        "crash": (0.16, -0.30, 0.30),
    }
    n = len(TRACKS["lead"])
    dry = np.zeros((2, n))
    send = np.zeros(n)
    for k, (g, p, s) in mixdef.items():
        dry += pan(TRACKS[k] * g, p)
        send += TRACKS[k] * g * s
    ir = reverb_ir()
    wet_l = fft_conv(send, ir)
    wet_r = fft_conv(send, np.roll(ir, 113))
    wet = np.stack([wet_l, wet_r]) * 0.5
    out = np.zeros((2, n + len(ir) - 1))
    out[:, :n] += dry
    out += wet
    # シームレスループ: ループ長を超えた余韻を先頭に折り返す
    L = int(round(LOOP_SEC * SR))
    loop = out[:, :L].copy()
    tail = out[:, L:]
    loop[:, : tail.shape[1]] += tail[:, :L]
    # ほんのり温かく（軽い飽和）+ 正規化
    first = out[:, :L]                       # 1 周目（前周の余韻なし）は試聴版の頭に使う
    peak = np.abs(loop).max()
    warm = lambda x: np.tanh(x / peak * 1.2) / np.tanh(1.2) * 0.89  # noqa: E731
    return warm(loop), warm(first)


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").T.copy()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- MIDI 書き出し（DAW 取り込み用）
def vlq(v):
    out = [v & 0x7F]
    v >>= 7
    while v:
        out.insert(0, (v & 0x7F) | 0x80)
        v >>= 7
    return bytes(out)


def write_midi(path):
    TPB = 480
    spec = {  # (チャンネル, GM 音色, トラック名)
        "lead": (0, 74, "Recorder (lead)"),
        "harmony": (5, 71, "Clarinet (harmony)"),
        "guitar": (1, 24, "Nylon Guitar"),
        "piano": (6, 0, "Piano"),
        "strings": (7, 48, "Strings"),
        "violin": (8, 40, "Violin"),
        "horn": (10, 60, "French Horn"),
        "bass": (2, 32, "Acoustic Bass"),
        "accordion": (3, 21, "Accordion"),
        "glock": (4, 9, "Glockenspiel"),
        "drums": (9, 0, "Percussion"),
    }
    tracks = []
    tempo = int(60_000_000 / BPM)
    meta = (b"\x00\xff\x51\x03" + tempo.to_bytes(3, "big") + b"\x00\xff\x58\x04\x04\x02\x18\x08"
            + b"\x00\xff\x03" + vlq(len("Yunagi-dori".encode())) + b"Yunagi-dori" + b"\x00\xff\x2f\x00")
    tracks.append(meta)
    for key, (ch, prog, nm) in spec.items():
        ev = []
        for b, d, m, v in MIDI_EVENTS[key]:
            on = int(round(b * TPB))
            off = int(round((b + d) * TPB))
            vel = max(1, min(127, int(v * 127 if key != "drums" else 80)))
            ev.append((on, 1, bytes([0x90 | ch, m, vel])))
            ev.append((off, 0, bytes([0x80 | ch, m, 0])))
        ev.sort(key=lambda e: (e[0], e[1]))
        data = b"\x00\xff\x03" + vlq(len(nm)) + nm.encode()
        if ch != 9:
            data += b"\x00" + bytes([0xC0 | ch, prog])
        last = 0
        for tick, _, msg in ev:
            data += vlq(tick - last) + msg
            last = tick
        data += b"\x00\xff\x2f\x00"
        tracks.append(data)
    with open(path, "wb") as f:
        f.write(b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), TPB))
        for t in tracks:
            f.write(b"MTrk" + struct.pack(">I", len(t)) + t)


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(outdir, exist_ok=True)
    arrange()
    loop, first = mix()
    loop_wav = os.path.join(outdir, "yunagi-dori_loop.wav")
    write_wav(loop_wav, loop)
    # 試聴用フル版: ループ 2 周 + 8 秒フェードアウト（ゲームOST 風）
    fade = int(8 * SR)
    full = np.concatenate([first, loop, loop[:, :fade]], axis=1)
    full[:, -fade:] *= np.linspace(1, 0, fade) ** 2
    full[:, :441] *= np.linspace(0, 1, 441)  # 再生開始のクリック防止（10ms）
    full_wav = os.path.join(outdir, "yunagi-dori_full.wav")
    write_wav(full_wav, full)
    write_midi(os.path.join(outdir, "yunagi-dori.mid"))
    print(f"loop length: {LOOP_SEC:.2f}s ({TOTAL_BEATS // BAR} bars @ {BPM} BPM)")
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", full_wav, "-b:a", "192k",
                        os.path.join(outdir, "yunagi-dori_full.mp3")], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", loop_wav, "-c:a", "libvorbis", "-q:a", "6",
                        os.path.join(outdir, "yunagi-dori_loop.ogg")], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print("ffmpeg 変換をスキップ:", e)


if __name__ == "__main__":
    main()
