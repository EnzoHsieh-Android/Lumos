C1 [✅] `_capture_counts_from_finders` 純函式:跨 finder key 正規化(casefold+strip)、finder 內去重(用 `seen` set)、Counter 計數各 key 被幾個 finder 找到、`sorted(..., reverse=True)` 降序回傳 | 證據: scripts/lumos:3474-3491

C2 [✅] CLI `lumos loop capture-counts --finder ... [--from-pitfalls <range> --repo <root>]` 存在,算 capture_counts+殘餘估計,吐可貼的 `canary record --capture-counts` 建議串 | 證據: scripts/lumos:3851(cmd_loop_capture_counts)、3892-3895(印出 `→ canary record ... --capture-counts ...`)、14327-14333(argparse `capture-counts` 子指令 + `--finder`/`--from-pitfalls`/`--repo`)

C3 [✅] `--from-pitfalls <range>` 自動呼叫 `_pitfall_diff_collect`(即 `pitfalls --diff` 共用計算),按 `source` 欄位分組成確定性 finder | 證據: scripts/lumos:3868-3886(`_pitfall_diff_collect(from_pitfalls, ...)` → `by_source.setdefault(src, []).append(...)`)

C4 [✅] `_pitfall_diff_collect` 是從 `_pitfall_diff_mode` 抽出的純計算函式(docstring 明寫「純計算、不印」),`_pitfall_diff_mode` 呼叫它再印;供「印」與「收割」共用 | 證據: scripts/lumos:11649-11651(`_pitfall_diff_collect` docstring:「純計算、不印...供 _pitfall_diff_mode(印)與 loop capture-counts(收割成異質 finder)共用同一計算」)、11757-11762(`_pitfall_diff_mode` 呼叫 `_pitfall_diff_collect`)

C5 [✅] capture_counts = 各 distinct finding-key「被幾個 finder 找到」的次數列表,餵給 `_estimate_remaining_defects`(Chao1 f1*(f1-1)/(2*(f2+1)))算殘餘 | 證據: scripts/lumos:3508-3521(`_estimate_remaining_defects` docstring 與公式)、3887(`cmd_loop_capture_counts` 內 `remaining = _estimate_remaining_defects(cc)`)

C6 [✅] 編排流程第4步用 `lumos canary record caught --loop code-<topic> --round rN --capture-counts <串> ...` | 證據: skills/lumos-code-loop/reference.md:206,221-222(範例指令);scripts/lumos:14245-14261(`canary record` 子指令 `kind` positional 含 `caught`,`--loop`/`--round`/`--capture-counts` 旗標齊全)

C7 [✅] `lumos loop status code-<topic> --gate --panel` 的 PASS 判準 = 「輪有效」+「存活 max≤minor」兩條合取 | 證據: scripts/lumos:3742,3745(`print(f"✅ PANEL GATE PASS ({loop_id} 輪 {rid}: ... 輪有效 ∧ 存活≤minor)")`);14297(argparse help 同文字敘述)

C8 [✅] 2026-08-14 決定將 capture-recapture 殘餘估計降級為 advisory、不進合取閘,理由鑑別力≈0(殘餘<1 組下輪 major+ 67% vs ≥1 對照組 79%,p≈0.25) | 證據: skills/lumos-design-loop/reference.md:106(「~~capture-recapture 殘餘 < 門檻~~ ⛔ 2026-08-14 降 advisory 不進合取(鑑別力≈0:67% vs 對照 79%,p≈0.25;見 Projects/收斂閘殘餘估計降級_計劃)」);scripts/lumos:3569,3606-3610(程式碼面同步降級為印 advisory 觀測、不進合取)

C9 [✅] panel_width(派幾個 LLM reviewer)由 tier 決定 | 證據: governance/autonomous_loop/difficulty.py:52-58(`params(tier)` 回 `{"need":3,"maxr":8,"panel_width":5}` for high、`{"need":2,"maxr":6,"panel_width":3}` for standard;docstring 明寫「panel_width(loop 三輪壓縮):tier 驅動平行審計員數」,模組頭部標「風險分級器(risk-tiered-review)」);scripts/test_lumos.py:8988-8999(`t_difficulty_panel_width` 驗 high=5/standard=3)。注:節點 `risk-tiered-review` 本身在圖譜(禁讀範圍),以設計 doc 路徑 `docs/design/2026-07-03-risk-tiered-review.md` 及程式碼佐證

