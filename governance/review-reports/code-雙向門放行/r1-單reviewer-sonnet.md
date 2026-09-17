severity: blocker

## F1 條款區塊指紋沒收「門判定」的全部輸入,推送前把危險內容悄悄塞進雙向門計劃可以繞過設計審
severity: blocker
blocking: yes

`_clause_block_sha`(門留痕的過期判定唯一依據)只雜湊「[S] 條款定義行」與「門判定訊號 2(連到的節點的合約/標籤)」,完全不包含全文關鍵字掃描(訊號 1)、自帶 risk/ 標籤(訊號 3)、`door:` 欄位(訊號 4),也不包含「實務隱患」節本身的已排除行內容。

引句:「條款區塊指紋(留痕綁的是它,不是整檔——r3 邊界席:整檔會被 updated: 這種維護弄成過期):」
引句:「每條 [S] 定義行剝行內程式碼、去 [keeps]、壓空白,按編號排序;再加門判定訊號 2 的輸入(連結節點+原因)。」
引句:「if _clause_block_sha(text, rows_b, _door_linked_signals(env, n, text)) != rec.get("clause_sha"):」
引句:「bad.append(f"{prel}:雙向門留痕過期(條款、測試名、或它連到的節點的合約/標籤變了),重跑 lumos spec-gate {Path(prel).stem}")」

這支門的整個設計前提是:「雙向門不派審,推送閘是它唯一的閘」(README 級宣稱,見門判定與 `_spec_gate_push_check` docstring),意思是雙向門一旦放行,不會再有人工或審查迴圈盯著它。既然如此,推送前這一關必須能偵測「這份計劃現在還算不算雙向門」,而不是只驗「條款測試還綠不綠」。但 `_spec_gate_push_check` 判斷留痕是否有效,唯一比對的就是 `clause_sha`,而 `clause_sha` 的輸入集合明顯比 `_door_judge` 用來決定門的輸入集合窄。

重現(在 /tmp 建的臨時 repo,不動正式 repo):
1. 建一份計劃「甲」,`## 實務隱患` 節四類已排除都合格、正文乾淨 → `lumos spec-gate Projects/甲_計劃` 判定「雙向門」,S1 紅,PASS(雙向門),留痕 `clause_sha=8b30726e...`。
2. `git commit` 這份計劃。
3. 改**正文**(不碰 `[S1]` 那一行),塞入「這支功能其實會呼叫 Stripe billing 扣款退款流程」這種金流敘述,`git commit`。
4. `lumos spec-gate --push-check HEAD~1..HEAD --repo .` → 輸出 `[spec-gate 推送前] ✓ 甲_計劃:留痕裡的 1 支測試全綠(t_flip)`,**rc=0,放行**。
5. 對照:同一份現在的檔案直接跑 `lumos spec-gate Projects/甲_計劃 --no-run`,工具自己也承認「現在」應該判單向門:`[spec-gate] 門: 單向門(關鍵字「Stripe」(第 7 行,金流))`。

也就是說:作者(或任何寫入這份計劃的人)只要不動 `[SN]` 那一行,事後想加什麼危險敘述都行,推送閘完全看不出來,雙向門的留痕永遠「有效」,這份計劃就這樣繞過設計審一路推上去。這不是風格問題,是這批改動最核心的安全機制(「雙向門不派審」)被自己的過期偵測邏輯放水。

file: `scripts/lumos:4930`(_clause_block_sha 定義)、`scripts/lumos:5584-5585`(push-check 的 clause_sha 比對與過期訊息)——皆以 /tmp/seat-reviewer(從 HEAD ecc9f52e 建的 detached worktree)裡的行號為準。

## F2 已排除行不過濾引用塊(`>`),範本/免責聲明文字也能被算成「合格已排除」
severity: major
blocking: yes

`_door_exclusions`/`_excluded_line` 從「## 實務隱患」節收集已排除行時,對每一行只做前綴清理(`_EXCL_LEAD_RE` 裡含 `>`),不像 `_rollback_section_chars` 那樣把整行是引用塊(`ln.lstrip().startswith(">")`)的行直接排除在外。

引句:「「已排除:<類>:<理由>」行的★唯一★解析——判定(掃描跳不跳這行)與證明(算不算四行之一)共用同一支」
引句:「實務隱患節裡合格的已排除行:回 ({類: 理由}, {合格行的行號});同類多行取第一行。」
引句:「return sum(len(re.findall(r"[^\W_]", ln)) for _no, ln in rows if not ln.lstrip().startswith(">"))」(這是 `_rollback_section_chars` 明確排除引用塊的寫法,對照組)

重現:計劃「乙」的「## 實務隱患」節寫「以下引用自範本文件,僅供參考格式,不代表本計劃實況:」,接著把四行「已排除:…」全部放進 `>` 引用塊(等於作者自己在文字上明講「這不是本計劃的真實狀況」)。`lumos spec-gate Projects/乙_計劃 --no-run` 仍印出「[spec-gate] 門: 雙向門(硬單向門訊號都沒命中;四類已排除:…)」——引用塊裡的範本文字被當成真的排除理由收下。

這跟 F1 是同一類問題(門判定的輸入集合定義不夠嚴謹),但觸發路徑不同、程式碼位置不同,獨立列一條。既然工具在同一支檔案裡對「回退節」已經有「引用塊不算實字」的先例(明確設計決定),「實務隱患」節卻沒有比照,是同一份 PR 內部不一致的疏漏,不是風格偏好。

file: `scripts/lumos:4839`(_excluded_line)、`scripts/lumos:4851`(_door_exclusions)——皆以 /tmp/seat-reviewer 裡的行號為準。

---

驗過但沒發現問題的路徑(附帶說明,非發現):
- `_test_exists_before` 的 `git grep -w`:`t_green` 對 `t_green2` 不誤判(word boundary 正確擋掉)。
- `_plan_first_commit` 取 `--diff-filter=A` 輸出最後一行(最舊)當首次進歷史的提交,方向正確。
- `_spec_gate_push_check` 裡 `idx` 快取:嘗試建構「後面平台設定讀不動時 return 0 會丟掉前面已經算出的 bad 清單」場景,但因為 `_clause_bindings_for`(在到達 `idx` 快取之前就會先跑一次同樣的平台索引建構並回報 err)已經先攔下設定錯誤、`continue` 掉那份計劃,不會走到共用 `idx` 快取那段,所以這條路徑在目前呼叫順序下摸不到,沒有列成發現。
- `_h2_section_lines` 對「實務隱患」標題帶編號前綴/括號後綴、節內三級標題、節後另一個二級節的邊界:讀 code 確認與 patch 自帶的 `t_spec_gate_section_bounds` 邏輯一致,沒有另外試出反例。
