# trend-shorts

話題の企業・人物を紹介する、1080×1920・約55秒のYouTube Shortsを作るRemotionプロジェクトです。
ナレーションは VOICEVOX（青山龍星）。1本の動画は `episodes/<slug>.json` 1ファイルで決まります。

- 作り方の手順（Claude Code のスキル）: `../.claude/skills/company-shorts/SKILL.md`
- 別のプロンプトで新しい回を作るときの文面: `PROMPT.md`
- 見本の回: `episodes/polsia.json`

## クイックスタート

```bash
bash scripts/setup.sh                        # 初回のみ：npm・VOICEVOX（core / onnxruntime / 声）
bash scripts/build.sh episodes/polsia.json   # ナレーション → 動画 → チェック画像 → 概要欄テキスト
npx remotion studio                          # 最後にビルドした回をプレビュー
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
| `visuals` | 各シーンの画面上の文字（カード・数値・ラベル）。数値はカウントアップする |
| `lines` | ナレーション14行。`scene`・`text`（字幕、`\n` で改行）・`reading`（読み上げ文）・`highlight`（黄色マーカー） |

シーンは `hook → who → launch → growth → how → shadow → outro` の7つで、各2行です。

## ファイル構成

- `scripts/setup.sh` / `scripts/build.sh` … 準備とビルド
- `script/tts.py` … VOICEVOXでナレーションを作り `src/timeline.json` を出力
- `script/contact_sheet.py` … チェック用の静止画一覧を作る
- `src/Scenes.tsx` … シーンごとの映像（`visuals` を表示）
- `src/parts.tsx` / `src/theme.ts` … 共通パーツ・配色・タイミング計算

VOICEVOXの音声を使った動画は、概要欄に「VOICEVOX:話者名」のクレジットが必要です。
