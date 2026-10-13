severity: major

**1. 非預設組別或跑多次的週抽種子,判定行會回報上一週的結果**
severity: major
blocking: 是
引句:「        return {"notify": False, "reason": "沒有週抽紀錄"}」(用來比對的程式段是 `_is_weekly_row`,原文為「and r.get("arm", "with") == "with" and r.get("runs", 1) == 1)」)
file: `scripts/scenario_probe.py`(`weekly_alert_line` 與 `_is_weekly_row`)
1. 輸入:`--seed 2026-W42 --runs 3`(或 `--arm` 非 with)。`main` 照寫歷史,再呼叫 `weekly_alert_line(a.history, a.seed)`。種子符合週格式,所以會往下算。
2. 這一列被 `_is_weekly_row` 濾掉,`wk[-1]` 變成上一週的列。判定行說的是上週的結果,不是剛跑的這批。
3. 重現:歷史是 `[W41 沒過 x, W42 runs=3 全過]`,呼叫 `weekly_alert_line(p, "2026-W42")`,印出 `週評通知:是 — 同判準歷史只有 0 週,基準不足,照舊有題沒過就通知:x`。這批全過卻發了通知。
4. 自主迴圈用預設值跑,所以平常不會踩到。人工手動帶週種子重跑時會誤發,也可能把該叫的漏掉。
5. 修法:`weekly_alert_line` 在最後一列不是週抽列時回 None,讓 shell 退回舊規則。

**2. 同一週重跑的多列被當成多個「過去週」,「連續兩次」和基準週數都會被灌水**
severity: major
blocking: 是
引句:「    same = [r for r in wk[:-1] if g and r.get("grader") == g and not r.get("inconclusive") and not r.get("fatal")]」
1. `same` 沒有依 seed 去重。同一種子抽到的題一樣,重跑等於又出現一次。
2. 重現(歷史依序為列 1 到 5):`W39 8/8 ids[a]`、`W40 8/8 ids[b]`、`W41 8/8 ids[c]`、`W42 7/8 failed[a] ids[a,d]`、再一列相同的 `W42`。`weekly_alert` 回 `是 — 同一題連續兩次出現都沒過:a`。其實是同一週的同一次失敗被算了兩遍。
3. 基準也會被灌水:`[W42 8/8 ids z] ×3 + [W42 7/8 failed q]` 回 `notify False`,把「基準不足」那條路繞過去了。實際只有 1 週歷史,應該照舊通知。
4. 修法:`same` 排除與 `this` 同 seed 的列,並且每個 seed 只留最後一列。

**3. 沒有題號(`ids`)的同判準舊列被算進基準,「基準不足」退路提早失效,重複失敗偵測是瞎的**
severity: major
⚠(程式行為已重現;現場歷史是否真有「有 grader 欄但沒有 ids」的列,我這邊的快照看不出來)
blocking: 是
引句:「    if len(same) < _ALERT_MIN_WEEKS:」
1. 計劃寫的是「要累積 3 週同判準、帶題號的歷史才真的生效」,程式只數 grader 相同的週。2026-10-03 起已有帶 grader 但沒有 `ids` 的列。
2. 這些列湊滿 3 週後,就走過基準不足那關。但 `_repeated_failures` 對它們一律 `q in (r.get("ids") or [])` 為 False,`prev` 取不到,重複失敗永遠判不出。
3. 重現:`[W41 7/8 failed[a] 無 ids, 3 列 8/8 無 ids, W42 7/8 failed[a] ids[a,b]]`(都用現行 GRADER_VERSION)回 `否 — 單次沒過,下次抽到再看:a`。計劃的原意是先走基準不足、有題沒過就通知。這會多漏通知。
4. 修法:`same` 另外要求 `r.get("ids")` 非空。

**4. 歷史列有 `passed` 但缺 `total` 時,`weekly_alert_line` 會丟 KeyError,而且沒有人接**
severity: minor
blocking: 否
引句:「    k, n = sum(r["passed"] for r in same), sum(r["total"] for r in same)」
1. `_is_weekly_row` 只要求 `"passed" in r`,`total` 沒檢查。
2. 重現:`[3 列正常, {"seed":"2026-W41","passed":8,"grader":G}, 本週列]` 呼叫 `weekly_alert` 丟 `KeyError('total')`。
3. `main` 對 `weekly_alert_line` 沒有 try,這個例外會讓探針進程帶 traceback 退出。歷史已寫好,shell 沒有判定行就退回舊規則,不會死,但退出碼會被改掉。
4. 修法:`_is_weekly_row` 一併檢查 `total` 是數字,或在 `weekly_alert_line` 外包 try 回 None。

沒有發現問題的部分:
- **shell 解析**:判定行印在總結行之後,`grep -E '個情境 Claude 自己敲對了'` 抓的是第一行,不受影響。`grep ... || true` 在 `set -euo pipefail` 下不會讓腳本死掉。`${verdict#*— }` 與 `case 週評通知:是*)` 是按位元組比對,非 UTF-8 locale 下沒問題。我看過原始碼位元組,冒號是同一種(半形)。判定行的原因與題號只經環境變數 `MSG` 傳給 python,不會被當成指令執行。
- **舊版探針**:沒有判定行時,`verdict` 為空,走 `p≠n` 的舊退路。`[ -n "$verdict" ] && log` 在 `set -e` 下不會中止。
- **相鄰路徑**:`_codex_home_dir` 的退路等同原樣。載入失敗時 `_LUMOS_MOD` 不快取,下次會重載,無副作用。程式碼裡其他讀 `history.jsonl` 的地方,我沒看到有依賴固定欄位集合、會被新增的 `ids` 弄壞的跡象;沒逐一打開每個讀取點。
- **Wilson**:`_wilson_interval(k, n, z=1.96)` 在 n<=0 回 None,程式有擋。`cur[1] < base[0]` 的方向與邊界合理。基準不足退路用 `bool(failed)`,等同舊規則(`failed` 只含有效場次)。
- **測試品質**:五支測試每支都有可翻紅的斷言,但上面 1 到 3 都沒有對應測試,同週重跑、非 with 組別、缺 `ids` 的同判準舊列三種情況都沒覆蓋。這幾種輸入我沒逐支做拿掉實作的翻紅變異驗證。S4 的 `mod.main()` 回傳值沒檢查,不影響判定。

我建的暫存目錄 `/tmp/lumos-seat-work/code-週評通知/正確性-sonnet/` 已刪。

總結:最高等級 major
