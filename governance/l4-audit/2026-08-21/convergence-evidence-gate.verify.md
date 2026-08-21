C1 [✅] K=2 生效門檻靠 LUMOS_PANEL_K2_CUTOFF env(預設 2026-08-06)、首筆 ts[:10] 比對、不回溯既有 loop | 證據: scripts/lumos:3559-3565 (`_panel_k2_active`：`cutoff = os.environ.get("LUMOS_PANEL_K2_CUTOFF", "2026-08-06")` / `ts = str((rounds[0] if rounds else {}).get("ts") or "")` / `return ts[:10] >= cutoff`)

C2 [❌] 「三條合取」與現況不符——2026-08-14 降級後 `_panel_round_conjuncts` 只剩兩條合取(輪有效∧存活≤minor);capture-recapture 已降 advisory、不再 append 進 fails。函式確為兩處(latest 與 prev_rid quiet)共用、prev 輪 quiet 僅印一行摘要兩點屬實 | 證據: scripts/lumos:3568-3569(docstring「單輪兩條合取」)、3604-3620(capture-recapture 區塊只 print、不 `fails.append`)；反例：scripts/lumos:3705 呼叫處註解仍寫「三條合取」(`# A案:三條合取抽出共用`)是舊註解未同步、非現況；呼叫共用兩處於 3705/3716，prev quiet 一行摘要見 3717-3719/3724

C3 [✅] cluster 路徑 K=2 用同一 `_panel_k2_active` 判窗、且要求前一輪為有效輪(`valid_of`)才算過 | 證據: scripts/lumos:3822-3830(`_k2c = _panel_k2_active(all_rounds or [])`；`prev_valid = len(rids_) >= 2 and valid_of.get(rids_[-2], False)`；不過則 `fails.append("K=2前一輪未乾淨")`)

C4 [✅] `_panel_probe_verdict`：`sha256(f"{loop_id}:{rid}:{toks}")%2==0` 決定應抽/免抽,輸入純取自 append-only 帳(token 由 record 端自動鑄) | 證據: scripts/lumos:3624-3631

C5 [❌] 席數縮至 3、不計入既有輪次 cap、上限 1 次三項參數在 `scripts/lumos` 裡**無任何機械實作**——probe-* 輪只是一般 round-id 字串,`cmd_loop_next` 的 cap 計數 `rounds_count = len({r["round"] for r in rounds})`(含全部 distinct round,無 probe 排除邏輯),也沒有任何程式碼限制同 loop 只能開一次 probe-*、或檢查該輪席數=3。唯一機械化的是「應抽/免抽」判定與(下一條 C6)自然撤銷；「席數3/不計cap/限1次」只在 skills/lumos-code-loop/SKILL.md 以散文寫成操作慣例,屬人守紀律,非閘機械驗證 | 證據: scripts/lumos:4841(`rounds_count = len({r["round"] for r in rounds}) if panel_fmt else len(rounds)`，無 probe 排除)；grep 全檔 `probe-`/`席.*3`/`上限.*1` 僅命中列印訊息 scripts/lumos:3743/3844("★應抽查★——加開 probe-* 輪(不計 cap...)"，純文字建議非強制)；skills/lumos-code-loop/SKILL.md:39 記載「材料全量、席數可縮 3、不計 cap、冒 major 自動撤銷收斂;抽查上限 1 次/loop」與 C5 文字相符，但此為 skill 散文非 lumos 程式碼強制

C6 [✅] probe 輪冒 major 使 K=2 窗自然滑入髒輪、gate 回報 FAIL,無新機制(K2 前一輪檢查與 latest fails 共用既有 `_panel_round_conjuncts`) | 證據: scripts/test_lumos.py:12488-12495(`t_panel_k2_and_probe` ④撤銷自動化：record probe-r3 major → `g3.returncode == 1`)；機制路徑 scripts/lumos:3698(`rid, latest = next(reversed(groups.items()))` 會把最新 round-id 當成 latest，probe-r3 append 後即成 latest)+3705(對 latest 跑既有 `_panel_round_conjuncts`)

