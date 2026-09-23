severity: minor

## F1 guard_verdict 接過來的訊息在「祖先但動了代碼」那個分支會重複一次 sha、且括號變兩層嵌套

severity: minor
blocking: no

引句:「reason = f"tier=high 且留痕 sha 過時(留痕={rec_sha[:8]} 目標={marker_sha[:8]};" + (_vwhy or "非純簿記增量") + ")"」

實跑重現(在真的高風險假 repo 跑 `code-loop pass` 後再正常 `git commit` 動 app.py,不 rebase、不 amend):`_codeloop_guard_verdict` 回的 `reason` 是

```
tier=high 且留痕 sha 過時(留痕=8890baad 目標=e269a5fa;記錄 sha 8890baad 之後動了代碼(非純簿記增量))
```

`_vwhy` 在「是祖先但動了非簿記檔」這個分支回的字串本身已經是完整一句(`scripts/lumos:28731`:`記錄 sha {rec_sha[:8]} 之後動了代碼(非純簿記增量)`),被接進 `scripts/lumos:29157` 的外層字串後,`留痕=8890baad` 跟後面 `記錄 sha 8890baad` 重複講了兩次同一個 sha,而且外層開的 `(` 到 `_vwhy` 內部自己的 `(非純簿記增量)` 又閉了一次、外層的 `)` 再閉一次,變成雙層巢狀括號。資訊沒有錯(仍然正確講出「動了代碼」),只是讀起來比較繞、跟「壓過提交」分支(`_vwhy` 是完整獨立句子、不含 sha 重複)的觀感不一致。不影響邏輯與測試斷言(兩條路都只做子字串比對),純粹是訊息可讀性的小疵。

## 已驗證但沒發現問題的路徑(重點攻擊的兩點)

- **git 回傳碼判讀(第 3 點)**:實際在乾淨 git repo 量了三種情況——`git merge-base --is-ancestor` 對「不是祖先但是同一段歷史內」回 1;對「兩條完全無關的孤兒分支歷史」也回 1(仍落在「不是祖先」語意內,`scripts/lumos:28727` 那句「多半是壓過提交或 rebase」對這種情況措辭不夠精準但本來就用「多半」保留餘地,不算新引入的錯);對「sha 打錯 / 物件不存在」回 128,屬於 `scripts/lumos:28712` 新開的 `not in (0, 1)` 分支,訊息正確講「找不到」而不是「壓過提交」。跟第一版(全部非零都當「不是祖先」)相比,這版嚴格更準確。新測試 `t_codeloop_record_invalid_after_squash_says_why` 的 ③ 段(`scripts/test_lumos.py:143-145`)把這個分支的訊息改回舊版行為會翻紅(手動 mutation 驗過,見下)。

- **guard_verdict 那條路接過來的訊息對不對(第 4 點)**:分別重現了「壓過提交/amend 改寫歷史」與「祖先但正常 commit 動了非簿記代碼」兩種失效,兩種情況下 `reason` 都正確帶出對應原因(前者講「壓過提交」+ 兩條重來指令,後者講「動了代碼」),沒有講錯或講成另一種情況的訊息。

- **新測試 `t_codeloop_check_after_squash_says_why` 是不是真的在測它宣稱的那條路**:直接呼叫 `_codeloop_guard_verdict()` 讀 `reason`(不是看 CLI 整段輸出),依文件裡的翻紅釘把 `scripts/lumos:29157` 手動改回第一版固定字串 `"非純簿記增量"` 後重跑,`② 那一句就講得出多半是壓過提交,並給重來的指令` 確實翻紅;改回來後恢復綠。確認不是假綠。

- **`_roster_kind` 分類與 `--outcome` 互斥排除(第 1、2 點,雖非本輪重點攻擊但一併驗了)**:`docs/.canary-log.jsonl` 裡目前真實存在的 `code` 開頭迴圈名單裡,只有 `codestage`、`code側刪除傳播守衛` 沒有連字號(且都不是代碼審),其餘上百筆 `code-*` 全部有連字號,跟這次改法的假設一致。用 mutation 把 `_roster_kind(str(loop)) == "code"` 改回 `str(loop).startswith("code")`,新測試 ⑤(`codestage-*` 不該被擋)會翻紅;把 `outcome is None` 這個條件拿掉,新測試 ⑥(`--outcome` 結局帳不該被擋)也會翻紅。`scripts/lumos:7603-7605` 已經有「`--outcome` 與 `--report`/`--snapshot` 等審查欄位互斥」的既有擋,所以「只記結局的帳結構上就不帶報告與快照」這句話是成立的,不是巧合。

- 額外跑了既有回歸測試 `t_codeloop_guard_verdict`(涵蓋 pass 後正常再 commit → HEAD 移動 → 作廢 blocked 的情境)與整支 `t_code_loop_record_requires_provenance_from_first_row`、`t_codeloop_record_invalid_after_squash_says_why`、`t_codeloop_check_after_squash_says_why`,全部綠(13 / 7 / 4 / 3 案例皆通過)。

## 沒查的部分
派工單要求只看「第一輪四條發現折入之後的修正差異」,`docs/` 手冊那句「順序提醒」不在這份 patch 裡(patch 只動 `scripts/lumos` 與 `scripts/test_lumos.py`),沒有另外去找手冊檔案核對,因為派工單說第二輪只審這份凍結 patch 的差異。
