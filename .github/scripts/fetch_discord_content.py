#!/usr/bin/env python3
"""
Discord の各チャンネルから当日の最新投稿を取得してまとめる。
ディベートのコンテキスト生成用。

環境変数:
  DISCORD_BOT_TOKEN - Bot Token

出力: 標準出力にチャンネルごとの本文テキストを出力
"""
import sys, json, os, datetime
from urllib.request import urlopen, Request
from urllib.error import HTTPError

BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
BOT_UA = "DiscordBot (https://github.com/takeyamar0000/jsr-bot, 1.0)"

CHANNELS = {
    "朝刊":       "1496382012326678559",
    "夕刊":       "1496381928411238570",
    "今日の論文": "1496584184767053855",
    "動画要約":   "1496593916949172335",
    "AIツール紹介": "1496590113159909396",
}

def get_latest_bot_message(channel_id: str, limit: int = 5) -> str | None:
    if not BOT_TOKEN:
        return None
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit={limit}"
    req = Request(url, headers={
        "Authorization": f"Bot {BOT_TOKEN}",
        "User-Agent": BOT_UA,
    })
    try:
        with urlopen(req) as resp:
            messages = json.loads(resp.read())
    except HTTPError as e:
        print(f"  Error fetching channel {channel_id}: {e.code}", file=sys.stderr)
        return None

    # ボットの投稿を新しい順に探す
    for msg in messages:
        if msg["author"].get("bot") and msg.get("content"):
            content = msg["content"].strip()
            if len(content) > 50:   # 短すぎるシステムメッセージを除外
                return content
    return None

sections = []
for name, ch_id in CHANNELS.items():
    content = get_latest_bot_message(ch_id)
    if content:
        # 先頭800文字に切り詰め（プロンプトが長くなりすぎないように）
        trimmed = content[:800] + ("…" if len(content) > 800 else "")
        sections.append(f"=== {name} ===\n{trimmed}")
    else:
        sections.append(f"=== {name} ===\n（本日の投稿なし）")

output = "\n\n".join(sections)
sys.stdout.write(output)
