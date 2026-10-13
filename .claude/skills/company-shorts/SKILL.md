---
name: company-shorts
description: 話題の企業・人物を紹介するYouTube Shorts（1080×1920、30〜60秒、VOICEVOX青山龍星のナレーション、白背景＋カード＋マーカー字幕の演出）を trend-shorts/ のRemotionプロジェクトで作る。「〇〇を紹介するショートを作って」「次の回を作って」「企業紹介の動画」などで使う。
---

# 企業・人物紹介ショートの作り方

プロジェクト: `trend-shorts/`（Remotion）。1本の動画 = `trend-shorts/episodes/<slug>.json` 1ファイル。
見本は `trend-shorts/episodes/polsia.json`。

## 毎回そろえるもの（シリーズの統一感）
- **見た目**: 白背景・グラデーションなし・薄い格子、青（良い情報）／赤（注意・マイナス）のカード、
  黒文字＋黄色マーカーの字幕、上部に赤いシリーズラベルと2行タイトル。→ コード（`src/`）の配色・部品はそのまま使う。
- **エフェクト**: ポップイン、数字のカウントアップ、赤いスタンプ、警告カードの揺れ、チャンネル登録ボタンの押下。
  → シーンタイプに組み込み済み。新しい演出が必要なら同じ配色・動きの方向で追加する。
- **声**: VOICEVOX:青山龍星（vvm 15, styleId 13, speed 1.15）。
- **ネタ選び**: 下の「題材の選び方」に従う。

## 毎回自由に変えてよいもの
- **構成**: シーンの数・順番・種類、行数、長さ（30〜60秒）は題材に合わせて決める。
  見本と同じ7シーン構成にする必要はない。冒頭2〜3秒で「え？」と思わせ、最後は問いかけか登録の呼びかけで終える、だけ守る。

## 題材の選び方
- 直近1〜2週間に海外または日本で話題になった企業・人物。`episodes/` の既存回と重複しない。
- 「驚きの数字」（売上・顧客数・評価額・人数・期間など）があり、意外性（少人数、短期間、異業種、逆転）がある。
- 成功だけでなく「光と影」（課題・失敗・リスク）も語れる。
- 一次報道（WSJ、Bloomberg、日経、TechCrunch など）と本人・会社の発信で確認できる。

## 事実の扱い
- 売上実績／売上見込み／年換算（ARR）／企業評価額／利益を区別して書く。本人発表の数字は「本人発表」「報道によると」。
- 円換算は1ドル=150円で統一し、概要欄に書く。裏付けが取れない話は断定しないか使わない。出典は画面に出さず概要欄へ。

## エピソードJSON
- `series`, `title`（「？」で2行に分かれる。各行15文字以内）, `description`（概要欄。VOICEVOXクレジットは自動付与）,
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
数値は "約375億円" のように書くとカウントアップする。`tone: "red"` で赤系。

## 手順
1. 題材を選ぶ（候補3つ→1つに決める）。WebSearch で事実確認。
2. 構成を決めて `episodes/<slug>.json` を書く。
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