C10 [✅] d1 決定:code-loop panel = LLM reviewer + 確定性工具(SARIF linter/測試/type/mutation),辯方改為可執行反證,非直接沿用 design-loop 的 canary 機制換名字 | 證據: skills/lumos-code-loop/SKILL.md:225(「code-loop ≠ design-loop 換名字(2026-07-09 文獻)...最佳解是異質 ensemble 非「多個多樣 LLM」」)、226(「確定性驗證器(linter SARIF/測試/type checker/mutation)不佔 reviewer 席、不進輪有效...參與三通道...錯誤剖面與 LLM 正交」)、227(「辯方用可執行 falsification(跑測試/repro/mutation 確認或殺一條 finding)> 論證反證」)。「d1」決策標籤本身查無(僅圖譜節點會有,禁讀範圍),但內容三項主張皆對得上 skill 文字

C11 [❌] 測試覆蓋數字已過期:`t_capture_counts_from_finders`實5案例(對)、`t_loop_capture_counts_cli`實7案例(對)、`t_loop_capture_counts_from_pitfalls`實5案例(對)、`t_pitfalls_lint_integration`實15案例(對),但 `t_pitfalls_diff` 實測 12 個 check() 而非宣稱的 11 個(逐一數:rc0/資源/效能/tier-high/class形態軸/line皆int/requests.post第3行/SELECT第5行/.md-skip/測試檔skip/INSERT併發/CJK檔名,共12);「全套 865 passed」已過期——實跑 `python3 scripts/test_lumos.py` 全套現況 = **2885 passed, 0 failed**,scripts/test_lumos.py 內部亦另有「1460 passed」硬編字串(t3242)與「2039 passed」註解(t19969)佐證套件持續成長,865 是舊快照 | 證據: scripts/test_lumos.py:5529-5587(`t_pitfalls_diff` 12 個 `check(`)、5740-5939(`t_pitfalls_lint_integration` 15 個 `check(`)、9413-9428(5)、9431-9453(7)、9455-9490(5);實跑 `python3 scripts/test_lumos.py` 輸出尾行「2885 passed, 0 failed」(exit 0);scripts/test_lumos.py:3242,19969(過往里程碑字串佐證持續成長)

C12 [✅] 確定性 finder 來源包含 SARIF linter(讀 `.lumos/lint.json`)、測試 gate、mutation 存活結果 | 證據: scripts/lumos:3476-3478(`_capture_counts_from_finders` docstring 明列「LLM reviewer、.lumos/lint.json SARIF linter、測試失敗、mutation 存活」);10363-10365(`_lint_load_config` 讀 `.lumos/lint.json`);10487-10552(`_lint_run_and_parse` 解析 SARIF v1/v2.1)

C13 [✅] `--from-pitfalls` 依 `source` 欄位分組——每個 linter driver / pitfalls 內建各算一個獨立確定性 finder | 證據: scripts/lumos:3873-3882(`by_source.setdefault(c.get("source") or "pitfalls-builtin", []).append(...)`;逐 source 各自 append 進 `parsed` 成獨立 finder)

C14 [✅] finding-key 三種產生管道:①LLM reviewer 手動 `--finder`、②`pitfalls --diff`命中經`--from-pitfalls`自動收割、③測試失敗/mutation 存活(亦經 `--finder` 手貼) | 證據: scripts/lumos:3855-3859(`cmd_loop_capture_counts` docstring:「異質 finder 一律先正規化...LLM reviewer 的 finding、pitfalls --diff 的 SARIF linter 命中、測試失敗、mutation 存活,每個 finder 給一個 --finder」)

C15 [✅] `lumos loop capture-counts` 是 vault-free 純機械原語,執行不寫入知識圖譜 | 證據: scripts/lumos:14788-14790(`if args.cmd == "loop" and args.lcmd == "capture-counts": # 純機械原語(不碰圖譜):跨異質 finder 算 capture-recapture 重疊,vault-free` → 直接 `return cmd_loop_capture_counts(None, ...)`,搶在下方 `vault = args.vault or find_vault(...)` 的 vault 查找/建立之前 return)

✅14 ❌1 ❓0 ⏭0
