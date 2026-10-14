severity: minor

已讀,無 finding 的部分:`_plain_label` 加 `_lens_visible` 的出口消毒、`_gov_ts`、計數相減、捷徑帳不寫。我另外做了一次破壞測試。

**消毒**
- 實測 `_plain_label` 加 `_lens_visible` 能擋零寬字元、U+2028、DEL 和方向覆寫字元。這些都被轉成可見的 \uXXXX。
- 決策內容的換行與框線都被拆掉。
- 內容裡偽造的「機器附加」或「參考資料結束」字樣只剩純文字。它們出現在框內、前面有「決策內容:」,沒有框線可冒充系統話。
- 這部分已讀,無 finding。

**計數相減與判定大小寫**
- 判定字串是精確比對,和索引讀取端(`_residual_ask_index`)一致。「Untestable」這種大小寫變體兩邊都不算,沒有不一致。
- 同一筆問答只換格式(欄位順序、空白)會被算成新增一筆。這是偏吵的方向,可接受。
- 這部分已讀,無 finding。

**`_gov_ts`**
- 它接受不帶時區、Z 結尾、日期而已的格式,出界或非字串回 None,行為和原本自寫的那套一致。
- 已讀,無 finding。

**測試強度**
- 我在暫存 clone 裡把 `_residual_ask_row_untestable` 的比對字串改壞、清掉 `__pycache__` 後重跑 `-k residual_new`。`t_pitfalls_residual_new_untestable_ask` 等 3 條翻紅(27 通過、3 失敗),所以計數那段有抓到行為。
- 暫存 clone 與留下的 gctl-run 現場都已刪除。
- 缺口:`t_dispatch_lens_residual_new_section` 只測了框線與長度。零寬字元、多行、控制字元沒有直接斷言,目前只靠 `_lens_visible` 在出口擋。

severity: minor
blocking: 否 — 要手改帳檔且同一條合約已有 12 筆以上問答才成立,pitfalls 分級仍會升 high
引句:「rows = sorted(rows, key=lambda x: x[0])」
問題:派工鏡頭列問答時,拿帳裡 ts 的原始字串排序,再截取最後 12 筆。新增的問答列也被當成一般列排進去,沒有優先列出。
具體失敗情境:手寫進帳的 untestable 問答把 ts 寫成「0000-x」之類,字串排序會排在最前。同一條合約只要已有 12 筆較新的問答,這幾筆新增列就落進「較早的 N 筆問答未列」。提示只說「較早的」,看不出被藏起來的正是這次新增的列。必答題的指示照樣附上,但審查席看不到要查的那幾筆。我用合成資料實測重現:12 筆正常列加 3 筆偽造 ts 的新增 untestable 列,輸出只列 c0 到 c11,新增的 3 筆全被藏。
修法方向:先列「這次新增」的列再補舊的,或改用 `_gov_ts` 排序,讀不出的 ts 排最後。
佐證:patch `scripts/lumos` 的 `_lens_residual_contract_lines`,工作樹對應處 `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos`

最高等級 minor,blocking 0 條。
