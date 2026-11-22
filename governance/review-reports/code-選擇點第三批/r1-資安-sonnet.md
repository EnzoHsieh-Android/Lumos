severity: clean

## 三類逐類結果

**① 提示注入:已看,無新增面。**
- 新增的「整個呼叫」錨點與 `_choice_also` 擴充,只改變壞法落在哪、補哪個 import。
- 補 import 的字串 `import {imp}` 來自型錄「需補的 import」欄,並受 `_CHOICE_IMPORT_RE` 限制,只能是 `套件.名稱` 形式,被掃的 Kotlin 原始碼無法控制它。
- `_choice_also` 中取自原始碼的 `orig`(`b[s:e]`)只用來跟檔頭 import 比對,不會進入輸出文字。
- 壞法 `old`/`new` 含被掃原始碼的原文並進入派工與治理帳,這是第一、二批既有的外來文字回顯,依威脅模型放行,本批沒有新增回顯路徑。

**② 讀寫與執行越界:已看,無。**
- `drop_call` 的編輯是 `(mv["A"][1], e, b"")`,兩端都來自 ast-grep 對同一份位元組的位移,編輯只作用在記憶體中的位元組,不產生路徑,也不寫檔。
- 位移不合理時不會寫到範圍外。`_choice_anchor` 先用 `_CHOICE_GAP_SKIP_RE.match(b, mv["A"][1], hit["e"])` 和 `_CHOICE_CALL_NAME_RE.match(b, k, hit["e"])` 找方法名。
- 若 `$A` 結尾超過命中結尾,或後面接不到 `.`/`?.` 加識別字,`pos` 超過 `endpos` 會讓比對回 None,`_choice_anchor` 回 `(None, None)`,該命中被丟棄。
- 能產生編輯的命中,錨點一定落在 `[mv["A"][1], e]` 之內,所以 `drop_call` 的起點不會大於迄點,不會因負向切片誤刪。
- 測試裡的 `subprocess.run([sg, "scan", …])` 是參數清單,不經 shell。`sg` 由既有的 `_ktpack_sg()` 解析,規則與原始碼檔都寫在 `tempfile.mkdtemp` 的暫存目錄。
- 新增檔案中沒有密鑰、信箱,也沒有可被環境變數覆蓋的下載網址。

**③ 非刻意、一步就能繞過的守衛:已看,無。**
- 新的 ERROR 判定改成「錨點行到命中結尾」,涵蓋範圍變窄,但目的是避免 `.retry` 被接收者裡的語法錯誤靜默吃掉,不是新增一條讓守衛被意外走過的路徑。
- 這個改動沒有引入 `LUMOS_SKIP_*` 或環境變數相關的分支。

總結:最高嚴重度 clean,blocking 共 0 條
