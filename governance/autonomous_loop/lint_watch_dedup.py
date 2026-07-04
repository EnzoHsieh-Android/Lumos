"""lint-watch 去重 + 放行側效(所有 JSON 讀寫在 python;shell 不碰 JSON)。"""
import json, sys, os


def new_candidates(candidates, seen_path):
    seen = set()
    if os.path.exists(seen_path):
        with open(seen_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                    seen.add((o.get("name"), o.get("latest")))
                except json.JSONDecodeError:
                    continue
    return [c for c in candidates if (c.get("name"), c.get("latest")) not in seen]


def _line_message(new):
    lines = [f"🔧 lint 升級候選({len(new)}):"]
    for c in new:
        typ = c.get("registry", "").split(":", 1)[0]
        lines.append(f"{c['name']} {c['current']}→{c['latest']}({typ})")
    return {"messages": [{"type": "text", "text": "\n".join(lines)}]}


def main(argv):
    if len(argv) < 3:
        print("usage: lint_watch_dedup.py <seen_path> <pending_path> <today>", file=sys.stderr)
        return 2
    seen_path, pending_path, today = argv[0], argv[1], argv[2]
    try:
        manifest = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("", end="")
        return 0
    cands = manifest.get("candidates") or []
    new = new_candidates(cands, seen_path)
    if not new:
        print("", end="")
        return 0
    with open(pending_path, "w", encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False, indent=2)
    with open(seen_path, "a", encoding="utf-8") as f:
        for c in new:
            f.write(json.dumps({"name": c["name"], "latest": c["latest"], "seen": today}, ensure_ascii=False) + "\n")
    print(json.dumps(_line_message(new), ensure_ascii=False), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
