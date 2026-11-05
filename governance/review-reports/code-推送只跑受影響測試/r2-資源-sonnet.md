severity: minor

我只審了範圍內的程式、測試與說明,卷證不在內。對 `4cc9c425..9918ed76` 與 `d8134d85..9918ed76` 兩段差異逐 hunk 讀完。沒有會擋的問題,只有一條測試餘裕的疑慮。

severity: minor
**
**blocking: 否**
標題:拆出新測試後,原測試 `t_prepush_docs_and_light_run_subset` 的餘裕仍不足 3 倍
引句:「從 t_prepush_docs_and_light_run_subset 拆出(那支加這段會超過每支 180 秒上限)。」
file: `scripts/test_lumos.py:48409`
- 在 push-subset 頂端跑 `python3.14 scripts/test_lumos.py -k t_prepush_docs_and_light_run_subset`,最慢段印出 204.3 秒,上限 360 秒,餘裕 2 倍,工具標 ⚠ 餘裕不足 3 倍。
- 360 秒的覆寫在 `4cc9c425` 就已存在,所以這不是這輪修補新加的上限。
- 拆出之後它仍超過一般的 180 秒。慢機器若比這台慢 1.75 倍就會逾時,把推送前閘擋下。
- 這是測試成本問題,不會做出錯的行為。歸因:有證據的原有負擔,只是修補沒把它降到餘裕內;修前耗時我沒量,未判定是否改善。

**逐條答鏡頭**

1. **子程序收不收得掉:沒有殘留路徑。**
   - `_pitfalls_pushed_mainline` 走到的 `_diff_range_ends` 與 `_note_reread_mainline_names`,內部的 git 子程序都用 `subprocess.run(timeout=…)`。
   - `subprocess.run` 逾時或被 Ctrl-C 打斷時會先殺掉子程序再回傳,不會留孤兒(同樣是呼叫鏈上讀碼判斷,未跑實驗)。
   - 掛鉤新的 `_down` 段沒有新增子程序,只有原本就有的 `grep` 與 `python -c`。
   - pitfalls 呼叫的行為與原本一樣,每個 ref 多一次 pitfalls(`--pushed-ref` 參數只是多帶),沒有新增背景程序。
2. **時間預算:方向保守。**
   - 10 秒預算只用在 `_note_reread_mainline_names`,內部每次 git 取「20 秒與剩餘時間」的較小值,剩餘為 0 就不跑。
   - 逾時或查候選失敗時,集合退成只含 `main`、`master`。
   - 因此預設分支不叫 main/master、遠端 HEAD 也查不到時,推該分支會被當功能分支降成子集。這個行為沿用既有的集合設計(計劃已審),不是修補引入的。
   - 多 ref 推送是逐 ref 各算一次;任一 ref 是主線就整次全套,測試 `t_prepush_feature_branch_mixed_with_main` 綠。
3. **記憶體與二次方:沒有新增。**
   - 新碼只讀一份 pitfalls JSON,並多做幾個 `grep -q` 比對,沒有整本帳或整份大檔載入。
   - `_test_suite_for_range` 只多回一個布林值。
   - 單次 git 子程序輸出沒有二次方結構。
4. **測試成本**(`python3.14 scripts/test_lumos.py -k <名>` 實測,本機):

   | 測試 | 最慢段耗時 | 餘裕 |
   |---|---|---|
   | `t_prepush_docs_and_light_run_subset` | 204.3 秒(上限 360 秒) | 2 倍,⚠ |
   | `t_prepush_feature_branch_already_light` | 24.1 秒(上限 180 秒) | 7 倍 |
   | `t_prepush_feature_branch_*` 另外五支 | 34.9 到 40.0 秒 | 4 到 5 倍 |

   - 兩次 `-k` 跑完分別是 18 passed 與 3 passed;`-k t_prepush_feature_branch` 另跑,20 passed、0 failed。
   - `t_pitfalls_` 系列我另啟了一次背景執行,其輸出檔內容只有 `t_prepush_feature_branch` 那次的結果,所以 `t_pitfalls_pushed_mainline`、`t_pitfalls_suite_computed` 的耗時沒量到。
   - 暫存目錄:跑完後 `/tmp` 底下沒有 `gctl-run`、`ppfb`、`prepush` 開頭的殘留(`ls /tmp | grep -c` 得 0)。我沒建任何自己的臨時目錄,不需要刪。
5. **pitfalls manifest:** 這輪沒有內建題,併發類題判範圍外、標誤報,沒做別的。
6. **圖譜鏡頭:沒做。** 派工詞標明固定席節點算不出來,我沒用 `scripts/lumos show` 讀那 8 篇,所以逐篇判定未驗。

**修補鏡頭三問**

- **原問題的修復效果:**
  - 已驗:`_down` 兩條降級路徑共用同一段,原本判 light 的功能分支不印降級行。
  - 同一案例:`t_prepush_feature_branch_already_light`。輸入是 push-check 判 light 的功能分支推送,預期跑 docs 加 keys 兩片、不印「推功能分支:」。
  - 修後結果是 3 條斷言都綠。
  - 修前我沒另取版本跑,所以只能說修後行為成立,修前是否紅未判定,不能歸因。
- **修補處的正常、錯誤與相鄰呼叫路徑:**
  - 推 main、混推 main 與功能分支、`suite_computed` 為 false、舊版 lumos、`light_ok` 為 false、自主迴圈旗標,這些路徑的對應測試修後全綠。
  - `computed` 改成每條回傳都帶,讀端直接索引 `_sr["computed"]`,漏帶時 pitfalls 會失敗、掛鉤因拿不到 JSON 而照全套。這是保守方向,測試 `t_pitfalls_suite_computed` 有守。
  - 我只核對了這幾條,未自行對修前版本跑同一批輸入。
- **新發現的同一案例在修前、修後:** 唯一一條新發現是上面那條 minor。修前的耗時我沒量,未判定。

**未驗範圍:** 圖譜 8 篇固定席節點;修前版本的對照執行;慢機器上實際逾時的重現。

相關路徑:
- `/Users/enzo/orca/workspaces/lumos-toolchain/push-subset/scripts/hooks/pre-push`
- `/Users/enzo/orca/workspaces/lumos-toolchain/push-subset/scripts/lumos`
- `/Users/enzo/orca/workspaces/lumos-toolchain/push-subset/scripts/test_lumos.py`
