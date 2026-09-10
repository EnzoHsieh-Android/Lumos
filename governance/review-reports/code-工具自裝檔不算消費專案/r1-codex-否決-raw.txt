severity: blocker

### F1 目錄級略過把使用者自己的 hook/template 程式永久藏掉

severity: blocker  
blocking: 是 — 消費專案可把自己的程式放入永久略過範圍，high tier 守衛不會要求 code-loop。  
引句:「return r in _VENDORED_TOOLKIT or any(r == d or r.startswith(d + "/") for d in _VENDORED_DIRS)」

1. 這個前綴判斷將 `scripts/hooks/**` 與 `scripts/templates/**` 全數視為 Lumos 所有，無法分辨安裝檔與使用者後加的檔。  
file: `scripts/lumos:12976` deinit 明定保留這兩個目錄內的使用者自有檔。  
2. pre-push 以 `pitfalls --no-lint` 的 claims tier 決定是否要求代碼審，略過後會直接降為 standard。  
file: `scripts/lumos:22603` 守衛直接取 pitfalls 的 tier。  
3. 最小翻紅測試（未執行，遵守只讀）：在無 `skills/lumos-project-notes/SKILL.md` 的消費 repo 新增並提交 `scripts/hooks/custom.py` 內的 `open("x")`，`pitfalls --diff HEAD~1..HEAD --no-lint --json` 應回報該檔並為 high；目前會是零 claims、standard。

### F2 about_code 的「repo 內」檢查可用絕對路徑或 .. 跳脫

severity: major  
blocking: 是 — 新寫入守衛宣稱只接受 repo 內路徑，實際可寫入 repo 外的壞引用。  
引句:「if not v or not (root / v).exists():」

1. `root / v` 在 `v` 為絕對路徑時直接忽略 `root`，而 `../` 也只要指向既存檔案就會通過，沒有 `resolve()` 後的 containment 檢查。  
file: `scripts/lumos:10814` 唯一驗證只有存在性。  
2. about_code 的既有規約是 repo 相對的程式檔路徑。  
file: `scripts/lumos:12085` 明定為 repo 相對路徑。  
3. 最小翻紅測試（未執行，遵守只讀）：建立 `<repo-parent>/outside.py` 後執行 `lumos set S about_code ../outside.py`，預期 rc=2 且筆記不動；目前會 rc=0 並寫入跳脫路徑。

### F3 新 set 會靜默刪除既有合法的多檔 about_code

severity: major  
blocking: 是 — 正常的多檔標記被一次單值 set 無提示抹除，後續固定席與脈絡召回少看檔案。  
引句:「fm[a:b + 1] = [f"about_code: {v}"]     # 清單形(含範本的空 [])或壞掉的純量,一律換成一行乾淨路徑」

1. about_code 仍被正式定義為 list 欄位，且規約允許一篇標 0 至 3 支程式檔。  
file: `scripts/lumos:10533` about_code 仍在 `LIST_KEYS`。  
file: `scripts/lumos:12085` 說明允許「0~3 支」。  
2. 對現有 `about_code: [src/a.py, src/b.py]` 執行 `set ... src/c.py` 時，實作直接改成唯一的 `src/c.py`，a/b 沒有搬遷、警告或拒絕。  
3. 最小翻紅測試（未執行，遵守只讀）：給既有 a/b 清單與有效 c 檔後執行 set，預期 rc=2 且 a/b 不變；目前 rc=0 且欄位只剩 c。

風險掃描清單（1條）：誤報 — file: `scripts/lumos:17562` 的 `open(...)` 位於 `_stack_changed_ok` 的說明字串，並非檔案開啟呼叫。

總結:最高 severity blocker,blocking 共 3 條
