"""Shared helpers for the 10 rotating templates (templates/templates.json)."""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = {t["no"]: t for t in json.loads((ROOT / "templates/templates.json").read_text())}


def episodes(folder=ROOT / "episodes"):
    """Published episodes, newest first."""
    eps = [(f, json.loads(f.read_text())) for f in folder.glob("*.json")]
    return sorted(eps, key=lambda fe: (fe[1].get("date", ""), fe[1].get("template", 0)), reverse=True)


def next_template_no(exclude=None):
    eps = [e for f, e in episodes() if exclude is None or f.resolve() != exclude.resolve()]
    if not eps:
        return 1
    return eps[0].get("template", 0) % len(TEMPLATES) + 1
