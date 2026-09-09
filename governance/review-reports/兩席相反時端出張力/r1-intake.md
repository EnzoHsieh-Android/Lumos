preflight-4: ran

# r1 收貨留痕(兩席相反時端出張力)

## 前掃(派席前;乾淨 agent,固定四項)

- ①未定義的詞:無(本案自創欄位在首次出現處定義;其餘為專案既有術語或世界解引用)。
- ②壞引用:1 條,存在類 → 直接修真檔不算 finding
  - `_stack_key_for_file(F)` 漏了第二個必填參數 → 改成 `_stack_key_for_file(F, repo_root)`(既有簽名 `(file_rel, repo_root)`,scripts/lumos:15247)。
- ③範圍自相矛盾:無(「合法不擋/不合法擋」「不加新 kind/進帳可數」「死題候選只看 na」三處查過是重申不是矛盾)。
- ④機械宣稱驗語意:20 條,19 對、1 部分對 → 修真檔並留痕:
  - 修改前:「文字門檻與 `chosen` 值再驗一次(治理帳重建來的紀錄不信形狀,同表態閘 r1 正確性席 f3 慣例)」
  - 修改後:「…(治理帳重建來的紀錄不信形狀:缺欄一律 `str(… or "")` 接住,同 `_lens_dispositions_lines` 的防禦寫法、表態閘 r1 正確性席 f3;`_one` 自己既有的另一道是「任一例外接成該題無法驗證、不整份 fail-open」,r1 正確性席 f1/邊界席 f1,本案沿用)」
  - 為什麼:「r1 正確性席 f3」那條引註貼在 `_lens_dispositions_lines`(scripts/lumos:19642),`_one` 自己的引註是 f1(例外不整份 fail-open);行為宣稱屬實、出處引錯。不動核心裁定節。
- 修後重凍快照 r1-snapshot.md、r1-dispatch.json 的 spec_sha256 同步更新。

## 席報告機械重現表(收齊後填)

