severity: minor

## c1 殺傷力期間連收兩次終止訊號,收尾被第二次打斷,工作樹殘留
severity: minor
blocking: 否
歸因:有證據的原有漏查。修前對 SIGINT 連送兩次,同樣留下殘骸;修前對 SIGTERM 完全沒有收尾。修後單次 SIGTERM 能乾淨收掉。
引句:「進來前是「忽略」的(例:nohup 開的)照留忽略,不替人改掉。不在主執行緒(signal 丟 ValueError)就不裝。」
file: `scripts/lumos:75698`(`_on` 每次收到訊號都 `raise KeyboardInterrupt`,處理器一直裝到 with 區塊結束,涵蓋 `_isolated_worktree` 的 finally 清理)

失敗場景:
1. 關終端時,核心送一次 SIGHUP,shell 對工作再送一次 SIGHUP。對話工具逾時若先 SIGTERM 再補一次,情形相同。
2. 第一個訊號讓 `KeyboardInterrupt` 進入 `_isolated_worktree` 的 finally,開始跑 `git worktree remove --force`。大型 Android 專案要花數秒。
3. 第二個訊號在這段期間再丟一次 `KeyboardInterrupt`。`subprocess.run` 被中斷,後面的 `shutil.rmtree(parent)` 沒執行。
4. 結果是 `$TMPDIR/<prefix>*/wt` 與 git 的工作樹登記留下來。只能靠下次清殘骸(超過一天)才會清掉。

我在修後版本做的實驗:
- 子程序進入 `_situation_rule_signals()` 與 `_isolated_worktree`(repo 約 18000 個檔)。
- 送 SIGTERM 兩次,間隔 0.02 秒或 0.1 秒:兩次都是 `wtdir exists: True`。
- 間隔 0 秒(兩次合併成一次):`False`。
- 只送一次:已清掉。
- 修前版本對 `_isolated_worktree` 連送兩次 SIGINT:`wtdir exists: True`。

## c2 計劃含單獨的 `\r` 時,寫回會把它悄悄改成換行
severity: minor
blocking: 否
歸因:有證據的原有漏查。修前與修後輸出一致。
引句:「只處理 LF 計劃(CRLF 由 _situation_rule_read 先拒絕)。」
file: `scripts/lumos:5362`(`_note_lines` 把單獨的 `\r` 也當行分隔)

失敗場景:
1. 計劃某行是「後面\r的段」,沒有 `\r\n`,所以 `_situation_rule_read` 不拒絕。
2. `_situation_rule_insert` 用 `_note_lines` 切行,再用 `"\n".join` 組回,那個 `\r` 就變成 `\n`。
3. 我在修前、修後各跑一次 `_situation_rule_insert`:輸出都不含 `\r`,無關行被拆成兩行。
4. 修補只擋了 `\r\n`,同一類「靜默改行尾」沒有收乾淨。

