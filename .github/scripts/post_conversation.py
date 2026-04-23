#!/usr/bin/env python3
"""
複数キャラクターの会話を Discord に順番投稿する。
JSON 配列を stdin から受け取る: [{"speaker": "Nova", "message": "..."}, ...]

環境変数:
  WEBHOOK  - Discord Webhook URL
"""
import sys, json, os, time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

WEBHOOK = os.environ["WEBHOOK"]

DISPLAY = {
    "Nova": "🎙️ Nova",
    "Sage": "🧠 Sage",
    "Ren":  "⚡ Ren",
}

def post(username: str, message: str) -> None:
    payload = json.dumps({
        "username": username,
        "content":  message,
    }).encode("utf-8")
    req = Request(WEBHOOK, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req) as resp:
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
    speaker = msg.get("speaker", "Nova")
    message = msg.get("message", "").strip()
    if not message:
        continue
    display = DISPLAY.get(speaker, speaker)
    post(display, message)
    # 最後のメッセージ以外は間を空けて自然な会話に見せる
    if i < len(script) - 1:
        time.sleep(1.8)

print(f"Posted {len(script)} messages.")
