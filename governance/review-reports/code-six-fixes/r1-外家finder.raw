severity: major
blocking: 是
引句:「with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):」
file: `scripts/lumos:17646`
場景: 30 秒只在呼叫前檢查，單次 `cmd_impact` 若耗時 31 秒仍會繼續，最終撞上 hook 的 45 秒 timeout、整份設計鏡頭落空；翻紅重現：mock `cmd_impact` 為 `time.sleep(31)`，斷言 `cmd_dispatch_lens_spec` 在 30 秒內返回會失敗。

severity: major
blocking: 是
引句:「_append_governance_log(Path(gr), [{"gate": "delguard", "kind": "ok", "hard": False,」
file: `scripts/lumos:14276`
場景: `_delguard_vault_scan` 因 deadline 返回部分結果後沒有再次 `_over()`，仍記 `kind=ok` 並輸出 `degraded:false`，會把超時灌成成功、直接扭曲預定的 ok/degraded 比例；翻紅重現：mock `_delguard_vault_scan` 使時鐘跨過 deadline 後返回 `[]`，斷言治理帳不得含 `kind=ok`，目前會失敗。

severity: major
blocking: 是
引句:「sp = Path(spec_path)」
file: `scripts/lumos:17605`
場景: `spec_path` 未限制在 repo／知識圖譜內，`python3 scripts/lumos dispatch-lens --spec /etc/hosts --repo . --json` 實測 rc=0；同理正規式允許 `scripts/../../outside.py`，可讓 `cmd_impact` 讀 repo 外檔案內容，違反這個 hook 的專案邊界。

severity: minor
blocking: 否
引句:「if cand in seen or cand.endswith(".md"):」
file: `scripts/lumos:17625`
場景: 正規式明列的 `docs/methodology/x.md` 隨後必被 `.endswith(".md")` 排除，該類程式化 methodology 檔永遠不會跑 impact；實測 regex 能抽到它，但過濾後清單為空。

severity: minor
blocking: 否
引句:「listed = [{"node": n, "kind": "計劃連結", "contract": None, "files": []} for n in linked if n not in pinned]」
file: `scripts/lumos:17670`
場景: 直接連結的 Systems/Issues 若同時被 impact 命中，就從前置 `linked` 區剔除並落到後面的 pinned 排序，違反「計劃直接連結放最前」；現有測試只覆蓋未重疊節點，抓不到此例。

severity: minor
blocking: 否
引句:「res = (run_one_codex(sc, work, a.timeout, a.model, a.arm, a.stop_block, a.codex_bypass_hook_trust) if a.runner == "codex"」
file: `scripts/scenario_probe.py:497`
場景: 題目的 `max_turns:30` 只經 Claude `run_one` 消費，`--runner codex --only s15-new-verification` 完全忽略它；CLI help 與題庫未揭露 runner 限制，會讓同一題在兩種 runner 下具有不同但未說明的預算語意。

severity: clean
blocking: 否
引句:「what = rng or spec」
file: `scripts/hooks/claude/dispatch-lens-hook.py:131`
場景: marker 只接受單一 `\S+` token，空白與換行無法進入；引號或反引號雖會原樣回填，但內容早已存在原派工詞，且 subprocess 使用 argv、不經 shell，未形成新的執行注入面。

severity: clean
blocking: 否
引句:「set -- $counts」
file: `governance/autonomous-loop.sh:259`
場景: Bash 函式的位置參數是函式區域，`set --` 不會污染呼叫端；空 `$5` 由 `${5:-}` 安全處理，而 replay 首行確為單行 JSON。

severity: clean
blocking: 否
引句:「( cd "$DIR/.." && python3 scripts/lumos testmap build )」
file: `governance/daily-governance.sh:47`
場景: wrapper 明確使用 `set -uo pipefail` 而非 `set -e`，所以 testmap 非零只被記入 `rc`，不會截斷 wrapper 或阻止完成訊息。

max severity: major
