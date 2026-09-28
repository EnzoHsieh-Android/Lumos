severity: clean

角色:資安審查員,站在攻擊者那一邊看這次(第 4 輪)修正差異——只審 r3→r4 這份 patch 本身改到的程式,不審沒被這輪碰到的既有邏輯。

## 逐類檢查

### 1. 不可信輸入流到危險操作(設定檔 JSON 解析、git 參數、cat-file、檔名)
已看,無 finding。

- 這輪新增的 `_drift_gate_explicit` 只是把 `.lumos/config.json` 的 bytes 丟給 `json.loads`,失敗被 `except (ValueError, UnicodeDecodeError)` 接住回 `False`,不影響任何危險操作、不進 subprocess、不進 eval。
  引句:「except (ValueError, UnicodeDecodeError):
        return False」
- 這輪改到的所有 git 呼叫(`_ns_git`→`_lens_git`、`_nodehome_cat_blobs`)沿用既有作法:參數一律用 list 傳給 `subprocess.run`,沒有 `shell=True`;路徑一律放在 `--` 之後,不會被當成選項解析。用 `grep -nE "eval\(|exec\(|pickle|shell=True|os\.system|subprocess\.call|yaml\.load\b"` 掃整份 patch 是 0 筆。
  file: `scripts/lumos:23073`(`_nodehome_cat_blobs` 用 `["git", "-C", str(repo_root), "cat-file", "--batch"]` 的 list 形式,attacker 能控制的只有 stdin 裡的 `spec` 字串,而且已檢查不含換行,不會跨行注入額外的 batch 指令)
- `Env.from_texts` 新增的 `unreadable` 參數只是把「解不開的路徑」建成一篇空白 lint 筆記(欄位、targets 都是空的),不會把攻擊者能控制的檔名或內容送進任何解析器之外的操作;`n.stem` 只做字串切片,不做檔案系統存取。
  引句:「n.rel, n.stem, n.mtime = nfc(r), nfc(r.rsplit("/", 1)[-1][:-3]), 0」

### 2. 登入與權限
已看,無 finding。這份 diff 沒有任何身分驗證、授權判斷或權限提升邏輯——`drift check` 是推送前/CI 的內容一致性檢查,不是存取控制;RULE 註記本身已明講「這道閘…只防疏忽、不防存心繞過」,這是既有、非這輪改動的設計取捨,不是這輪新開的洞。

### 3. 密鑰與個資
已看,無 finding。沒有新增任何讀取、記錄或印出密鑰/個資的程式碼;新印出的訊息(doctor 開關提醒、scan 判不了清單、settle 的錯誤訊息)都只帶檔名、行號、筆記摘要片段,沒有秘密性質的內容進 log。

### 4. 加密與傳輸
已看,無 finding。這份 diff 完全不涉及網路呼叫或加密邏輯。

### 5. 執行邊界
已看,無 finding。沒有新的子行程、沒有新的檔案寫入路徑(`home_rel` 的檔案開啟邏輯在這輪只是把既有的迴圈抽成 `_guard_planned_idx`,比對邏輯不變,`home_rel` 的來源與正規化沒有變動);`_nodehome_cat_blobs` 呼叫沒有新增。

### 6. 行動端
已看,無。這是純 CLI/伺服器端工具,無行動端程式碼。

### 新依賴
已看,無。整份 patch 只用到 Python 標準庫(`subprocess`、`json`、`re`、`time`、`hashlib`),沒有新增第三方套件。

## 總結
這輪修正(r3→r4)本身沒有引入可利用的資安洞——沒有新的不可信輸入流向危險操作、沒有新的權限/密鑰/加密/執行邊界問題。最嚴重等級 clean,blocking 共 0 條。
