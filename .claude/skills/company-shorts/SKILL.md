---
name: company-shorts
description: 話題の企業・人物を紹介するYouTube Shorts（1080×1920、30〜60秒、VOICEVOX青山龍星のナレーション、白背景＋カード＋マーカー字幕の演出）を trend-shorts/ のRemotionプロジェクトで作る。「〇〇を紹介するショートを作って」「次の回を作って」「企業紹介の動画」などで使う。
---

# 企業・人物紹介ショートの作り方

プロジェクト: `trend-shorts/`（Remotion）。1本の動画 = `trend-shorts/episodes/<slug>.json` 1ファイル。
見本は `trend-shorts/episodes/polsia.json`。

## 毎回そろえるもの（シリーズの統一感）
- **土台の見た目**: 白背景・グラデーションなし・カード＋字幕。`src/` の部品を使い、配色は下のパレットから選ぶ。
- **声**: VOICEVOX:青山龍星（vvm 15, styleId 13, speed 1.15）。
- **ネタ選び**: 下の「題材の選び方」に従う。

## 毎回必ず変えるもの（常連さんを飽きさせない）
同じ型が続くと飽きられる。**前回と「型」「スタイル」「シーン構成」のすべてを変える。**
`scripts/build.sh` は `script/variety_check.py` で直近の回と比べ、似すぎていると止まる。

### 1. 型（`format`）— 直近2回と違うものを選ぶ
| format | 中身 | 向いているシーン例 |
|---|---|---|
| `story` | 挫折→転機→成功→影の物語 | profile, reveal, growth, warning |
| `quiz` | 「何人で運営？」など問題→正解で驚かせる | quiz, timeline, versus |
| `ranking` | 「〇〇な会社TOP3」で比べる | ranking, stats, bigtext |
| `versus` | ふつうの会社 vs この会社 | versus, grid, chart |
| `numbers` | 3つの数字で丸わかり | stats, chart, growth |
| `quote` | 本人の言葉から入る（実際の発言のみ） | quote, timeline, bigtext |
| `secrets` | 成功の理由を3つ | bigtext, grid, versus |
| `contrarian` | 「実はやばい？」課題から入って評価する | warning, bigtext, chart |

### 2. スタイル（`style`）— palette は前回と違うもの、5項目のうち3つ以上を前回から変える
| キー | 選択肢 |
|---|---|
| `palette` | `blue` `green` `orange` `purple` `teal`（メインの色） |
| `pattern` | `grid` `dots` `stripes` `plain`（背景の模様） |
| `motion` | `pop` `slide` `zoom` `wipe`（シーンの切り替わり方） |
| `caption` | `marker`（黄色マーカー） `box`（黒い帯） `underline`（下線） |
| `header` | `center`（中央） `left`（左寄せ＋色帯） |

### 3. シーン構成（`scenes`）
- 最初のシーンの type を前回と変える。前回使っていない type を1つ以上入れる。
- 直近3回とシーンの並びが50%以上一致しないようにする。
- 長さは30〜60秒で自由。冒頭2〜3秒で「え？」と思わせ、最後は問いかけか登録の呼びかけで終える。

## 題材の選び方
- 直近1〜2週間に海外または日本で話題になった企業・人物。`episodes/` の既存回と重複しない。
- 「驚きの数字」（売上・顧客数・評価額・人数・期間など）があり、意外性（少人数、短期間、異業種、逆転）がある。
- 成功だけでなく「光と影」（課題・失敗・リスク）も語れる。
- 一次報道（WSJ、Bloomberg、日経、TechCrunch など）と本人・会社の発信で確認できる。

## 事実の扱い
- 売上実績／売上見込み／年換算（ARR）／企業評価額／利益を区別して書く。本人発表の数字は「本人発表」「報道によると」。
- 円換算は1ドル=150円で統一し、概要欄に書く。裏付けが取れない話は断定しないか使わない。出典は画面に出さず概要欄へ。

