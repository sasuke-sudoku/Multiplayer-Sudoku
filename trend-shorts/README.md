# trend-shorts

話題の企業・人物を紹介する、1080×1920・約55秒のYouTube Shortsです（Remotion製）。
ナレーションは VOICEVOX（冥鳴ひまり）です。

## 構成

- `script/script.json` … 台本と声の設定（`voice` = VOICEVOXの話者、`text` = 字幕、`reading` = ナレーションの読み方、`highlight` = 黄色で強調する語）
- `script/tts.py` … 台本から VOICEVOX CORE でナレーションを作り、`public/voice/*.wav` と `src/timeline.json` を出力
- `src/Scenes.tsx` … シーンごとの映像（hook / who / launch / growth / how / shadow / outro）
- `src/parts.tsx` … 背景・ヘッダー・字幕・出典表記などの共通パーツ

## 手順

### VOICEVOX の準備（初回のみ）

`voicevox/` フォルダ（git管理外）に次の3つを置きます。

- [VOICEVOX CORE](https://github.com/VOICEVOX/voicevox_core/releases) 0.16.4 の Python wheel（`voicevox_core-0.16.4-cp310-abi3-manylinux_2_34_x86_64.whl`）→ `pip install` する
- [onnxruntime](https://github.com/VOICEVOX/onnxruntime-builder/releases) の `voicevox_onnxruntime-linux-x64-1.17.3.tgz` → 展開する
- [音声モデル](https://github.com/VOICEVOX/voicevox_vvm/releases) の `.vvm`（冥鳴ひまりは `1.vvm`）

声を変えるときは `script/script.json` の `voice`（`vvm` と `styleId`）を書き換えます。
**動画の概要欄には「VOICEVOX:話者名」のクレジットを必ず書いてください**（利用規約で決められています）。

### 作成

```bash
pip install pyopenjtalk-plus
python3 script/tts.py          # 台本を直したら音声とタイミングを作り直す
npm i
npx remotion studio            # プレビュー
npx remotion render TrendShort out/trend-short.mp4
```

動画の長さはナレーションの長さに合わせて自動で決まります。
新しい回を作るときは `script/script.json` を書き換え、`src/Scenes.tsx` で各 `scene` の映像を編集してください。
