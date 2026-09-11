severity: major

C1 週檔沒有保存「推了哪些、之後讀了哪些」
severity: major
blocking: 是
引句:「+                                   "zero_push": push is None, "cooldown_inherited": inherited, "pushed_n": len(push["nodes"]) if push else 0,」
file: `governance/eval/lens-utilization/recount.py:642`
輸入一筆推了 `Systems/pushed.md`、隨後成功 Read 同節點的編輯，實跑得到的 `ARCHIVE_KEYS` 只有 `pushed_n`、`misses` 等欄，沒有 pushed/read/touched 清單。`write_archive` 原樣落盤，因此主要產物無法回答設計要求的「推了哪些、之後讀了哪些」。

C2 多檔編輯會把一支檔的冷卻推播套到所有新檔
severity: major
blocking: 是
引句:「+                if p0 is not None and t0 is not None and set(e0["files"]) & set(e["files"]) and 0 <= t - t0 < ttl_sec:」
file: `governance/eval/lens-utilization/recount.py:637`
輸入為 01:00 改 `a.py` 並推 A，01:05 同一 apply_patch 改冷卻中的 `a.py` 與 impact 為空的 `new.py`；實跑 `new.py` 得到 `zero_push=false, cooldown_inherited=true, pushed_n=1`。實際 hook 對 `new.py` 沒推任何筆記，故零推播與 miss 分母都被量錯。

C3 新量測繞過既有 Codex 逐字稿版本閘
severity: major
blocking: 是
引句:「+            ev, sx = analyze_codex(objs, slug, repo_set, hook_ok, idx_nodes)」
file: `governance/eval/lens-utilization/recount.py:987`
輸入 `cli_version=999.0` 加一筆現行形狀的 apply_patch；版本表只有 `0.144.1/0.153.2`，實跑仍輸出 `UNSUPPORTED_VERSION_EDITS=[…src/x.py…]`。Codex 升版後格式若漂移，週報不會照既有承諾跳過，而會靜默產生錯列。

C4 一行壞 JSON 會丟掉整份 Codex 逐字稿
severity: major
blocking: 是
引句:「+            objs = [json.loads(ln) for ln in Path(f).read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip().startswith("{")]」
file: `governance/eval/lens-utilization/recount.py:980`
實掃現有逐字稿找到 `rollout-2026-07-21T14-41-13-….jsonl` 第 75 行 `JSONDecodeError`，其餘 127 個物件可讀且包含 5 次 search；按此 comprehension 會拋例外，外層直接跳過整檔。append-only 稿只要留下半行，該 session 的編輯與搜尋便全部消失。

C5 宣稱的 300 秒不是總時間預算
severity: major
blocking: 是
引句:「+    relate, existed = Relater(repo, vault, budget, impact_timeout), Existence(repo, vault)」
file: `governance/eval/lens-utilization/recount.py:948`
最小測試設 `budget=0`、12 篇 miss，並把每次 `git log` stub 成 20ms，實跑輸出 `elapsed_seconds=0.291, git_calls=12, budget_hit=True`。預算只管 impact；逐字稿掃描與 `Existence` 每節點最長 20 秒的子行程都無上限，miss 多時仍可長時間占住自主迴圈的整跑鎖。

C6 換行分隔的兩個 search 被當成一個查詢
severity: minor
blocking: 否
引句:「+_CHAIN_RE = re.compile(r";|&&|\|\|")」
file: `governance/eval/lens-utilization/recount.py:779`
輸入 `lumos search "zero"\nlumos search "hit"` 及先零後一筆命中的輸出，實跑得到單一 segment `['zero','lumos','search','hit']` 且 verdict 為 `zero`。shell 換行也是命令分隔符，這會製造假的零命中。

C7 沒有實作設計指定的缺時間沿用
severity: minor
blocking: 否
引句:「+                    edits.append({"idx": idx, "ts": o.get("timestamp"), "id": tid, "files": [rel]})」
file: `governance/eval/lens-utilization/recount.py:609`
輸入前一行有 W37 時間、下一行 Edit 缺 timestamp，實跑得到 `ts=None, IN_W37=False`，沒有沿用前一行時間。現存抽樣未發現缺時間的 Edit，因此降為 minor，但它與 S4 明文驗收不一致。

C8 `about_code` 合法單值形態完全讀不到
severity: minor
blocking: 否
引句:「+        m = re.search(r"(?m)^about_code:\s*\n((?:[ \t]+-[^\n]*\n?)+)", fm)」
file: `governance/eval/lens-utilization/recount.py:699`
現有受追蹤節點寫 `about_code: scripts/lumos`，實跑 `_about_map` 得到 `present_in_about_map=False`。若節點只靠這個合法單值欄關聯檔案，miss 會從「關於欄」掉進「判不出」。

圖譜前八篇判定：

G1 `Issues/canary-record未落盤事件.md`：不影響；diff 未改 canary record 落盤或讀回路徑。  
G2 `Systems/design-loop.md`：不影響；未改處置閘、條款辨識或 `.md` 審材判定。  
G3 `Systems/bound-tests-gate.md`：不影響；未改 code-loop check 或綁定測試執行。  
G4 `Systems/canary-audit.md`：不影響；未改 record/second 與 loop-status telemetry 語意。  
G5 `Systems/guard-kill.md`：不影響；未改 rc 優先序或 JSON stdout。  
G6 `Systems/lumos-cli-lifecycle.md`：不影響；未碰 CLAUDE.md re-inject。  
G7 `Systems/slim-get-一行安裝.md`：不影響；未改任何 `.ps1`。  
G8 `Systems/slim-install-安裝器.md`：不影響；未改安裝器、manifest、shim 或 CLAUDE.md 注入。

全份最高嚴重度是 major,blocking 共 5 條。