## エピソードJSON
- `date`（YYYY-MM-DD）, `format`, `style`（上の表）
- `series`（シリーズ名。型に合わせて変えてよい。例: 🧠 企業クイズ）, `title`（「？」で2行に分かれる。各行15文字以内）, `description`（概要欄。VOICEVOXクレジットは自動付与）,
  `voice`, `images`（`founder`・`logo`・`site`、空欄可）
- `scenes`: `{ "id", "type", "data" }` の配列。好きな順・好きな数で並べる。同じ type を何度使ってもよい。
- `lines`: ナレーション。`scene`（scenes の id）、`text`（字幕。`\n` で改行、1行15文字以内）、
  `reading`（読み上げ文。漢字かな交じり、英語の固有名詞はカタカナ）、`highlight`（黄色マーカーの語）。
  同じ scene の行は連続させる。1シーン1〜3行。

### シーンタイプ（`data` の形は `src/theme.ts` の `SceneData`、使用例は `episodes/polsia.json`）
| type | 用途 | data |
|---|---|---|
| `stats` | 驚きの数字を縦に並べる | `stats[{label,value,tone}]`, `tagline` |
| `bigtext` | 問い・結論・一言を大きく | `kicker`, `lines[]`, `highlight`, `tone` |
| `profile` | 人物・会社のプロフィール | `name`, `emoji`, `rows[{label,value}]`, `chips[]`, `chipMark` |
| `reveal` | 会社・サービスの登場 | `date`, `name`, `flow[]`, `pill` |
| `growth` | 成長の数字（グラフ＋メイン＋カード） | `main{label,value}`, `cards[{label,value,tone}]` |
| `versus` | 比較・ビフォーアフター | `before{label,value,tone}`, `after{...}`, `arrow` |
| `grid` | 仕組み・要素を4つ並べて最後にスタンプ | `tasks[]`, `taskTag`, `stamp` |
| `warning` | 課題・リスク → その後 | `header`, `warnLabel`, `warn`, `after`, `afterHighlight` |
| `question` | 視聴者への問いかけ＋登録ボタン | `question[]`, `questionHighlight`, `comment` |
| `ranking` | 3〜4位までのランキング（下位から順に出る） | `title`, `items[{label,value}]`（1位が先頭） |
| `quiz` | 選択肢クイズ。2行目で正解を表示 | `question`, `choices[]`, `answer`（0始まり）, `note` |
| `timeline` | 年表。点と線が伸びていく | `events[{date,text,tone}]` |
| `quote` | 発言を1文字ずつ表示（実際の発言のみ） | `quote`, `by`, `highlight` |
| `chart` | 折れ線グラフが伸びる | `label`, `unit`, `points[{x,y}]` |
数値は "約375億円" のように書くとカウントアップする。`tone: "red"` で赤系。
見本: `episodes/polsia.json`（story型）、`examples/polsia-quiz.json`（quiz型・同じ題材を別の型で作った例）。

## 手順
1. 題材を選ぶ（候補3つ→1つに決める）。WebSearch で事実確認。
2. `episodes/` の直近の回の `format`・`style`・`scenes` を確認し、すべて変えた構成を決めて `episodes/<slug>.json` を書く。
   `python3 script/variety_check.py episodes/<slug>.json` が OK になるまで直す。
3. ビルド:
   ```bash
   cd trend-shorts
   bash scripts/setup.sh          # 初回のみ
   bash scripts/build.sh episodes/<slug>.json
   ```
   出力: `out/<slug>.mp4`、`out/<slug>-check.png`（各行の終わりの静止画一覧）、`out/<slug>-description.txt`。
4. `out/<slug>-check.png` で文字のはみ出し・重なり・折り返しを確認し、直して再ビルド。
5. 動画・概要欄テキスト・出典URL・未確認の点をユーザーに渡す。

## 注意
- 権利が確認できない報道写真は使わない（本人・会社の公開素材、自分で撮ったスクショ、利用許可のあるものだけ）。
- 青山龍星は企業が関わる利用では事前確認が必要。クレジット表記は必須（概要欄）。
- ネットワーク制限下では `build.sh` が `/opt/pw-browsers` のChromium（または `REMOTION_BROWSER`）を使う。
  VOICEVOX は GitHub Releases から取得する。
