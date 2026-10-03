severity: minor

## 問 1 分層與依賴方向
結構對齊。S20 的散文撤除判斷仍留在 `_doctor_test_ref_lines`,只把「撤除」字面比對拆成兩個純函式(`_ns_tr_prose_retire` 判一行、`_ns_tr_prose_candidate` 判一條款的下一層),輸入是字串與行號,沒有碰檔案、git 或 Env,依賴方向跟同組 `_ns_tr_*` 一致(doctor 呼叫 note-shape 零件,不反向)。「已作廢不列」直接重用既有 `_ns_tr_retired(sp)`(scripts/lumos:29070),沒有另寫一套判作廢。唯一的落差是擺放位置:新常數與兩個函式放在 `_doctor_test_ref_lines` 之後、`cmd_note_shape` 之前,而同組常數集中在 28943–28951、同組輔助函式都擺在使用者之前(例如 `_ns_tr_collect` 29314 在 `_doctor_test_ref_lines` 之前)。見 F1。

## 問 2 命名與錯誤處理
鄰居的判斷函式多半叫 `_ns_tr_is_new`(29127)、`_ns_tr_placeholder`(29011)、`_ns_tr_retired`(29070),新函式 `_ns_tr_prose_retire` 讀起來像動作且跟 `_ns_tr_retired`(條款標了作廢)只差一個字,但意思不同(一行說明在講撤除)。見 F2。錯誤處理:兩個新函式是純字串判斷、不丟例外,跟鄰居的純判斷函式一致;呼叫端沿用原本的寫法,沒有新增或移除 try。

## 問 3 第二種做法
全檔我找了「裁定」「撤除」「改寫」「維持」的判斷零件:`_DRIFT_M1_NOT_YET_RE`(33886)判的是「尚未撤除」這類否定現況句,目的不同;`_NS_NEG_*`(28004–28033)判否定現況,也不判裁定動作詞;全檔沒有現成的「裁定後接動作詞」判斷可重用。所以新增 `_NS_TR_VERDICT_RE` 與 `_NS_TR_KEEP_VERBS` 不算第二種做法。已作廢條款的排除重用了 `_ns_tr_retired`,對。常數寫法(正則加字串元組、`startswith(元組)`)跟 `_NS_NEG_*`、`_NS_TR_PLACEHOLDERS` 的風格同類。沒有 major。

## F1 新常數與輔助函式擺在使用者之後、離同組常數區很遠
severity: minor
blocking: 否
引句:「_NS_TR_VERDICT_RE = re.compile(r"裁定[^:：\n]{0,20}[:：]\s*")」
file: `scripts/lumos:29403`
1. 同組 `_NS_TR_*` 常數集中在 `scripts/lumos:28943-28951`,新常數卻落在 29403,在 `_doctor_test_ref_lines` 之後。
2. 同組輔助函式慣例是先定義再被呼叫(`_ns_tr_collect` 29314 在 `_doctor_test_ref_lines` 之前)。新函式在呼叫者之後,執行上沒問題,但跟鄰居擺法不同。
3. 建議常數併進 28943–28951 那一塊,兩個函式移到 `_doctor_test_ref_lines` 上方。

## F2 `_ns_tr_prose_retire` 的名字跟 `_ns_tr_retired` 太像、且不像判斷式
severity: minor
blocking: 否
引句:「def _ns_tr_prose_retire(ln):」
file: `scripts/lumos:29070`(`_ns_tr_retired`)、`scripts/lumos:29127`(`_ns_tr_is_new`)
1. `_ns_tr_retired(sp)` 是「條款本身標了 superseded」;`_ns_tr_prose_retire(ln)` 是「這行說明在講撤除」,同一個詞根、兩個意思,而且就在同一個 if 裡一起出現(`not _ns_tr_retired(sp) ... _ns_tr_prose_candidate`),容易讀混。
2. 鄰居的判斷函式用 `is_`/名詞形(`_ns_tr_is_new`、`_ns_tr_placeholder`),建議改成 `_ns_tr_prose_says_retire` 或 `_ns_tr_is_prose_retire`。

不對齊共 2 條,其中 major 0 條
