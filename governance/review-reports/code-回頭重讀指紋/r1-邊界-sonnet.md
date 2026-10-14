severity: minor

我在臨時目錄實跑了約 30 種邊界,實驗目錄已刪。結果是沒有找到會漏判(該重讀卻當成已對照)的 blocker 或 major。找到 2 個 minor。

已實跑、行為正確(改動前後指紋都不同,或安全退回 v1):
- 檔名帶空白、`-` 開頭、`[a]`、`*`、tab、雙引號、換行、NFD。
- 非 UTF-8 檔名位元組,以及非 UTF-8 的內容。
- 符號連結改目標、子模組指標改版、只改檔案模式、刪檔、新增空檔(含加執行權限)。
- 二進位檔、換頁符號、CRLF 對 LF、檔尾無換行。
- 型別變更(退回 v1,原因記「型別變更」)。
- about_code 是資料夾或拼錯(退回 v1,原因記「樹裡找不到」)。

severity: minor
blocking: 否 — 只會多提醒(誤報方向),不會漏判,而且提醒本身不擋推送。
引句:「macOS 預設把參數轉成 NFC,樹裡存 NFD 時傳原樣路徑也會得到空 diff」
問題:v2 指紋那次 `git diff` 的 `-diff`/文字判定取自目前簽出的工作樹的 `.gitattributes`,不是取自被推的頂端。
具體失敗情境:
- feat 分支新增 `*.dat -diff`,並改了 `x.dat`。
- 在 feat 簽出時算指紋是 `bf6b3583…`;換成在 main 簽出、用 feat 的頂端算,是 `cfca7f48…`。
- 所以「簽出另一個分支再推」或「作者本機與 CI 的 `.gitattributes` 不同」會讓指紋對不上,重新要求重讀。
- 目前的測試(`t_reread_fp_same_for_prepare_and_check` 的 ④、⑤)只驗了「簽出不同分支但屬性檔相同」。
- 可以用 `--attr-source=<頂端>` 或 `GIT_ATTR_NOSYSTEM`、`core.attributesFile=/dev/null` 釘住。本機 git 2.39 沒有 `--attr-source`,要先確認支援的版本下限。
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos` 的 `_NOTE_REREAD_FP_GIT` 沒有釘屬性來源。

severity: minor
blocking: 否 — 這是測試缺口,行為本身實測正確,但改壞不會翻紅。
引句:「在本機重現要靠刻意寫錯的旗標,不另造」
問題:下面這些分支沒有任何測試走到,拿掉或改壞對應的程式,測試仍然全綠。
- 單檔退回:「太大」(`_NOTE_REREAD_FP_MAX`)、「型別變更」。
- 整篇退回:「樹裡找不到」(資料夾或拼錯的 about_code)。
- 路徑與檔案種類:`--literal-pathspecs` 對 `[x]`、`*` 檔名;符號連結、子模組、刪檔、新增檔。
- 我檢查了測試 patch,沒有出現對應的 `[x]`、`*` 檔名或這幾種檔案種類的案例;patch 註解還明說 `:(literal)` 前綴「不另造」。
具體失敗情境:
- 某天有人把 `_note_reread_fp_file` 的 `ent["status"] == "T"` 判斷刪掉。型別變更時 `git diff` 會輸出刪除加新增兩段、同名,`files[name]` 被後一段覆蓋,前半段內容改動不進指紋。
- 或者有人把 `--literal-pathspecs` 拿掉:`*.py` 檔名會把別支檔的 diff 混進指紋。
- 兩者目前都沒有測試會紅。
建議:各補一條帶這些檔案種類與檔名的案例,並確認拿掉對應旗標或判斷時會紅。

已讀,無 finding:
- `--raw -z` 解析(`_note_reread_fp_parse_raw`):成對取中繼與路徑、遇到不以 `:` 開頭的標記就略過,NFC/NFD 同鍵時照原樣位元組排序。
- 分岔點的取法(`_lens_default_base`):只有本機主線、沒有遠端 → 退回 v1;頂端等於分岔點 → 退回 v1;偵測到 HEAD 與其他分支(detached HEAD)走「零條分支 → origin」路徑。
- 交叉合併:分岔點交給 `_push_pick_base` 取歷史最長的,結果不隨順序變。
- `_codeloop_default_base` 搬成共用函式:行為與舊版等價。
- 紀錄歸屬判斷(`_note_reread_own_fps`):擋複製改名與 cherry-pick 的邏輯成立。
- `_patch_file_changes` 兩個新參數:預設值不變,資安席舊路徑不受影響。

最高等級 minor,blocking 0 條。
