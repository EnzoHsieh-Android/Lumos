# code-派工鏡頭跨repo不再靜默 r3 收貨

席報告 2 份(正確性 1 條 minor、架構對齊 1 條 major + 1 條 minor),都是新席。派工標記終點寫完整提交編號,兩席都回報看到「lumos 自動附加」固定席段(9 篇、8 篇)。quote-check 兩份全錨;正確性席 refcheck 一筆 missing 是把行內指令 `scripts/lumos dispatch-lens <範圍> …` 當成路徑抽出,不是證據引用。

彙整 id:正確性 c1、架構對齊 a1–a2。載體:架構對齊席。輪內有 major → 全折、不放行任何一條。

## 機械重現

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| a1 | `grep -n _plain_label scripts/hooks/claude/*.py`;抽 ★注入框★ 區塊比 sha | impact/ci-status/lumos-entry/memory-sweep 四份逐字相同(41 行同 sha),派工鏡頭掛鉤沒有、另寫 `_clean_field` | HIT |
| c1 | 測試格 t_dispatch_lens_hook_fail_reason_notice:會談專案路徑帶 U+2028、\x0b、\x1e | 修前說明行原樣帶著三個字元 | HIT |
| a2 | 讀碼:`_dispatch_lens_fail` 印 `{"lens_fail": code}`,同指令 spawn_error/lock_error 列用布林鍵且帶 ensure_ascii=False | 形狀與參數不同 | HIT |

## 編排者另外發現(o1,一併折)

查證 a1 時發現派工鏡頭掛鉤 `_claim_codex_seat` 在領席超時那條路呼叫 `_frame_injected`,整支檔從沒定義它(`git log -S"def _frame_injected"` 對這支檔零筆;主線 Lumos/main 同樣)。最小重現:載入掛鉤、把 subprocess.run 換成丟 TimeoutExpired → `NameError: name '_frame_injected' is not defined`。框一致性守衛(t_all_injection_paths_are_framed_and_unified ③)把這支檔列在清單上,但找不到框常數就略過,所以沒抓到。屬原有漏查,兩席都沒報。

## 處置

全折(3 條 + o1):
- a1 o1:把同層掛鉤共用的 ★注入框★ 區塊(框常數、`_frame_injected`、`_plain_label`)逐字抄進派工鏡頭掛鉤;`_clean_field` 改成先過正典 `_plain_label`(cap=300)、外面多清反引號與 U+2028/U+2029/U+0085,正典本身不動(同 memory-sweep `_clean` 的既有寫法)。框守衛補一條「清單上每支檔都要有框常數」;新增 t_dispatch_lens_hook_claim_timeout_framed。
- c1:同上,控制字元由正典濾掉、Unicode 換行類在外層換空白;測試格用席位的輸入。
- a2:補 ensure_ascii=False;文件字串講明形狀為何跟布林旗標列不同(同一失敗的六個原因,一鍵帶代碼、掛鉤一處查表),順手把「三種」改成「六種」。

## 修補因果(regression-set)

三條都判「有證據的原有漏查」:a1 的手寫清理在 r2 修補前就在(r2 只是具名合併);c1 席位對修前 a8b38648 與修後 f74169f4 跑同一輸入、輸出相同;a2 修補沒碰 CLI 端(兩版 grep 結果相同)。regression-set = none。

## 先紅後綠

改測試後修碼前:claim_timeout_framed 2 條紅(NameError)、fail_reason_notice 2 條紅、injection_paths_are_framed 1 條紅(['dispatch-lens-hook.py'])。修後三支全綠(2/14/13 過)。
