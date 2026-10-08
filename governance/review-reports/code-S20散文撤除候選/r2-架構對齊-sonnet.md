severity: clean

## 1. 分層與依賴方向
新函式 `_ns_tr_says_retire`、`_ns_tr_sub_says_retire` 只被同檔的 `_doctor_test_ref_lines` 呼叫(`scripts/lumos:29425`),它們只用同組常數 `_NS_TR_VERDICT_RE`、`_NS_TR_KEEP_VERBS`(`scripts/lumos:28952-28953`),不碰 I/O、不跨層。常數搬進 `_NS_TR_HEAD`(`scripts/lumos:28951`)後面的同組常數區,跟 `_NS_TR_SPLIT_RE`、`_NS_TR_HAS_REF_RE`(`scripts/lumos:28947-28950`)並列;函式放在 `_ns_tr_format`(`scripts/lumos:29374`)之後、`_doctor_test_ref_lines` 之前,先定義再使用,跟同檔鄰居的順序一致。以前常數和函式夾在 `_doctor_test_ref_lines` 之後的做法,這次已拉回同組區,對齊變好。

## 2. 命名與錯誤處理
命名沿用 `_ns_tr_*` 函式前綴和 `_NS_TR_*` 常數前綴(`scripts/lumos:29072` `_ns_tr_retired`、`29129` `_ns_tr_is_new`)。判斷函式用 `says_retire` 動詞形,跟 `_ns_tr_retired` 的形容詞形略不同,但這是「判一行文字」與「判條款欄位」兩種不同對象,不算不一致。常數行尾註解的寫法跟 `_NS_TR_BUDGET`、`_NS_TR_GREP_CAP`(`scripts/lumos:28945-28946`)同風格。兩支函式沒有 try/except,跟鄰居純判斷函式相同(`_ns_tr_retired`、`_ns_tr_is_new` 也沒有)。

## 3. 第二種做法
沒有。切段用既有的 re.finditer 加切片,語言內建的 `str.startswith(tuple)` 取代迴圈;`_NS_TR_KEEP_VERBS` 用 tuple 是 startswith 需要的,跟 `_NS_TR_PLACEHOLDERS` 的 frozenset 用途不同(後者是成員測試),不算第二種做法。沒有新增並行的撤除判斷路徑:舊的 `_ns_tr_prose_retire`、`_ns_tr_prose_candidate` 已整組刪除、改名,不留兩套。

不對齊共 0 條,其中 major 0 條
