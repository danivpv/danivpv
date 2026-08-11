---
name: session-recovery
description: >
  Recover interrupted, truncated, or past working sessions by inspecting the SQLite database at C:\Users\daniv\.gemini\antigravity-ide\conversations\<conversation-id>.db. Use when asked to load, recover, resume, or inspect a past or interrupted session, or when given a conversation ID to load.
compatibility: Requires Python 3 with sqlite3 (stdlib). Windows paths. Antigravity IDE only.
---

# Session Recovery

Use this skill to recover full context, user request history, and execution state from any past Antigravity IDE conversation.

## Recovery Procedure

Run both scripts below in sequence. Replace `<conversation-id>` with the actual ID.

### Step 1 — Extract User Request History

```python
import sqlite3, re, sys
sys.stdout.reconfigure(encoding='utf-8')
db = r'C:\Users\daniv\.gemini\antigravity-ide\conversations\<conversation-id>.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT idx, data FROM gen_metadata WHERE size > 0 OR data IS NOT NULL ORDER BY idx DESC LIMIT 1;")
row = cur.fetchone()
if row and row[1]:
    matches = re.findall(rb'<USER_REQUEST>(.*?)</USER_REQUEST>', row[1], re.DOTALL)
    for i, m in enumerate(matches, 1):
        print(f"\n[Turn {i}] " + "-"*40)
        print(m.decode('utf-8', errors='ignore').strip())
```

### Step 2 — Inspect Recent Execution Steps

```python
import sqlite3, re, sys
sys.stdout.reconfigure(encoding='utf-8')
db = r'C:\Users\daniv\.gemini\antigravity-ide\conversations\<conversation-id>.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT idx, step_type, step_payload, render_info FROM steps ORDER BY idx DESC LIMIT 25;")
TYPE_MAP = {5:"replace_file_content",7:"grep_search",8:"view_file",9:"list_dir",
            15:"Model Output",21:"run_command",101:"System Message",132:"manage_task"}
for idx, st, p, r in cur.fetchall():
    tool = TYPE_MAP.get(st, f"Turn Anchor ({st})" if st in [14,23,98,99] else "Unknown")
    def strings(blob):
        if not blob: return []
        return [m.decode('utf-8','ignore').strip() for m in re.findall(rb'[\x20-\x7e\t\r\n]{6,}', blob)
                if not re.match(rb'^[0-9a-fA-F\-]{36}$', m) and not re.match(rb'^[0-9a-zA-Z_\-\+\/\=]{30,}$', m)]
    print(f"Step {idx} | {st} ({tool})")
    pts = strings(p); rts = strings(r)
    if pts: print(f"  Payload: {pts[:3]}")
    if rts: print(f"  Render:  {rts[:3]}")
```

### Step 3 — Recovery Checklist

After running both scripts:

1. Identify the **last explicit user request** from Step 1 output.
2. Verify completed actions by matching against `replace_file_content` (type 5) and `run_command` (type 21) steps from Step 2.
3. Check for background tasks: type 132 (`manage_task`) or type 101 (system messages).
4. Report to the user what was completed, then resume from the next pending item.

## Database Schema (quick reference)

Read [`references/recover.md`](references/recover.md) for detailed schema documentation if needed (all `step_type` values, `gen_metadata` structure, etc.).
