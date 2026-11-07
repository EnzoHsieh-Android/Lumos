severity: minor

我先逐條核對第二輪通才席 F1 到 F3,再找新問題。

**F1(lint-new 內部失敗被記成綠)已修好。**
- 我讀了 `_lint_wt_unready`、`_lint_wt_pairs`、`_lint_wt_blobs` 三條失敗路徑,都回 `failed`。
- `_lint_new_wt_json` 對不認得的值也落到 `failed`。
- 我另外確認 `env-unavailable` 這條 rc3 在 JSON 層不是 `not-checked`,會落成 `failed`,鉤子記 error。
- `python3.14 scripts/test_lumos.py -k slh_r2` 是 30 passed。
- 只留下下面新的 F1 和 F2。

**F2(`check-graph-sync.py` 的無用匯入 `time`)已修好。**
- 檔內只剩第 743 行的 `import time as _tm`。
- 我對三支鉤子跑 `ruff --select F`,只在 `stop-lint-hook.py`、`impact-hook.py` 驗到通過。
- `check-graph-sync.py` 有幾個舊的 F841、F541,不是這次造成的。

**F3(`new_only` 參數)已修好。**
- 我 grep 了 `scripts/`,沒有任何呼叫端帶 `new_only`,只剩 docstring 的歷史說明。

F1
severity: minor
blocking: 否
標題:`_unchecked_kind` 遇到 `unchecked_kind` 不是字串時會丟 TypeError。這違反它自己寫的「值不認得一律記 error」,也違反筆記裡「欄位缺或不認得記 error」的說法。
引句:「    return {"deliberate": None, "timeout": "timeout"}.get(data.get("unchecked_kind"), "error")」
失敗情境:以字典查表時,值如果是 list 或 dict,查表本身會丟 `TypeError: unhashable type`。
- 輸入→實際→預期,我實跑過:`_unchecked_kind({"unchecked_kind": ["x"]})` 和 `{"unchecked_kind": {"a":1}}` 都丟 TypeError,預期回 `"error"`。
- 例外沒人接,會一路穿出 `_on_stop`。`_hookevent.guard` 記一筆 error 後把例外再丟出去,鉤子帶 traceback 結束。
- 這樣少了「這回合沒檢查到」那行 stderr 提示,也不是「記 error、rc0」的行為。
- 新增的 `t_slh_r2_unchecked_field` 只測了缺欄位和 `"whatever"` 這種字串,沒測非字串。
- 目前只有版本錯位或別的程式寫出這種 JSON 才會走到,所以列 minor。
- 修法:先 `isinstance(k, str)`,否則回 `"error"`。
佐證 file: `scripts/hooks/claude/stop-lint-hook.py:374`

F2
severity: minor
blocking: 否
標題:筆記宣稱「判定裡沒寫明的 rc3 一律 failed」,但判定函式本身對沒寫明的 `not-checked` 預設成 `deliberate`(記 ok),方向相反。
引句:「判定裡沒寫明的 rc3 一律 failed」
失敗情境:
- `_lint_new_wt_verdict` 結尾是 `if out["status"] == "not-checked" and not out.get("unchecked_kind"): out["unchecked_kind"] = _LINT_WT_DELIBERATE`。
- 目前進來的只有 `report_only` 和 `sep_emptied`,剛好都是刻意不查,所以現在沒錯。
- 但日後有人在判定裡新增一條 `status = "not-checked"` 的失敗路徑而忘了寫 `unchecked_kind`,就會被這行預設成「刻意不查」,鉤子記 ok。
- 這正是 r2 通才席 F1 要消除的「靠推測記成綠」。只有 JSON 層(`_lint_new_wt_json`)的預設是 `failed`,兩層方向不一致。
- 這算修的深度不夠:只改了鉤子,沒把預設方向也翻過來。
- 修法:判定函式末尾不補預設。把 `report_only` 和 `sep_emptied` 兩處各自明寫 `deliberate`,沒寫的交給 JSON 層落 `failed`。
佐證 file: `scripts/lumos:40608`

F3
severity: minor
blocking: 否
標題:計劃的依據表說範圍 2 第 5 條有寫 `unchecked_kind`,但那一條的正文這次沒改,仍只寫「rc3 印一行」。
引句:「範圍 1 第 8 條、範圍 2 第 5 條」
失敗情境:
- 依據表新增那一列指向「範圍 1 第 8 條、範圍 2 第 5 條」。
- 範圍 2 第 5 條在計劃裡仍寫「其他(含未捕捉例外的 rc1、空輸出、rc3)一律不擋;rc3 印一行到 stderr」。
- 這一條沒說 rc3 要照 `unchecked_kind` 記 ok、timeout 或 error。
- 下一個只讀範圍 2 的人會看不到這個行為。
- 行為本身在 [[Systems/回合結束寫法檢查]] 有寫,所以只是計劃內部對不上。
- 修法:在範圍 2 第 5 條補一句,或把依據表那格改成只指向範圍 1 第 8 條。

總結:最嚴重是 `_unchecked_kind` 對非字串值丟 TypeError(F1)。我沒找到會讓錯誤行為在正常路徑上線的缺陷,會擋 0 條。

補充:
- 我讀過的其他改動(SIGINT、SIGHUP 共用收尾、`finally` 補收 lint-new、`OverflowError` 與 `RecursionError` 補接、`_mark_event` 三份逐字複本)沒找到新破口。
- 筆記引用的 `t_*_r2_*` 測試名我逐一比對,`scripts/test_lumos.py` 裡都有。
- 我只實跑了純函式,沒在 `/tmp` 建任何暫存檔。
