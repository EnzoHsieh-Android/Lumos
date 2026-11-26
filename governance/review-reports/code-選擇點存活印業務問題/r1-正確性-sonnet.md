severity: minor

沒有 blocker 或 major 的發現。我讀完整份 diff,並追了它碰到的 repo 程式碼。我沒有跑新測試,也沒有跑任何重現。

**發現 1:合併快篩判存活的路徑沒有被測試蓋到,改壞它測試照綠**
- 位置:`scripts/lumos` 的 `_choice_points_line`,以及測試 `t_choice_survivor_why`。
- 決定印不印的那行是 `wl = _choice_why_line(mut.get("why")) if st.startswith("存活") else ""`。
- 帳上狀態函式也可能回 `"存活(合併快篩判)"`。實際跑起來存活多半是這個狀態,因為合併快篩預設開。
- 測試裡 choice-points 的斷言是 `cl[j2].endswith("存活")`,只走到假 repo 裡純 `存活` 的情況。
- 改壞後測試照綠的具體變異:把 `startswith("存活")` 改成 `== "存活"`。這樣合併快篩判存活的行在實際使用中就不印為什麼欄,但新測試的每條斷言照樣通過。
- 規格本身只講了一半:WHY 筆記與 docstring 寫「是存活時」,diff 的說明寫「以存活開頭」。測試照的是前者。
- 這個缺口代價低,因為整個改動只換輸出。
- 引句:「wl = _choice_why_line(mut.get("why")) if st.startswith("存活") else ""」
severity: minor
- blocking: 否

**查過、沒問題的項目**

- **空值與佔位字:** `_choice_why_line` 處理 `None`、`""`、只有空白、`—`、`(無)`。單元測試都有蓋到。
- **換行與控制字元:** `" ".join(split())` 會收掉所有空白類字元,包含 `\x1c` 到 `\x1f`、`\x85`、`\u2028`。其餘的 C0/C1、雙向覆寫與零寬字元再由 `_kill_esc` 跳脫。檔案:`scripts/lumos:26905`。新輸出這一行沒有終端控制字元的洞。
- **長度:** 字串沒有截斷。型錄由 repo 自己維護,我講不出一個會壞的輸入。
- **缺 `why` 鍵:** 兩處呼叫端都用 `.get("why")`。`row.get("why")` 一定取得到,因為列字典建出來就帶 `why` 鍵。檔案:`configs/ast-grep/kotlin-android/check.py:1457`。
- **整個字典被別處使用:** 我 grep 過有沒有地方把壞法字典序列化、雜湊或寫進帳與快取。碰到它的只有逐欄取值的帳事件,它自己組 `extra`,見 `scripts/lumos:79224`。新的 `why` 鍵不會漏進帳、指紋或 identity。
- **帳上狀態字樣:** `存活(合併快篩判)` 與 `存活` 符合開頭判斷。`已放行`、`過期`、`跑不出結果`、`沒跑` 不印為什麼行。已放行的存活不印為什麼行,跟「存活時」的敘述一致。不唯一與沒有壞法的路徑在碰到為什麼之前就回去了。
- **型錄漂移:** choice-points 印的是型錄當下的 `why`,不是帳上那次的。帳不存 `why`,所以型錄一改立刻反映。對顯示用的提示來說合理,沒有狀態因此壞掉。
- **冪等:** 純輸出,不寫任何狀態。
- **推送閘與放行預判:** `_choice_push_*` 不呼叫新函式,改動只多印輸出,閘不受影響。
- **重構等價:** `_choice_points_line` 與原本內嵌的程式逐分支相同。主迴圈改成 `print("\n".join(...))`,單元素清單的輸出跟原來一樣。
- **角色卡:** hook 沒附卡,略過。

**圖譜固定席逐條判定**
- `lumos-cli-read`(search 排除 superseded 節點):不影響。這次沒碰搜尋程式。
- `guard-kill`(rc 優先序與 `--json` 純度):不影響。新的印出在 `_ChoiceKillRun.finish`,寫到 `sys.stdout`(`scripts/lumos:79199`),沒碰 rc,也沒碰 `cmd_guard_kill` 的 JSON 路徑。
- `pitfalls-code-loop`、`loop-convergence-recording`、`design-loop`:不影響。沒有閘或帳邏輯的改動。
- `測試假綠形態`(還原翻紅釘要配前置斷言):新測試先斷言存活那行的列號(`i2 is not None and "存活" in lines[i2]`),再斷言下一行,前置條件成立。
- `bound-tests-gate`、`lumos-cli-lifecycle` 與其餘只列名的節點:不影響。
- `規格閘` 的 WHY 行 `[出處:]`、`[因:]`、`[test:]` 都有填。
- `anchor-baseline.json` 只是為新增的測試檔更新雜湊與說明。

總結:這份報告最高等級是 minor
