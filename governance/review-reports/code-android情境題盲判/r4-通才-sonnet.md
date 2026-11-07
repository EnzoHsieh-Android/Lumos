severity: minor

**第三輪 3 條的驗收**
- 帳尾沒換行時,表態、盲判、pass/skip 都修好了。
- 我在複本裡實跑:帳尾是 `\r`、`\r\n`、空檔、半行 `{"gate": "ci", "ki`、符號連結(帳尾有換行與沒換行各一次),結果都一樣。
- 新事件獨立成行,`_codeloop_read_dispositions` 讀得回,`_codeloop_read_from_ledger` 也讀得回 pass。
- 帳尾是 `\r` 時多補一個 `\n`,等於 `\r\n`,讀側把它當一個行尾,沒有多出空行。
- 空檔回 False,不會多補換行。
- `_ledger_tail_needs_newline` 只做一次 `fstat`、`lseek`、讀 1 個位元組,帳很大時成本是 O(1)。
- 帳是目錄或管線時回 False,不卡住。
- 帳是捷徑時它跟隨捷徑,看的是寫入器實際會追加的那個檔。

**新測試改壞驗證**
基準 6 passed。每次改壞前都先還原,結果如下:

| 改壞 | 結果 |
|---|---|
| 拿掉 `_codeloop_gov_log` 的補換行 | 紅(1 failed) |
| 拿掉 `_codeloop_gov_append` 的補換行 | 紅(2 failed) |
| 拿掉 `_codeloop_gov_append` 的 `UnicodeEncodeError` | 紅 |
| 拿掉 `_codeloop_gov_log` 的 `UnicodeEncodeError` | 沒紅(6 passed),見 F1 |

**F1**
severity: minor
blocking: 否
- 場景:有人把 `_codeloop_gov_log` 的 `except (OSError, UnicodeEncodeError)` 改回 `except OSError`,測試全綠。
- 輸入→實際→預期:`code-loop pass` 的 `--note` 帶孤立代理字元(例如 `x\udcff`),會讓 `json.dumps(ensure_ascii=False)` 的結果編不成 UTF-8,`f.write` 丟 `UnicodeEncodeError`。改回去後這個例外會直接炸出 `code-loop pass`。預期是有測試守著。
- 原因:新測試的 `x\udcff` 例外案例只打 `_codeloop_gov_append`,沒打 `_codeloop_gov_log`。
- 影響:屬於測試抓不住錯。現行程式本身沒問題。
- 引句:「    except (OSError, UnicodeEncodeError):   # 同 _codeloop_gov_append:不能編碼的字串也不丟堆疊」
- file: `scripts/test_lumos.py`(新測試 `t_codeloop_writers_add_missing_tail_newline` 末段 `bad = dict(ev, dispositions=...)`)

**沒有標的項目**
- `_codeloop_gov_log` 寫不進去時仍靜默,`code-loop pass` 照印「已留痕」。這是作者已記在 Issue 的範圍外項目,我沒再標。
- 檢查帳尾與開檔追加之間有競態窗口。依專案的單人、依序操作威脅模型,不標。

總結:最嚴重是 minor(`_codeloop_gov_log` 的編碼例外沒有測試守著),會擋 0 條。

我已刪除複本和 3 個 `gctl-run-*` 暫存現場,repo 沒動。
