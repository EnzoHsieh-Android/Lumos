severity: major

我讀完整份 patch 和 `scripts/lumos` 的相關函式,下面兩條要處理的在推送閘,一條在訊息文字,第一條可直接用一次正常操作觸發。

## 發現

### 1. 一次正常操作就能讓已完成計劃的推送閘整批失效
severity: major
blocking: 是
引句:「已完成,留痕對不上現在的計劃(」
- **誰**:使用者本人,或照常收尾計劃的 AI。
- **從哪**:同一個提交裡把風險低計劃的 `status` 從 doing 改成 done,或去改一份已經 done 的計劃。這是收尾時本來就要做的事。
- **送什麼**:計劃正文改過,造成留痕過期(`_spec_gate_push_stale` 回傳原因)。例如條款或綁定的測試名變了,或不做清單被補進危險詞,又或正文被補進訊號讓門重判成風險高。
- **拿到什麼**:
  - 這次推送改到計劃檔本身、狀態是 done 時,`_live` 判成要跑。
  - `_spec_gate_push_one(done=True)` 在 `stale` 為真時,在跑測試與 `_spec_gate_push_light` 之前就先 `return None, "提醒…不擋"`。留痕裡的測試因此根本不跑,連紅的也一併放過。
  - 門重判成風險高的改動也只剩一行提醒。
  - 輕量設計審這道守衛也被走過。改前,已完成且被碰到的計劃不算 `full`,會走 `_spec_gate_push_nogo_only` 重判不做清單,略過危險詞就要求輕量審。改後它走 `full` 路徑,而 `done` 的過期提早返回,`nogo_only` 不會被叫到。
- 設計意圖(d3)只講「完成後改條款拿不到紅」。它沒有區分「本次提交才把 doing 改成 done」,而這正是實作中途改條款、結案時留痕過期的常見情形。以前這種情形會擋在「重跑 spec-gate」,現在只靠把狀態改成 done 就通過。
- file: `scripts/lumos:9527`(`_spec_gate_push_stale`)

### 2. 否定句提醒放寬後,漏掉真正的現況句
severity: minor
blocking: 否
引句:「(nxt == "" or nxt in _NS_NEG_MOD_BREAK or nxt in _NS_NEG_MODAL or nxt.isspace()」
- **誰**:寫筆記的 AI。
- **從哪**:`lumos note-shape` 的否定現況句提醒。
- **送什麼**:`FACT:目前還沒有提交前/推送前掛鉤 [來源:部署]`。「前」後面緊接任何標點(Unicode 類別 P,例如 `/`)現在都算子句記號。
- **拿到什麼**:這句明明是現況否定句,卻不被唸。
- 我用 `_ns_negation_hits` 實測:新版回傳 `[]`,把 `_ns_neg_clause_break` 換回舊判法則回傳 `[('還沒', 7)]`。
- 提醒本來就不擋,所以只算縱深防禦。

### 3. 規格閘教人用的 `git restore` 步驟,漏了前置條件檢查
severity: minor
blocking: 否
引句:「2. 改的是既有檔:git restore --source=<實作前的提交> -- <那支檔>,把它暫時換回實作前的版本(測試檔留現在的)」
- **誰**:照訊息操作的 AI 或使用者。
- **從哪**:`lumos spec-gate` 擋下「實作後才跑」時印出的補法。
- **送什麼**:第 1 步沒做就直接執行第 2 步。這個情境本來就是實作還沒提交。
- **拿到什麼**:`git restore --source` 直接覆寫工作目錄裡那支檔,未提交的實作隨之消失。
  - 第 4 步的 `git restore -- <實作的檔>` 沒帶 `--source`,是從 index 還原。實作只改了工作目錄、沒暫存也沒提交時,換不回來。
  - 新檔被手改成空殼後,若實作不在 index 或提交裡,同樣換不回來。
  - 訊息第 1 步有寫要先提交,所以只在跳過第 1 步時才會出事。
- 訊息沒有提醒「同一個工作目錄有別的會談的未提交改動時,暫時提交會一起收進去」。
- file: `~/.claude/CLAUDE.md` 並行會談條款

## 已看,無
- **①提示注入**:
  - 紀律範本只在第 2 條鐵則加了 `summary-add` / `summary-line` 兩個指令名,是靜態文字。
  - `summary-add` 的內容擋掉所有 `splitlines` 認得的換行,且必須以摘要前綴開頭,無法跳出摘要區塊或帶出 YAML 結構。
  - lint 與 doctor 新增的提醒,印筆記內容時都經 `_esc_clean` 並截到 20 至 120 字。
- **②節點越界**:`summary-add` 的節點經 `env.find` 解析,沿用既有寫入原語 `atomic_write_verify`,沒有新增路徑。
- **②`refcheck`**:
  - `_git_ignored` 先剔除絕對路徑與含 `..` 的路徑,再以 `--` 傳給 `check-ignore`。
  - `_ref_cmdline_token` 只切第一個詞,只做 `exists` 判斷,不讀內容。
- **②「(新增)」路徑**:只拿來比對集合,不會變成讀寫目標。
- **②密鑰、信箱、下載來源**:這份 diff 沒有新增。
- **②`_nodehome_worktree_homes`**:路徑來自 `git ls-files -z`。對工作目錄裡指向外部的捷徑檔只讀取並解析開頭欄位,不寫、不外洩。
- **③`home check` / `note-shape` 沒帶範圍改為預設 `--staged`**:`scripts/hooks/pre-commit`、`scripts/hooks/pre-push` 與 `.github/workflows/ci.yml` 都明寫旗標,沒有靠預設的呼叫端。
- **③規格閘實作後重跑(a)路徑**:
  - rc0 要求「已有條款指紋與門規則版本都相同的風險低留痕」,且沒過的全是「已綠」。
  - 留痕只在第一次以紅證據通過時才會寫,所以「先寫實作再補測試」的計劃拿不到這個放行。
  - 推送閘仍會跑留痕裡的測試。
- **③治理帳新增的 `spec-gate-record`**:讀取沿用 `_gov_vc_gate_events` 的路徑守衛。留痕裡的 `tests` 要先對應到 repo 自己發現到的測試(real/dangling)才會被跑,沒有新增 shell 插值。偽造留痕屬範圍外。

最嚴重 severity:major,blocking 共 1 條。
