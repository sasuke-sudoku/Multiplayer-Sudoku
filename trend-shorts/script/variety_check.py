"""Refuse an episode that looks or plays too much like the recent ones.

Usage: python3 script/variety_check.py episodes/<slug>.json
Compares against the other files in episodes/ (newest `date` first). Exit 1 with reasons when too similar.
"""
import difflib, json, pathlib, sys

STYLE_KEYS = ["palette", "pattern", "motion", "caption", "header"]
DEFAULT_STYLE = {"palette": "blue", "pattern": "grid", "motion": "pop", "caption": "marker", "header": "center"}

path = pathlib.Path(sys.argv[1]).resolve()
ep = json.loads(path.read_text())
others = []
for f in sorted(path.parent.glob("*.json")):
    if f.resolve() == path:
        continue
    others.append(json.loads(f.read_text()))
others.sort(key=lambda e: e.get("date", ""), reverse=True)

def style(e):
    return {**DEFAULT_STYLE, **e.get("style", {})}

def types(e):
    return [s["type"] for s in e["scenes"]]

errors = []
for key in ("date", "format"):
    if not ep.get(key):
        errors.append(f"'{key}' がありません")

if others:
    prev = others[0]
    recent = others[:3]
    if ep.get("format") in [e.get("format") for e in others[:2]]:
        errors.append(f"format '{ep.get('format')}' は直近2回で使っています")
    same = [k for k in STYLE_KEYS if style(ep)[k] == style(prev)[k]]
    if style(ep)["palette"] == style(prev)["palette"]:
        errors.append(f"palette '{style(ep)['palette']}' が前回と同じです")
    if len(same) > 2:
        errors.append(f"style が前回と似すぎています（同じ: {', '.join(same)}）。3つ以上変えてください")
    if types(ep)[0] == types(prev)[0]:
        errors.append(f"最初のシーンの type '{types(ep)[0]}' が前回と同じです")
    if not set(types(ep)) - set(types(prev)):
        errors.append("前回使っていないシーンタイプを1つ以上入れてください")
    for e in recent:
        ratio = difflib.SequenceMatcher(None, types(ep), types(e)).ratio()
        if ratio >= 0.5:
            errors.append(f"シーンの並びが「{e.get('title', '?')}」と {ratio:.0%} 一致しています（50%未満にしてください）")

if errors:
    print("variety check: NG")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"variety check: OK（format={ep.get('format')}, scenes={' → '.join(types(ep))}）")
