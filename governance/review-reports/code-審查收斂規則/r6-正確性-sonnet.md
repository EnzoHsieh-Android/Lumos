severity: minor

審查範圍:修補差異 `/tmp/code-審查收斂規則-r6-repair-lumos.patch`。我讀了全部內容,並在 `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-Backend-improve/fe5c4f58-e7fb-477f-be55-0823b5438608/scratchpad/cr-rc6-正確性/` 實跑 `_residual_note_hits`(程式 HEAD 為 31982220)。沒有找到會讓該升的沒升的 blocker 或 major。下面是四條 minor,主要是多升、誤導訊息與快取。

severity: minor
blocking: 否 — 只會多升或多印必答題,不會漏升
引句:「舊索引,跑 lumos guard residual --reindex 補上),當成改到存著已登記殘留的筆記,要過高風險代碼審」
問題:`_residual_index_entries` 的 `note_path` 解不出筆記時就不記那筆。決策被 superseded 或刪掉、指標對不到、決策所在筆記在 repo 外,都會造成這種情況。重建索引後那筆仍是 `notes` 缺項,所以在 `_residual_index_notes` 裡永遠是 None。之後每一次改到圖譜檔的推送都走 `notes_unknown`,理由卻寫成「舊索引,跑 --reindex 補上」。照做修不好,而且是每次推送都升 high。
具體失敗情境:索引有一筆殘留,它指的決策後來被標為 superseded、沒有解出節點。之後任何一個只改圖譜筆記的推送都會升 high,理由叫人跑 `--reindex`。跑完索引內容不變,下次照升。
佐證:``scripts/lumos:19170-19177``(`note_path`),``scripts/lumos:44651-44668``(`_residual_note_hits`)

severity: minor
blocking: 否 — 派工鏡頭只是多印一段並多一條必答題
引句:「if left() < 1:」
問題:`_lens_residual_new_lines` 一開頭只看剩餘預算,不管這個 repo 有沒有殘留。鏡頭前段(外部碼表等)用掉約 40 秒,沒有任何殘留的 repo 也會多一段「算不出來」加逐條必答題,而那題問的是「上面列的每一條合約」,上面其實什麼都沒列。
具體失敗情境:鏡頭前段耗時 41 秒、repo 沒有 residual-index.json。輸出多一個注入框,內容只有「⚠ 這次新增的殘留算不出來(派工鏡頭的時間預算用完)」,後面接著必答題。
佐證:``scripts/lumos:48959-48962``

severity: minor
blocking: 否 — 快取會讓保守提示重複出現,不會漏
引句:「if not (no_cache or os.environ.get("LUMOS_DISPATCH_LENS_NO_CACHE")):」
問題:鏡頭輸出的快取鍵只有 repo、base、head、schema 版本,但殘留段的內容會受時間預算和暫時性 git 讀取失敗影響。一次逾時或讀不出產生的「算不出來」,連同缺掉的真實清單,會被快取下來。同一範圍之後再派工,即使現在讀得出來,仍拿到舊的「算不出來」,直到範圍的 sha 改變。`_LENS_SCHEMA=5` 沒有處理這種情況。
具體失敗情境:第一次派工遇到 git 逾時,殘留段印出「算不出來」;第二次派工同範圍,快取命中,審查席仍然看不到殘留決策與問答。
佐證:``scripts/lumos:50267-50268``

severity: minor
blocking: 否 — 只有舊索引才走這條路;誤中是多升,漏掉的條件很窄
引句:「return rel.lower().endswith(".md") and any(f in segs for f in folders)」
問題:`_residual_graph_file` 只在舊索引沒記筆記時用,有兩個偏差。多升:`docs/<名>-knowledge/` 底下任何檔(例如 `.lumos/idx.json`)都算圖譜檔。另外任何目錄層級只要含 `Projects` 之類的資料夾名,例如 `src/Projects/api/notes.md`,也會算。漏升:`folders` 取自殘留指標的第一段,而 `"/" in k[2]` 的條件讓位於圖譜根目錄、不帶資料夾的指標(例如 `Home#d1`)算出空集合。再加上圖譜不在 `docs/*-knowledge/` 或 `docs/knowledge/` 時,改到那篇決策筆記不會被認成圖譜檔。
具體失敗情境:實測 `["src/Projects/api/notes.md"]` 與 `["docs/lumos-toolchain-knowledge/.lumos/idx.json"]` 都回 `notes_unknown`。`k2=("S","f","Home#d1")` 搭配 `["Home.md"]` 回傳空。
佐證:``scripts/lumos:44642-44648``,``scripts/lumos:44651-44668``

已讀,無 finding 的部分:
- **`notes` 新舊索引互讀**:`_residual_index_notes` 對缺欄位、非 dict、同鍵衝突都回 None。鍵都用 `_residual_ref_key` 的正規形,寫入與讀取一致。`_residual_index_row_key` 加了 notes,`_residual_index_mismatch` 的欄位名清單與 `w[2:]` 對齊。
- **`notes`、`notes_unknown`、`notes_moved` 判定**:實測舊索引、新索引、NFD 與 NFC、頂端沒記、頂端換篇都符合預期。頂端索引讀不出時 `hnotes` 為 `{}`,不會誤報 moved,該情況由 `head_bad` 接住。
- **`asks_unknown` 與 `asks_dropped`**:兩個理由已分開。起點讀不出就不再讀頂端,回傳 `(None, None, "起點")`,不會把兩種讀不出混成一種。全 repo 搜尋後沒有其他讀者還在比對舊的 `asks_dropped == -1`。鏡頭端不論治理帳有沒有被改都會讀,但這是更保守,不是漏洞。
- **`_residual_blob_at` 與 deadline**:預算不足回 unreadable,`show` 失敗後再用 `ls-tree` 分辨 missing 的邏輯保留。
- **`_lens_residual_asks_shown` 排序**:`_gov_ts` 已擋掉非字串與時間出界,排序鍵不會丟例外。
- **排序級別與 5 條上限**:真實殘留變動排級 0,偽造問答排級 2,擠不掉真的。
- **入口清環境**:`GIT_GRAFT_FILE=/dev/null/...` 在 git 2.39.2 下靜默忽略,不報錯。

最高等級 minor,blocking 0 條。
