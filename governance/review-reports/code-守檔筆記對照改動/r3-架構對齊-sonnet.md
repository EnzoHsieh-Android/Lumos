severity: minor

四項對齊檢查結論:(1) 共用路徑守衛 `_repo_path_unsafe` 確實取代了 `_note_audit_safe_dir` 與 `_drift_ledger_path_err` 兩份舊寫法,行為逐步比對一致(符號連結先於資料夾檢查、解析後在 repo 內、OSError 由呼叫端接);全檔其餘 `is_symlink()` 都是單檔或 config.json 檢查、或家目錄 uid 版(`_mkdir_trusted_under_home`,判準不同),沒有第三份同形的逐層守衛。(2) 留痕有效性判程式檔重用 `_nodehome_code_kind` 與 `_head_is_shebang`,沒另寫副檔名清單。(3) `lumos gov` 跳過非物件行與 LOOP_CLOSE 讀帳那處同形。只有第 (4) 項有問題,見 F1。

## F1 新增的 Unicode 類別過濾是既有 _drift_m1_special_chars 的第二份(類別集合還偏離一個)
severity: minor
blocking: 否
引句:「_NOTE_REREAD_CTRL_CATS = ("Cc", "Cf", "Zl", "Zp")」
佐證行:file: `scripts/lumos:28895-28898`(既有 `_drift_m1_special_chars`:同一組類別加 "Cs",判「路徑或名稱帶控制、方向控制、零寬、行段分隔或非 UTF-8」,同樣是「路徑要不要當成特殊字元處理」的謂詞)
佐證行:file: `scripts/lumos:9793-9797`(`_esc_clean` 是清洗層,新的 `_note_reread_show` 是在它後面再疊一層 category 取代,清洗本身是疊加而非另起,這部分可接受)
1. 專案裡已經有「Cc/Cf/Zl/Zp(+Cs)」這組類別的路徑謂詞 `_drift_m1_special_chars`;r2 修法另開了常數 `_NOTE_REREAD_CTRL_CATS` 與 `_note_reread_has_ctrl`,同樣的判準現在兩份,日後補類別(例如 Cn、Co 或新的方向字元)要改兩處,正是第 2 輪架構席才叫併掉的那種漂移。
2. 兩份已經不一致:對含孤立替身字元的路徑,舊謂詞為真、新謂詞為假。當場重現:`any(category(c) in ("Cc","Cf","Zl","Zp","Cs") for c in "a\udcffb")` 得 True,去掉 "Cs" 得 False。差異在計劃裡有理由(reread 要讓非 UTF-8 路徑照常對照),所以目前不會出錯行為,因此不算 blocking;但該把差異做成參數(例如共用一支 `_path_special_chars(s, surrogate=True)`,drift 傳 True、reread 傳 False),讓類別集合只有一個出處。
3. 修法建議不影響行為:抽共用謂詞並保留兩邊現有語意;`_note_reread_show` 繼續疊在 `_esc_clean` 之上即可。

## F2 簿記判程式檔讀 blob 沒走既有的帶上限批次讀取
severity: minor
blocking: 否
引句:「blobs = _nodehome_cat_blobs(repo_root, [f"{sha}:{f}" for f in ask for sha in (marker_sha, rec_sha)],」
佐證行:file: `scripts/lumos:24037-24050`(同檔已有 `_nodehome_cat_blobs_capped`,註明上限放在批次讀取這一層)
1. 這裡只需要首行,卻用不設上限的 `_nodehome_cat_blobs` 把簿記資料夾內沒副檔名的整個 blob 讀進記憶體;同一支程式已有帶大小上限的變體。給不出會出錯的具體場景(簿記資料夾內的無副檔名大檔很少),且讀不到時保守當程式檔,所以放行;若改用 capped 版,超限回 None 也會走保守路徑,行為一致。

最高等級:minor
