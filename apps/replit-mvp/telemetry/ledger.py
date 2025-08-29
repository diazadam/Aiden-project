from __future__ import annotations
import json, os, time
from typing import Any, Dict, List

LEDGER_PATH = os.path.join(os.path.dirname(__file__), "..", "skills_store", "ledger.jsonl")
os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)

def _now_ms() -> int: return int(time.time() * 1000)

def append_entry(entry: Dict[str, Any]) -> None:
    entry = dict(entry); entry.setdefault("ts", _now_ms())
    # redact any obvious secrets
    for k in list(entry.keys()):
        if k.lower() in {"token","api_key","secret","pin"}: entry[k] = "REDACTED"
    # limit size
    try:
        s = json.dumps(entry, ensure_ascii=False)
        if len(s) > 64_000:
            entry["message"] = (entry.get("message") or "")[:400] + " …"
            entry.pop("data", None)
    except Exception:
        pass
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def read_recent(limit: int = 20) -> List[Dict[str, Any]]:
    if not os.path.exists(LEDGER_PATH): return []
    out: List[Dict[str, Any]] = []
    with open(LEDGER_PATH, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell(); chunk=8192; buf=b""; lines=[]
        while size>0 and len(lines)<limit+5:
            read=min(chunk,size); size-=read; f.seek(size)
            buf=f.read(read)+buf; parts=buf.split(b"\n"); buf=parts[0]
            for line in parts[1:]:
                if line.strip(): lines.append(line.decode("utf-8","ignore"))
        if buf.strip() and len(lines)<limit+5: lines.append(buf.decode("utf-8","ignore"))
    for s in reversed(lines[-limit:]):
        try: out.append(json.loads(s))
        except: pass
    return out