| id | 席 | 命令/查證 | 結果(HIT/MISS) | 處置 |
|---|---|---|---|---|
| F1 | 外家codex | `python3` 載入 scripts/lumos 叫 `_stack_norm_line('   async { // still comment')` | HIT:回 `'   async {'`——區塊註解內不以 `*` 開頭的行被當程式碼(`/* start` 與 ` * inside` 才回 None);既有正規化沒有跨行狀態,適用性與候選共用這條天花板 | 折:S3 與〈二〉改寫成「行註解與以 * 開頭的區塊註解行不算命中;區塊註解內裸行是既有正規化的天花板,跟適用性同款,承認不修」+ 對照檔整檔掃描可帶狀態,增行(hunk 片段)不能 |
| F2 | 外家codex | 讀 spec〈一〉:`existing` 只要求「非空清單」;讀 `_dispositions_verdict` 21494-21500:deadline 只在每題開始前查;`_one` 逐項驗 | HIT:合法輸入可放上千個 `existing`,單題內無上限、無時間檢查(引句錯一個標點:快照原文是「…一項一個 `path:line`，去重後…」,語意成立) | 折:寫側與讀側都釘 `existing` ≤20 項、每項 ≤300 字、hazard/suggestion ≤2000 字;超過=形狀壞(寫側 rc2、讀側 problems) |
| F3 | 外家codex | 讀 spec〈三〉漂移守衛段:只釘三處 | HIT:九處同步只有三處有測試 | 折:`t_tension_doc_sync` 釘本 repo 內全部九處(四份 skill 檔+三篇 Systems+Issues+效能檢核目錄那一格) |
| A1 | 架構對齊 | 讀 `_one` 21484:satisfied 的 evidence 走 test:/path:line 兩條 | HIT:spec 的 tension evidence 只講 path:line,同鍵名語意窄化沒明講 | 折:tension 的 evidence 規則改成「同 satisfied(path:line 或 test:名),同一條驗法」 |
| A2 | 架構對齊 | `scripts/lumos:16406` 既有 `n_files` 對外鍵是 `"files"` | HIT:對外鍵不帶 n_ 前綴是既有慣例 | 折:`n_files` 改名 `files`(去重路徑數) |
| A⚠ | 架構對齊 | 派工鏡頭 tension 尾巴用「｜」分隔四欄 vs 其他三值簡單串接 | 編排者裁:保留「｜」——同函式內既有 todo 也是「issue + 空白 + reason」拼接,四欄用分隔符是可讀性需要,`｜` 在本檔錯誤訊息與筆記 DEP 行皆有既有用法 | 不折,記理由 |
| G1 | 通才 | 讀 spec 第 27 行 KEY 與第 80 行派工詞草稿 | HIT:摘要寫「三欄」、正文列四欄(existing/hazard/suggestion/chosen) | 折:摘要改「四欄」 |
| G2 | 通才 | `scripts/lumos:21779` 另一處硬編「只認小寫 satisfied/na/todo」 | HIT:批次失敗提示行也寫死三值,DEP 沒點名 | 折:DEP 與〈一〉寫側加「`_cmd_codeloop_dispositions` 的規則提示行同步改四值並列 tension 必填欄」 |
| G3 | 通才 | 同 F2(兩席獨立一致) | HIT | 折:同 F2 上限 |
| G4 | 通才 | 同 F1(兩席獨立一致;通才判 minor、外家判 major) | HIT | 折:同 F1,承認天花板改寫 S3 |
| G5 | 通才 | 讀 `_stack_changed_ok`:比 `arch["files"]` 的過濾多排 review-reports 與簿記檔 | HIT:候選檔全集若只用 arch["files"],簿記檔上的候選 qid 可能不在 applicable | 折:候選只算「在 arch["files"] 且 `_stack_changed_ok(F)` 為真」的檔;不變量測試加簿記路徑反例 |
| G6 | 通才 | 讀 `_dispositions_template` carry 分支:`dict(prev)` 整包淺拷貝;validate 不擋未知鍵 | HIT:舊 hint 會被存進帳、再被 carry 帶回 | 折:carry 分支明寫 `ent.pop("hint", None)`;寫側不擋未知鍵維持既有 |
| G7 | 通才 | `scripts/lumos:17057` 對照檔清單印法有 `[:6]` | HIT:候選印法沒比照上限 | 折:可能撞最多印 6 行,其餘一句「另有 N 條,--json 看全量」 |
| H1 | 接手 | 讀 `_norm_rel` 11867-11874 + `t_new_verification_bidirectional` | HIT:`--systems` 要帶 `Systems/` 前綴,裸名 rc2 | 折:S7 指令改 `--systems Systems/棧別提問表態閘,Systems/arch-alignment-lens --plan Projects/兩席相反時端出張力_計劃` |
| H2 | 接手 | 同 F3(兩席獨立一致) | HIT | 折:同 F3,守衛釘九處 |
| H3 | 接手 | 讀 `_pitfall_diff_collect` docstring「純計算、不印」+ pitfalls 不寫帳 | HIT:候選次數沒有持久分母,REVISIT 兩個數字數不出來 | 折:候選的持久落點=表態寫側——樣板帶的 `hint` 隨表態存進治理帳事件(寫側不剝未知鍵,既有),事件另記 `candidates:<帶 hint 的題數>`;gov --stats 印「候選題 N、其中 tension M」;REVISIT 改成數這兩個;「pitfalls 印過幾次」承認數不出、刪掉 |
| H4 | 接手 | 讀 4537-4538:`_human = satisfied+na+todo` | HIT:tension 不進分母會讓 8 na + 5 tension 被標死題 | 折:`_human` 併入 tension;死題判準文字改「人答 ≥10 且全是 na」語意不變但分母含 tension |
| H5 | 接手 | 讀 cmd_install/_install_skills(symlink)、cmd_update、cmd_bootstrap 13656 註解 | HIT:skills 是 symlink 即時生效;落後的是消費專案 vendored 的 scripts/lumos,要 `lumos update` | 折:隱患條目改寫成「消費專案 vendored 工具要 `lumos update` 才認得 tension;舊副本會拒收 tension(寫側 rc2)」 |
| B1 | 邊界 | 同 G1(兩席獨立一致) | HIT | 折:同 G1 |
| B2 | 邊界 | 讀 spec 寫側:chosen 只說「值不在兩者」 | HIT:大小寫規則沒明文 | 折:chosen 同 status 只認小寫,訊息明講 |
| B3 | 邊界 | 讀 spec 讀側:只講「每個 existing 走…」 | HIT:`existing=[]` 迴圈零次 → 判過 | 折:讀側先驗 existing 非空且為清單,空=problems |
| B4 | 邊界 | 同 F2/G3(三席獨立一致) | HIT | 折:同 F2 |
| B5 | 邊界 | 讀 spec 印法:「前 3 項」切原清單 vs N=去重路徑數 | HIT:同檔多行時印出 1 檔名卻寫共 2 檔 | 折:印「前 3 個不同路徑」+ 共 N 檔 |
| B6 | 邊界 | `grep errors="replace"\|errors="ignore"` scripts/lumos 多處;UnicodeDecodeError 極少 | HIT:既有讀檔慣例是永不失敗,照慣例寫測不出 unreadable | 折:候選讀對照檔明寫「讀 bytes、`decode("utf-8")` 嚴格,UnicodeDecodeError→unreadable」並在 spec 註明這是刻意偏離既有 replace 慣例的原因(要能分辨讀不到與讀到) |
| B7 | 邊界 | 讀 `_arch_alignment_hints`:sibs 空 → 不收 | HIT:零對照檔的新檔完全沒訊號 | 折:S3 與〈二〉明寫邊界「沒有對照組=沒有候選也沒有 unreadable,這是對照組機制的既有邊界」;不加輸出 |
| B8 | 邊界 | 讀 spec 預算:上限以「對照檔數」計 | HIT:上限可切在同一改動檔的對照組中間 → 假陽性 | 折:上限改以改動檔為單位(整組讀完或整組不算),最多 20 個改動檔(=60 對照檔),超過的檔不判候選、`candidates_truncated` |
| B9 | 邊界 | 讀 spec 效能句 | HIT:秒數宣稱無測試 | 折:刪掉「毫秒到百毫秒級」,只留上限與「不宣稱秒數」 |
| B10 | 邊界 | `git check-ignore -v governance/code-loop/main.dispositions.json` | HIT:marker 在 gitignore,治理帳才版控 | 折:不可逆條目改寫「治理帳版控可還原;marker 不版控,遺失走既有退治理帳 fallback」 |
