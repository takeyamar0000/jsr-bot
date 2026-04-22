#!/usr/bin/env python3
"""
Sanitize Claude Code output for Discord posting.

- Cuts any preamble/meta-commentary before the first known header emoji
- Strips trailing "Sources:", "参考:", etc. sections
- Truncates to 1900 characters (UTF-8 safe, character-based not byte-based)

Usage: python3 sanitize.py < input.txt > output.txt
"""
import sys

text = sys.stdin.read().strip()

# Skip preamble: cut to earliest occurrence of any known header emoji
HEAD_MARKERS = ['📖', '🌅', '🌙', '🚀', '📄', '📅', '🧰', '🎓', '🎙️']
earliest = -1
for m in HEAD_MARKERS:
    idx = text.find(m)
    if idx >= 0 and (earliest == -1 or idx < earliest):
        earliest = idx
if earliest > 0:
    text = text[earliest:].rstrip()

# Remove trailing "Sources:" / "参考:" / "引用:" / "References:" sections
TAIL_MARKERS = ['Sources:', 'Source:', '参考:', '参考URL:', '引用:', 'References:']
for marker in TAIL_MARKERS:
    idx = text.find(marker)
    if idx > 0:
        text = text[:idx].rstrip()
        break

# Character-based truncation (UTF-8 safe)
if len(text) > 1900:
    text = text[:1897] + '...'

sys.stdout.write(text)
