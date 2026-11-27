severity: clean

已看,無可利用的洞。三類逐類結論如下,最後附幾項已核對過的點。

**①提示注入:已看,無。**
- 判讀材料裡的壞法原文、改壞後原文和包住那一行的程式碼,都用「比內容最長反引號串多一個」的圍欄包起來(`_choice_layer_fence`),無法用反引號跳出圍欄。
- 判讀結果回顯到 choice-points 與存活清單時,引句、問題、理由都過 `_kill_esc` 並截到 `_CHOICE_LAYER_SHOW` 字。
- 判讀結果的 `basis` 要求 `plan` 屬於該份材料涉及的計劃、`where` 是真實的條款號或段名、`quote` 必須逐字出自那一段,所以外來的自由文字進不了條款引用。
- 計劃正文沒有圍欄,已放行記在議題第 19 條,不重報。

**②讀寫與執行越界:已看,無。**
- 配方寫檔路徑:`_kill_target` 先對 `os.path.join(wt, file)` 做 `realpath`,再要求落在 `wt_real + os.sep` 底下,所以 `../`、絕對路徑、指向工作樹外的符號連結都過不了。它另外逐段(不分大小寫)擋 `.git`,工作樹裡的 `.git` 檔案、`.GIT` 和指進 `.git` 的符號連結也擋得住。逐支流程、合併快篩、合批編譯三處共用這道圍欄。
- 還原:`git checkout -- :(literal)<相對路徑>` 照字面認路徑,不會被 pathspec 魔法展開;`restore()` 直接寫回原文時用的 `t` 也來自同一道圍欄。
- 判讀檔以內容雜湊當檔名。讀端 `_choice_layer_doc_read` 要求路徑符合 `governance/choice-layers/<64 位十六進位>.json`、檔名等於 sha、內容雜湊對得上,並有大小上限和形狀檢查,攻擊者無法用 `../` 指到別處。寫端經 `_note_audit_safe_dir` 拒絕符號連結和越出 repo 的目錄,檔案寫入走 `_write_bytes_atomic`(O_EXCL 暫存檔加 `os.replace`),`os.replace` 取代符號連結本身而不跟過去。檔名可預測,但要預先植入連結還得猜到檔案內容雜湊,不可行。
- 清單編號 `--list` 用 `[0-9a-f]{12}` 的 `fullmatch`;旁檔路徑由工作目錄加清單編號加計劃路徑雜湊組成,沒有外來字串進路徑。
- `_choice_layer_prune` 只刪非符號連結的一般檔,且先過 `_repo_path_unsafe`。
- 新增的 `governance/choice-layers/` 進 `_BOOKKEEPING_DIRS`,只影響紀錄與程式碼的分類,不會執行任何東西。
- 沒有新增 shell 插值,`subprocess` 都是 list 形式的引數;patch 內沒有新寫入的密鑰或信箱。

**③非刻意、一步就能繞過的守衛:已看,無。**
- 判讀的有效性(`pending` 與 `new_sha` 比對)取決於 `deps_sha` 指紋。計劃或條款一改,指紋就對不上,判讀變成「待複核」,不會因為平常的一次編輯就被放行。
- 撤回(layer 0)要求至少 `_CHOICE_LAYER_REASON_MIN` 個實字的理由,且該行必須是帳上有判讀的存活行。
- `_kill_revert` 還原失敗(回 None)會讓整組作廢;`restore()` 在 checkout 失敗後也會比對內容,對不上才中止,不會靜默放過。

總結:最高等級是 clean
