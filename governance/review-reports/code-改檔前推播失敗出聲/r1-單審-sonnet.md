severity: clean

我逐段對過舊版 `46739ab5` 與新版 hook。我也在真 repo 讀了 `_vault_in`、`_ttl_*` 系列與五支新測試。沒有找到可以具體重現的錯誤行為,所以不交 finding。以下是各項查證結果。

**「搬成獨立函式、行為不變」宣稱**
- **冷卻標記撤法一致。** 舊版四處撤標記:非 0 結束碼、逾時或啟動失敗、輸出為空、`ctx` 為空。新版四種情況都落在同一個出口(`_impact_for_file` 尾端的 `if not ctx.strip()`),撤的條件仍是 `session_id and not in_cooldown`,用同一個 token。
  - 逾時、啟動失敗、rc3、非 0:`_run_impact` 回 None,`_ranked_ctx(None)` 回空字串,走該出口。
  - 輸出為空或 `{}`:`_run_impact` 回 None 或 `{}`,同樣回空字串,走該出口。
  - 以上對照舊版都撤標記,一致。
  - `bad_output` 是新增的出聲分類,舊版這裡也撤標記。
  - 只有零命中時 `_ranked_ctx` 才會走到 `build_ranked_context` 的空判斷,同舊版。
- **rc3 的 stderr 行**逐字保留,新增的 `fails.append` 排在 print 之後,沒有改變 stderr 輸出。
- **多檔預算與 skipped 列名**公式沒動,`len(paths) - len([s for s in skipped if s in paths])` 與 `_plain_label` 都原樣。`_query_files` 只是把迴圈搬出來,`left`、`tmo` 與 `skipped` 的處理沒變。
- **ttl 分鐘數**:`_ttl_min` 的 try/except 與型別檢查原樣,`max(1, int(...))` 仍在。
- **輸出組裝**:`_emit_chunks` 的輸出格式不變。

**`_has_graph` 對照 `_vault_in`**
- `scripts/lumos` 的 `_vault_in` 判三種:`docs/*-knowledge` 目錄、`docs/knowledge` 目錄、獨立根(`MOC/` 加 `Verification/` 或 `Systems/`)。hook 的複本與它等價。
- 差別只在 hook 讀不到目錄時回 False,lumos 會丟例外,這個差別是合理的。
- `t_impact_hook_graph_check_agrees` 的 8 個佈局都直接跟 `_vault_in` 比對,覆蓋了「是檔案不是目錄」與「只有 MOC」兩個邊界。
- 被查的是另一個 worktree 時:多檔路徑用 `frepo`(`_sibling_worktree_root(fp, repo) or repo`)判斷。找不到 lumos 的路徑用 `paths[0]` 的 worktree 根判斷,不是啟動目錄。兩邊都是被查的那個 repo,符合預期。

**噪音(誤報與漏報)**
- 非圖譜專案的六種失敗在 `_fail_notes` 之前就被擋掉,不出聲也不記事件。測試以 graph=False 實跑六種情況證明。
- 零命中走 `_ranked_ctx` 回空字串,不進 fails。
- 漏報只有一個邊角:`CLAUDE_PROJECT_DIR` 設在圖譜專案的子目錄、而且 lumos 又找不到時,`_has_graph(repo)` 只看那一層,會靜默。這是計劃自己選的「只看該 repo 層」,而且觸發條件很窄,我給不出具體失敗案例,所以不列。

**注入安全**
- 框內只有固定字彙原因,加上 rc 的整數(非整數印 `?`)。
- 框外 `FAIL_TAIL` 是常數。
- 檔名、lumos 的 stderr 或 stdout 原文都不會進說明。測試也斷言了「內部錯誤原文」不出現。
- 框內框外的劃分與既有慣例一致。

**記號檔 `voice-<code>`**
- 放在 `lumos-impact-<sid>/` 底下,和既有冷卻標記同一個目錄,跟著 24 小時惰性清理消失。
- 沒有 `session_id` 時回 True(多講一次)。
- `touch(exist_ok=False)` 是原子操作,並行時只有一個 hook 會講。
- 寫不進去(OSError)時回 True,寧可多講。
- `session_id` 含 `/` 或 `..` 時,路徑建構方式與既有 `_ttl_marker_path` 相同,沒有新增風險。

**測試品質**
- S1 測六種失敗各自的框內與框外、不留標記、不轉原文,也測了非圖譜專案與零命中的對照組。
- S3 到 S6 分別測只講一次、多檔一成一敗、事件種類(timeout、error、混合記 error)與圖譜判定一致。
- 兩個覆蓋缺口我評估後不列:
  - `_voice_once` 沒有直接測「無 `session_id` 時每次都講」。這是文件寫明的行為,沒有具體改壞場景能證明它重要。
  - 零注入不留標記由既有測試 `main 接線` 守(`scripts/test_lumos.py:51406`)。

**圖譜固定席**
- 派工詞說這次沒附固定席節點,所以沒有合約行可逐條判,也沒有「帶殘留徽章」的合約。
- 我讀過的筆記只有 diff 裡的 `Projects/主動影響幅度偵測_計劃` 那一行翻案。它把「純靜默」改成「圖譜專案裡講一句並記事件」,且明標翻案出處,與新行為一致。

**角色卡**
- 這次改的是 hook 本身,不是前端或後端應用碼,沒有 fe- 或 be- 題號適用。

severity: clean
