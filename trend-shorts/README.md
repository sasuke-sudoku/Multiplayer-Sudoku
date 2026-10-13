# trend-shorts

海外のAIトレンドを紹介する、1080×1920・約58秒のYouTube Shortsです（Remotion製）。

## 構成

- `script/script.json` … 台本（`text` = 字幕、`reading` = ナレーションの読み方、`highlight` = 黄色で強調する語）
- `script/tts.py` … 台本から Open JTalk（pyopenjtalk）でナレーションを作り、`public/voice/*.wav` と `src/timeline.json` を出力
- `src/Scenes.tsx` … シーンごとの映像（hook / who / launch / growth / how / shadow / outro）
- `src/parts.tsx` … 背景・ヘッダー・字幕・出典表記などの共通パーツ

## 手順

```bash
pip install pyopenjtalk-plus scipy numpy
python3 script/tts.py          # 台本を直したら音声とタイミングを作り直す
npm i
npx remotion studio            # プレビュー
npx remotion render TrendShort out/trend-short.mp4
```

動画の長さはナレーションの長さに合わせて自動で決まります。
新しい回を作るときは `script/script.json` を書き換え、`src/Scenes.tsx` で各 `scene` の映像を編集してください。
