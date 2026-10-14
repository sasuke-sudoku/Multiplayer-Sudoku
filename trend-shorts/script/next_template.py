"""Print which template the next episode must use, and what it contains.

Usage: python3 script/next_template.py
"""
from templates import TEMPLATES, next_template_no

t = TEMPLATES[next_template_no()]
print(f"次のテンプレート: {t['no']}. {t['name']}（{t['concept']}）")
print(f"シリーズ名: {t['series']}")
print("スタイル: " + ", ".join(f"{k}={v}" for k, v in t["style"].items()))
print("シーン（この順番・この type で作る）:")
for i, s in enumerate(t["scenes"], 1):
    print(f"  {i}. {s['type']:<9} … {s['role']}")
