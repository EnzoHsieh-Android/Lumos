severity: clean

# 代碼審第 3 輪 正確性-opus:回頭重讀守檔筆記(第 2 輪修正本身)

沒有 blocking 級或修法錯誤。以下是實際跑過的查證,除了第 3 條的 `lumos gov` 為了讀真實帳在 /Users/enzo/harness/lumos-toolchain 跑(唯讀指令,跑完確認使用帳沒有多寫一行),其餘都在自己的 clone(`git clone --shared` 到 hcc-r3-work-正確性-opus/repo)裡做;沒有對任何 repo 下 git 寫入指令。

## 查證紀錄(不是 finding)

1. **留痕有效性新判法,拿真實歷史比新舊版**:把 94c1e82f 版的 scripts/lumos 當舊版、HEAD 當新版,各自在行程內載入,沿本 repo 第一親代鏈最近 500 個提交,每個提交 c 配上往前 1、3、10 個提交當紀錄點(共 1486 對),兩版各跑一次 `_codeloop_record_valid`。結果:**判定不同 0 對**;舊版判有效 185 對、新版也是 185 對;沒有一對超過 2 秒。另對三個動到 `governance/replay/.weekly-stamp`、`.rotation-cursor`(簿記資料夾裡目前僅有的兩支沒副檔名的檔)的真實提交,直接呼叫 `_codeloop_bookkeeping_code`,三個都回 False(不算程式),也就是批次讀取首行那條路在真實戳記檔上判對了。
   file: `scripts/lumos:37978`
2. **共用路徑守衛抽出後兩邊的行為與訊息**:筆記內容審那邊,連結/不是資料夾/跑出 repo 三種訊息與舊版逐字相同;差別只有兩處、都是變好:跑出 repo 的路徑現在在建資料夾之前就擋(舊版先 mkdir 到 repo 外再拒收),建好後重查也改成逐層查。存量漂移那邊,連結與跑出 repo 的訊息照舊,只有 OSError 的訊息從「出錯那一層」改成「帳檔路徑」,沒有測試或呼叫端依賴那段字。`-k repo_path_guard` 8 綠、`t_drift_fix_*` 十支逐支跑都綠(一次把 `-k drift_fix` 整批丟下去時被環境用 144 砍掉,輸出是空的;逐支跑都過,判斷跟這次改動無關)。
   file: `scripts/lumos:26409`
3. **`lumos gov` 跳過非物件行不會漏算合法事件**:本機真實的八本帳(治理帳 98392 行、canary 2264 行…)逐行解析:壞 JSON 0 行、合法但不是物件的 0 行。舊版與新版 `lumos gov --since 400`、`--stats` 的輸出逐位元組相同(6676/6754 行)。舊版遇到非物件行會丟 AttributeError 整個當掉,所以新版跳過的那些行,舊版本來就一筆都沒算進去,不算漏。帶 U+2028 的合法事件被 splitlines 切碎、整筆算不進去這件事新舊一樣,不是這次引入的;而回頭重讀自己寫帳的路徑已先清掉那類字元。
   file: `scripts/lumos:7264`
4. **prepare 略過工作目錄紀錄的口徑**:`wip = 工作目錄紀錄 - 已提交紀錄`,只拿來略過跟提示;check 照舊只認已提交的,所以推送前的提醒不會因為工作目錄的檔被放掉。`--all` 照舊全產。工作目錄紀錄只比檔名裡的對照指紋、不讀內容,這跟 check 認已提交紀錄的方法一樣,正規式也擋掉 .tmp 殘檔。`-k prepare_skips_uncommitted` 4 綠。
   file: `scripts/lumos:27112`
5. **Unicode 類別過濾**:`_NOTE_REREAD_CTRL_RE` 沒留下舊的引用;`unicodedata` 在模組頂端已 import;項目檔頭的兩個指紋欄位在解析時已限定 16 位十六進位,寫帳的路徑也過 `_note_reread_show`,治理帳不會再被這條路寫進行分隔字元。`-k unicode_separator` 3 綠、`-k gov_skips` 2 綠、`-k code_loop_bookkeeping` 9 綠、`-k codex_dispatch_stdin` 1 綠、`-k nodehome_side_deadline` 4 綠。
   file: `scripts/lumos:26755`

最高等級:clean
