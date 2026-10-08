severity: major

## resources-F1

severity: major  
blocking: 是

引句:「刪除/改名仍查快照兩版；仍不把symlink、資料JSON、ignore檔作程式寫回證明。」

佐證 file: `scripts/lumos:27109`

觀察：較廣集合若只由範圍起點、終點兩版的 `side.files` 建立，會遺漏只存在於中間提交的測試檔。例：基線已宣告 `scripts/test_ephemeral` 的家；提交 A 新增該測試、同批改程式並寫回其家；提交 B 刪除該測試。推送 A+B 時，兩端都沒有該檔，較廣集合不含它；即使 A 的 `g_paths` 與 `content_notes.own` 都正確，S13 仍會誤判 rc1。現有 deleted-test 只測「起點存在、終點刪除」，殺不到此例。

判準：逐提交正向路由既以「同提交一支合法自家改動」為充分證據，分類視圖也必須能表示只存在於該提交快照的路徑；否則需明文縮小承諾並補相應控制。

## resources-F2

severity: major  
blocking: 是

引句:「提交索引與單提交diff、普通與最佳化皆成立。」

佐證 file: `scripts/test_lumos.py:47824`

觀察：24 個控制全部使用有副檔名的 `.py` 測試檔；提交前案例的工作樹也與索引一致。既有索引測試只讓 Systems 節點在索引與工作樹分歧，未覆蓋新路由分類。因此，若實作錯從工作樹讀取無副檔名測試的 shebang，24 個控制仍會全數符合預期。具體反例：索引中的 `tests/check` 有 `#!`，未暫存工作樹移除 `#!`；正式合約應依索引放行，但錯誤實作會拒收。

判準：S1 明列索引語意，需有一個無副檔名 shebang 測試令索引與工作樹相反，證明新視圖確實讀 `side` 快照。

## resources-F3

severity: minor  
blocking: 否

引句:「shebang沿用side快取、不新增程序或持久資源。」

佐證 file: `scripts/lumos:27116`

觀察：舊窄掃描在測試判定處直接跳過，所以無副檔名測試不會填入 `side.shebang`；後續較廣掃描首次分類它時仍須呼叫 `_reader`。對歷史提交或與磁碟不同的索引內容，該 reader 會執行 `git show`，故「不新增程序」不成立；快取只能避免之後重讀。

判準：應改稱「不重複讀取已分類的 shebang」，或設計批次讀取／補上程序數與耗時控制。

## 風險總結

最高 severity：major；blocking：2。

- 守衛：兩項 blocking，分別是中間提交漏路由與索引語意未被測試釘住。
- 併發：仍使用獨立快照與局部快取，未見共享可變狀態問題。
- 效能資源：額外兩次全路徑分類成立；無副檔名測試可能另增 `git show`，見 F3。
- 回退：局部移除新視圖即可，未見資料相容或帳面不可逆問題。
- 外部送出、金流、不可逆：只做本機判定，未觸及。
- 固定圖譜節點：快照列示 0 條正式合約；既有安家、S13b、foreign-ref、tag-only 與啟動條件未見設計上改動。
- 已讀且無 finding：問題定位、最小候選其餘邊界、回退、外部送出與不可逆。
- 唯讀環境無可寫暫存區，未執行 fixture；此限制不列為產品 finding。

## 已讀材料

- `governance/review-reports/test-home-writeback/r1-snapshot.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `governance/review-reports/test-home-writeback/preflight-intake.md`
- `governance/review-reports/test-home-writeback/r1-graph-context.txt`