C7 [✅] 循序模式 K=2 對應 `--need 2`,邏輯為 `converged = len(rounds) >= need and all(good(r) for r in rounds[-need:])` | 證據: scripts/lumos:4463

C8 [❌] 「平行 panel 模式收斂為 K=1」作為現況總結不成立——2026-08-06 起(今日 2026-08-21 已過 cutoff)新 loop 預設走 K=2；`next(reversed(groups.items()))` 只是取「latest 輪」做基本合取檢查的第一步，K2 啟用時會再加驗 `prev_rid`(3708-3719)，並非「只看最後一輪」即定生死。此描述僅對 cutoff 前的舊帳(legacy K=1)成立 | 證據: scripts/lumos:3698(`next(reversed(groups.items()))` 僅取 latest)、3708-3719(k2 額外檢查前一輪)、3559-3565(cutoff 判斷)

C9 [❌] 「tier=high 實務上走 panel、故現行收斂條件是 K=1」與現況相反——skills/lumos-code-loop/SKILL.md:39 明載「2026-08-06 起新 loop=K=2...tier=high 走這條」，且程式碼 `_panel_k2_active` 對今天建立的所有新 loop 一律判定為 K=2(cutoff 已過)。K=1 只適用於 cutoff 前開的舊 loop | 證據: skills/lumos-code-loop/SKILL.md:39；scripts/lumos:3559-3565、3708

C10 [✅] `--panel` 落地日期與判準皆對：git log 顯示 `--panel` 收斂謂詞於 2026-07-09 落地(4783be4)；現行 `_panel_round_conjuncts` 「輪有效」= 記帳席(caught+none)≥2 且 0 missed,「存活嚴重度」= max≤minor,兩者合起來即 C10 所述三個布林條件的合取 | 證據: git log(`4783be4 2026-07-09 feat(loop): loop status --panel 收斂謂詞...`)；scripts/lumos:3578-3596(輪有效:記帳席≥2∧missed=0)、3598-3603(存活 max≤minor)

C11 [✅] capture-recapture 已於 2026-08-14 降 advisory、逐字比對數據(67% vs 79%、p≈0.25)相符,且不進合取(fails 不 append) | 證據: scripts/lumos:3604-3606(「★2026-08-14 降 advisory,不進合取★...理由=鑑別力≈0(殘餘<1組下輪major+ 67% vs ≥1對照組79%,p≈0.25)+f1≤1公式退化」)、3607-3620(全區塊只 print,無 fails.append)

C12 [✅] legacy(無 --panel)路徑 K-streak∧G1∧G2 完全未動,僅 panel 判準有異動 | 證據: scripts/lumos:4457-4557(`cmd_loop_status` 的 legacy K-streak/G1/G2 區塊與此前分析一致，未見任何 panel 相關改動滲入)

C13 [✅] GATE PASS(循序)= K-streak(必要)∧G1(_refcheck_scan 0 missing/0 超界)∧G2(findings 單調不增、末輪≤1、末步下降,K=1 退化末輪需=0)∧G3(帶 --spec 驗雙 hash 鏈,窗內無記錄直接 FAIL 非 advisory) | 證據: scripts/lumos:4494-4502(G1 用 `_refcheck_scan`，`bad` 非空即 `fails.append("G1")`)、4504-4522(G2:`if need == 1: drained = fs[-1] == 0` / 否則 `mono and fs[-1] <= 1 and (fs[-1] == 0 or fs[-1] < fs[-2])`)、4549-4560(G3:`elif info == "unbound": ... fails.append("G3")` 直接 FAIL 非 advisory)

C14 [✅] `_build_prompt` 用 sentinel(`<<<EVIDENCE-BEGIN>>>` 等)定界三段材料,`_parse_worst` 優先解析末行、失敗才 fallback 全文掃描,回傳 (sev, parse_fallback) 二元組 | 證據: governance/autonomous_loop/cross_audit.py:38-47(`_parse_worst`回傳`(m.group(1), False)`或`(..., True)`)、50-61(`_build_prompt` 三段 sentinel)

