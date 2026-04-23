#!/usr/bin/env python3
"""
複数キャラクターの会話を Discord に順番投稿する。
JSON 配列を stdin から受け取る: [{"speaker": "Ai", "message": "..."}, ...]

環境変数:
  WEBHOOK            - Discord Webhook URL
  POST_DELAY_SECONDS - メッセージ間の待機秒数（デフォルト 2）
"""
import sys, json, os, time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

WEBHOOK = os.environ["WEBHOOK"]
DELAY   = float(os.environ.get("POST_DELAY_SECONDS", "2"))

# 表示名
DISPLAY = {
    "Ai":   "🎙️ アイ",
    "Haru": "💡 ハル",
    "Ren":  "⚡ レン",
    # 旧名前との後方互換
    "Nova": "🎙️ アイ",
    "Sage": "💡 ハル",
}

# アニメ風アバター画像（DiceBear adventurer スタイル）
AVATARS = {
    "Ai":   "https://api.dicebear.com/9.x/adventurer/png?seed=AiChan&size=256&backgroundColor=ffd1dc",
    "Haru": "https://api.dicebear.com/9.x/adventurer/png?seed=HaruSan&size=256&backgroundColor=c8f7c5",
    "Ren":  "https://api.dicebear.com/9.x/adventurer/png?seed=RenChan&size=256&backgroundColor=c8dff7",
    "Nova": "https://api.dicebear.com/9.x/adventurer/png?seed=AiChan&size=256&backgroundColor=ffd1dc",
    "Sage": "https://api.dicebear.com/9.x/adventurer/png?seed=HaruSan&size=256&backgroundColor=c8f7c5",
}

BOT_UA = "DiscordBot (https://github.com/takeyamar0000/jsr-bot, 1.0)"

def post(speaker: str, message: str) -> None:
    payload = json.dumps({
        "username":   DISPLAY.get(speaker, speaker),
        "avatar_url": AVATARS.get(speaker, ""),
        "content":    message,
    }).encode("utf-8")
    req = Request(WEBHOOK, data=payload, headers={
        "Content-Type": "application/json",
        "User-Agent":   BOT_UA,
    })
    try:
        with urlopen(req) as _:
            pass
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"URL error: {e}", file=sys.stderr)
        sys.exit(1)

script = json.loads(sys.stdin.read())

if not script:
    print("No messages to post.", file=sys.stderr)
    sys.exit(0)

for i, msg in enumerate(script):
    speaker = msg.get("speaker", "Ai")
    message = msg.get("message", "").strip()
    if not message:
        continue
    post(speaker, message)
    if i < len(script) - 1:
        time.sleep(DELAY)

print(f"Posted {len(script)} messages.")
