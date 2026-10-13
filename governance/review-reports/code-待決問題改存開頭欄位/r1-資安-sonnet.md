severity: minor

逐類結果如下。

**1. 不可信輸入流到危險操作**

- **命令注入,`_pq_git_show` 與 `git_range`:已看,無可利用的洞。**
  - 參數是 list,沒有 shell,也沒有 `shell=True`。`path` 來自 `git diff --name-only` 的輸出。它前面有 `rev:` 綴著,而且必須以 `vrel + "/"` 開頭並以 `_計劃.md` 結尾,所以不會被當成選項。
  - `rev` 來自 `git_range` 的 `re.fullmatch` 切分,可能以 `-` 開頭,例如 `--output=…`,而組成 `f"{rev}:{path}"` 時 `rev` 在最前面。但 `git_range` 來自本機 pre-push 掛鉤傳入的 sha 範圍,陌生 repo 的內容送不進這個值。同一個字串已經被既有的 `git diff --name-only <git_range>` 原樣使用,這次改動沒有增加新的暴露面。我寫不出誰能控制它,所以不立為發現。
  - `git show <rev>:<path>` 只讀 object db,沒有路徑跳出圖譜資料夾的問題。
- **路徑與模板注入:已看,無。**
  - `pq_parse` 與 `_strict_list_scan` 只用 regex 做字串判斷,沒有 eval、反序列化或模板。
  - `question-add` 與 `question-set` 的寫入檔案路徑是 `env.vault / rel`,`rel` 由 `env.find` 解出。`_pq_fmt` 擋掉換行、CR、tab,並用 `_yaml_plain_ok` 與 `_yaml_quote` 處理引號。命令列參數無法換行,所以無法在 frontmatter 注入第二個鍵或另起一題。
- **題目文字含終端控制字元:有發現,見下。**

**2. 登入與權限、守衛繞過**

已看,無。惡意計劃最多讓 `spec-gate` 回 1 或多印提醒,方向是更嚴。推送前提醒明確不改回傳碼。讀不懂時 `_pq_push_remind` 只 `continue`,不放行也不擋。這同時是一個可被利用的「繞過」入口,但我沒找到攻擊路徑:要在讀不懂時繞過風險低計劃的閘,仍然走原本的 `_spec_gate_push_scan`,沒有被改動。

**3. 密鑰與個資**

已看,無。錯誤訊息只含欄位行號與被截斷的 40 字內行內容(`raw[:40]`、`v[:40]`),都是筆記自己的 frontmatter 內容。這次改動沒有新增帳檔寫入,也沒有環境變數或檔案內容外寫。

**4. 加密與傳輸**

已看,無。

**5. 執行邊界**

已看,無。這次改動沒有新增 hook、安裝腳本或 CI 執行的檔案,沒有寫入全域設定。新增的 `subprocess` 呼叫(測試檔以外)只有 `_pq_git_show` 一處,固定執行 `git`。

**6. 行動端**

不適用。

**新依賴**

無。

---

**發現 1:題目文字不過濾終端控制字元,直接印到終端**

severity: minor
blocking: 否
引句:「print(f"    • {q['id']} [{q['stage']}/{q['status']}] {q['text']}")」
- 攻擊路徑(推論,因為依終端而定):誰是陌生 repo 或協作者的惡意提交者。從 repo 內的 `_計劃.md` frontmatter 進來。送的是 `pending_questions` 裡 `text:` 含 ESC(0x1b)、OSC 或 CSI 序列的題目,例如用雙引號包住、內容有清屏或移動游標的序列。`_strict_scalar` 只擋空值、`|>[{` 開頭與引號寫法,不擋控制字元。拿到的是受害者跑 `lumos spec-gate`、`lumos pitfalls --stage` 或 push(`_pq_push_remind`)時,終端被偽造或覆蓋輸出,例如蓋掉「✗ 不能進實作」或偽造「✓」行。因為回傳碼與寫入內容不變,實際只是欺騙顯示。
- 同族出口:`_pq_push_remind` 的 `{q['text']}`、`_pitfalls_stage` 的 `{q['text']}`。
- 佐證 file:`scripts/lumos`(r1-review.patch 第 851、878、1204 行的新增列)。
- 建議方向:`_strict_scalar` 讀入時就拒絕 C0 控制字元(除了已擋的換行與 tab),或在三個印出處統一過濾。寫入端 `_pq_fmt` 目前也只擋 `\n\r\t`,可一併擋。

總結:這份 diff 沒有可直接利用的洞(沒有命令、路徑或反序列化注入,沒有繞過守衛,沒有新依賴),只有 1 條縱深防禦類 minor,是題目文字的終端控制字元沒過濾。
