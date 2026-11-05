severity: minor

這輪修補我沒找到會讓行為出錯的問題。只有一條 minor:Systems/規格閘 筆記沒寫新的擋下標題分流。

**1. Systems/規格閘 筆記沒有「擋下標題依原因分流」的現況句**
severity: minor
blocking: 否
引句:「標題照帳讀不到講(代碼審 r1)」
file: `scripts/lumos:16585`(`_spec_gate_push_bad_head` 三種標題),筆記只在 `docs/lumos-toolchain-knowledge/Systems/規格閘.md:90` 講「帳讀不到就擋」。
- 場景:人讀筆記,看不到推送前擋下標題分「帳讀不到、預期值表簽核、風險低留痕」三種。
- 這不會讓人做錯事,而且程式可查,所以只算措辭覆蓋不全。
- 歸因:有證據的修復回歸。標題分流是這一輪補的。
- 查證:`grep -n "bad_head\|標題" Systems/規格閘.md` 在修後沒有對應句。我沒有逐版比對修前。

## 三問的回答

**① 原問題的修復效果,有什麼行為證據?**

我在 `git clone --shared` 到暫存目錄的修後版(3d2b45a)上,逐一改壞再跑測試。結果每個都紅:

| 改壞的地方 | 變紅的測試 |
|---|---|
| 預期值表那段讀帳失敗,標題換回 `_EXPECTED_PUSH_TAG` | `t_push_check_expected_bad_ledger`,S11 標題那條 |
| 拿掉 gov 列對 `expected-signed` 的 token 分支 | `t_push_check_expected_ai_signed`,S8「人簽 1 次、AI 簽 2 次(同提交兩次各算)」 |
| 把 `_expected_table_sha` 的 `ensure_ascii` 改成 True | `t_expected_table_fingerprint`,固定值那條 |
| `_live` 不認「done 但這次推送改到計劃檔」 | `t_push_check_expected_scope`,S7 done-touched 那條 |
| `_spec_gate_expected_part` 表不合時回 `None` 而不是 1 | `t_spec_gate_expected_table_high`,S4 |

- 固定值 `8d9437…7c30` 我另用 `hashlib.sha256(json.dumps(列, ensure_ascii=False))` 重算過,一致。
- 「`gov` 列 token 接回條件鏈」只是重構,值沒變。修前是在 `**` 展開裡覆蓋 `token`,修後是進條件鏈,結果都是 `str(token or "")`。
- 這一項我只能靠讀程式和上面的改壞實驗判斷,沒有直接比對修前輸出。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**

- `_spec_gate_expected_part` 的呼叫端只有一處,`scripts/lumos:15481`。
  - 表不合回 1,其餘回 `None`,語意和同函式內的 `_spec_gate_pending` 一致。
  - 測試沒有直接呼叫它。
- `cmd_gov` 的 token 在四種事件上和修前一致:
  - canary/blocked 是 `ts+note`。
  - code-loop 的 dispositions / recall-miss 是 `written_at` 或 `ts`。
  - fix-check 和 `expected-signed` 是自帶 token。
  - 其他是空字串。
- `-k` 子集全綠:
  - `gov_stats` 59 項。
  - `push_check_expected` 22 項。
  - `spec_gate_push` 21 項(preserve:風險低留痕擋法)。
  - `oneway_keeps_halfset` 3 項。
  - `expected_ai_signed` 2 項。
  - `discipline` 45 項。
- 手冊的說法對得上程式:
  - 條款欄寫 `[S1]`(帶方括號)會被擋,寫 `S1` 通過。
  - 生效日常數是 2026-11-06。
  - 簽核的互動終端、逾時記 AI 簽,和 `_cmd_signoff_expected` 一致。

**③ 新發現在修前、修後各是什麼結果?**

- 唯一一條是上面的 minor,屬於筆記措辭,沒有修前修後的行為差異。
- 其餘我試過的邊界都沒翻出新問題。

**未驗範圍**
- 治理帳讀不到時,`_expected_push_one` 自己那條備援路徑,在整個推送流程裡幾乎走不到。測試是直接呼叫它,這是作者在測試註解裡自己說明的。
- 版號升 v1.5 之後,別的專案跑 `lumos update` 的提示流程,我沒跑。
- 我沒有重現修前的行為,所以標題分流與 token 重構的「修前結果」只是讀程式推論。
- 暫存目錄 `/tmp/lumos-seat-work/code-高風險測試證據加嚴/正確性-sonnet/w` 已刪。另留有原檔備份 `lumos.orig` 和空的 `正確性-sonnet` 目錄,沒刪。

總結:全份最高 minor