## c3 「計劃已寫過」的救法,在寫完計劃、記帳前被中斷時走不通
severity: minor
blocking: 否
歸因:有證據的修復回歸(部分)。修前重跑會插第二條重複條款,修後重跑被拒絕,但訊息指的補記方法不存在。這點由程式讀取確認,沒有跑整條流程。
引句:「治理帳沒有那一筆 situation-rule 就照補記方法補(印出那一行事件加到」
file: `scripts/lumos:75828`(補記事件只在 `_gate_event` 回傳非 True 時才印)

失敗場景:
1. 計劃已寫入,程序在記治理帳之前被 SIGKILL 或當機,補記事件一行都沒印出來。
2. 使用者照訊息重跑。`_situation_rule_insert` 在殺傷力之前就以「已寫過 S?」拒絕,殺傷力不會重跑。
3. 事件需要 `kill_verdict` 與 `recipe_id`,得靠殺傷力那次的結果,使用者拿不到。
4. 規格閘會把這條當一般的新行為條款,所以要先手動刪掉計劃裡的那一條才能重跑。訊息沒教這一步。

## 附:三問、圖譜鏡頭

**①原問題的修復效果有何行為證據**
- 我自己跑的:
  - 插入點跳過縮排續行:修後 S3 插在 S2 的續行之後,修前插在 S2 與其續行之間。
  - 同文同測試不重插:修後拒絕,不同測試仍照插。
  - `_situation_rule_clause_problem`:
    - 放行 `` `items[size]` ``、`` `a || b` ``、``` ``a|b`` ```。
    - 擋 `a\|b`、`[S٣]`、`\u200b[S1]`、`[Test:`。
  - 測試名 18 種(含 `::`、`#`、`.`、中文、NFD)寫入後,`refs` 與測試名逐字相等,所以 `_spec_gate_ruled_ids` 的 `got[1] == {test_name}` 不會誤殺合法人裁。
  - SIGTERM 單次收尾:乾淨(見 c1 的控制組)。
- 讀程式確認的:
  - 配方檔路徑改從 repo 頂算。`cmd_guard_kill` 的 worktree 建在平台根所在 repo 的頂層,配方的 file 也是以 `wt` 為根解析,兩者一致。
  - 平台根就是 repo 頂時,`top` 與 `root` 相同,行為不變。
  - `log_recipe_id` 取自 `res["recipe_id"]`,與殺傷力帳本寫的是同一個值。
- 沒驗的:CRLF 拒絕、`--plan` 路徑逸出、子目錄平台的整條 `cmd_situation_rule` 流程、全答不適用但填出處的核對。我沒有解整份 repo,也沒跑 `test_lumos.py`,這幾項記未判定。
- `t_kt_bj_specs_are_data` 只檢查指示字串存在,抓不到行為。這是提示文字,沒有可行的行為測試,只算覆蓋面。

**②修補處的正常、錯誤與相鄰呼叫路徑**
- 同一段第二次人裁不同條款:不同條款文字、同條款文字配不同測試,都照插。只有「同文同測試」被擋,我認為合理。
- `_kt_sit_has_applies` 變寬後,全答不適用但某列填了 spec 就會算名單。名單算不出來時的錯誤訊息仍寫「答適用的列沒辦法核出處」,措辭略偏,不影響行為。
- `_expected_requirement` 把人裁集合移到門與生效日之後,語意不變。條款全被人裁扣光時,仍會多算一次 `_door_judge`,只是效能,不影響結果。
- `_spec_gate_ruled_ids` 的另外兩個呼叫端(`_spec_gate_twoway_gate` 與簽核指令)不傳 `events`,仍各自讀帳,行為與修前相同。

**③新發現的同一案例,修前與修後**
- c1:修前 SIGINT×2 殘留。修前 SIGTERM 無收尾,直接被預設處理終止。修後 SIGTERM×2 殘留。
- c2:修前、修後相同。
- c3:修前會插第二條重複條款,修後是死路。

**圖譜鏡頭**
- 派工附的固定席節點為空(鏡頭計算超時),我沒有拿到可逐條對照的節點。
- 我只從這輪文件 hunk 判斷:`規格閘`、`guard-kill`、`棧別提問表態閘` 三篇與計劃檔的敘述,和修後程式一致。
  - 「綁的測試恰好是帳上那支」對應 `got[1] == {e["test_name"]}`。
  - 「先過門與生效日才讀治理帳、同一輪只讀一次」對應 `_expected_requirement` 與 `_expected_gov`。
  - `log_recipe_id` 的敘述屬實。
  - `.lumos-keep` 標記:`_isolated_worktree` 寫入,`_isolated_worktree_sweep` 跳過,與敘述一致。
- 計劃「天花板 8」寫的是收尾收程序群組,未提雙訊號。c1 是這一條的邊界,沒有破壞已宣稱的合約。

我的暫存實驗(`/private/tmp/lumos-seat-work/code-情境題引規格出處/正確性-sonnet/a/`)還在,收貨後可刪。

最嚴重 severity: minor,blocking 共 0 條。
