"""Check an episode follows its template and the 1→10 rotation.

Usage: python3 script/template_check.py episodes/<slug>.json
Set SKIP_ROTATION=1 to allow a template out of order (e.g. for examples/).
"""
import json, os, pathlib, sys
from templates import TEMPLATES, next_template_no

path = pathlib.Path(sys.argv[1])
ep = json.loads(path.read_text())
errors = []

no = ep.get("template")
if no not in TEMPLATES:
    errors.append(f"'template' は 1〜{len(TEMPLATES)} の番号で指定してください（今: {no!r}）")
else:
    t = TEMPLATES[no]
    want = [s["type"] for s in t["scenes"]]
    got = [s["type"] for s in ep.get("scenes", [])]
    if got != want:
        errors.append(f"シーンがテンプレート{no}と違います\n    必要: {' → '.join(want)}\n    実際: {' → '.join(got)}")
    if os.environ.get("SKIP_ROTATION") != "1" and path.resolve().parent.name == "episodes":
        expected = next_template_no(exclude=path)
        if no != expected:
            errors.append(f"順番では今回はテンプレート{expected}です（指定: {no}）")
if not ep.get("date"):
    errors.append("'date'（YYYY-MM-DD）がありません")
if "style" in ep:
    errors.append("'style' は書かないでください（テンプレートの style が使われます）")

if errors:
    print("template check: NG")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"template check: OK（テンプレート{no}. {TEMPLATES[no]['name']}）")
