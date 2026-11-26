severity: major

**Finding 1**
severity: major
blocking: 是
`scripts/lumos:79666`(修補後)與 `docs/lumos-toolchain-knowledge/Projects/選擇點存活回指條款_計劃.md:114-118`

修補新增了 reach_why 原因「名稱檢查沒過」,也新增 run 事件欄位 `cov_judged`,但這份計劃的〈範圍〉4 兩處都沒補,r2-repair.patch 對這份計劃只改了〈用詞〉兩條。
- 計劃第 115 行的 reach_why 表寫「只用下表」,表裡九項沒有「名稱檢查沒過」。
- 計劃第 118 行的 run 欄位清單沒有 `cov_judged`。
- 三個月後的接手者照計劃讀帳或寫讀端,會把「名稱檢查沒過」當非法值,也不知道 `cov_judged` 存在。
- 這個原因不在 `_CHOICE_REACH_TEMP`,所以 `--reach-only` 不會重補它,計劃表也沒標它是不是暫時性。這是接手者最容易誤判的地方。
- `_CHOICE_REACH_WHY` 在整個 `scripts/lumos` 只有定義、沒有任何讀寫端使用,所以程式不會擋這個不一致,守住表的只有計劃文字,而計劃沒跟上。

引句:「+_CHOICE_REACH_WHY = (*_CHOICE_REACH_TEMP, "覆蓋例外", "這一行沒有指令紀錄", "名稱檢查沒過")」

最小重現:`grep -c '名稱檢查沒過' docs/lumos-toolchain-knowledge/Projects/選擇點存活回指條款_計劃.md` 得 0;`grep -c cov_judged` 同樣是 0,但程式已經寫出這兩個值。

**Finding 2**
severity: minor
blocking: 否
`scripts/lumos:18585-18587`(gov 事件讀取的 `ck` 子字典欄位白名單)

修補在 `_GOV_FIELD_TYPES` 補了 `cov_judged` 的型別,也改了 `Systems/規格閘.md` 的說明,寫「run 那筆多 merged、single(加上…cov_judged…)…gov 的 ck 子字典帶出這些與 ran」。但 `ck` 的欄位清單(`"ran", "base_secs", "merged", "single", "merge_tripped", … "cov_full"`)沒有 `cov_judged`。
- 讀端看不到 `cov_judged`,沒法用 gov 驗證 `merged + single + cov_judged == ran`。
- 現在 `_render_gov_choice` 沒讀 merged、single,所以不影響當下行為。
- 但新寫的說明與程式不符,而且這條加總恆等式本身無法從 gov 驗證。

引句:「+    **dict.fromkeys(("reach_n", "cov_secs", "cov_skipped", "cov_selected", "cov_full", "cov_judged"), (int,)),」

審查範圍內沒找到其他破壞:
- `LOOP_NOT_CLOSE_EVENTS` 已含 `("choice-kill","reach-run")`。
- `cov_sha` 的 None 改成寫空字串,型別仍是 str,過得了 `_gov_event_types_ok`。
- `_choice_reach_valid` 與 `_choice_kill_pick` 對 None 的處理一致。
- 修補沒動 guard-kill 的 rc 優先序,也沒動 `--json` 輸出。
- 新增的 stderr 警告只在 choice-kill 路徑上出現。
- `--max-mutants` 預設改為 None,argparse 說明有同步。
- 所有 `_choice_reach_cur` 的呼叫端都已改成新簽名,`_choice_cov_robo`、`_choice_cov_pkg_dirs`、`_CovBase` 沒有殘留引用。

總結:最高等級是 major(1 條 major、1 條 minor)
