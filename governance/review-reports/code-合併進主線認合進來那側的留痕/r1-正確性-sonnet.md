severity: minor

審查範圍:逐 hunk 讀完 diff;在 mktemp 臨時 clone(ebc944d2)跑 `python3.14 scripts/test_lumos.py -k merge_side`,12 項全綠(最慢 109s/上限 180s)。未動 repo。

## F1 淺 clone 判斷的逾時例外沒接,違反「判不了一律不認」,表態那關會變 fail-open
severity: minor
blocking: 否 — 要 git rev-parse --is-shallow-repository 慢過 1 秒才會觸發,實務罕見;但方向是放寬,應補。

引句:「if _git_is_shallow(repo_root, timeout=max(1.0, deadline - __import__("time").monotonic())):」

走法:`_git_is_shallow`(file: `scripts/lumos:6018`)只接 OSError,TimeoutExpired 照它自己的 docstring 往上丟。這裡沒有 try,別的 git 呼叫都走 `_merge_side_git`(逾時回 None)才會變成「不認」,唯獨這一行會丟例外。
- 審查那關:例外穿過 `_codeloop_review_block`、`_codeloop_guard_verdict` 直到 `cmd_codeloop`,整支崩掉(靠呼叫端把非零當擋,不是這段本身 fail-closed)。
- 表態那關:`merge_side` lambda 在 `_dispositions_verdict` 內被叫,例外被 `_codeloop_guard_verdict` 的 `except Exception` 接成 `_gate_failopen` 並 `dv["blocked"]=False`(file: `scripts/lumos:47363` 附近)。原本「沒有表態記錄」是確定擋下,現在多了一條逾時就放行的路。
重現(已跑):把 `_merge_side_start` 換成回假起點、`subprocess.run` 對 `--is-shallow-repository` 丟 `TimeoutExpired`,呼叫 `_codeloop_merge_side(".", "b"*40, "x..y", time.monotonic()+20)` → 輸出 `RAISED TimeoutExpired`(應回 `(None, 原因)`)。
修法:改走 `_merge_side_git(... ["rev-parse","--is-shallow-repository"] ...)` 判 stdout,或包 try/except 回不認。

## F2 每條一般擋下訊息都被接上「合併判斷不成立」的雜訊,且每次擋下多跑兩個 git
severity: minor
blocking: 否 — 只影響訊息與少量耗時,不改判定。

引句:「reason = f"{reason};{why}"」

走法:非合併提交的高風險推送(最常見)走到 `_codeloop_review_block` → `_codeloop_merge_side_pass` → `_merge_side_start`;本機直接叫 check(diff_range 為 None,raw_range 為 None)時 why=「沒有推送範圍,認不了合進來那一側」;一般提交則經 `_git_is_shallow` + `rev-list --parents` 後得到「目標不是兩個母的合併提交」。結果原本乾淨的「tier=high 且無留痕(尚未跑 code-loop pass/skip)」變成後面拖一句與使用者無關的話,同一句也寫進 `skipped-env` 治理帳的「原本會擋的理由」。測試只用子字串比對所以沒紅。建議:只有目標真的是兩母合併提交時才接原因。
env 跳過先後:合併側認得到就先放行、不記 skipped-env(合理);認不到才走 env 跳過,原因字串變長,其餘行為不變。

## F3 新增的長測試只有 2 倍餘裕
severity: minor
blocking: 否 — 目前綠,但 CI 變慢會偶發超時。

引句:「def t_codeloop_check_merge_side_pass():」

走法:該案例 9 個情境各自 init repo、真跑 `code-loop pass`、再跑完整 `check`(含受波及合約測試),實測 109.0s,超時上限 180s,runner 自己印「餘裕不足 3 倍」。建議拆成多支。

## 逐項確認(無問題,附理由)
- 共用 `_codeloop_ledger_events`:預篩、kind 白名單、gate 判斷與舊兩支讀法一致;新增 isinstance(dict) 與 head_sha 必為非空 str,只把舊版會 AttributeError/後續 `[:8]` 崩的行改成跳過;dispositions 多一個 `"code-loop"` 子字串預篩,僅對被跳脫成 `code-loop` 的行不同,寫入端 json.dumps 不會產生。dispositions 的 branch 欄舊版寫呼叫端參數、新版寫事件的 branch,兩者因已過濾 branch 相等。
- 同 head_sha 多筆:`reversed(cands)` 取最後寫的優先,逐筆驗證失敗才往前,不會因第一筆無效就整批放棄。
- `_codeloop_merge_side_pass` 回 `(dict, None)`,`_codeloop_review_block` 的 `if ok_v: return ok_v` 取到 dict,型別正確。
- `_disp_record_for`:rec 為 None 時 why 空、訊息只多接 mwhy;過期時 why 中間夾 mwhy 後才接「——改了碼要重表態」,回傳與擋下點與原本一致;merge_side 為 None(既有測試的 4 處直接呼叫)行為與原本逐字相同。
- 第一母鏈不足 20、帳本缺檔/空帳本、淺 clone、八母/三母、全零或空樹起點:各自回 None+原因,不放行。cache 讓兩關共用帳本與期限;期限用完後 `_merge_side_git` 回 None 一律不認(`_codeloop_record_valid_ex` 的 max(0.1,…) 在期限後仍會各跑一次最多 0.1s,但前面的 `_merge_side_git` 已先擋住,迴圈有界)。
- 圖譜鏡頭:固定席筆記(guard-kill、lumos-cli-read、lumos-cli-lifecycle、測試假綠形態、design-loop 的 INVARIANT)與本改動無交集:未動 search 濾網、guard kill 的 rc、re-inject、處置閘第五步;pitfalls-code-loop 的既有 PITFALL(壓提交失效訊息、簿記豁免)走的 `_codeloop_record_valid` 沒改。
- 角色卡:未附卡,略過。

總結:max severity = minor;blocking 條數 = 0。
