#!/usr/bin/env python3
"""
💬-雑談 に未返信のメッセージがあるか高速チェック。
Claude / Node.js 不要。stdout に "true" か "false" を出力。

環境変数:
  DISCORD_BOT_TOKEN  - Bot Token
  DISCORD_CHANNEL_ID - チャンネルID
"""
import sys, json, os, datetime
from urllib.request import urlopen, Request
from urllib.error import HTTPError

BOT_TOKEN  = os.environ.get("DISCORD_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "")
WINDOW_MIN = int(os.environ.get("REPLY_WINDOW_MINUTES", "12"))  # 5分間隔 × 少し余裕

def bail(reason: str) -> None:
    print(f"false  # {reason}", file=sys.stderr)
    print("false")
    sys.exit(0)

if not BOT_TOKEN or not CHANNEL_ID:
    bail("token or channel not set")

try:
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=5"
    req = Request(url, headers={
        "Authorization": f"Bot {BOT_TOKEN}",
        "User-Agent": "DiscordBot (https://github.com/takeyamar0000/jsr-bot, 1.0)",
    })
    with urlopen(req) as resp:
        messages = json.loads(resp.read())
except HTTPError as e:
    bail(f"Discord API {e.code}")
except Exception as e:
    bail(str(e))

if not messages:
    bail("no messages")

latest = messages[0]

# ボット発言なら返信済み
if latest["author"].get("bot", False):
    bail("latest is bot message")

# 時間ウィンドウ外
ts  = datetime.datetime.fromisoformat(latest["timestamp"].replace("Z", "+00:00"))
now = datetime.datetime.now(datetime.timezone.utc)
age = (now - ts).total_seconds() / 60
if age > WINDOW_MIN:
    bail(f"message is {age:.1f}m old")

print(f"true   # new message from {latest['author']['username']}", file=sys.stderr)
print("true")
