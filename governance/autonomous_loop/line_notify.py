import json, subprocess

def build_message(title, confidence_summary, pr_link):
    txt = f"\U0001F504 自主迭代 loop：今天備好 1 個待放行 spec\n\n《{title}》\n可信度：{confidence_summary}"
    txt += f"\nPR：{pr_link}" if pr_link else "\n(dry-run，未開 PR)"
    return {"messages": [{"type": "text", "text": txt}]}

def send(message, token):
    out = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST",
         "https://api.line.me/v2/bot/message/broadcast",
         "-H", f"Authorization: Bearer {token}",
         "-H", "Content-Type: application/json", "-d", json.dumps(message, ensure_ascii=False)],
        capture_output=True, text=True)
    try: return int(out.stdout.strip())
    except ValueError: return -1
