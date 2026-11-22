severity: clean

三類都已看過,沒有可利用的洞。這輪改動只動到兩處:本機解析 Kotlin 原始碼、產生壞法的函式,和只跑固定 ast-grep 規則與測試的程式。沒有新增 hook、安裝腳本、CI、下載網址或環境變數入口。

**① 提示注入:已看,無。**
- 這批改動沒有新增把自由文字(筆記、檔名、分支名、帳本欄位、席報告)送進派工詞或 hook 附加段的路徑。
- 新程式只用位元組位移與正規式比對 Kotlin 原始碼。
- 命中的原始碼文字(`_choice_also` 取的 `orig`)只拿來跟 import 行做字串比對,沒有拼進指令或派工詞。

**② 讀寫與執行越界:已看,無。**
- 新增的 `_cb_points` 和 S9 測試只在 `tempfile.TemporaryDirectory` 底下寫檔。
- 它們以 list 形式呼叫 `subprocess.run([sg, "scan", …])`,沒有 `shell=True`,也沒有用外來字串拼命令。
- `sg` 來自既有的 `_ktpack_sg()`,這批沒改它。
- 規則檔路徑由列號 `row['id']` 組成,列號來自型別表,不是外來輸入。
- 新增的 `api.yml` 規則只含 `regex` 與關聯規則,不執行任何東西。
- 已用正則掃過整份 r2-snapshot.patch,沒有信箱、金鑰、token、curl 或 wget 這類字樣。

**③ 非刻意、一步就能繞過的守衛:已看,無。**
- 「整個呼叫」錨點對 ERROR 覆蓋的起算行改成「錨點行起」(`_choice_err_start`)。
- 這只影響某個壞法會不會被產出,不影響任何安全守衛。
- 沒找到「使用者本人或照常操作的 AI 用一個指令或一次編輯就意外走過去」的路徑。
- 擁有者的 ast-grep 找不到時,舊的 `_cb2_points` 回 None、新的 `_cb_points` 在 skip 給了時 raise `_SrcOnly`,只是跳過測試,不是守衛旁路。

總結:最高嚴重度 clean,blocking 共 0 條
