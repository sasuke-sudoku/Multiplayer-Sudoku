"""Generate narration wavs with Open JTalk (pyopenjtalk) and write src/timeline.json."""
import json, pathlib, numpy as np, pyopenjtalk, scipy.io.wavfile as wf

ROOT = pathlib.Path(__file__).resolve().parent.parent
SPEED = 1.25
GAP = 0.15  # seconds of silence after each line

script = json.loads((ROOT / "script/script.json").read_text())
out = ROOT / "public/voice"
out.mkdir(parents=True, exist_ok=True)
lines = []
for i, line in enumerate(script["lines"]):
    wav, sr = pyopenjtalk.tts(line["reading"], speed=SPEED)
    wav = wav / max(1.0, np.abs(wav).max()) * 0.9 * 32767 if np.abs(wav).max() > 32767 * 0.9 else wav
    idx = np.where(np.abs(wav) > 300)[0]
    pad = int(0.04 * sr)
    wav = wav[max(0, idx[0] - pad): idx[-1] + pad]
    name = f"{i:02d}.wav"
    wf.write(out / name, sr, wav.astype(np.int16))
    lines.append({**line, "file": f"voice/{name}", "seconds": round(len(wav) / sr + GAP, 3)})
script["lines"] = lines
(ROOT / "src/timeline.json").write_text(json.dumps(script, ensure_ascii=False, indent=2))
print(f"total {sum(l['seconds'] for l in lines):.1f}s")
for l in lines: print(l["seconds"], l["text"])
