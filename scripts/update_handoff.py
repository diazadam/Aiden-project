#!/usr/bin/env python3
import re, subprocess, sys, pathlib, datetime
root = pathlib.Path(__file__).resolve().parents[1]
hand = root/"HANDOFF.md"
block = subprocess.check_output(["bash","-lc", f"{root}/scripts/handoff.sh"], text=True)
text = hand.read_text() if hand.exists() else "# HANDOFF\n\n<!-- handoff:summary:start --><!-- handoff:summary:end -->\n"
start = "<!-- handoff:summary:start -->"; end = "<!-- handoff:summary:end -->"
new = re.sub(f"{start}.*?{end}", f"{start}\n{block}\n{end}", text, flags=re.S)
hand.write_text(new)
print("Updated HANDOFF.md")