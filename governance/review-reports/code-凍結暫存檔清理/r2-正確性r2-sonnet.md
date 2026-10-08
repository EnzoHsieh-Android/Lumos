severity: minor

## 三問的已驗主張

**①原問題修復的行為證據**
- 我在 `/tmp/lumos-seat-work/code-凍結暫存檔清理/正確性r2-sonnet/t`(從 HEAD=155f9bb3 clone)跑了 `python3.14 scripts/test_lumos.py -k loop_replay`,結果 27 passed、0 failed。
- 我自己用 fixture 手動重凍沒帶 `--note`,rc=2。訊息是「擋下:判定檔沒有更新——…(現行仍是 r1),這次要凍的是 r1;重凍要帶 --note…」。
- 我沒有另外跑修前版本。依程式碼,修前的擋下發生在寫暫存檔之後,所以會留下固定名的 `.verdict.tmp`。

**②修補處的正常、錯誤與相鄰路徑**
- **判定檔壞掉或不是 JSON:** `try` 抓 `(OSError, ValueError, AttributeError)`。
  - 不是 JSON 或有非 UTF-8 位元組時,`JSONDecodeError` 與 `UnicodeDecodeError` 都屬 `ValueError`,所以被抓到,`cur` 為 "?"。
  - JSON 是 list 或 `null` 時,`.get` 丟 `AttributeError`,同樣被抓到。
  - 這條路徑不會讓擋下變成例外,rc 仍是 2。
  - 這幾種壞檔輸入我沒有實跑,是依程式碼推演。
- **`.gitignore` 範圍:** 我跑了 `git check-ignore -v` 測 `governance/replay/x/verdict.json`、`verdict-2026-10-07-010101.json`、`.verdict.1-ab.tmp`。只有最後一個被規則 `governance/replay/*/.verdict*.tmp` 命中。前兩個沒被誤蓋。
- **版控裡殘留的暫存檔:** `git ls-files | grep 'verdict.*tmp'` 為 0,主線兩個已提交的 `.verdict.tmp` 確實刪了。
- **`rc_w, _refroze = …` 解包:**
  - 真函式固定回二元組,所有路徑都對。
  - 測試替身 ④ 回 `(2, None)`,符合。
  - 替身若仍回舊的 `int` 或 `(x,)`,會在 `try` 內丟 `TypeError` 或 `ValueError`。`finally` 仍會刪自己的暫存檔,例外往外傳。只有測試會碰到這種替身,不算缺陷。
- **測試 ⑤ 的 `sleep(1.1)`:**
  - 歸檔檔名取到秒,上一次寫歸檔的是 ③。
  - ③ 之後只有 ④(替身,不歸檔)和 ⑤,而 ⑤ 前睡了 1.1 秒,所以 ⑤ 的歸檔秒數一定比 ③ 大。
  - 不會撞名,也沒有偶發失敗的路徑。
  - `m.os.replace` 是全域替換,但只對結尾是 `.tmp` 的來源丟錯。`_write_lf` 的暫存檔結尾是 `.tmp-wlf`,不受影響,且 `finally` 會還原。
- **新舊互讀:** 舊版留下的 `.verdict.tmp` 不會被新版讀或刪,新規則會忽略它。

**③同一案例的修前與修後**
- 案例是已有判定檔、重凍不帶 `--note`。
  - 修後:rc=2,不留自己的暫存檔,現行 `verdict.json` 位元組不動,別人的 `.verdict.tmp` 保留。這是測試 ②,已通過。
  - 修前:依程式碼推,暫存檔會留下。
- 下面 F1 是新發現的另一個案例,修前修後行為相同。

### F1 用管線或只看尾端時,「判定檔沒有更新」會出現在 `[disposal]` 與 PASS 橫幅之前
severity: minor
blocking: 否 — rc 仍是 2,檔案也沒動,只是訊息順序讓人容易誤讀。
引句:「判定檔沒有更新要講白:這行常被夾在一長串 [disposal] 與 GATE PASS 後面,只看 PASS 會以為凍好了」
失敗場景:
- 這次修補的目的,是讓使用者即使只看最後幾行也知道沒凍好。
- `cmd_loop_replay` 在擋下之前,先由 `_loop_status_disposal(readonly=True)` 把 `[disposal]` 行與 `✅ DISPOSAL GATE PASS` 印到 stdout。
- 擋下訊息走 stderr。stdout 接管線時是區塊緩衝,stderr 是行緩衝。
- 所以用 `lumos loop replay rp --freeze … 2>&1 | tail -1` 時,最後一行是 `✅ DISPOSAL GATE PASS (rp 輪 r1: …)`。
- 「判定檔沒有更新」那行排在最前面,被 `tail` 或 `grep PASS` 濾掉。
- 使用者仍會看到 PASS 而以為凍好了,而且 rc=2 在管線裡也被吞掉。
- 只有直接接終端機、兩條流依序刷出時,訊息才在最後。
歸因:有證據的原有漏查。擋下前先印 PASS 橫幅、擋下訊息走 stderr,這個結構修前修後一樣。r2 的訊息改動沒有解決這件事,也沒有讓它變糟。
佐證行:
- 重現命令:`<lumos> --vault <v> loop replay rp --freeze --spec <spec> --repo <repo> 2>&1 | cat`。我在已凍過一次並提交的 fixture 上跑,擋下訊息出現在第 1 行,橫幅在最後。同一指令改用 `| tail -1`,只剩 `✅ DISPOSAL GATE PASS …`。
- 兩版程式碼都有這個結構:`scripts/lumos:1154`(擋下檢查在 `_loop_status_disposal` 之後),加上 `scripts/lumos:24897` 的 print。
- 建議:擋下時 `print(..., file=sys.stderr, flush=True)`,同時把擋下檢查提前到 `_loop_status_disposal` 之前,或在擋下後補印一行尾端摘要。

## 未驗範圍
- 我沒實跑「判定檔是壞 JSON」那條路徑,只依程式碼推演。
- 我沒做兩個重凍同時跑的真並行實驗,只確認檔名含 `os.getpid()` 與 `uuid4().hex[:8]`,跟 `_write_lf` 同一做法。
- 我沒跑全套測試,只跑了 `-k loop_replay`。

總結:共 1 條,最高 minor
