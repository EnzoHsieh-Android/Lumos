severity: minor

# code r1 正確性席(sonnet)審查報告

審材:r1-snapshot.patch;對照真代碼 `/Users/enzo/harness/lumos-rtb3/scripts/lumos`(HEAD 718d32bd)。
實驗腳本放 scratchpad 的 x.py、y.py(在 repo 根以 in-process 載入 lumos,未改 repo)。

## 已走過、判無洞的路徑
- `_slot_scan` 重構:用 20 萬條隨機字串(字母表含 `[` `]` 反引號 `test` `:` `：` `test-gone` `出處` tab 換行)對照改之前的 slot_parse 原樣實作,0 筆不同;未收尾欄位、落單反引號、全形冒號都一致。
- 新舊互讀:sig 沒有任何地方存檔跨版本比。兩處消費(file: `scripts/lumos:27301`、`scripts/lumos:27397`)的兩側都走同一支 `_nodehome_parse_note`,合併提交的 olds 也是,沒有「舊版算的 vs 新版算的」。
- 邊界:空字串 sig 為 ('', '', '');整篇只有標記的行被丟;CRLF(`- [test:t_x]\r` 整行丟、`a [test:t_x]\r\nb` 保留 \r)正常;正文有沒收尾圍欄時 `_visible_lines` 退回寬鬆讀法,圍欄後的標記原樣留(多擋方向,兩側一致)。
- 效能:20 萬個標記同一行 0.40 秒;10 萬個未收尾 `[test:` 0.03 秒;本 repo 662 篇筆記 parse 共 0.34 秒。無二次方路徑。
- `_NODEHOME_BARE_ITEM_RE` 定義在使用它的函式之後,但只在呼叫時查名,不出錯。

## F1 英文單行說明能藏在 [test:] 值裡,整行不算寫說明
severity: minor
blocking: 否——只有刻意或英文專案才碰得到,且方向是少擋、不是壞資料;門本身可由 node_home.gate 調整。
file: `scripts/lumos`(`_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")`,見 diff 的 `_nodehome_test_tag_value_ok`)
引句:「_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")」
場景:字元集含空白與逗號句點,≤200 字的英文句子「像測試名」。實測 `P("實作在 x\n- [test:t_old]") == P("實作在 x\n- [test:Retries now return 2 when input is empty, see ticket 42]")` 為 True(y.py)。英文寫的專案(或在中文筆記裡寫英文說明)把新寫的行為說明塞進 `[test:...]`,同提交改程式也不會被寫回落點擋。測試 ⑥ 只驗中文,測試 ④ 還把英文句子當合法。設計取捨已在計劃裡以「中文藏不進去」為界;此處指出界線對英文文本不成立,屬已知限度,不是實作與設計不符。

## F2 兩個空行夾住的單獨標記行,刪掉或加上仍會被算成內容有變
severity: minor
blocking: 否——多擋方向(誤判有改),且有既有出口(換綁定時別獨立成段)。
file: `scripts/lumos`(`_nodehome_strip_test_tags` 的 `continue` 整行丟棄)
引句:「if k and _NODEHOME_BARE_ITEM_RE.fullmatch(line):」
場景:正文 `a\n\n[test:t_a]\n\nb` 與 `a\n\nb`:丟掉標記行後前者變成 `a\n\n\nb`(三個換行),後者 `a\n\nb`,sig 比對只對每行 rstrip、不收斂連續空行,實測 `P(...)==P(...)` 為 False(y.py);同一篇改成 `[test:t_b]` 則為 True。所以「刪一個獨立成段的綁定」在這個形狀上跟計劃宣稱的「只換、加、刪綁定都不算」不一致。測試 ⑤ 只覆蓋清單符號行(前後無空行夾住),沒碰到。

## 圖譜鏡頭
本次派工沒附固定席節點(鏡頭計算超時),不能逐條判固定席。自行看 diff 內二篇系統筆記:`每支檔有家` 新增的 KEY 行與 `筆記內容閘` 的 WHY 行與程式行為一致(sig 兩側同函式、掃描單一份),未見該節點宣稱被破壞。唯一落差是 F2 與「只換、加、刪測試綁定標記也不算」的字面略寬。

## 角色鏡頭
後端卡 be-api-compat、be-authz:本改動是本機 CLI 內的字串比對函式,無對外 API 欄位、無端點、無授權檢查,不適用。

最高嚴重度:minor
