#!/usr/bin/env python3
"""
Claude の出力から最初の完全な JSON 配列を抽出する。
余分なテキスト・コードブロック・前置き・後置きをすべて無視する。

json.JSONDecoder.raw_decode() を使って「最初の完全な JSON 値」だけを取り出す。
"""
import sys, re, json

text = sys.stdin.read()

# ```json ... ``` または ``` ... ``` ブロックのマーカーだけ除去（中身は保持）
text = re.sub(r'```json\s*', '', text)
text = re.sub(r'```\s*', '', text)

# 最初の '[' を探し、そこから raw_decode で完全な JSON 配列を取り出す
decoder = json.JSONDecoder()
start = text.find('[')

if start == -1:
    print("No JSON array found in output", file=sys.stderr)
    sys.stdout.write("[]")
    sys.exit(0)

try:
    data, _ = decoder.raw_decode(text, start)
    if not isinstance(data, list):
        print("Parsed value is not a list", file=sys.stderr)
        sys.stdout.write("[]")
        sys.exit(0)
    sys.stdout.write(json.dumps(data, ensure_ascii=False))
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}", file=sys.stderr)
    sys.stdout.write("[]")
