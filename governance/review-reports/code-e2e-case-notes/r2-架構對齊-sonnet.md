severity: minor

我只核了新碼本身,沒有真的把 `lumos android-e2e coverage` 跑起來。修補後提交碼以更正過的 8a3a4643b65e2b782e1bae0266adc42082af25eb 為準。我用 `git cat-file` 確認它存在,也跟 binding 的 after_commit 逐字相同。

**1. 分層與依賴方向:對齊**
- 新的 `_e2e_note_refs` 和 `_e2e_note_gaps` 掛在 `_e2e_coverage_report` 底下,由 `_e2e_coverage_cmd` 和 `_e2e_coverage_line` 呼叫(scripts/lumos:42171、42252、42295)。跟同一個報告既有的三項是同一條呼叫鏈。
- 它們往下呼叫的都是既有函式:`find_vault`(33922)、`load_vault_safe`(859)、`load_platforms`、`extract_contracts`、`resolve_test_refs`、`_note_from_text`(900)。我沒看到跨層直呼。
- `_platform_name_files`(26384)放在 `_residual_test_files` 旁邊,往下走 `_walk_test_files`(6695)、`_strip_test_comments`(6829)、`_test_name_of_match`(6801),跟 `discover_test_methods`(6847)的取名路徑一樣。

**2. 命名與錯誤處理:大致對齊**
- 新函式的命名、說明字串的寫法(「→ 回傳形狀」、引用單源計劃節點)跟鄰居一致。
- 錯誤處理也一致:`except (ValueError, OSError)` 之後降級並寫進 `info`;`resolve_test_refs` 丟 ValueError 就 `continue`,跟 `_residual_test_files`(26412 附近)的做法相同。
- 輸出走 `_esc_clean` 和 `_e2e_cov_names`,沒有另開日誌管道。
- 有一處小出入,見 A1。

**3. 第二種做法:大致沒有**
- 殘留索引原本的取名迴圈被抽成 `_platform_name_files`,新增的涵蓋報告和 `_residual_test_files` 都改呼叫它。這是把重複收斂成一份,不是多一份。
- 正文比對用 `pats` 自己組了一條正規式。`_test_name_boundary_re`(6482)只擋英數底線,而路徑的邊界要擋 `/`、`.`、`-`,兩者語意不同。再加上一個專用的路徑邊界函式,可以算是合理的新需求。
- 讀圖譜用 `load_vault_safe`,跟 `_secinv_build` 同一套。

**修補三問**
1. 把對齊修對了:流程檔名字改成從 maestro 平台的測試名索引反查,不再另讀流程檔,跟殘留索引共用同一支 `_platform_name_files`。`_residual_test_files` 的外部行為沒變(26412 起)。
2. 沒有讓原本對齊的地方變得不對齊:`_residual_test_files` 只是少了內嵌迴圈,快取鍵 `cache[plat]` 沿用。原本把 `_titled` 算在每個檔案的迴圈裡,抽出後移到迴圈外,語意相同。既有三項(`unowned`、`unused_flows`、`unused_screens`)的產出沒動。
3. 沒有帶進新的第二種做法。

### A1 筆記快照直接 `_note_from_text`,沒走既有的 `Env.from_texts` 建構
severity: minor
blocking: 否
引句:「for inv in extract_contracts(_note_from_text(rel, text))[0]:」
歸因:未判定
1. 專案裡把 `load_vault_safe` 的快照轉成可解析筆記,既有的做法是 `_secinv_env`(7485)。它先檢查 NFC 路徑碰撞,再交給 `Env.from_texts`(978)。
2. 這份 diff 直接用 `snap["texts"]` 逐篇 `_note_from_text`,沒做碰撞檢查,也沒做 `nfc` 正規化。
3. 結構上沒有自創工具函式,所以我只判 minor。兩個後果:兩篇 NFC 同名的筆記在這裡都會被讀;`snap["unreadable"]` 只被算進 `info` 的數字,不會變成可帶 lint 的空筆記。
4. 這是一個取捨,而不是已確認的缺陷。涵蓋報告只需要合約行,照 `_secinv_env` 建整個 Env 成本偏高。⚠ 我沒有實測 NFC 碰撞時兩邊會差多少。
file: `scripts/lumos:42197`

不對齊共 1 條,其中 major 0 條
