severity: minor

審查席:邊界-sonnet,r3。鎖檔我沒碰,照派工詞審查。派工沒附固定席節點,固定席逐條判定無對象可判。

我在臨時目錄開了修前、修後兩個 worktree,把 `_seat_noise_name` 和 `_finding_seat_required_block` 抽出來,對兩版各跑同一批極端輸入;另對 `docs/.canary-log.jsonl` 的 795 個 auditor 各跑一遍。測試 `python3.14 scripts/test_lumos.py -k finding_seat` 在修後版是 65 passed、0 failed。臨時 worktree 與暫存腳本已刪。

## Finding 1
severity: minor
blocking: 否
file: `scripts/lumos:18071`(`_seat_noise_name`,修後的切席名正規式 `_SEAT_SPLIT_RE`)
引句:「全程線性,不用會回溯的尾端正規式(代碼審 r2 資源 1:十萬字元的席名原本要跑 40 秒)。」
失敗場景:
- 席名含換行時,`_SEAT_SPLIT_RE = ^(.*?)-(?=[A-Za-z])(.*)$` 沒有 DOTALL,`(.*)` 遇到換行就停,`$` 對不上。
- 每個「連字號後接英文字母」的位置都會掃到換行才失敗,所以是平方時間。
- 輸入:席名 `"a-"*30000 + "\nx"`(6 萬字元),在 `gov --stats` 的 `_seat_noise_counts` 呼叫處走到這一行。
- 修前 5.52 秒,修後 5.47 秒,完全沒變。
- 另一個輸入 `"中-a"*20000 + "\n中"` 兩版約 3.3 秒。
- 照平方推算,十萬字元約 15 秒以上。
- 新測試只用 `"長"+"1"*100000+"_-x"`,沒有換行,抓不到這個。
- 修補把「線性」寫進註解,但含換行的席名仍不成立。
歸因:有證據的原有漏查。兩版數字相同,修補沒有造成也沒有修好。
查證命令:對兩版 worktree 的 `scripts/lumos` 抽出該函式,餵上述輸入量時間(結果如上)。
正常席名沒有換行,所以只算 minor。修法是 `re.DOTALL`,或先把換行換成空白。

## Finding 2
severity: minor
blocking: 否
file: `scripts/lumos:19611`(`_finding_seat_required_block`)
引句:「first = min(good) if good else (rec_k if not keys else None)   # 首筆=帳上時間最早那筆;帳上沒有任何一筆才看本筆」
失敗場景:
- 帳上所有列的 ts 都壞,而且 `LUMOS_FINDING_SEAT_SINCE=9999-01-01`,本筆是生效日後的正常時間。
- 此時 `first=None`,走進第一個 `if`,然後 `first is not None and first >= const` 為假,於是靜默回 None。
- 沒有「提醒」,治理帳也沒有 `finding-seat-since-overridden`。
- 修前同輸入走 `finding-seat-badts`,rc2 擋下。
- 這正是 r2 資安 1 要補的「環境變數殘留不能靜默關掉必填」,而全帳皆壞的分支漏了。
- 帳上有好列、或帳是空的分支,實測都有留事件。
歸因:有證據的修復回歸。修前是擋下,修後是靜默放行。
查證命令:
- 兩版各呼叫 `_finding_seat_required_block("/x","code-a","aud",rec,[{"ts":"壞"}])`,rec 的 ts 為 `2026-12-01T09:00:00+08:00`。
- 修前回傳 2 且記 blocked,修後回傳 None 且沒有任何事件、stderr 空。
- 要走到這裡得同時有環境變數覆寫與全壞帳,單人工具下影響小。

## 修補的實測結果(修前→修後)
- **`_seat_noise_name`**
  - `正確性-2-sonnet`:修前變成 `正確性--sonnet`,修後原樣。
  - `外家codex-5-mini`:修前變成 `外家codex--mini`,修後原樣。
  - `中文3-4-sonnet`、`中r-2-sonnet`:同樣的雙連字號問題,修後都修好。
  - ` 空白席-sonnet `:修前不併,修後併成 `空白席-sonnet`。
  - 不變的名字:`架構對齊r2-sonnet`→`架構對齊-sonnet`、`外家finder2-codex`→`外家finder-codex`、`中r2-sonnet`→`中-sonnet`、`code-發現-r2-sonnet`、`中文-`、`-sonnet`、`r2`、純數字、`a-`、空字串、`邊界2-3sonnet`,修前修後相同。
  - 全形數字 `邊界２-sonnet`:修前去掉全形的 2,修後保留。這是改成只認 ASCII 數字的副作用,實務上沒人這樣取名。
  - 真帳 795 個 auditor:修前修後的歸一結果沒有任何差異,也沒有雙連字號,結果再跑一次也不變。
- **必填判斷的邊界**
  - 恰好等於生效日 00:00:00+08 的本筆:擋,修前修後相同。
  - 早 1 秒:放行。
  - 本筆沒有 ts:擋(照常數必填),修前修後相同。
  - 本筆 ts 沒帶時區:擋。
  - 環境變數是亂字串(如 `abc`):退回常數,擋。
  - 本筆早於生效日、帳上有壞時間列:修前擋 badts,修後放行,符合計劃「變回選填」。
  - 本筆不早於生效日、帳上有壞列:修前修後都擋 badts。
  - 帳上有好列加壞列、本筆晚於生效日且環境變數覆寫:修後留 `finding-seat-since-overridden` 事件並放行。
  - 帳上有壞列、本筆晚於生效日、沒有覆寫:擋 badts,脫困指示(補帶 `--finding-seat`)能走通。

## 三問
1. **原問題的修復效果有何行為證據?**
   - 雙連字號、前後空白、逐席併列、早於生效日不必填,以及覆寫時留治理帳事件,修前修後的對照如上,都有實測。
   - 效能只修好「無換行的長數字尾」。含換行的席名仍是平方時間(Finding 1)。
   - 全壞帳加覆寫的情況,修後反而靜默放行(Finding 2)。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 三種擋下(`finding-seat-missing`、`finding-seat-badts`、`finding-seat-unknown`)都改成在原處呼叫 `_gate_event_or_warn(..., hard=True)`,迴圈名與席名過 `_esc_clean`。
   - 擋下訊息的席名來自 `repr`,照抄後 `_finding_seat_write_block` 會先 strip 再 NFC 比對,所以空白與合成字元都能記成。
   - 只有席名含單引號或反斜線時,照抄 repr 給 shell 會出問題,屬極端案例,不報。
   - `--help` 寫「要跟 --loop、--round」,但 `scripts/lumos:19938` 只檢查 `loop`,`--round` 沒有被強制。沒有迴圈時的路徑照舊擋下,這點不構成失敗場景,只提醒措辭比實作嚴。
   - 手冊日期的測試 `t_finding_seat_docs_match_since` 跑過,與常數一致。
3. **新發現的同一案例在修前、修後各是什麼結果?**
   - Finding 1:修前 5.52 秒,修後 5.47 秒,沒有差別。
   - Finding 2:修前 rc2 擋下,修後 rc0 靜默放行。

最嚴重等級 minor
