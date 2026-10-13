severity: major

## 1. 「本週無法下結論或事故 → 通知」這一支沒有任何測試鎖住
severity: major
blocking: 是
引句:「    if this.get("inconclusive") or this.get("fatal"):」
- 重現:在 /tmp 複本把這行改成 `if False:`,再跑 `-k weekly_alert`、`-k probe_history_records_ids`、`-k autoloop_probe_alert`,結果是 18、3、5 全綠。
- 這支很重要。整批被排除時 `failed=[]`,`passed=0`,分母退回整批。舊規則 p≠n 會叫,拿掉這支後基準不足那條路 `bool(failed)` 為 False,整週靜默。
- 在現行程式上這支行為是對的:我手造 `inconclusive=True`、`passed=0`、`total=8` 的本週,得到 notify=True。問題只在沒有測試守它。
- 歸因:有證據的原有漏查。查證命令是上述複本突變加跑三組 `-k`。
- 同一個案例,修前(603b44b3)沒有這支規則,修後有,但仍沒有測試。

## 2. weekly_alert_line 遇到非 UTF-8 歷史檔會丟例外,違反「任何意外 → None」的承諾
severity: minor
blocking: 否
引句:「        raw = Path(history_path).read_text(encoding="utf-8").splitlines()」
- 重現:歷史檔內放 `b'\xe5\x82 broken\n'` 加一列正常週抽,呼叫 `weekly_alert_line(path, "2026-W42")`,得到 UnicodeDecodeError。
- 原因是這行只包 `except OSError`,UnicodeDecodeError 是 ValueError 子類,不在其中。
- 這個呼叫位於主程式的 `finally` 區塊內,例外會讓主程式帶 traceback 結束。結束碼從 3 變成 1,也印不出「保留最後副本」。
- 結果行已先印出,shell 又有 `|| true`,所以會退回舊規則,實際傷害有限。但 docstring 寫的是「讀不了歷史 → None」。
- 歸因:有證據的修復回歸。「判定行只在最後一列是這次才印」是這輪修補才加的,查證命令同上,重現可以當場翻紅。

## 3. 其餘保護層單獨移除也不翻紅(測試缺口,逐層結果)
severity: minor
blocking: 否
引句:「                or r.get("inconclusive") or r.get("fatal")):」
- 基準週排除 inconclusive、fatal 的過濾:改成 `or False` 後三組測試全綠。有儀器事故的過去週混進基準時,它的 ids 只含部分題目,會讓「這題上次有沒有過」判錯。
- 引句:「    if not rows or not _is_weekly_row(rows[-1]) or rows[-1].get("seed") != seed:」。刪掉 `seed !=` 的比對,三組測試全綠。測試用的是 runs=3 的列,走的是 `_is_weekly_row` 那一支。
- 引句:「    if w is None:」。把這個分支改成 `if False:`,三組測試全綠。這是 Wilson 載不進時的退路,沒有案例走到它。
- 引句:「    if cur and base and cur[1] < base[0]:」。`<` 改成 `<=` 測試全綠,邊界沒釘。
- 能翻紅的有:arm、runs 與整數檢查,它們的突變讓 `weekly_alert` 那組紅了。另外 Wilson 整段、`_ALERT_MIN_WEEKS` 改 2 或 4、ids 不寫入都會翻紅。
- 歸因:有證據的原有漏查。

## 判斷邏輯與 shell 介面:沒找到錯誤的路徑
- 基準週剛好 3 週:`len(same) < 3` 為 False,會走重複失敗與 Wilson 那條,正確。
- 同週多列:只留最後一列。
- 基準不足退路:`bool(failed)` 等價於舊規則的 p≠n,inconclusive 已在前面單獨處理。
- 判定行的位置:`weekly_alert_line` 只在 `--history` 且寫完歷史後才印,不是週抽種子回 None。
- shell:`[ -n "$verdict" ] && log ...` 在 `set -e` 下不會退出,測試的情境三與四涵蓋了空判定行。
- shell:`case` 只看 `週評通知:是` 前綴,整行放進 MSG。reason 含任何字元都沒有被拆字串。我在 repo 內 grep 沒找到其他地方依賴舊訊息「本週有題沒過」。

## 三問
- ①原問題的修復效果:同週重跑、無題號列、舊判準列的三個案例,都有測試能在移除對應過濾時翻紅,我實測 `drop_arm`、`drop_int_check`、`wilson_off` 和 `min_weeks` 都紅。inconclusive、fatal 的過濾沒有行為證據。
- ②修補處的路徑:正常路徑(週抽、有題沒過、判定行印出、shell 照判定送 LINE 或不送)成立。錯誤路徑裡,缺欄位、壞行、判斷丟例外都退回 None。非 UTF-8 檔是例外,見第 2 條。相鄰路徑(手動種子、runs>1)不印判定行,成立。
- ③同一案例修前與修後:
  - 第 1 條:修前沒有此規則,修後程式正確但無測試。
  - 第 2 條:修前沒有 `weekly_alert_line`,修後非 UTF-8 檔會丟例外。

清理:我建立的 /tmp 實驗目錄和 7 個 `gctl-run-*` 暫存現場都已刪除。

總結:最高等級 major
