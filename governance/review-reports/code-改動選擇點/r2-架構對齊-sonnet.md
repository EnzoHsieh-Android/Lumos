severity: minor

## a1 選擇點的 AI 放行不再出現在開場提醒
severity: minor
blocking: 否。結構跟鄰居不同,但健檢(doctor)那一段仍會印,沒有整條功能壞掉。

- **哪個輸入:** 放行檔 `.lumos/lint-waivers.json` 裡有一筆 `choice:<檔>:<指紋>`,`origin` 是 `ai`、還沒人看過。
- **走到哪:** `_lint_waivers_ai_pending`,再到開場提醒(`code-loop check` 那條路)。
- **壞在哪:** 鄰居情境段(`kt-situation:`)有自己的 `lv["ai_pending_situation"]`,也有自己的一行提醒。修補把放行檔拆成三份,但 `_lint_waivers_ai_pending` 只接 `lint` 和 `sit` 兩份,選擇點那份兩邊都不算。開場提醒因此看不到選擇點的 AI 放行,只有 doctor 還印。
- **預期 vs 實際:** 預期照情境段的做法,選擇點也有自己的計數欄位和提醒行。實際是修前這筆算進 `ai_pending`(標籤寫錯,但看得到),修後是 0。
- 引句:「`lint, sit, _choice = _lint_waivers_split(cur)`」
- 引句:「`return sum(1 for it in (sit if situation else lint).values() if _lint_waiver_ai_unacked(it))`」
- file: `scripts/lumos:79190` 與 `scripts/lumos:79191` 只設兩個欄位 `ai_pending` 和 `ai_pending_situation`;`scripts/lumos:80321` 到 `80324` 只印這兩行提醒。
- **歸因:有證據的修復回歸。** 我用同一支探針,在兩版各讀一個只含一筆 AI 放的 `choice:` 放行的放行檔:

| 版本 | `_lint_waivers_ai_pending(d)` | `situation=True` |
|---|---|---|
| 修前 7826895c1 | 1 | 0 |
| 修後 4dd1ed800 | 0 | 0 |

  修後 doctor 仍印「選擇點放行裡 1 條是 AI 放的、還沒人看過」。這是探針直接呼叫 `_lint_waivers_doctor_bits` 的結果,沒有跑完整 doctor。

## 三問

**1. 分層與依賴方向:跟鄰居一致。**
- 主線判斷改走共用的 `_note_reread_mainline_names`(`scripts/lumos:77490` 附近的 `_choice_range`),跟 `_push_mainlines` 同源。
- 讀 git 改走 `_lens_git_dl`(`scripts/lumos:69325`),跟 `_git_timeout` 的時限做法一樣。
- 起 ast-grep 子程序仍走 `_choice_sg_run` 到 `_lint_spawn`(`scripts/lumos:76953`),沒有直呼底層。
- 推送前新增的測試檔物件編號查詢,時限用 `_CHOICE_GOV_BUDGET`,跟同檔 `_choice_push_ledger` 與 `_choice_push_waivers` 各自開一份時限的做法一致(`scripts/lumos:78276`、`78296`)。
- 寫帳新增的 `_choice_gate_event` 疊在 `_gate_event_or_warn` 和 `_gate_event_fit` 上,跟 `_drift_m1_fit`、note-reread 的每個閘一支包裝的慣例相同。
- `_choice_scan` 回傳改成三個值,呼叫端(`_choice_compute` 和兩支測試)都已跟上。`_choice_err_lines` 在程式裡已無殘留引用。

**2. 命名與錯誤處理:除 a1 外一致。**
- `choice-points` 的 rc 3 符合它自己 docstring 寫的「3 ast-grep 不在或掃描算不出來」(`scripts/lumos:77539`)。
- 寫帳失敗訊息沿用 `_gate_event_or_warn` 的 `telemetry-write-failed`,再補一句「沒記到的是什麼」。
- `check.py` 的 `sg_arg` 只有 `kotlin-android` 一份 check.py,沒有別處重複。

**3. 第二種做法:沒有 major 級的新增。**
- `_count_overlapping` 是專案第一支重疊計數,沒有既有同功能函式。我 grep 確認同族的 `.count(old)` 都已換掉,剩下只有 `\n` 計數和 `verdicts.count` 這類不相關的用法。
  - 證據:`hay="x\nx\nx\nx\nx\n"`、`needle="x\nx\nx\n"`,修前 `str.count` 回 1,修後 `_count_overlapping` 回 3。
- `_choice_err_cover` 和 `_choice_iv_cover` 是新的二分區間判定。既有 `_in_spans`(`scripts/lumos:4589`)假設區間不重疊、只判點,而乾節點區間會巢狀、判的是區間包含,不能直接重用。我不標。
- 逐檔掃描的子程序管理沒有另起一套,只是在 `_choice_scan` 迴圈裡多呼叫 `_choice_scan_one`。
- 測試檔物件編號查詢本來就在(修前就有 `_choice_test_blobs`),修補只是延伸它並改成共用 `_lens_git_dl`。

## 已驗的正向主張

- **`check.py --catalog-only --sg /nonexistent/sg`:** 修前只印「型錄問題 0 個」,完全不提 `--sg`。修後多印「選擇點規則樣本:沒檢查到(--sg 給的 /nonexistent/sg 不能執行)」。
- **修後 `-k choice_scan`:** 7 個通過、0 個失敗,包含 `t_choice_scan_per_file` 和 1500 條呼叫的真 ast-grep 案例。
- **同一個 `--point` 流程裡的兩條寫帳:** 選擇點那條(`_choice_gate_event`)把「沒有治理帳」當成沒寫失敗,情境段那條(`scripts/lumos:78712`,`_gate_event(...) is not True`)把它當寫失敗。我讀到差異,但選擇點流程本身要讀治理帳,沒有帳就先 rc 2,所以我給不出具體失敗場景,沒標。

## 未驗範圍

- 完整 doctor、開場提醒的整體輸出沒跑,a1 的 doctor 那一半只驗到 `_lint_waivers_doctor_bits`。
- 沒對全套跑測試(派工詞禁止),也沒跑 `-k lint_waive`、`-k choice_push` 等其他子集。
- 知識圖譜筆記只快速掃過,沒逐條對照寫法。
- 固定席節點這次沒附(鏡頭計算超時),我沒有補算。

臨時目錄 `/tmp/lumos-seat-work/code-改動選擇點/架構對齊-sonnet/` 仍在,按規定由編排者收貨後刪。

最嚴重:minor;blocking 共 0 條
不對齊共 1 條,其中 major 0 條
