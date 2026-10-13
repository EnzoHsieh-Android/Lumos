severity: minor

已看完整份 patch,並在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r9-資安-甲-sonnet/` 用 75620ccf 版的主程式實測。沒有找到可直接利用的洞。以下三條都是縱深防禦類,第 1、2 條已實跑出現象,第 3 條屬推論。

**發現 1:簽核帳可以被一個 `--note` 偽造出第二行**
severity: minor
blocking: 否
引句:「fd = os.open(log, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o666)」
佐證 file: `scripts/lumos:9215`(`_signoff_write_locked`/`_signoff_append`)、`scripts/lumos:9251`(組 row)、`scripts/lumos:16744`(`_guard_signoff_refs` 讀帳)
- 攻擊路徑:誰是能控制 `lumos signoff --note/--by/--ref` 文字的人,例如被注入的 AI。送的是含 U+2028、U+2029 或 U+0085 的 `--note`,例如 `x<U+2028>{"node":"A.md","ref":"FORGED"}`。
- 為什麼成立:`json.dumps(ensure_ascii=False)` 不會跳脫這幾個字元,所以 `_signoff_append` 寫進去仍是單一邏輯行。我實測 `splitlines()` 讀回來是 2 行。
- 拿到什麼:`_guard_signoff_refs` 用 `splitlines()` 讀帳,偽造的那一行被當成真簽核。`guard abandon` 要「對得上的簽核紀錄」,偽造的 `ref` 可以對上。
- 影響有限:呼叫端本來就能直接簽核,而且圖譜寫明這個帳「作用是留痕不是防偽造」。這輪新加的 `O_APPEND` 寫法沒有堵這個洞。

**發現 2:決策自由文字仍收「看不見」的格式字元**
severity: minor
blocking: 否
引句:「raise ValueError("決策開頭欄位的自由文字不能含控制字元(ESC、tab 等),檔案沒動")」
佐證 file: `scripts/lumos:21388` 附近(`_fmt_decision_value`,在 patch 該段新增的控制字元檢查處)
- 攻擊路徑:誰是被注入而呼叫 `decision-add` 或 `decision-amend` 的 AI,或是貼上不可信文字的人。送的是帶 Unicode 標籤字元 U+E0041.. 或 U+202E(從右到左覆寫)的 `content/context/why`。
- 為什麼成立:新檢查只擋類別 Cc。我實測 `_fmt_decision_value("正常\U000e0041\U000e0042")` 和 `"a\u202eb"`、`"a\u200bb"` 都原樣通過。
- 拿到什麼:決策筆記裡可以藏人眼看不到、AI 讀得到的指令(標籤字元能逐字編碼 ASCII)。成功訊息印到終端時,U+202E 還能讓顯示順序反過來。待決問題那邊已有嚴格的看不見字元管制,決策文字沒有同等待遇。
- 這是一條推論:前提是有別的攻擊面讓不可信文字流進決策指令。

**發現 3:`_write_refusal_reason` 只檢查最後一段路徑,上層目錄是符號連結時不會擋**
severity: minor
blocking: 否
引句:「st = path.lstat()」
佐證 file: `scripts/lumos:20451`(`_write_refusal_reason`)
- 攻擊路徑:誰是陌生消費專案的作者,從 repo 裡放符號連結目錄(例如 `Projects -> ../outside`)。
- 為什麼成立:我實測 `_write_refusal_reason(vault/Projects/victim.md)` 回 `None`,允許寫入。`lstat` 只看最後一個名字。
- 沒有實際落地:`vault.rglob("*.md")` 在 Python 3.14 不跟符號連結目錄,筆記進不了 `env.notes`,所以 `env.find` 找不到。目前走不到寫入,屬縱深防禦缺口。
- 簽核帳 `log` 的路徑是 `vault.parent / .signoff-log.jsonl`,同樣沒檢查上層目錄,只有最後一段用 `O_NOFOLLOW` 擋。
- 這是一條推論,沒有可達路徑。

**其餘各類(已看,無)**
- **鍵名文法:** 引號鍵、跳脫解碼、`&`/`!` 前綴、`? ` 都試過。我另外構造了「flow 映射裡鍵與冒號分行」(`{"text"⏎ : x}`)這種寫法,它不被偵測。但那段位在 `pending_questions` 清單外,別的解析器也不會把它當題目,所以不構成讓阻塞題消失。
- **block scalar 界線:** 用 `&a`/`!!str` 前綴時鍵欄位位置算得比實際大,只會多報、不會漏報。
- **`_signoff_append`:** 寫入前先用 `lstat` 一次判完,開檔再加 `O_NOFOLLOW`;失敗時 `ftruncate` 截回,第一次建的帳整個刪掉。我沒找到能截斷或寫到別的檔的路徑。`BaseException` 還原筆記的分支也正確。
- **WriteBlocked:** 拿掉各分派的重新拋出後,內層 `(ValueError, RuntimeError)` 或 `(RuntimeError, OSError)` 的接法都會印「擋下」並回 2,最外層 `_cli` 兜底。訊息在建構時已清洗,沒有未清洗的終端輸出。我沒有逐一檢查其他程式碼裡的 `except Exception: pass`,那些是這輪以前就有的。
- **emoji 與看不見字元額度:** 整份值的看不見字元合計最多 64 位元、ZWJ 一串最多 3 個,只剩小容量的位元通道。這屬縱深防禦,不另列。
- **密鑰、加密傳輸、執行邊界、新依賴、行動端:** 已看,無。

這份 patch 沒有可直接利用的洞,只有 3 條縱深防禦類的 minor,最高也只到 minor,且都不阻擋推送。
