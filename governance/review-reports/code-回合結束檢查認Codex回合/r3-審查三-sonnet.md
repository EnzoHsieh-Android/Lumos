severity: minor

整份改動(snapshot 與 repair)讀完,沒發現會做出錯行為的地方。只有一條 minor:測試 ⑦ 的說明比實際抓得到的多。我沒有真的跑 `-k stop_lint`,下面是讀碼加手動驗證。

## 修補差異回歸(鏡頭 1)

**收工端行為沒變。** 原本是 `if _stop_dir_ok: try: json.loads(read_text) except (OSError, ValueError, RecursionError): rec = None`。現在是三元式加 `_read_turn_rec`,四種情況結果相同:
- 目錄不可信:原本根本不讀,`rec` 維持 None;現在 `else None`,一樣。
- 檔案不存在或讀不了(`OSError`,含目錄、權限):兩邊都回 None。
- 非 JSON(`ValueError`,含 `UnicodeDecodeError`):兩邊都回 None。
- 解出來不是物件:兩邊都交給後面的 `isinstance(rec, dict)` 判斷,印「沒記到起點」。

引句:「rec = _read_turn_rec(turn_dir / sid) if sh._stop_dir_ok(turn_dir) else None」

**送出提示端新增了讀檔。** 之前是無條件覆寫,現在多讀一次舊紀錄。
- Claude Code 每次的 `prompt_id` 都不同,`_kept_start` 對不上就回 None,仍寫 `time.time()`,行為不變。
- `key` 為 None 時直接回 None,寫入的 `prompt_id: null` 跟舊版一樣。

引句:「t = _kept_start(d / sid, key) or time.time()」

**⑦ 的兩種壞紀錄都走到了 `_kept_start` 的舊紀錄判斷,但沒走到 `_read_turn_rec` 的 `except`。** 我用 `python3.14` 驗過:
- 負數時刻:`{"prompt_id":"t-j","t":-1}` 是合法 JSON 的 dict,在 `_turn_start` 的 `t > 0` 被擋掉,回 None 後改寫成新時刻。這條路確實走到。
- 深層巢狀:`"[" * 100000 + "]" * 100000` 在 3.14 直接解成 `list`,不丟 `RecursionError`,被 `isinstance(rec, dict)` 擋掉。

引句:「for label, junk in (("時刻是負數", '{"prompt_id": "t-j", "t": -1}'), ("深層巢狀", "[" * 100000 + "]" * 100000)):」

## Finding

1. 測試 ⑦ 的說明寫「讀起點紀錄不接壞檔 → ⑦紅」,實際不成立。
   - 輸入與路徑:拿掉 `_read_turn_rec` 的整個 `except (OSError, ValueError, RecursionError)`,⑦ 兩個案例都不會丟例外,照綠。
   - 沒被 ⑦ 抓到的情況:送出提示端遇到非 JSON 的壞檔(內容是 `garbage`,`json.loads` 丟 `ValueError`)。拿掉 `except` 後,`_on_prompt` 會在 `_kept_start` 那行崩掉、rc1,不寫新紀錄。
   - 收工端沒有這個洞:`t_slh_r2_turn_start_edges` 的 `"[" * 200000`(沒收尾,丟 `JSONDecodeError`)會讓拿掉 `except` 的收工端翻紅。
   - 影響:送出提示端沒有守衛,只剩說明文字在宣稱有。
   - 為什麼標 minor:壞檔只有手動改壞才會有,UserPromptSubmit 非零退出不阻擋,屬覆蓋可以更完整,所以 minor。
   - 修法:⑦ 加一個非 JSON 內容的案例,例如 `"not json{"`。

引句:「不管回合編號一律保留 → ⑤換 turn_id 紅;認領名額不看回合編號 → ⑥紅;讀起點紀錄不接壞檔 → ⑦紅。」

severity: minor
blocking: 否

## 其他逐項查過(都乾淨)

- **Claude Code 退步:** `_turn_key` 先看 `prompt_id` 再看 `turn_id`,Claude Code 路徑跟舊版一致。
  引句:「for k in ("prompt_id", "turn_id"):」
- **無限擋:** 防重擋的 `rec.get("prompt_id") != pid` 判斷沒動。同一個 `turn_id` 保留起點,頂多讓起點變早,不會多擋。
  引句:「if not isinstance(rec, dict) or not pid or rec.get("prompt_id") != pid or since is None:」
- **該擋沒擋:** 插話保留原起點,正是為了補這個洞。
  引句:「t = _kept_start(d / sid, key) or time.time()」
- **API 相容(鏡頭 5):** 起點檔鍵名維持 `prompt_id`,值改成回合編號,新舊紀錄互相讀得懂。授權題不適用,這是本機鉤子,沒有端點。
  引句:「json.dumps({"prompt_id": key, "t": t})」
- **圖譜:**
  - 固定席各節點(測試假綠形態、授權與歸屬、各 CLI 與 bound-tests 節點等)只因 `scripts/test_lumos.py` 掛上牽連。這次只新增一個測試函式與註解,沒有動任何 `INVARIANT` 行、白名單或授權檔。
  - 「還原翻紅釘需前置斷言」那條合約,⑦ 的負數案例有前置(確實走到 `_turn_start`),深層巢狀案例沒有,算在上面那條 finding 裡。
  - 筆記裡「3.14 不再丟 `RecursionError`」的說法我驗過,是對的。
  - 引句:「Python 3.14 解析深層巢狀 JSON 不再丟 RecursionError,那個攔截只對舊版直譯器有作用」

最高等級 minor,blocking 0 條。

涉及檔案(皆為佐證,未修改):
- `scripts/hooks/claude/stop-lint-hook.py:210-270`、`:425`
- `scripts/test_lumos.py:135253`(`t_slh_r2_turn_start_edges`)
