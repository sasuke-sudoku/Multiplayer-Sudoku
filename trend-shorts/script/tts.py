"""Generate narration wavs with VOICEVOX CORE and write src/timeline.json.

Usage: python3 script/tts.py [episode.json]   (default: episodes/polsia.json)

VOICEVOX_DIR must contain the *.vvm voice models and the voicevox_onnxruntime
folder (see README). The Open JTalk dictionary bundled with pyopenjtalk-plus is reused.
"""
import io, json, os, pathlib, sys, wave
import pyopenjtalk
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile

ROOT = pathlib.Path(__file__).resolve().parent.parent
VV = pathlib.Path(os.environ.get("VOICEVOX_DIR", ROOT / "voicevox"))
GAP = 0.12  # seconds of silence after each line

src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "episodes/polsia.json"
script = json.loads(src.read_text())
voice = script["voice"]
ort = Onnxruntime.load_once(filename=str(next(VV.glob("voicevox_onnxruntime-*/lib/libvoicevox_onnxruntime.so.*.*"))))
synth = Synthesizer(ort, OpenJtalk(os.path.join(os.path.dirname(pyopenjtalk.__file__), "dictionary")))
with VoiceModelFile.open(VV / f"{voice['vvm']}.vvm") as model:
    synth.load_voice_model(model)

out = ROOT / "public/voice"
out.mkdir(parents=True, exist_ok=True)
for old in out.glob("*.wav"):
    old.unlink()
lines = []
for i, line in enumerate(script["lines"]):
    query = synth.create_audio_query(line["reading"], voice["styleId"])
    query.speed_scale = voice["speed"]
    query.volume_scale = 1.8
    query.pre_phoneme_length = 0.05
    query.post_phoneme_length = 0.05
    data = synth.synthesis(query, voice["styleId"])
    with wave.open(io.BytesIO(data)) as w:
        seconds = w.getnframes() / w.getframerate()
    name = f"{i:02d}.wav"
    (out / name).write_bytes(data)
    lines.append({**line, "file": f"voice/{name}", "seconds": round(seconds + GAP, 3)})
script["lines"] = lines
(ROOT / "src/timeline.json").write_text(json.dumps(script, ensure_ascii=False, indent=2) + "\n")
print(f"total {sum(l['seconds'] for l in lines):.1f}s")
