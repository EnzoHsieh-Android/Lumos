severity: major

## F1 預覽用拉之前載入的舊程式算,套用卻跑拉之後的新程式,兩邊會算出不同的區塊
severity: major
blocking: 是(不改的話,實作者會做出「預覽印的 START 行版本戳、甚至區塊算法,跟套用實際寫的不同」的預覽,違背做法第 2 點宣稱的「兩邊不會算出不同的結果」)
引句:「結尾印「確認後跑 `lumos update --no-pull` 套用剛才預覽的版本」」
file: `/home/user/Lumos/scripts/lumos:19808`
file: `/home/user/Lumos/scripts/lumos:20327`
全域 `lumos` 是 symlink 指到來源 clone 的 scripts/lumos(install 做的)。預覽流程是先 git pull 再算:程序在 pull 前已載入舊版程式,`LUMOS_VERSION`、`_START_TEMPLATE`、`_reinject_claude_block` 的算法都是舊的。接著使用者照結尾提示跑 `lumos update --no-pull`,這次載入的是 pull 後的新版程式,START 行用新的 `LUMOS_VERSION`(START 行在差異裡,見 `ReInjectResult` 的 diff 含 old_start_line)。結果:來源剛 bump 版本時,預覽差異顯示舊版本戳,套用寫入新版本戳;若新版改了區塊組法或目標選擇,差異更不同。S2 的測試用 `--no-pull`(沒有 pull,程式不變)抓不到這個情況。spec 的「靠 --no-pull 對上」只解決來源內容,沒解決程式碼本身也被 pull 換掉。

## F2 套用提示漏帶 --source(與 --allow-stale 情境),套用的可能是另一個來源
severity: major
blocking: 是(實作者照字面印固定字串,使用者用 `--source X` 預覽後照抄提示,套用會改用預設來源,裝的不是預覽的那一版,等於同意的內容跟實際寫入的不同)
引句:「結尾印「確認後跑 `lumos update --no-pull` 套用剛才預覽的版本」」
file: `/home/user/Lumos/scripts/lumos:20495`
`_lumos_src` 優先序是 `--source` > `$LUMOS_HOME` > 預設路徑;提示字串寫死,沒要求回填預覽時實際用的 `--source`。預覽時帶了 `--source` 的使用者,照提示套用就換了來源。

## F3 預覽會少報套用實際寫入的整檔改動(CRLF/BOM 整檔正規化)與工具指紋檔
severity: minor
blocking: 否(不影響區塊內容正確,是預覽對「規範檔會變成什麼」的揭露不完整)
引句:「所以每個目標檔都印完整差異。」
file: `/home/user/Lumos/scripts/lumos:20334`
`_reinject_claude_block` 讀入時整檔去 BOM、CRLF 轉 LF,只要區塊有差就整檔以 LF 寫回(程式註解 ★整檔都會被正規化★)。差異只比區塊(`old_start_line + old_body` 對新),CRLF 檔的其餘行全被改行尾,預覽的「完整差異」完全看不到。另外套用還會寫 `.lumos/vendored.json`(`_vendored_manifest_write`),做法第 5 點「其餘動作只列名」的清單漏了這一項(補設定骨架、hooks 路徑、全域 hooks 之外)。

## F4 「appended」「created」沒有現成差異,spec 沒說預覽怎麼算;AGENTS 檔是插檔首不是檔尾
severity: minor
blocking: 否(實作者會自己補,但 S2「跟套用寫進的內容一致」對這兩態無可比對的定義)
引句:「目標檔不存在(會新建)、有檔但沒有區塊(會接上)、區塊標記壞掉(不會自動改)也各講一句。」
file: `/home/user/Lumos/scripts/lumos:20352`
`diff` 僅 `updated` 帶值,created/appended 是 None。「各講一句」與「每個目標檔都印完整差異」互相不一致;appended 時 CLAUDE.md 接檔尾,AGENTS 檔插在第一個標題行後(影響 32 KiB 截斷),預覽講一句會漏掉位置;真的 update 對 AGENTS appended 還會印原內容前 8 行請人檢查語意衝突,預覽沒提。

## F5 回傳碼與 S4 措辭:來源 repo 自身路徑、broken、只換版本戳
severity: minor
blocking: 否
引句:「預覽成功回 0;來源無效、拉不下來照真的 update 的規矩回 2。」
file: `/home/user/Lumos/scripts/lumos:20931`
來源 repo 自身那條真的 update 在任一目標 `sentinel_broken` 或 `no_template` 時回 2,消費專案那條則一律回 0;spec 一句「成功回 0」沒分兩條路,預覽遇 broken 該回什麼未定。S4「沒有任何規範檔會變」也沒定義只有 START 版本戳不同(body 相同)算不算會變——真的 update 會寫檔(`old_start_line != start_line`)。

## F6 來源缺範本時預覽與套用不同;拆函式對 Check D 的約束未寫
severity: minor
blocking: 否
引句:「預覽時專案裡的範本還是舊的,所以改從來源的範本算。」
file: `/home/user/Lumos/scripts/lumos:3219`
真的 update 對「來源沒有該檔」是 `continue` 跳過(專案舊範本留著),預覽若直接讀來源範本會得 None/不同結果,須沿用同樣的跳過語意。另外 `_expected_claude_body(root, slug)` 同時被 doctor Check D(讀 `repo_root` 的範本)與 reinject 共用;spec 只說拆 `_reinject_claude_block`,沒寫明要把「範本來源」做成參數、Check D 與 init/無 hooks 路徑(`cmd_init` 呼叫 `_reinject_all`)仍讀專案自己的範本。實作者若改成預設讀來源,Check D 會拿來源範本比專案區塊而誤報漂移。

## 圖譜鏡頭與平行路徑
- 已讀、其餘各節(範圍、PRIOR-ART/RETIRE-IF、回退、天花板):無 finding。
- `--dry-run` 與 `--no-pull`:不拉,算現有來源,一致。與 `--allow-stale`:拉失敗沿用現有來源,預覽可行,但提示仍是 `--no-pull`,套用沿用同份來源,一致(受 F2 的 --source 問題影響)。與 `--source`:見 F2。
- `cmd_init` 共用 `_vendor_toolchain`:spec 拆預覽邏輯時須保持 init 路徑不變,spec 沒明講但「不做:改變不帶旗標行為」已涵蓋。
- 來源 repo 自身(`root.resolve()==src.resolve()`):預覽讀本地範本,正確;無 pull,`--no-pull` 無作用,spec 做法第 6 點與程式一致。
- 實務隱患:預覽跟套用對不上(見 F1、F2,spec 自述的隱患漏了程式碼自身被 pull 換掉這一種);不小心寫檔(預覽先 pull 會動來源 clone 的 jsonl 檢出與合併,但不碰專案,spec 已聲明拉的是來源);金流/對外送出/不可逆/守衛面:無,spec 排除理由成立。

最嚴重等級為重大,阻擋性 2 條(F1、F2)。
