# trend-shorts

話題の企業・人物を紹介する、1080×1920・30〜60秒のYouTube Shortsを作るRemotionプロジェクトです。
ナレーションは VOICEVOX（青山龍星）。1本の動画は `episodes/<slug>.json` 1ファイルで決まります。

- 作り方の手順（Claude Code のスキル）: `../.claude/skills/company-shorts/SKILL.md`
- 別のプロンプトで新しい回を作るときの文面: `PROMPT.md`
- 毎日のルーティン用の文面: `ROUTINE.md`
- 投稿済みの回: `episodes/`（最新回の template 番号から次の番号が決まる）
- テンプレート見本: `examples/template-01.json` 〜 `template-10.json`

## クイックスタート

```bash
bash scripts/setup.sh                        # 初回のみ：npm・VOICEVOX（core / onnxruntime / 声）
bash scripts/build.sh episodes/polsia.json   # ナレーション → 動画 → チェック画像 → 概要欄テキスト
npx remotion studio                          # 最後にビルドした回をプレビュー（先に build.sh が必要）
```

出力は `out/` に入ります（`<slug>.mp4`、`<slug>-check.png`、`<slug>-description.txt`）。

## エピソードJSON

| キー | 内容 |
|---|---|
| `series` | 左上の赤いラベル |
| `title` | 上部のタイトル。「？」の前が1行目、後ろが青字の2行目 |
| `description` | 概要欄の本文（出典・注意書き）。VOICEVOXクレジットは自動で付く |
| `voice` | VOICEVOXの話者（`name` / `vvm` / `styleId` / `speed`） |
| `images` | `founder`・`logo`・`site` の画像パス（`public/` からの相対。空欄なら代わりの表示） |
| `scenes` | シーンの並び。`{ id, type, data }` を好きな順・数で並べる（type の一覧はスキル参照） |
| `lines` | ナレーション。`scene`（scenes の id）・`text`（字幕、`\n` で改行）・`reading`（読み上げ文）・`highlight`（黄色マーカー） |

シーンタイプ: `stats` `bigtext` `profile` `reveal` `growth` `versus` `grid` `warning` `question` `ranking` `quiz` `timeline` `quote` `chart`。

10個のテンプレート（`templates/templates.json`）を **1→2→…→10→1 の順番** で使います。エピソードには `template` 番号を書き、
シーンの type と順番はテンプレートに合わせます（スタイルは自動）。次の番号は `python3 script/next_template.py` で確認できます。
`build.sh` は `script/template_check.py` で構成と順番を確認し、違えば止まります。見本は `examples/template-01.json`〜`template-10.json`。

## ファイル構成

- `scripts/setup.sh` / `scripts/build.sh` … 準備とビルド
- `script/tts.py` … VOICEVOXでナレーションを作り `src/timeline.json` を出力
- `script/contact_sheet.py` … チェック用の静止画一覧を作る
- `src/Scenes.tsx` … シーンタイプごとの映像
- `src/parts.tsx` / `src/theme.ts` … 共通パーツ・配色・タイミング計算

VOICEVOXの音声を使った動画は、概要欄に「VOICEVOX:話者名」のクレジットが必要です。
