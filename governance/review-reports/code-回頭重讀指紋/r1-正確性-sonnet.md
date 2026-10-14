severity: minor

以下是正確性席對 patch 的審查結果。我讀完主程式 patch 與工作樹上的相關函式,另外在臨時 git repo 跑了 `_note_reread_contrast_fp_v2`(包含模式變更、符號連結、資料夾、拼錯路徑、主線前進)。沒有找到 major 以上的漏判路徑。

## Finding 1:同一段改動搬到別的函式,只要前後三行相同,v2 指紋不變

severity: minor
blocking: 否 — 要前後各三行完全相同才會撞指紋,而且判定者看過的是同一段文字的改動,風險小;但這是 v2 專門放寬出來的新漏判面,v1 不會有

引句:「headers=False:`@@` 後面的段落標頭(函式名)不算——標頭取自 hunk 之前最近一行頂格的行」

問題:v2 把 `@@` 行號和函式名標頭都拿掉,只剩 hunk 內的增刪行與前後三行。資安席原本就是為了擋「同一段 `-check(user)/+allow(user)` 從公開端點搬到管理員端點」才加進函式名標頭(見同一函式文件字串的 r3 外家實測)。v2 把這道擋拿掉,而且沒有以位置或標頭以外的東西補回來。

失敗情境:
- 輸入:筆記 N 的 about_code 列了 `f.py`。作者在 `check_a` 加上 `+    allow(user)`,前後三行是 `x = 1`、`y = 2`、`z = 3`。判定者讀這份 diff,紀錄以 v2 指紋存檔。
- 之後作者把這行改加在 `check_b`(複製貼上出來的相似函式,前後三行相同),`check_a` 那邊還原。
- 結果:`bp..tip` 的 diff 只差行號和函式名,v2 指紋相同,`_note_reread_hits` 判成 "v2" 已對照。判定者從沒看過 `check_b` 的改動,N 裡講 `check_b` 的句子沒人重讀。
- 實測:對兩份只差行號(10 與 90)和函式名(`check_a` 與 `check_b`)的 patch 呼叫 `_patch_file_changes(headers=False, lf_only=True)`,回傳的雜湊完全相同(`0a85cc7f…`)。

佐證:file: `scripts/lumos:26054`(函式文件字串)、`scripts/lumos:26085-26092`(`headers` 分支)、`scripts/lumos:36330`(v2 呼叫 `headers=False`)。
補強方向:v2 的 hunk 序列可以多帶「該 hunk 在檔內第幾個改動段」,或帶 hunk 之前一個不頂格的錨點行;不補的話,RETIRE-IF 抽查要特別找這一類。

## Finding 2:v2 因判定者材料被縮短退回 v1,這件事 check 看不到

severity: minor
blocking: 否 — 只會多擋(要重讀)不會漏判

引句:「cuts 給一個 list 時,有任何一支檔的內容被截掉(走到平均截斷、接了「[截斷:」那行)就在裡面放一個 True」

問題:退回 v1 的判斷只在 `_note_reread_item`(prepare)裡做。`reread-check` 的 `_note_reread_fp_info` 不組判定者 diff,所以對這篇仍算出 v2,並把 v2 指紋印在 "對照指紋" 後面。

失敗情境:
- 輸入:某篇的 about_code 裡有 `scripts/lumos` 這類大檔,分岔點到頂端的 diff 超過 100000 字。
- prepare 把紀錄改記成 v1 檔名,但 check 這篇仍印 v2 指紋。
- 每次主線帶進 about_code 檔的改動,v1 指紋就變,v1 紀錄失效;check 又不會命中 v2。結果是主線每前進一次就重新擋一次,這正是這個功能要消除的症狀。
- `prepare_todo` 也用 v2 指紋去對工作目錄的未提交紀錄,對不上而重派。

佐證:file: `scripts/lumos:36631-36653`(`_note_reread_item` 的 `cuts` 退回)、`scripts/lumos:36340-36351`(`_note_reread_fp_info` 沒有截斷判斷)、`scripts/lumos:37085-37090`(`prepare_todo` 用 `fps[rel]`)。

## 已讀,無 finding

- **v1 一字不改**:`_note_reread_contrast_fp` 只動了文件字串,雜湊輸入沒變,所以升級前的紀錄照舊算數。
- **判「已對照」順序**:先 v1,再 v2;v2 要求紀錄是這條分支自己新增的。
  - 三個條件的實作(分岔點樹裡沒有該檔名、內容的 `contrast_fp` 等於檔名前 16 字、範圍終點不是分岔點的祖先)方向都對。
  - 祖先判斷:`merge-base --is-ancestor` 的回傳 1 表示不是祖先,視為分支自己的。回傳 128 且本機找不到該提交,也視為分支自己的。逾時當作不是分支自己的。
  - 紀錄資料夾在分岔點不存在時,`_note_reread_tip_names` 回空集合而不是失敗,所以不會把所有 v2 擋掉。
- **退回 v1 的路徑都走到**:
  - 無遠端主線、在主線上、樹裡找不到(含資料夾與拼錯)、全部未改、型別變更、太大、diff 空、逾時、材料被縮短。
  - 實測:資料夾、拼錯、全是未改的符號連結都回 `樹裡找不到` 或 `全部未改`,沒有拋例外。
  - 只改模式(`chmod +x`)的檔仍算出指紋。
  - 主線改了 `f.py` 的別處,指紋不動。
- **分岔點**:
  - `_lens_default_base` 搬出後 `_codeloop_default_base` 行為不變(同樣的遠端判斷、候選、取最長歷史)。
  - 回頭重讀不加本機 main/master。
  - 預算逾時時會回 None,於是退回 v1。
- **逐檔 diff**:
  - 全域旗標放在 `diff` 之前,沒有 `:(literal)` 前綴,`-U3`、`--no-renames`、`--full-index`、hunk 釘住和 `diff.suppressBlankEmpty` 都釘上。
  - `_patch_file_changes` 新參數預設值不改資安席的行為。
  - `lf_only` 用 `split("\n")` 不會在換頁符號切行。
  - `--raw -z` 的解析、NFC 與 NFD 同鍵多項、大小檢查(`cat-file --batch-check`)都沒有漏的地方。
- **資料狀態**:
  - 新舊互讀:舊程式讀新的 v2 檔名只會多擋;新程式讀舊紀錄走 v1。
  - 寫一半:紀錄寫入沿用既有的原子寫。
  - 衍生資料:`scan["fpinfo"]` 與 `scan["fpfile"]` 只存在於一次掃描內。
  - 時間:預算保留 3 秒,逾時只會讓 v2 退回 v1,方向是多擋。
  - 不可逆:沒有新增不可逆寫入。
- **事件欄位**:
  - `branch` 欄不會被代碼審留痕的讀者誤讀,因為那些讀者先限定 `gate == "code-loop"`。
  - `_gate_event_fit` 就地縮減同一個 `extra`,量與寫的是同一行。
  - `note-reread` 的 covered、none、reminded 走本機帳,所以 12 月的抽查要合讀兩本帳。

最高等級 minor,blocking 0 條。
