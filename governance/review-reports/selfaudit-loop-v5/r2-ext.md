### 1. blocker

引句:「範圍刀=`git -C <sandbox> diff --name-only`(相對沙盒 repo 根,與 repo_rel 同空間嚴格相等)」

問題：沙盒在建立並 commit 快照後，才刪除五組「審計脈絡」；其中至少 583 個是 tracked files。這些刪除會全部出現在 `git diff --name-only`，因此任何 FAIL→修復流程的範圍刀都不可能嚴格等於單一 `repo_rel`，必然被判越界、落 pending。自動修復閉環實質上永遠走不到複審成功回寫。

查證：`scripts/scenario_probe.py:91-110`（先 rsync、`git add -A`、commit 快照）；`/tmp/selfaudit-loop-v5-r2.md:67-69`（快照後刪除五項）；`/tmp/selfaudit-loop-v5-r2.md:83-89`（diff 嚴格等於單篇，否則 abort）；`git ls-files` 實查五項共 583 個 tracked files。

能翻紅的最小重現：

```bash
tmp="$(mktemp -d)"
git clone -q . "$tmp/repo"
cd "$tmp/repo"
rm -rf governance/review-reports governance/pending governance/l4-audit
rm -f docs/.governance-log.jsonl docs/.canary-log.jsonl
printf '\nprobe\n' >> docs/lumos-toolchain-knowledge/Systems/design-loop.md
test "$(git diff --name-only | wc -l | tr -d ' ')" = 1
# FAIL：輸出遠大於 1；範圍刀必判越界
```

### 2. major

引句:「★柵欄擋下(stale)=時序巧合非失敗→不落 pending、不鎖,記週帳後重新排隊」

問題：`stale` 雖宣稱「重新排隊」，但該次派工已留下 `started`，而配額只數本週 `started`。若 quota=2 的兩篇都 stale，本週剩餘每日進場皆為零配額，只能等下週，並非下輪照常入選。這把正常併發更新變成最長近一週的審計延遲，且與「時序巧合非失敗、不鎖」的結局語意衝突。

查證：`/tmp/selfaudit-loop-v5-r2.md:90-98`；`/tmp/selfaudit-loop-v5-r2.md:129-132`。現有 autonomous loop 每日從 backlog 選案，見 `governance/autonomous-loop.sh:139-147`。

能翻紅的最小重現：

```bash
python3 - <<'PY'
quota = 2
week = [
    {"stem": "a", "kind": "started"},
    {"stem": "a", "kind": "stale"},
    {"stem": "b", "kind": "started"},
    {"stem": "b", "kind": "stale"},
]
remaining = quota - sum(r["kind"] == "started" for r in week)
assert remaining > 0, "stale 應可在下輪重新排隊"
PY
# AssertionError：remaining == 0
```

### 3. major

引句:「整段「讀配額→派工→終局 append」用 `fcntl.flock` 鎖週帳檔」

問題：鎖被持有至 agent 派工終局，而每個 `subprocess.run` 可持續 900 秒。僅兩篇直接 PASS 就持鎖約 30 分鐘；若兩篇都走審計→修復→複審，最壞可達約 90 分鐘。同期第二個 autonomous-loop 進場會無期限阻塞在 flock，連後續既有週考、nags 與 gap loop 都無法前進；目前規格也沒有 lock timeout 或只鎖「配額預約」的窄臨界區。

查證：`/tmp/selfaudit-loop-v5-r2.md:67-75`（每篇最多三次、每次 timeout 900）；`/tmp/selfaudit-loop-v5-r2.md:93-98`（鎖涵蓋派工至終局）；既有 autonomous loop 的前置週考與 gap 流程位於 `governance/autonomous-loop.sh:84-147`。

能翻紅的最小重現：

```bash
lock="$(mktemp)"
python3 - "$lock" <<'PY' &
import fcntl, sys, time
with open(sys.argv[1], "a") as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    time.sleep(1800)  # 兩篇各一次 900 秒
PY
holder=$!
python3 - "$lock" <<'PY'
import fcntl, sys
with open(sys.argv[1], "a") as f:
    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
PY
# BlockingIOError：第二次 loop 無法進場；實作若用 blocking LOCK_EX 則掛住
kill "$holder"
```

最嚴重 severity：blocker
