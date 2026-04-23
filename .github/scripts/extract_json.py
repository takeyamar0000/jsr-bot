#!/usr/bin/env python3
"""
Claude の出力から JSON 配列を抽出する。
コードブロック・前置き・後置きを除去して純粋な JSON を返す。
"""
import sys, re, json

text = sys.stdin.read().strip()

# ```json ... ``` または ``` ... ``` ブロックを除去
text = re.sub(r'```json\s*', '', text)
text = re.sub(r'```\s*', '', text)
text = text.strip()

# JSON 配列を探す
match = re.search(r'(\[.*\])', text, re.DOTALL)
if not match:
    print("[]", file=sys.stderr)
    sys.stdout.write("[]")
    sys.exit(0)

try:
    data = json.loads(match.group(1))
    sys.stdout.write(json.dumps(data, ensure_ascii=False))
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}", file=sys.stderr)
    sys.stdout.write("[]")
