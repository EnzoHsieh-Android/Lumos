severity: blocker
# r3 外家否決席(Codex)——棧別提問表態閘(末輪)

前輪九條驗收：

F1 已解：讀側明定依 kind 分別重建最後一筆 pass/skip 與 dispositions，兩種留痕不再互相擠掉。  
F2 已解：寫側順序改為治理帳先寫，失敗 rc2 且不寫 marker。  
F3 已解：`test:` 證據改用工作樹 discovery 加 `git grep` 對 `at_sha` 樹，未追蹤測試不能充證據。  
F4 已解：hook 編輯內容與 push diff 增刪行已分成兩個母體，只承諾共用 when 與正規化。  
F5 已解：推送判定明定同時掃增行與刪行，大改動門檻亦以兩者加總。  
F6 已解：`stack_questions` 保留整組題的舊語意，另增 applicable/meta。  
F7 已解：強制範圍已縮為分支 ref，tag 明文維持 advisory。  
F8 已解：最後一筆改以檔案行序判定，同 sha 後者覆蓋，並要求兩程序交錯測試。  
F9 未解：push-side 20 秒預算已補，但 hook 的 2 MB 宣稱仍被既有 8,000 字元／512 distinct token 前置截斷打穿。

### F10 — hook 掃描上限接錯層

severity: blocker  
blocking: 是；照 spec 實作 lumos 的 2 MB 上限，hook 仍只送入最前約 8 KB，後段觸發題會靜默漏掉。  
spec 段落：一、哪些問要答／效能預算；驗收條款 S3。  
問題：2 MB 上限放在接收端無法修復 `extract_delta_query` 的更早截斷，必須同步改傳輸形狀或明定 hook 直接傳完整 delta。  
查證佐證：file: `scripts/hooks/claude/impact-hook.py:412` 將 `cap_chars` 固定為 8000；file: `scripts/hooks/claude/impact-hook.py:434` 逐段截斷，file: `scripts/hooks/claude/impact-hook.py:437` 又施加 512 distinct token 上限，最後才於 file: `scripts/hooks/claude/impact-hook.py:790` 送給 lumos。  
引句:「改檔前的 delta 掃描上限 2 MB（超過只掃前 2 MB 並註記）」

### F11 — 表態分支座標無法對齊推送目的地

severity: blocker  
blocking: 是；合法的 `HEAD:另一分支名` 推送會讓表態永遠寫在本地 checkout 分支、check 卻按遠端目的分支查找，使用者無法用 spec 提供的命令解除阻擋。  
spec 段落：三、表態何時寫、閘放哪裡／寫側原語與 pre-push。  
問題：`dispositions <檔>` 沒有 branch 參數或座標轉移規則，但 pre-push 明定以 remote ref 分支核對；`--carry` 同樣不知道該讀本地還是目的分支。  
查證佐證：file: `scripts/lumos:21029` 寫側既有慣例固定取 checkout branch；file: `scripts/hooks/pre-push:197` 從 remote ref 取得 `_rbranch`，並於 file: `scripts/hooks/pre-push:202` 傳給 check。  
引句:「pre-push 對每個分支 ref 無條件呼叫 check」

### F12 — 壞 config 的核心閘語意未定

severity: major  
blocking: 是；設定檔解析失敗時，規格只裁定 `test:` 證據要 BLOCKED，卻沒裁定 gate 模式與 ask-all 門檻，守衛可能在同一錯誤下分別 fail-open、套預設或阻擋。  
spec 段落：一、大改動全問；三、閘條件與 `.lumos/config.json` 壞掉時。  
問題：值域錯誤已有 fallback，但整份 JSON 壞損缺少單一解析結果及 `gate`／`ask_all_over_lines` 行為矩陣；應把解析失敗的適用性與強制語意納入 S5。  
查證佐證：file: `scripts/lumos:17529` 的既有 `_ci_config` 對同一設定檔採解析失敗即功能全關，證明不能靠「直讀慣例」推導本案應採何種安全方向。  
引句:「設定檔壞掉時：`test:` 證據一律判「無法驗證：設定檔解析失敗」」

最後一行總結：最嚴重 severity：blocker；blocking 共 3 條。
