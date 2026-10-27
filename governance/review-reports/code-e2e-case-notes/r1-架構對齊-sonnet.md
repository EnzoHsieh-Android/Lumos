severity: major

## 三問

**1. 分層與依賴方向:對齊。**
- 新碼是 `_e2e_flow_names`、`_e2e_note_refs`、`_e2e_note_gaps`。它們放在 `_e2e_coverage_report` 旁邊,由它呼叫(`scripts/lumos:42157`)。
- 輸出層 `_e2e_coverage_cmd`、`_e2e_coverage_line` 只讀 `rep` 的鍵,沒有跨層直呼。這跟既有三項一樣(`scripts/lumos:42261` 一帶)。
- 合約綁定走 `extract_contracts` 加 `resolve_test_refs` 加 `load_platforms`(`scripts/lumos:42201-42208`)。`_residual_test_files`(`scripts/lumos:26384-26400`)和 `scripts/lumos:30913-30920` 也是這樣走,沒有繞過。

**2. 命名與錯誤處理:對齊。**
- 命名用 `_e2e_` 前綴加繁中 docstring,和 `_e2e_cov_names` 等鄰居一致。
- `resolve_test_refs` 丟 `ValueError` 就略過,和 `scripts/lumos:30920` 的 `continue` 同一寫法。
- `load_platforms` 失敗時降級並把原因放進 `info`,不丟出去。鄰居 `_residual_test_files` 用 `except Exception` 靜默回 `{}`;新碼只收 `(ValueError, OSError)` 且會印原因。這不算衝突,因為 `load_platforms` 文件寫明只丟 `ValueError`。
- 日誌方式一致:都是 `print` 加 `_esc_clean`,沒有自創日誌。

**3. 第二種做法:有兩處。**
- A1:流程檔的 `name:` 自己讀,沒走既有的測試設定檔走訪。
- A2:整個圖譜自己載入一次,doctor 路徑沒用手上已經有的 `env`。

### A1 自己讀流程檔 name:,沒走既有的測試設定檔走訪
severity: major
blocking: 是
引句:「out[f] = set(MAESTRO_NAME_RE.findall(txt)) if MAESTRO_FLOW_RE.search(txt) else set()」
1. 專案裡「從 maestro 流程檔取 `name:`」只有一條路:`_walk_test_files(root, profile, with_path=True)`,再套 `profile["method_re"]`、`_strip_test_comments`、`_test_name_of_match`。`_residual_test_files`(`scripts/lumos:26405-26412`)已經用它建出「name → 檔」的對照。
2. 注釋寫明走訪「只有一份」,理由是兩邊各寫一份時,檔案篩選改了只改一邊,沒有東西會翻紅(`scripts/lumos:6700-6703`)。
3. `_e2e_flow_names` 手抄了 `file_must_match`(`MAESTRO_FLOW_RE.search`)和 `method_re`(`MAESTRO_NAME_RE.findall`)兩段規則,這就是那條注釋要避免的狀況。
4. 它省掉了三件事:
   - `_strip_test_comments` 和 `_test_name_of_match` 的取名細節。
   - 平台設定裡的 `root`。綁定那邊是以平台 `root` 找流程檔,這裡改從 repo 根按對照表路徑讀。
   - 平台的 `profile` 本身。profile 若改了篩選或取名規則,這裡不會跟著變。
5. 方向也相反:既有索引是 name → 檔,這裡是檔 → name。計劃寫了「借用同一支正規式」,但只借了正規式,沒借走訪。
6. 已有的做法能用:`_residual_test_files` 這類 name → 檔對照可以直接拿來比對對照表的流程路徑(轉成 repo 相對路徑)。
- ⚠ 交編排者:這是計劃有意識的選擇。我判 major 是因為它完全符合題目定義的第二種做法。若編排者認為「對照表給的是檔案路徑,必須檔 → name」足以豁免,可降為 minor。
file: `scripts/lumos:42171-42180`

### A2 圖譜用另一套載入器讀一次,doctor 路徑沒用手上已載入的 env
severity: minor
blocking: 否
引句:「snap, info = load_vault_safe(vault), []」
1. `load_vault_safe` 目前只有 `_secinv_build` 的兩個呼叫點在用(`scripts/lumos:9949`、`14963`)。這些是「不可信圖譜、輸出當證據」的指令。
2. 其餘所有消費 `extract_contracts` 的地方都是從 `env.notes`(`load_vault` / `Env`)取筆記,例如 `scripts/lumos:30913-30915`、`26376`、`23014`。
3. 新碼用 `load_vault_safe` 加 `_note_from_text` 重組筆記。涵蓋報告只印提醒、不是證據,這個選擇的理由沒有寫進圖譜。
4. doctor 的呼叫點(`scripts/lumos:4157-4158`)手上已有 `env`,卻只傳 `root` 進去,同一個圖譜在同一次 doctor 內等於又讀一遍。
5. 結構沒錯:CLI 路徑沒有 `env`,需要自己載入。只是兩個入口各走各的載入。
- ⚠ 判不準:鄰居沒有「CLI 與 doctor 共用函式、一邊有 env 一邊沒有」的先例可對,所以只判 minor。
file: `scripts/lumos:42186-42189`

不對齊共 2 條,其中 major 1 條
