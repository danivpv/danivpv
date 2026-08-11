# Session Recovery (`/recover`)

## Recovery Procedure

### Step 1: Extract Chronological User Requests (`gen_metadata`)
To retrieve the exact sequence of user prompts and instructions right up to the interruption point, run this Python script via `run_command`:

```python
import sqlite3
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = r'C:\Users\daniv\.gemini\antigravity-ide\conversations\<conversation-id>.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the latest checkpoint in gen_metadata
cursor.execute("SELECT idx, data FROM gen_metadata WHERE size > 0 OR data IS NOT NULL ORDER BY idx DESC LIMIT 1;")
row = cursor.fetchone()

if row and row[1]:
    idx, data = row
    print(f"=== RECOVERED USER REQUEST HISTORY (Checkpoint idx {idx}) ===")
    matches = re.findall(rb'<USER_REQUEST>(.*?)</USER_REQUEST>', data, re.DOTALL)
    for i, m in enumerate(matches, 1):
        txt = m.decode('utf-8', errors='ignore').strip()
        print(f"\n[Turn {i}] ----------------------------------------")
        print(txt)
        print("--------------------------------------------------")
```

### Step 2: Inspect Recent Steps & File Modifications (`steps`)
To see what the model actually executed during the last turn (e.g. what files were edited or checked right before interruption), run:

```python
import sqlite3
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = r'C:\Users\daniv\.gemini\antigravity-ide\conversations\<conversation-id>.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT idx, step_type, step_payload, render_info, metadata FROM steps ORDER BY idx DESC LIMIT 25;")
rows = cursor.fetchall()

print("=== RECENT STEP EXECUTION TRAJECTORY ===")
for idx, st, p, r, m in rows:
    def clean_strings(blob):
        if not blob: return []
        matches = re.findall(rb'[\x20-\x7e\t\r\n]{6,}', blob)
        results = []
        for match in matches:
            try:
                t = match.decode('utf-8').strip()
                # Exclude raw UUIDs and generic base64 to keep readable
                if not re.match(r'^[0-9a-fA-F\-]{36}$', t) and not re.match(r'^[0-9a-zA-Z_\-\+\/\=]{30,}$', t):
                    results.append(t)
            except:
                pass
        return results

    p_txt = clean_strings(p)
    r_txt = clean_strings(r)
    
    # Identify tool call names
    tool_name = "Unknown"
    if st == 5: tool_name = "replace_file_content"
    elif st == 7: tool_name = "grep_search"
    elif st == 8: tool_name = "view_file"
    elif st == 9: tool_name = "list_dir"
    elif st == 15: tool_name = "Model Output / Thinking"
    elif st == 21: tool_name = "run_command"
    elif st == 101: tool_name = "System Message"
    elif st == 132: tool_name = "manage_task / schedule"
    elif st in [14, 23, 98, 99]: tool_name = f"Turn Anchor ({st})"

    print(f"Step {idx} | Type {st} ({tool_name})")
    if p_txt: print(f"  Payload: {p_txt[:4]}")
    if r_txt: print(f"  Render:  {r_txt[:4]}")
```

### Step 3: Actionable Recovery Checklist
After extracting the history from the two scripts above:
1. **Identify the Last Explicit User Request**: Check the final `<USER_REQUEST>` block extracted from Step 1.
2. **Verify Completed Actions**: Match the user request against `replace_file_content` (`step_type = 5`) and `run_command` (`step_type = 21`) actions found in Step 2.
3. **Check Background Tasks**: If `step_type = 132` (`manage_task`) or `step_type = 101` indicates a running terminal build or linter task, verify its current status or log file before proceeding.
4. **Resume Seamlessly**: Proactively report to the user what was completed before the interruption and immediately pick up from the exact remaining item without repeating completed edits.
