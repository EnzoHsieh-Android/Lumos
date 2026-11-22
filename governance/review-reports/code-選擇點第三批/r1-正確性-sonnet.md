severity: minor

整體來說,逐 hunk 讀完、也實跑過,沒找到會做出錯誤壞法或損壞資料的洞。我檢查的主要項目如下:

- **retry、retryWhen 壞法**:拿掉呼叫都只刪到 `$A` 結尾到命中結尾,沒有刪過頭。實跑了這些寫法:換行、`?.`、鏈式、多個 retry、帶註解、`!!`、括號接收者、尾隨 lambda、多行引數、CRLF、字串樣板,產出的壞法文字都對。
- **`_choice_also`**:作用域兩列在檔頭單獨 import 原寫法時才補兄弟 import。第二批以前的 `運算元起始` 列沒有帶 import 的,所以沒有被誤補。
- **ERROR 覆蓋**:實跑 `}.retry(3)`,接收者前面有 ERROR 時照樣挑出。接收者已是 `$A` 全段,壞法一定只刪 `.retry(...)`,所以放過錨點前的 ERROR 是安全的。
- **規則**:C-38 到 C-55 用 `ast-grep` 實跑三十多種寫法,命中與排除都符合計劃預期值表。深巢狀 150 層的輸出最大約 190KB,沒有輸出爆量。
- **測試**:`python3.14 scripts/test_lumos.py -k batch3` 跑了 80 項全過,真 ast-grep 那幾支沒有被略過。我的 `choice-points --diff 855ef9bbb..763081c0d` 顯示改到的行 0,代表新樣本檔沒有被當產品碼掃到。
- **對照記錄**:自我變異記錄的 30 處守衛都有對應測試,我沒再找到沒被守到的關鍵分支。

**圖譜鏡頭**:固定席節點沒有附上,不逐條答。依 diff 判斷,改動只加了第三批的列、錨點「整個呼叫」和補 import 的分支。既有六種錨點的行為沒變,第二批 S7 釘值測試(`-k batch2`,68 項)全過,可佐證。

**角色卡**:這次沒有對外 API 欄位,也沒有端點或授權邏輯,be-api-compat 和 be-authz 兩題不適用。

## c1 C-48 的排除把顯式 `onBufferOverflow = BufferOverflow.SUSPEND` 也一起排掉
severity: minor
blocking: 否

引句:「帶 onBufferOverflow、又沒有值不是 0 的 extraBufferCapacity」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(C-48 的 `not: all: [has onBufferOverflow, not has extraBufferCapacity…]`)

失敗場景:只要引數清單裡有名叫 `onBufferOverflow` 的引數,規則就排除,不看它的值。`MutableSharedFlow<Int>(replay = 1, onBufferOverflow = BufferOverflow.SUSPEND)` 的 `SUSPEND` 是預設值,`replay` 換 0 之後仍然合法,建構不會丟例外。這個寫法本來該命中,卻被排除,改到這一行時沒有人被詰問「晚到的訂閱者要不要看到上一個值」。

重現:一支只有兩行的 Kotlin 檔,第一行是上面那個 `SUSPEND` 寫法,第二行是 `MutableSharedFlow<Int>(replay = 1)`。用 `ast-grep scan --config configs/ast-grep/kotlin-choice/sgconfig.yml` 掃,輸出只有第二行的 `C-48`,第一行沒有命中。

總結:最高嚴重度 minor,blocking 共 0 條
