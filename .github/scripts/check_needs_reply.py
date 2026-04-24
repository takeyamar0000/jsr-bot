#!/usr/bin/env python3
"""
💬-雑談 に未返信のメッセージがあるか高速チェック。
Claude / Node.js 不要。stdout に "true" か "false" を出力。

ロジック:
  新しい順に並んだメッセージを最新から見ていき、
  - 最初にBOT発言に遭遇したら → 返信済み = false
  - BOT発言の前に人間発言が1件でもあれば → 返信必要 = true
  - 10件すべて人間発言なら → 返信必要 = true

環境変数:
  DISCORD_BOT_TOKEN  - Bot Token
  DISCORD_CHANNEL_ID - チャンネルID
"""
import sys, json, os
from urllib.request import urlopen, Request
from urllib.error import HTTPError

BOT_TOKEN  = os.environ.get("DISCORD_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("DISCORD_CHANNEL_ID", "")
FETCH_LIMIT = int(os.environ.get("FETCH_LIMIT", "10"))

def bail(reason: str) -> None:
    print(f"false  # {reason}", file=sys.stderr)
    print("false")
    sys.exit(0)

if not BOT_TOKEN or not CHANNEL_ID:
    bail("token or channel not set")

try:
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit={FETCH_LIMIT}"
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

# 新しい順にスキャン
for m in messages:
    if m["author"].get("bot", False):
        # 最新のBOT発言に到達 = それより前に人間発言はない = 返信済み
        bail(f"already replied (latest bot: {m['author']['username']})")
    else:
        # まだBOT発言を見ていない = この人間発言はBOT返信より新しい
        print(f"true   # unanswered message from {m['author']['username']}", file=sys.stderr)
        print("true")
        sys.exit(0)

# 10件すべて人間発言（BOTが最近10件に存在しない = 長期未返信）
print("true   # no bot reply in last 10 messages", file=sys.stderr)
print("true")
