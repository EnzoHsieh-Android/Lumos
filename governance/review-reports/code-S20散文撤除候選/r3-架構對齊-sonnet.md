severity: clean

## 1. 分層與依賴方向
沒有跨層。改動只在同一組 `_ns_tr_*` 常數區與 `_ns_tr_says_retire`,沒有新增 import,也沒有新的呼叫方向。呼叫鏈還是 `_ns_tr_sub_says_retire` 呼叫 `_ns_tr_says_retire`(`scripts/lumos:29407`)。舊常數 `_NS_TR_KEEP_VERBS` 已全數取代,全檔和測試檔都沒有殘留引用(grep 為 0)。

## 2. 命名與錯誤處理
- 新常數 `_NS_TR_KEEP_LEAD_RE`、`_NS_TR_KEEP_WORD_RE` 用 `_NS_TR_` 前綴加 `_RE` 後綴的 re.compile 常數,和同區的 `_NS_TR_VERDICT_RE`、`_NS_TR_PREFIX_RE`(`scripts/lumos:28948`、`28952`)一致。
- 常數行尾用註解說明,也和鄰居一致。
- 這個函式是純字串判斷,不丟例外,也沒有 try/except,和 `_ns_neg_*` 一族(`scripts/lumos:28036` 起)的作法相同。

## 3. 第二種做法
- 「判一句話裡的否定或保留」的既有作法是正則加遮罩或切段,例如 `_NS_NEG_NOTLACK_RE` 與 `_NS_NEG_SEG_CUT_RE`(`scripts/lumos:28019`、`28030`)。
- 這次改成「用 `_NS_TR_VERDICT_RE` 切段,挖掉保留段,再用正則判剩餘文字」,仍是同一類做法,沒有引入新依賴,也沒有新的資料結構範式。
- 挖段用 slice 組字串,不用 `\0` 遮罩。這在鄰居裡有細微差異,但屬於實作手法,不是第二套機制,不列。
- `drop` 的 list comprehension 裡,下一個裁定位置的切片算式重複寫了兩次,屬純風格,不列。

不對齊共 0 條,其中 major 0 條
