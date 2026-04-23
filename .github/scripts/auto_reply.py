#!/usr/bin/env python3
"""
💬-雑談 の未返信メッセージに Sage が自動返信する。

ロジック:
  - 直近10件を取得
  - 最新メッセージがボット以外かつ30分以内 → Claudeで返信生成
  - 最新がボット発言 → スキップ（返信済み）

環境変数:
  DISCORD_BOT_TOKEN  - Bot Token（メッセージ読み取り用）
  DISCORD_CHANNEL_ID - 💬-雑談 のチャンネルID
  WEBHOOK            - Sage が返信投稿する Webhook URL
"""
import sys, json, os, time, subprocess, datetime
from urllib.request import urlopen, Request
from urllib.error import HTTPError

BOT_TOKEN  = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]
WEBHOOK    = os.environ["WEBHOOK"]
WINDOW_MIN = int(os.environ.get("REPLY_WINDOW_MINUTES", "35"))

BOT_UA     = "DiscordBot (https://github.com/takeyamar0000/jsr-bot, 1.0)"
HARU_AVATAR = "https://api.dicebear.com/9.x/adventurer/png?seed=HaruSan&size=256&backgroundColor=c8f7c5"

def discord_get(path: str) -> dict | list:
    url = f"https://discord.com/api/v10{path}"
    req = Request(url, headers={
        "Authorization": f"Bot {BOT_TOKEN}",
        "User-Agent": BOT_UA,
    })
    with urlopen(req) as resp:
        return json.loads(resp.read())

def post_webhook(content: str) -> None:
    payload = json.dumps({
        "username":   "💡 ハル",
        "avatar_url": HARU_AVATAR,
        "content":    content,
    }).encode("utf-8")
    req = Request(WEBHOOK, data=payload, headers={
        "Content-Type": "application/json",
        "User-Agent": BOT_UA,
    })
    with urlopen(req) as _:
        pass

# メッセージ取得
messages = discord_get(f"/channels/{CHANNEL_ID}/messages?limit=10")
if not messages:
    print("No messages found.")
    sys.exit(0)

# 最新メッセージ確認（Discord は新しい順）
latest = messages[0]

# ボット（自分自身含む）なら返信済み → スキップ
if latest["author"].get("bot", False):
    print("Latest message is from a bot. Skipping.")
    sys.exit(0)

# 時刻チェック（30分以内か）
ts_str = latest["timestamp"].replace("Z", "+00:00")
ts = datetime.datetime.fromisoformat(ts_str).astimezone(datetime.timezone.utc)
now = datetime.datetime.now(datetime.timezone.utc)
age_min = (now - ts).total_seconds() / 60
if age_min > WINDOW_MIN:
    print(f"Message is {age_min:.1f} min old. Outside window.")
    sys.exit(0)

user_name    = latest["author"].get("global_name") or latest["author"]["username"]
user_content = latest["content"]

print(f"Replying to {user_name}: {user_content[:80]}")

# Claude で返信生成
prompt = f"""あなたはJsR AcademyのAIアシスタント「ハル」です。知的で明るい女の子キャラクター。
研修生の「{user_name}」さんが次のメッセージを送りました:

「{user_content}」

以下のルールで返信してください:
- 親しみやすく、頼れる先輩のような口調（「〜ですね」「なるほど！」など）
- 180文字以内（絵文字OK）
- AIや学習に関係する内容なら丁寧に答える
- 雑談・近況なら自然に盛り上がる
- 自己紹介は不要
- 返信文のみ出力。前置き・説明・引用符は一切不要"""

env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
result = subprocess.run(
    ["claude", "-p", prompt],
    capture_output=True, text=True, timeout=60,
    env=env
)
response = result.stdout.strip()
if not response:
    print("Empty response from Claude.", file=sys.stderr)
    sys.exit(0)

# 180文字制限
if len(response) > 180:
    response = response[:178] + "…"

# クォート付きで投稿（返信感を出す）
post_content = f"> {user_content[:80]}{'…' if len(user_content)>80 else ''}\n\n{response}"
post_webhook(post_content)
print("Reply posted.")
