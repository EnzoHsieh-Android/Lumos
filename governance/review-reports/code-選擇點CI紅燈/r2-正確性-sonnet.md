severity: clean

## c1 run_id 型別表的讀端(str/int/None 三種值)
severity: clean
blocking: 否。程式裡讀 run_id 的地方,遇到這三種值都不出錯、也不誤判。
歸因:未判定(沒有發現)。

引句:「"run_id": (str, int, type(None)),」

- 型別表只用在 `_gov_event_types_ok`,它是 `isinstance` 判斷,str、int、None 都過。
- 治理帳的 choice-kill 映射只是把 run_id 原值複製出去。choice-kill 帳的寫端永遠是 12 碼字串,所以 None 不會被當成同一個 run。file: `scripts/lumos:18422`
- `_ci_latest_attempts` 對 None 走 `keep` 原樣保留,其餘轉成字串後分組,所以整數和字串不會分成兩組。file: `scripts/lumos:67187`
- 其餘 run_id 的讀寫在 e2e 總表,走另一條帳,跟這張型別表無關。

## c2 ci-wait 各寫帳路徑逐一核對
severity: clean
blocking: 否。沒有找到任何寫端寫出型別表不收的值,所以沒有事件會整行被跳過。
歸因:未判定(沒有發現)。

引句:「ci-wait 等不到 run 時(no-run、timeout-waiting)寫 null」

我對 `_ci_record` 的四個呼叫端(紅燈、全綠、no-run、timeout-waiting),逐欄核對了寫出的值:

| 欄位 | 寫出的值 | 型別表 |
|---|---|---|
| run_id | gh 的整數,或 None | 收 |
| attempt | gh 的整數,或 0 | 收(int) |
| conclusion | `r.get("conclusion") or "?"`,一定是字串 | 收 |
| workflow、title、url、failed_step | 字串,預設 `""` | 收 |
| sha、dedup_key | 字串 | 收 |
| branch | 沒登記在型別表,不受檢查 | 不受影響 |

- 唯一殘留的理論風險是 gh 回傳 `attempt: null`,但 gh 的欄位是整數,這不算具體輸入。
- 這一項既不是修補造成的新問題,也不是原有漏查。
- 版本對照:修前 ff4cb0909 是 `"run_id": (str, int),`,這個版本漏了 None。修後 c478bdcb3 補上 None,而 `no-run` 的寫端 `"run_id": None` 在兩版都存在,所以這是上一輪留下的漏洞,這次修掉了。

## c3 新測試 null 斷言的抗改壞力
severity: clean
blocking: 否。我試了兩種改壞,測試都有翻紅。
歸因:未判定(沒有發現)。

引句:「check("gov 見得到 run_id 為 null 的 no-run 事件", "no-run" in r.stdout, r.stdout[-400:])」

- 我把型別表改成 `(str, int)`,拿掉 None,新斷言翻紅。
- 我把型別表改成 `(str, type(None))`,拿掉 int,原有的「gov 見得到 CI 事件」翻紅。
- 讀 03-寫回圖譜.md〈實作測試品質〉做的對照:`"no-run" in stdout` 只有那一行能讓它成立,不是把實作重寫一次。
- 唯一的弱點是這行帳是測試手寫的,沒有走真正的 `_ci_record` 寫端,所以寫端以後改了形狀,這條測試不會翻紅。這是缺口,但沒有具體改壞能讓必要行為出錯,所以只算 minor 以下的觀察,不當 finding。

## c4 choice-kill 中斷測試還原 SIGINT
severity: clean
blocking: 否。
歸因:未判定(沒有發現)。

引句:「stdin=subprocess.DEVNULL, preexec_fn=_ppc_sigint_default)」

- `_ppc_sigint_default` 在同檔已有定義,另外三處也這樣用。file: `scripts/test_lumos.py:85520`
- 我在修後版本跑 `-k t_choice_kill_interrupt`,結果 3 passed、0 failed。

最嚴重:clean;blocking 共 0 條

臨時目錄 `/private/tmp/lumos-seat-work/code-選擇點CI紅燈/正確性-sonnet-r2` 已刪。
