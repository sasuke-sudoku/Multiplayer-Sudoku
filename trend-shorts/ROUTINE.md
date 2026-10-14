# 毎日のルーティン用プロンプト

ルーティン（毎日1回）の「指示」欄にそのまま貼り付けてください。毎回新しいセッションで動くので、前提はすべて文中に書いてあります。

```
あなたは YouTube Shorts「注目の企業・人物」シリーズの制作担当です。今日の1本を作ってください。
リポジトリは sasuke-sudoku/Multiplayer-Sudoku、作業フォルダは trend-shorts/ です。

■ 0. 準備（投稿履歴をそろえる）
- 投稿済みの回はブランチ shorts-episodes に貯めています。最初に次を実行してください。
    git fetch origin shorts-episodes && git checkout -B shorts-episodes origin/shorts-episodes
  （ブランチがまだ無いときは、今のブランチから git checkout -b shorts-episodes で作る）
- .claude/skills/company-shorts/SKILL.md を読み、その内容に従ってください。

■ 1. 今日のテンプレートを確認する
- cd trend-shorts && python3 script/next_template.py
- 表示された番号のテンプレートを必ず使います。テンプレートは 1→2→…→10→1 の順番で、飛ばしたり入れ替えたりしません。
- examples/template-<番号>.json を見本にします（中の数字や発言はサンプルなので使わない）。

■ 2. 題材を選ぶ
- 直近1〜2週間に海外または日本で話題になった企業・人物から候補を3つ挙げ、今日のテンプレートに一番合うものを1つ選ぶ。
  （例：クイズ型なら意外な数字がある会社、年表型なら歴史に起伏がある会社、名言型なら本人の印象的な発言がある人）
- trend-shorts/episodes/ の既存の回と同じ題材は選ばない。

■ 3. 事実を確認する
- WebSearch で一次報道（WSJ、Bloomberg、日経、TechCrunch など）と本人・会社の発信を確認する。
- 売上実績／売上見込み／年換算／企業評価額を区別する。円換算は1ドル=150円で統一する。
- 名言型は、実際の発言と出典がある場合だけ使う。確認できない話は断定しないか、使わない。

■ 4. エピソードを書く
- episodes/<slug>.json を作る。"date" は今日の日付、"template" は今日の番号。
- scenes の type と順番はテンプレートどおり。中身は題材に合わせて書く。style は書かない。
- 字幕は1行15文字以内（\n で改行）。出典と数字の注意書きは description（概要欄）に書く。画像は使わない。

■ 5. 動画を作ってチェックする
    bash scripts/setup.sh
    bash scripts/build.sh episodes/<slug>.json
- out/<slug>-check.png で、文字のはみ出し・重なり・不自然な折り返しを確認し、直して再ビルドする。
- 長さが30〜60秒に収まっていることを確認する。

■ 6. 保存して報告する
- episodes/<slug>.json をコミットし、git push origin shorts-episodes する（動画はコミットしない）。
- out/<slug>.mp4 と out/<slug>-description.txt をユーザーに送る。
- 日本語で次を報告する：テンプレート番号と名前、選んだ題材と理由、使った数字と出典URL、
  未確認・注意が必要な点、動画の長さ。

■ 守ること
- 数字・経歴・発言を推測で埋めない。実在の人物の写真や報道写真は使わない。
- 途中で止まった場合（ダウンロード失敗、ネットワーク制限など）は、どこで何が起きたかを報告して終わる。
```
