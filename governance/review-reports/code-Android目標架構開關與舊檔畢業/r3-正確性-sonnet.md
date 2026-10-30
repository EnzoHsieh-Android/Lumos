severity: clean

我在固定提交 1bb9609b8 上讀完整份 diff,並跑了 `python3.14 scripts/test_lumos.py -k arch_target`,182 案例全過。沒有找到 major 以上的問題,也沒有 minor 以上的新 finding。

## 修補鏡頭:三問

**①原問題的修復效果,有沒有行為證據。** 有,是修後的測試過,不是修前紅修後綠。

- 修前證據沒另存,配對案例記未判定,我也沒有重跑修前版。
- 以下三組都在固定提交上跑過,全綠:
  - 沒宣告只有清單時,doctor 印出清單摘要(`t_arch_target_legacy_doctor_lines`)。
  - git 列出 NFD 檔名、清單寫 NFC 時,「已不存在」數成 0。
  - 清單混了非字串元素時,`_arch_legacy_at` 回 `(set(), "unreadable")`,不丟例外(H2)。
- 說明行的 A2(少了 2 行、其中 1 支有改動)和 L(起點沒清單、分支新增清單,印「多了 1 行」)也過。
- 我另做了一次破壞試驗:把 `_arch_legacy_check_lines` 裡的退回路徑改成 `pf_targets = {}`,`t_arch_target_graduate_check_note` 仍全過。見下方 ③ 的 minor 備註。

**②修補處的正常、錯誤與相鄰呼叫路徑。**

1. 拿掉 `not h_warns` 條件後,不存在「宣告讀出規則相同、但其實有警告」的輸入。
   - 依據是 `scripts/lumos:57311` 的 `_arch_targets_config`:所有警告分支都回 `[]` 規則。
   - `_arch_targets_at` 在 git 失敗、讀不懂時同樣回 `[]` 規則。
   - 呼叫端只有在 ref 版規則非空時才會問畢業(`_arch_legacy_apply` 先判 `targets` 非空,`_arch_legacy_check_lines` 先判 `rules` 非空)。
   - 所以有警告就是 `h_rules == []`,不等於非空的 `rules`,不會畢業。這個條件是多餘的,拿掉不弄壞相鄰路徑。
2. `_arch_legacy_check_lines` 改吃 `pf_data` 後,各種呼叫情況都印對。
   - 有 `arch_alignment.targets`:說明行用分級已算好的目標檔,而 `pf_data` 與 `rng` 同源。
   - 唯一換掉範圍的路徑是 `scripts/lumos:67470` 一帶的重跑,它同時換 `disp_data` 與 `disp_range`,所以兩者仍一致。
   - 重跑失敗時,`disp_data` 與 `disp_range` 都退回 `data`、`diff_range`,一樣一致。
   - 範圍為 `None`(分支頂端已在主線上)時,兩者都不進來。
   - `pf_data` 為 None 或沒有 `arch_alignment` 鍵:程式走退回路徑,重算 `_arch_target_split`。
     - 這時只拿 `keep & judged` 數交集,所以沒扣清單的重算結果也一樣。
     - 畢業的檔本來就會被審,數字不變。
3. 判斷畢業的來源只有 `_arch_legacy_graduation` 一份,`_arch_legacy_apply`(推送前分級、兩條派工鏡頭)和說明行共用,沒有各算一遍。
4. 說明行用的 `pf_targets` 是第二份衍生資料,但同一個 `_arch_legacy_apply` 先算好,再被「分級輸出」與「說明行」各讀一次。
5. 分級沒跑或 `pf_data` 缺鍵時,只退回不扣清單的重算,對 `keep` 的交集結果不變,不會印錯。
6. `_arch_legacy_doctor_lines` 在函式內轉 NFC,且只在清單讀得懂時才轉。
   - 列檔失敗傳 `None` 仍走「算不出」。
   - 所有呼叫處(`scripts/lumos:57574` 與測試)現在都傳 list 或 `None`。
   - 函式內 `nfc` 對 list、set 都能用,沒有留舊簽章的呼叫。
7. 其他我走過但沒找到洞的輸入:
   - NFC 與 NFD 混寫。
   - 分支新增清單、起點沒有清單。
   - 沒宣告只有清單。
   - 宣告一字不改但清單讀不懂(畢業為空,說明行不印)。

**③新發現的同一案例,修前與修後各是什麼結果。** 無新 finding,不適用。

唯一的備註是 minor 以下,不標 finding:`_arch_legacy_check_lines` 的退回路徑沒有任何測試走到,我把它換成 `{}` 後測試照綠。它在正常流程裡幾乎走不到,因為 `pf` 沒有 targets 時,重算也會是空,所以不影響行為。

## 其他鏡頭

- 逐 hunk 讀 diff,涵蓋邊界組合、NFC/NFD、沒有主線、修補輪範圍、沒有宣告,沒有找到會判錯的輸入。
- 不可逆、寫一半、時間:不適用。這次只印說明行與 doctor 提醒,不寫檔。
- pitfalls manifest:這次沒有要答的題,略過。
- 角色卡:沒附,略過。

## 固定席逐條判定

- `Issues/code-loop守衛main-direct盲區`:不影響。改動不碰守衛的 main-direct 判定,只動目標架構基準的說明行。
- `Systems/lumos-cli-read` ★INVARIANT★(search 預設排除 superseded 但不排除 stale):不影響。這次沒有碰 search。
- `Systems/pitfalls-code-loop`:不影響。`arch_alignment` 的輸出形狀不變,只是多一個讀者讀它的 `targets`。
- `Systems/arch-alignment-lens`:不影響。畢業判定仍然是同一份,這次只拿掉多餘條件並調整說明行來源。
- `Systems/design-loop` ★INVARIANT★(處置閘第五步,審材必須是 .md 計劃):不影響。改動不碰處置閘,設計審派工鏡頭的讀法也沒變。
- `Systems/測試假綠形態` ★INVARIANT★(還原翻紅釘須配前置斷言):不影響。新測試 L、H2 都附前置條件(L 檢查 `out_l`,H2 直接斷言回傳值),也是先紅後綠的釘。
- `Systems/guard-kill` ★INVARIANT★(rc 優先序、`--json` 純度):不影響。沒有碰 guard kill。
- `Systems/reversibility-governance-ledger`:不影響。沒有新增不可逆動作。
- 其餘只列名的節點:不影響。diff 只涉及 `scripts/lumos`、`scripts/test_lumos.py` 與一篇計劃筆記,沒有改它們的行為。

我在審查席臨時目錄建的暫存(clone 與 lumos.py 拷貝)已刪。

最嚴重等級為 clean
