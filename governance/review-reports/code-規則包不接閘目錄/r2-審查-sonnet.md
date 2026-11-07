severity: minor

## F1 SARIF 探針不認相對路徑的 --sg,會誤報「SARIF 跑不起來」(be-api-compat:`--sg` 舊用法不相容)
severity: minor
blocking: 否
引句:「        claims, ok = lm._lint_run_and_parse("", str(HERE), timeout=SCAN_TIMEOUT,」
佐證:`configs/ast-grep/kotlin-android/check.py` 新的 `sarif_gate_rule_ids`,r2-repair.patch 約第 71 行;它經 `scripts/lumos:42146` 的 `_lint_wt_resolve_tool` 解析工具。
失敗場景:`--sg` 給相對路徑,例如從 `kotlin-android/` 目錄用 `--sg ../../../../../tmp/.../sg`,或工具實際在 repo 裡。
- 修補前:`subprocess.run([sg, ...], cwd=HERE)` 接受相對路徑,其他掃描也都接受。
- 修補後:`_lint_wt_resolve_tool` 因為「不是絕對路徑」回 None,`_lint_spawn` 回 None,`_lint_run_and_parse` 回 `([], False)`。
- 結果:其他掃描全綠,只有 SARIF 兩項誤報「SARIF 掃壞例樣本跑不起來(…:沒產出閘讀得懂的 SARIF)」,檢查回 2 個問題。
- 我實跑確認:改用相對路徑的符號連結,退出訊息就是上面這句,`規則 207 條,問題 2 個`。
- 原因句沒講真正原因(工具解析被拒,`fail_info["unresolved"]` 沒傳也沒讀),會誤導人去查 SARIF。
- 絕對路徑與 PATH 上的 `ast-grep` 不受影響,測試與 CI 都走絕對路徑,所以沒被抓到。

## F2 假工具測試缺同檔內的正向對照,「沒有檔案位置」案例分不出原因
severity: minor
blocking: 否
引句:「("規則對但沒有檔案位置(閘會靜默略過)", "echo '{\"runs\":[{" + _drv + ",\"results\":[{\"ruleId\":\"kt-livedata-setvalue-background\"」
佐證:`scripts/test_lumos.py` 的 `t_kotlin_rulepack_samples`,r2-repair.patch 約第 302 行。
失敗場景:這個案例只斷言 `len(hit)==2 and all("樣本" in b …)`。
- 如果 `_drv` 或 `_loc` 的 JSON 本身寫壞,讀不出任何東西,同樣得到 2 個含「樣本」的問題,測試照綠。
- 所以它沒證明「紅是因為缺位置」,違反〈測試假綠形態〉的前置斷言要求。
- 我手動把同一組假工具改成規則加位置齊全,確實 0 問題;但這個對照不在測試裡。
- 另外 `c.get("file") and c.get("message")` 這個過濾與 `_lint_run_and_parse` 自己的解析重疊:缺位置會被主程式吞掉。
- 唯一能由過濾獨立抓到的是空訊息,沒有任何案例涵蓋;把過濾拿掉,測試仍綠。

## F3 計劃文字沒跟上修補後的行為
severity: minor
blocking: 否
引句:「用 `sgconfig-review.yml` 掃 `kt-livedata-setvalue-background`(`rules-review/state.yml`)的壞例樣本」
佐證:`docs/lumos-toolchain-knowledge/Projects/規則包覆核兩級接新增告警閘_計劃.md` 範圍做 3 與驗收條款 S2,r2-repair.patch 約第 142、177 行。
失敗場景:
- 計劃仍寫「結果裡要各有一筆 `ruleId` 是那條規則」,錯誤句是「沒有 <規則> 的結果」。
- 實作已改成「借 `_lint_run_and_parse`、要有檔案位置與訊息」,訊息變成「沒有新增告警閘讀得到的 …」,並新增「自測要載入 scripts/lumos」一句。
- 讀計劃的人看不到這個新依賴,也看不到 F1 那類相對路徑限制。

## 修補三問
1. **修補有沒有做到:大致有。**
   - claims 欄位 `rule`、`file`、`message` 都存在(`scripts/lumos` 的 claim 字典)。
   - 呼叫契約符合:argv 非空時不走 `_lint_gate_covers`,cmd 傳 "" 沒問題;timeout 與 repo_root 也對。
   - 暫存 SARIF 在 finally 刪除;`_LINT_WT_REG` 在 check.py 呼叫時是 None,走非工作樹路徑,不登記、不遮蔽訊號。逾時有 `_kill_proc_group`,實跑後 TMPDIR 沒有 `lumos-lint-*` 殘留。
   - `-k kotlin_rulepack` 48 個全過;完整自檢 `規則 207 條,問題 0 個`。
   - `_TIMED_OUT` 用經過時間判斷:`not ok` 且 ≥120 秒幾乎只會是逾時,沒看到誤判路徑。
   - `next(d for d, c in CONFIGS if c == cfg)`:`SARIF_PROBES` 是模組常數,兩個 cfg 都在 CONFIGS,現狀不會丟 StopIteration。但這是模組內寫死的常數,沒有防護;不是漏洞。
2. **有沒有帶進新問題:有,就是 F1。** 借用閘的解析函式,同時繼承了閘對工具路徑的限制(必須是絕對路徑,且不在 repo 內)。
3. **同類地方有沒有沒修的:**
   - `loaded_count` 與 `scan` 仍直接 `subprocess.run`,沒有這個限制,所以同一個 `--sg` 在不同檢查裡行為不一致(F1 的根源)。
   - 舊測試名 `t_kt_rulepack_unwired_dir` 在 docs 與 scripts 裡只剩 jsonl 帳本,沒有殘留引用。

## pitfalls manifest
- 分級被內建風險型樣「共享狀態有沒有鎖保護」命中 `rules-unwired/coroutines.yml` 第 11 行。
- 該行只是規則文字含 Mutex,不是這次改的併發程式。
- 併發類題目在本 repo 判範圍外,標誤報。

## 固定席判定(LUMOS-IMPACT 沒附節點,以我讀到的為準)
- **Systems/kotlin規則包**:無合約。about_code 已補 `sgconfig-unwired.yml`;WHY 拆兩行,各自的 test 名都指向存在的測試(`t_kotlin_catalog_rows_wired`、`t_kotlin_rulepack_unwired_dir`)。
- **RULE 的 `[confirmed:]`**:文字有改但確認日期改回 2026-11-05,是誠實的做法,沒有人為宣稱重新確認。
- **Systems/測試假綠形態 ★INVARIANT★**:新案例只達成一半。F2 說明了缺前置斷言(同檔內沒有正向對照)。
- **角色鏡頭**:be-authz 這次沒有端點,不適用。be-api-compat 對應 F1,CLI 的 `--sg` 用法相容。

總結:最高等級為 minor,blocking 共 0 條
