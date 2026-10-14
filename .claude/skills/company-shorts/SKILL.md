---
name: company-shorts
description: 話題の企業・人物を紹介するYouTube Shorts（1080×1920、30〜60秒、VOICEVOX青山龍星のナレーション、白背景＋カード演出、10個のテンプレートを1→10の順番で毎日ローテーション）を trend-shorts/ のRemotionプロジェクトで作る。「〇〇を紹介するショートを作って」「次の回を作って」「企業紹介の動画」などで使う。
---

# 企業・人物紹介ショートの作り方

プロジェクト: `trend-shorts/`（Remotion）。1本の動画 = `trend-shorts/episodes/<slug>.json` 1ファイル。
見本は `trend-shorts/episodes/polsia.json`。

## 毎回そろえるもの（シリーズの統一感）
- **土台の見た目**: 白背景・グラデーションなし・カード＋字幕（`src/` の部品）。
- **声**: VOICEVOX:青山龍星（vvm 15, styleId 13, speed 1.15）。
- **ネタ選び**: 下の「題材の選び方」に従う。

## 10個のテンプレートを 1→2→…→10→1 の順番で使う
常連さんを飽きさせないため、テンプレートは毎回変わる。**順番は飛ばさない・入れ替えない。**
- 次に使う番号: `python3 script/next_template.py`（`episodes/` の最新回の次の番号と、作るべきシーンを表示）
- テンプレートの中身: `trend-shorts/templates/templates.json`（型・シリーズ名・スタイル・シーンの順番と役割）
- 各テンプレートの見本: `trend-shorts/examples/template-01.json` 〜 `template-10.json`
  （01 は実際の投稿回、02〜10 はレイアウト確認用のサンプル。数字・発言はそのまま使わない）
- エピソードには `"template": 番号` を書く。`style` は書かない（テンプレートのものが自動で使われる）。
  `scenes` の type はテンプレートと**同じ順番・同じ数**にする。`series` は省略するとテンプレートのものになる。
- `scripts/build.sh` は `script/template_check.py` でシーン構成と順番を確認し、違えば止まる。

| No. | 型 | 中身 | シーン | 色 |
|---|---|---|---|---|
| 1 | ストーリー型 | 挫折→転機→成功→影の物語で人物を追う | stats → profile → reveal → growth → grid → warning → question | blue |
| 2 | クイズ型 | 「社員は何人？」のような問題で始め、正解で驚かせる | quiz → timeline → versus → warning → question | green |
| 3 | ランキング型 | 同じテーマの企業・人物を3位から順に紹介し、1位を深掘り | bigtext → ranking → stats → warning → question | orange |
| 4 | 比較型 | ふつうの会社 vs この会社の対比で違いを際立たせる | versus → profile → grid → chart → question | purple |
| 5 | 数字で見る型 | 3つの数字だけで会社を丸わかりにする | stats → chart → growth → bigtext → question | teal |
| 6 | 名言型 | 本人の実際の発言から入り、その言葉の背景を追う | quote → profile → timeline → warning → question | blue |
| 7 | 成功の秘密型 | 成功の理由を3つに絞って解説する | bigtext → grid → chart → warning → question | orange |
| 8 | 逆張り型 | 「実はやばい？」と課題から入り、最後に公平に評価する | warning → bigtext → growth → versus → question | purple |
| 9 | 年表型 | 創業から今までを年表で一気にたどる | timeline → profile → stats → quiz → question | green |
| 10 | 図鑑型 | 会社をカード図鑑のように紹介する（事業・人・数字・強み） | reveal → profile → grid → ranking → question | teal |

## 題材の選び方
- 直近1〜2週間に海外または日本で話題になった企業・人物。`episodes/` の既存回と重複しない。
- 「驚きの数字」（売上・顧客数・評価額・人数・期間など）があり、意外性（少人数、短期間、異業種、逆転）がある。
- 成功だけでなく「光と影」（課題・失敗・リスク）も語れる。
- 一次報道（WSJ、Bloomberg、日経、TechCrunch など）と本人・会社の発信で確認できる。

## 事実の扱い
- 売上実績／売上見込み／年換算（ARR）／企業評価額／利益を区別して書く。本人発表の数字は「本人発表」「報道によると」。
- 円換算は1ドル=150円で統一し、概要欄に書く。裏付けが取れない話は断定しないか使わない。出典は画面に出さず概要欄へ。

## エピソードJSON
- `date`（YYYY-MM-DD）, `template`（1〜10）
- `series`（省略可。テンプレートのシリーズ名が入る）, `title`（「？」で2行に分かれる。各行15文字以内）, `description`（概要欄。VOICEVOXクレジットは自動付与）,
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
見本: `examples/template-01.json` 〜 `template-10.json`。

## 手順
1. 題材を選ぶ（候補3つ→1つに決める）。WebSearch で事実確認。
2. `python3 script/next_template.py` で今回のテンプレート番号を確認し、`examples/template-<番号>.json` を見本に
   `episodes/<slug>.json` を書く（シーンの type と順番はテンプレートどおり、中身は題材に合わせる）。
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
