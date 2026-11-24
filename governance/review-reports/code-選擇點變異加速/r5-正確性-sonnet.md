severity: clean

我沒找到 finding,三個被點名的疑慮都已驗過。

**已驗主張**(修後 f14bd5881、各測試單獨跑)

**一、新案例預期值手算正確,且兩個斷言各有翻紅對照。**
引句:「took = {"run aCase": 1.0, "run bCase": 5.0, "run cCase": 1.0}」
- 手算:剩 3.0。量第二支前,已量 [1],left=2,門檻 1×2×1.5=3.0,`3.0 < 3.0` 不成立,照量。
- 量第三支前,平均 3、left=1,門檻 4.5 大於 3.0,收手,回 False、baselines 有 2 支,與斷言一致。
- 把平均改成 `min(measured)` 後,量了 3 支,斷言翻紅,輸出 `True ['run aCase','run bCase','run cCase']`。這個改壞證明新案例能分出「平均」與「最小值」。舊的 1、3、1 秒案例做不到這點。
- 把單支上限的 `max(mg.remaining(), 1.0)` 拿掉後,剩 -5 秒那條翻紅(收到 `[-5.0]`)。保底案例有效。
- 全部 6 條斷言在修後通過。

**二、接線測試第二情境測到的就是合併基準那次呼叫,不會抓錯。**
引句:「mg.remaining = lambda: 60.0 if singles[0] < 3 else -5.0」
- `singles[0]` 只在 `spy` 的非合併呼叫累加。
- 讀 `_kill_merge_singles` 與 `_kill_merge_base`:三支單支基準每次呼叫前,`remaining()` 看到的 singles 是 0、1、2,都回 60。第三支跑完 singles 才變 3。
- 之後合併基準算上限用的 `max(mg.remaining(), 1.0)`,看到的就是 -5。
- `seen.clear()` 之後 `seen[0]` 就是合併基準的逾時,不會是快篩那兩次。
- 拿掉合併基準那處的 `max(…, 1.0)` 後,斷言翻紅,輸出 `[-5.0]`。
- 若單支數不是 3,remaining 會一直回 60,`seen[0]==1.0` 會紅,不會假綠。
- 這個計數切換依賴三支單支這個前提,前提變了會紅,不影響正確性。

**三、`--json` 解析失敗不會讓斷言假綠。**
引句:「any(r.get("verdict") == "survived" for r in rows) and not any("judged" in r for r in rows)」
- 解析失敗時 `rows=[]`,`any(survived)` 為 False,斷言紅。「不帶 judged」那半句在空列時其實是空真,但被前半句擋住。
- 實測:在 `_kill_merge_emit` 的存活列塞 `"judged": "merged"` 後,這條翻紅,輸出的列帶著 `'judged': 'merged'`。
- 取最後一行 `json.loads(out.strip().splitlines()[-1])["results"]`,在 `redirect_stdout` 下只有 JSON 一行,實測通過。

**其他檢查**
- 資源:`run()` 在 `finally` 還原 `m._kill_run` 並呼叫 `_ck_cleanup`,錯誤路徑上暫存目錄與 monkeypatch 都有收。
- 文件:guard-kill 的 PITFALL 行只加出處與修法文字。test 標籤 `t_choice_kill_merge_cap_wiring` 對應到實際測試。
- anchor-baseline 的 hash 與核可 note 屬簽章流程,不在正確性範圍。
- 未驗:修前 100d3851c 版本沒跑。新案例在修前不存在,沒有可比較的結果,歸因寫未判定。preserve 方向只看了同檔兩個既有案例仍綠,沒有補案例。

臨時 worktree 已移除,實驗用的改壞都在我自己的 worktree 裡做完並已還原。

總結:最高嚴重度 clean
