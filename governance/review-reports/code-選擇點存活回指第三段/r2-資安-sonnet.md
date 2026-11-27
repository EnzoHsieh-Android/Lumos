severity: clean

我讀了 r2-snapshot.patch 裡 scripts/lumos 新增的 choice-layer 整段(材料產生、分份與旁檔、結果檔驗證、判讀檔寫入與讀回、撤回),並對照 repo 內 `_write_lf`、`_repo_path_unsafe`、`_choice_layer_doc_read`。我沒有實際執行任何指令或構造輸入。

**①提示注入:已看,無。** 進到判讀代理材料的自由文字,是計劃的條款與正文、存活行的程式碼。這些本來就是被判讀的對象,也是作者可控的 repo 內容,屬既有設計。代理的輸出不會被直接執行,而是先過驗證才寫入:
- 每筆 file+fp 必須在清單裡。
- layer 必須是 1 到 4 的整數,欄位有字數上限。
- basis 的 plan 必須是材料涉及的計劃,where 必須是真實的條款號或段名。
- 引句長度要在範圍內,且必須逐字出自那一條或那一段。

第 4 層(建議等價)的 reason 只檢查字數,但後續的放行仍要人確認(lint-waive),不會自動過閘。所以這一層沒有可直接利用的路徑。

**②讀寫與執行越界:已看,無。**
- 清單編號限定 12 位十六進位(`re.fullmatch`),不能帶路徑。
- 分份檔名由清單編號和份數組成,旁檔名是清單編號加計劃路徑的雜湊前 12 碼,檔名都不是外來字串。
- 工作目錄走 `_note_audit_work_dir` 與 `_note_audit_safe_dir`,逐層擋符號連結並確認解析後在 repo 內。
- `_choice_layer_prune` 跳過符號連結、只刪一般檔。
- 旁檔和判讀檔都用 `_write_bytes_atomic` 寫,內部是暫存檔加 `os.replace`,換掉的是目標名本身,不會順著連結寫出 repo。
- 推送閘讀判讀檔時,`_choice_layer_doc_read` 要求路徑開頭是 governance/choice-layers/,檔名是 64 位十六進位,檔名等於事件記的 `judgment_sha`,內容雜湊也等於檔名,且有單份大小上限。帳上的 judgment 路徑無法指到別處。
- 寫入端的雜湊和 `json.dumps(sort_keys=True, indent=1)` 的 body 一致,與讀端驗法對得上。
- 這段沒有 shell 插值(`subprocess` 只在既有的 git `checkout` 一處,用 `:(literal)` 並限制 `.git`)。
- 新增內容沒有密鑰或信箱。

**③非刻意、一步就能繞過的守衛:已看,無。**
- 判讀整份先驗證,任一筆不合就整份拒收、什麼都不寫。
- 寫入前先預檢每份判讀檔的大小,不會寫到一半停住。
- 結果檔用 utf-8-sig 讀,帶 BOM 照讀,形狀不合就走 `_choice_layer_reject`,不會丟堆疊。
- 引句原始長度先擋,再比對實字數。
- 照平常一個指令或一次編輯,我找不到能讓判讀記進帳卻沒過驗證的路徑。
- 旁檔在 gitignore 的工作目錄裡,只供判讀代理閱讀,沒有進任何放行判斷。

總結:最高等級是 clean
