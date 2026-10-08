severity: minor

三問已驗。①修復有行為證據:修前版 `155f9bb3` 搭配新測試跑 `-k leaves_no_tmp`,②「不印 GATE PASS 與 [disposal]」那條翻紅(6 過 1 敗);修後版 `b657d12d` 的 `-k loop_replay` 為 28 過 0 敗。②相鄰路徑只驗到一條會翻紅的:提前之後,帳本沒有該 loop、帳形狀進不了處置判定等情況若同時已有判定檔又沒帶 --note,會先印「判定檔沒有更新」並回 2,不會先走到後面的原訊息(原本也回 2)。這幾種情況我只讀碼推演,沒有逐一實跑。路徑字元檢查在更前面(`scripts/lumos:1074` 附近),提前的判定檔路徑用的 root 與 loop_id 都已通過。判定檔是目錄、壞 JSON 或 list 時,`cur` 退成 "?",仍回 2。帶 --note 的重凍與第一次凍結不受影響,新舊測試都綠。下面 F1 是例外,是提前檢查留下的競態洞。③同一案例(重凍缺 --note、已有判定檔)修前被擋時 stdout 末行是 GATE PASS,修後 stdout 沒有任何 [disposal] 或 GATE PASS,stderr 才講沒更新、現行第幾輪。未驗:多行程真並行(只用 in-process 掛鉤模擬)、Windows 路徑語意。

### F1 --note 檢查提前後留下競態:檢查時沒判定檔、寫入時有,且沒帶 --note,會崩潰並已改動判定檔
severity: minor
blocking: 否 — 只在兩個重凍並行、且至少一方沒帶 --note 的窄窗口出現,但崩潰發生在判定檔已被換掉之後。
引句:「        _cur_v = root / "governance" / "replay" / loop_id / "verdict.json"」
失敗場景:A、B 兩個行程同時對同一個 loop 做第一次凍結,都不帶 --note。B 在 `_cur_v.exists()` 時沒有判定檔,檢查通過。A 隨後寫好 `verdict.json`。B 走到 `_replay_write_verdict` 時 `target.exists()` 為真,於是把 A 的檔歸檔、換上自己的,`refroze` 有值。接著 `_loop_gov_mark(env, loop_id, "replay-refreeze", note.strip())` 因 `note=None` 拋 `AttributeError`,使用者看到 traceback。這時判定檔已換,卻沒有治理帳留痕,等於繞過「重凍必須帶理由」。修前 `target.exists()` 與 --note 檢查在同一處,這個口子不存在。
最小重現:在 `/tmp/lumos-seat-work/code-凍結暫存檔清理/正確性r3-sonnet/c` 的 `scripts/test_lumos.py` 加了探針 `t_zz_race_probe`:在 `_replay_git_blob` 的掛鉤裡先寫入 `verdict.json`,再以 `note=None` 呼叫 `cmd_loop_replay`。實測輸出:`PROBE rc= AttributeError("'NoneType' object has no attribute 'strip'") ['verdict-2026-10-07-222913.json', 'verdict.json']`。
歸因:有證據的修復回歸。修前(`155f9bb3`)檢查與 `target.exists()` 同處,沒有這個窗口;修後檢查提前,寫入端沒有保留檢查。兩版查證:修後見上面探針(崩潰);修前依 patch 讀碼,`not note` 時先印擋下訊息並回 2,未實跑探針。
佐證行:`scripts/lumos:1081`(提前檢查)、`scripts/lumos:1170`(`_loop_gov_mark(... note.strip())`),另外 `_replay_write_verdict` 內的 `if target.exists():` 沒再檢查 note。建議在寫入端,或 `if _refroze:` 前,對 `refroze and not (note and note.strip())` 補一道防線。

總結:共 1 條,最高 minor
