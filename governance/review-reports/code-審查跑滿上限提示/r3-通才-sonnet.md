severity: clean

已看,無:
- `_SEV_ORDER` 現在整支檔只定義一次(scripts/lumos:7126),值為 `{"clean":0,"minor":1,"major":2,"blocker":3}`,跟被拿掉的那份(patch 顯示原提交版重複定義的那份)逐值相同;檔案裡所有使用點(6746/7232/7324/7421-7422/7436/7541/7544/7546/7964/7968/7972/8315/8504/30831)都還能解析到同一顆常數,沒有孤兒依賴指向已刪那份。6746 那處雖在檔案較早的行號用到 `_SEV_ORDER`,但那行在函式體內,Python 是呼叫時才查名字,不受定義搬到後面影響,已用測試證實不受影響。
- `_disposal_round_groups` 搬家(18177 行)後的函式本體,拿 patch 裡「-」區塊與「+」區塊逐行比對,兩邊文字逐字相同(只是位置換了),沒有夾帶內容變動。搬去的新位置在 `_disposal_security_step` 之前,呼叫點(`_cap_hint` 於 7409 行、處置閘本體於 18425 行)在執行期都能正常解析到它(同一模組,呼叫時機晚於整檔載入完畢),`-k cap_hint`/`-k disposal`/`-k loop_next` 三個子集全線通過(34+177+75 = 286 全綠)。
- `_disposal_round_groups` 裡「r3 修(3 席重疊)」那句註解宣稱「寫側已擋新寫入」,查了寫入端(scripts/lumos:7638-7639 `round_id.startswith("__")` 直接擋),確有此擋,註解沒有寫錯。
- `_cap_hint_print` 的 try/except 吞例外修法:用拆修法驗證過——把 try/except 拿掉重跑 `t_disposal_cap_hint_fail_open`,會在 `_review_yield_round` 因 `refuted_set` 被改成整數而噴 `TypeError: object of type 'int' has no len()`,測試翻紅;裝回 try/except 後綠。確認這條測試真的接住了 r1 那顆 blocker,不是空氣測試。
- `_cap_hint_lines` 「提示行一律印」的修法:拆修法驗證過——把「一律印」改回舊的 `if h["at_cap"] or h["hint"] != "unknown":` 判斷,`t_cap_hint_breaker_total_folded` 立刻翻紅(斷言「S8 只有一輪的熔斷:文字同時有「判不了」與「拆小」」失敗,因為熔斷觸發但未到 cap、hint 又是 unknown 時舊邏輯不印提示行),裝回一律印後綠。確認這條也是真的接住修正目標,不是空氣測試。
- 「標籤只印段首」的格式改法(P 從 `"[cap-hint] "` 改成 `"  "`,第一行改用字面 `"[cap-hint] " + ...`)配的測試 `t_loop_next_cap_hint_appended_without_changing_phase` 已更新斷言檢查「找到第一個 `[cap-hint]` 開頭行之後的每一行都以兩個空格起頭」,跑過確認通過,格式行為與測試斷言一致。
- 工作目錄凍結 patch 與目前 repo working tree 的 `git diff -- scripts/lumos scripts/test_lumos.py` 做過 byte-for-byte 比對,完全相同,審查材料沒有被中途動過。
- 相關測試子集三個都全綠:`-k cap_hint`(34 passed)、`-k disposal`(177 passed)、`-k loop_next`(75 passed),無新增失敗。
