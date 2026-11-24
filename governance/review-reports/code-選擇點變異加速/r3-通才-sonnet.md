severity: major

警告鎖檔 `baf3be87…json.warming` 不存在(`ls` 回 No such file),沒有鎖要處理。這份修補差異只動筆記與測試,`scripts/lumos` 在修前、修後兩端相同(binding 的 attribution_limits 與 `git show` 兩版比對一致),所以八角度裡逐行、被刪行為、跨檔追蹤、效率、修的深度都落在新增的測試與筆記上。

## 發現

### 1. 新增的端到端案例在並行負載下大量隨機紅,跟筆記自己登記的卡線 PITFALL 同族
severity: major
blocking: 是
引句:「呼叫端不帶剩下時限 → 上限 30,快篩睡滿 6 秒寫出 end 而紅。」
引句:「m._CHOICE_MERGE_UNIT_SECS = 0.5」
引句:「merge=mm._KillMerge(_ckm_time.monotonic() + 3, 2)), log=log, floor="30")」

file: `scripts/lumos:28819`(`_choice_merge_screen_cap`)
file: `scripts/lumos:28972`(`_kill_merge_singles`)

失敗場景:
- 合併能不能啟用,取決於開跑那道「剩下時限 ≥ 支數 × 單價 × 1.5」的門。這案單價是 0.5、三支,門檻是 2.25 秒。
- 總時限只給 3 秒,絕對餘裕約 0.75 秒。這 0.75 秒要涵蓋 `cmd_guard_kill` 建隔離工作樹、量單支基準之前的所有開銷。
- 機器一忙,時限先被吃掉,這個平台組就不合併。快篩從沒開跑,斷言 `[one, "1", "start"] in rows` 因此紅。
- 這跟同份修補寫進 guard-kill.md 的 PITFALL 是同一個根因:「固定開銷不隨比例縮小,絕對餘裕不夠」。該 PITFALL 只處理了重估測試那支,新加的這支又犯一次。

重現:在 after 版(744f7b6d6)的 worktree 同時開 4 份 `python3.14 scripts/test_lumos.py -k t_choice_kill_merge_screen_cap`。
- 結果:3 份紅、1 份綠。
- 紅的訊息都是「r2 通才 #1 … 快篩有開跑、被剩下時限收掉」。
- 紅時 rows 是 `alphaCase base start/end`,接著 `alphaCase 1 start/end`,表示快篩沒走合併道,退回逐支。
- 單獨跑同一指令 3 次全綠(各 6 passed)。

變異驗證(單跑,證明這案本身有牙):
- 把 `_choice_merge_screen_cap(m_el, c.floor, mg.remaining())` 的第三個參數改成 `1e9`,這案如預期紅。
- 把 `mg.remaining() < sum(measured)` 改成 `<=`,`t_choice_kill_merge_budget_edge` 的剩 6.0 秒那案如預期紅。
- 所以測試的判準本身是對的,問題只在餘裕太小造成的誤紅。

歸因:有證據的修復回歸。這支案例是本輪修補才加的,修前版沒有它(`git show 02fd3bdf5` 的 test_lumos.py 沒有「r2 通才 #1」那條斷言),修前不存在,所以不能「修前綠修後紅」比較。誤紅的機制由本修補新增的測試引入。
- 修前:不存在,無法比。
- 修後:4 並行 3 紅 1 綠、單跑 3 次綠。這是同一指令的兩次以上重跑,不是單次不穩。

修法方向(只供編排者參考):把 `_CHOICE_MERGE_UNIT_SECS` 設得更小,或總時限拉到至少比門檻多 5 秒以上,再讓快篩睡更久。這跟 PITFALL 自己寫的「保留絕對餘裕」一致。

## 已驗主張(同一案例證據)

1. 快篩上限接上剩下總時限(測試有牙)。
引句:「快篩在剩下時限(約 2 秒)到時被收掉、沒有 end;」
- 輸入:端到端案例。
- 預期:呼叫端改成不帶剩下時限就紅。
- 修後:單跑通過;把呼叫端第三參數改 `1e9` 後紅(上述變異)。
- 修前:無此測試,未判定。

2. 重估卡線。
引句:「直接呼叫 _kill_merge_singles,單支耗時固定 2 秒(換掉 _kill_run)、剩下時限固定,不睡。」
- 輸入:已量 2 秒、剩兩支。
- 預期:剩 6.0 秒量齊,剩 5.99 秒收手。
- 修後:`-k t_choice_kill_merge_budget_edge` 2 passed。
- 變異:把 `<` 改 `<=`,6.0 那案紅。
- 修前:無此測試,未判定。
- 這支案例沒有睡眠,不受負載影響,穩定。

3. 筆記與程式對得上。
引句:「合併快篩與合併基準的上限都不超過剩下的總時限(最少 1 秒)」
- 對到的程式:`_choice_merge_screen_cap` 的 `max(remaining, 1.0)`、`_kill_merge_base` 的 `max(mg.remaining(), 1.0)`。
- 做法 1 說 `_gradle_test_module` 只共用 `_gradle_module_parts`,回傳不變。`scripts/lumos:77436` 的 `_gradle_test_module` 呼叫 `_gradle_module_parts`,與筆記一致。

4. 簽章檔。`anchor-baseline.json` 只換指紋與簽核說明,列為 archive_only,不是行為。

## 三問回答

① 原問題的修復效果:快篩上限接線與重估卡線兩個行為,各有一支能翻紅的測試(上面變異已驗)。接線那支有誤紅問題(發現 1)。
② 修補處的正常、錯誤與相鄰呼叫路徑:修補不動產品碼,相鄰路徑(單支基準、逐支流程)行為不變。這部分只能靠兩端 `scripts/lumos` 相同來推。我沒另外跑 `-k t_choice_kill` 全組。
③ 新發現的同一案例修前修後:發現 1 的案例修前不存在,不可比。修後的並行紅是兩次以上重跑的結果(4 並行 3 紅,另單跑 3 綠)。

## 未驗範圍與輕微觀察(不計 finding)

- 計劃 S7 的文字是 `min(max(S × 2, 下限), 剩下的總時限)`,程式的合併基準上限是 `max(剩下總時限, 1)`,下限 1 秒沒寫進 S7 條款。這是精度問題,不影響操作,依派工說明歸 minor 且講不出失敗場景,不另立 finding。
- 沒有重跑 `-k t_choice_kill` 全組(編排者已跑 226 過 0 紅,屬他們的證據,我沒有獨立重現)。

總結:最高嚴重度 major