C15 [✅] §2.5c：≥major 指控須驗證後仍存活才 `cross_reject_count += 1`；全數機械反證則 `cross_verdict=endorsed-after-refute` 並放行,不計 reject | 證據: governance/autonomous_loop/orchestrator-prompt.md:64-65(「≥1 條 ≥major 指控經驗證存活...→ cross_reject_count += 1」/「全數被機械反證 → cross_verdict=endorsed-after-refute、放行...不消耗放行預算」)

C16 [✅] 三條向後相容：①不帶 --gate 分支結構未變(`cmd_loop_status` 內 `if not gate:` 提前 return,其後 G1/G2/G3 全在 gate-only 區塊)②`cmd_canary` 對 `--findings` 用 `if findings is not None: rec["findings"] = findings`,不給不寫鍵③`run_cross_audit` 對照 git diff 只新增 `parse_fallback` 鍵、其餘鍵(status/worst_severity/findings/usage)逐字未動 | 證據: scripts/lumos:4457(`if not gate:`)、3229-3230(`if findings is not None: rec["findings"] = findings`)；git show fe0db39 -- governance/autonomous_loop/cross_audit.py(diff 只在 return dict 加 `parse_fallback` 一鍵)

C17 [✅] 決策 d2：「留痕完整」因 {streak 通過}⊆{留痕完整} 恆真被判零判別力、誠實拆除,不湊三錨門面,gate 收斂為 K-streak∧G1∧G2 兩錨 | 證據: docs/design/2026-07-03-convergence-evidence-gate.md:46(「{streak 通過} ⊆ {留痕完整} 恆真,另設此錨是零判別力的裝飾...誠實拆除、不湊「三錨」門面」)、132(「原 G2「留痕完整錨」vacuous → 整錨拆除,gate 收斂為 K-streak ∧ G1(refcheck)∧ G2(發現枯竭...)」)；現行 code 中 `cmd_loop_status --gate` 確實只有 K-streak/G1/G2(+後補 G3 hash 鏈)三類判準、無獨立「留痕完整」檢查

C18 [✅] 決策 d3：cross_reject 計票由「qwen 喊 major 即計」(56c1596)改為「驗證後仍存活才計」(6b74106),全反證改走 endorsed-after-refute 放行 | 證據: git show 56c1596(`worst_severity ∈ {major,blocker} → ... cross_reject_count += 1` 無條件計)vs git show 6b74106 commit message(「§2.5c 計票改「驗證存活才計」(endorsed-after-refute/unanchored/parse_fallback)」)+ orchestrator-prompt.md:64-65 現況同 C15

C19 [✅] 交付測試規模全數核實：`t_canary_findings` 3 個 check()、`t_loop_gate` 16 個 check()、`TestCrossAudit` 新增 4 項單元測試(`test_parse_worst_last_line_priority`/`test_parse_worst_fallback_flags`/`test_ok_includes_parse_fallback_key`/`test_build_prompt_sentinels`)；在對應歷史 commit(1b76000,即該功能包最後一次提交)簽出獨立 worktree 實跑 `python3 scripts/test_lumos.py`,輸出逐字為「352 passed, 0 failed」 | 證據: scripts/test_lumos.py:112-123(`t_canary_findings` 3 checks)、126-207(`t_loop_gate` 16 checks，逐案計數:案3/4/5/6/7/8/9a/9b/10a/10b/11/12/gate缺findings/13a/13b/14=16)、scripts/test_autonomous_loop.py:213-244(TestCrossAudit 內 4 個新測試方法)；實測命令 `git worktree add .../wt-1b76000 1b76000 && python3 scripts/test_lumos.py` → 尾行 `352 passed, 0 failed`

✅14 ❌5 ❓0 ⏭0
