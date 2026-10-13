# 新しい回を作るときのプロンプト（コピーして使う）

Claude Code でこのリポジトリを開き、下の文を貼り付けてください。`company-shorts` スキルが手順を読み込みます。

---

company-shorts スキルを使って、新しい回の YouTube Shorts を作ってください。

- 題材: 【例：〇〇社 / 〇〇さん。おまかせなら「いま海外か日本で話題の企業・人物を探して」】
- 切り口: 【例：AIで少人数経営、急成長、意外な失敗 など（任意）】
- 画像: 【public/images/<slug>/ に置いた / なし】
- 声: 青山龍星（変更する場合は声の名前）

手順:
1. 一次報道と本人・会社の発信で数字を確認し、売上実績・見込み・評価額などの違いを区別する
2. 題材に合う構成を決めて episodes/<slug>.json を書く（形式は episodes/polsia.json と同じ、構成・長さは自由で30〜60秒）
3. bash scripts/build.sh episodes/<slug>.json で動画を書き出す
4. out/<slug>-check.png で文字のはみ出しを確認して直す
5. 動画・概要欄テキスト・出典URL・未確認の点を報告する

---

Claude Code 以外のAIに頼む場合は、`.claude/skills/company-shorts/SKILL.md` の中身も一緒に貼り付けてください。
