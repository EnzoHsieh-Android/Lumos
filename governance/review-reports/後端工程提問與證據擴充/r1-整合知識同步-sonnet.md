severity: major

審查範圍:逐節讀完 spec 全文,並對照 `scripts/lumos`、`scripts/test_lumos.py`、skills 與 ARCHITECTURE.md。spec 與圖譜計劃節點內容相同。`Verification/` 的 295 篇、276 篇 pass 兩個數字我實數過,是對的,不重報。

### F1
severity: major
blocking: 是(消費專案與本 repo 的文件同步缺口,會讓 `t_docs_command_count` 翻紅,屬必修)
- 段落:做法 B(`lumos capabilities`)、做法 C(`lumos evidence run` 與 `evidence check`)、分階段第 3 階段。
- 問題:本案新增兩個頂層命令,但整份 spec 沒有「文件與說明同步」這一項,階段 3 的完成判準只寫「綁定測試全綠、推送關卡過、CI 綠」。三個月後的接手者照做,會在推送前被文件計數守衛擋下。
- file: `ARCHITECTURE.md:108`、`ARCHITECTURE.md:112`、`ARCHITECTURE.md:142`:三處寫死「86 個頂層命令」。
- file: `scripts/test_lumos.py:27744`:`t_docs_command_count` 取 `--help` 的 choices 真值,和全部活文件比對。
- file: `scripts/lumos:50477`:子命令一句話說明表,要新增兩個鍵。
- file: `skills/lumos-project-notes/commands/INDEX.md:35`:03 寫回圖譜那列的命令清單,也要補。
- 判準:新命令一定會讓計數守衛翻紅,spec 沒有承接點。

### F2
severity: major
blocking: 是
- 段落:做法 D 第 7 列(`spec-trace` 認 `[evidence:]`)、實務隱患「守衛面」。
- 問題:spec 說 S10 的測試涵蓋 `INV_TAG_RE`、規格閘文法、`spec-trace` 三處,但沒寫兩件事。
  - 第一,`[evidence:]` 在風險低計劃裡算什麼。規格閘現行規則是「風險低不收 `[manual:]`、測試要存在」。`[evidence:]` 既不是 test 也不是 manual,spec 沒定它在風險低時是被收下還是被擋下。
  - 第二,skill 裡的條款寫法敘述會變成錯的。
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:16`:`②綁定+回退節(_clause_check(door);風險低不收 manual、測試要存在且名字互不相同)`。
- file: `skills/lumos-design-loop/SKILL.md:59`:寫「每條驗收條款寫 `[test:測試名]`,沒有測試可掛的寫 `[manual:…]`,處置閘第五步會擋沒標的」。
- file: `skills/lumos-project-notes/commands/05-設計審查迴圈.md:13`:同樣只列這兩種標記。
- file: `scripts/lumos:5491`:`INV_TAG_RE` 的標籤集合是 test、audit、kill、src、git、manual、keeps,沒有 evidence。
- 判準:`[evidence:]` 在低風險與高風險兩種計劃下的判定沒定義,skill 兩處敘述上線即過期。

### F3
severity: major
blocking: 是
- 段落:做法 C「pass 要有證據」與「繞過 `lumos set` 的寫法」,S8。
- 問題:spec 說「lint 對 2026-10-19 之後新建、狀態 pass、證據帳沒有有效列的驗證筆記報錯」,例外只有舊筆記。但同一種 `type: verification` 還有守衛紀錄,由 `lumos guard settle` 直接把 status 寫成 pass,靠合約測試綁定,不跑 `evidence run`。
  - 2026-10-19 之後每次轉正都會被新 lint 判錯,spec 沒寫豁免。
  - 同一支函式也被 `drift fix --kind c5` 共用。
  - 另外 `lumos new` 的 `date:` 是手填欄位,「新建」若以它判斷,改日期就能繞過;spec 沒指定判斷欄位。
- file: `scripts/lumos:15706`:`_guard_settle_record_lines` 把守衛紀錄的 status 改成 pass,docstring 寫明 settle 與 `drift fix --kind c5` 共用。
- file: `scripts/lumos:3272`:守衛紀錄的判定是 `type == verification` 且帶 `GUARD_MARK_FIELD`(`guards` 欄位)。
- 判準:不處理就會讓合約轉正流程在 10-19 後全面被 lint 擋住。

### F4
severity: minor
blocking: 否
- 段落:做法 C「驗證筆記狀態」(`_STATUS_ENUM` 加 `fail`、`blocked`)。
- 問題:狀態集合有三份衍生物,spec 只提改 `_STATUS_ENUM`,會留下過期敘述。
  - lint 的錯誤提示字串是手寫的一份,不會跟著列舉更新。
  - `_DRIFT_C3_STATUSES` 由列舉減掉 pending 算出,所以 `drift fix c3 --status` 會自動多出可寫 `fail`、`blocked`,spec 沒說這是否有意。
  - `QUERY_CLOSED_STATUSES` 不含 fail 與 blocked,「未結」類查詢會把它們算進去,語意沒交代。
- file: `scripts/lumos:6853`:手寫的 `"pass/stale/superseded/pending/abandoned"`。
- file: `scripts/lumos:38475`:`_DRIFT_C3_STATUSES` 的定義。
- file: `scripts/lumos:18472`:`QUERY_CLOSED_STATUSES`。
- 判準:都是會過期的敘述或語意,沒有立即失敗場景。

### F5
severity: major
blocking: 是
- 段落:做法 C「證據帳要被追蹤」與簿記名單、待決問題 Q2、分階段。
- 問題:證據帳的檔名與位置、原始檔目錄的位置都沒寫,而 spec 要求「加進簿記名單」,名單是逐字路徑字串。
  - 內部自相矛盾:做法 C 說原始檔目錄要加進簿記名單,Q2 卻還在問「原始檔進版控,或放忽略清單」,並標了阻塞。
  - 到消費專案的路徑沒寫:`lumos init` 與 `lumos update` 補 `docs/.gitignore` 的清單是固定的幾本本機帳,沒有「新帳檔要刻意不忽略」的說明。
  - 預設放哪、怎麼確保沒被舊專案的 `.gitignore` 吃掉,spec 沒寫。接手者只能自己選,CI 讀不到帳的失敗要上線後才發現。
  - `.lumos/config.json` 的 `capabilities` 區塊也沒寫缺區塊時的行為(空清單還是報錯)。專案骨架 `_init_config_skeleton` 與 `lumos update` 都不會補這一塊。
- file: `scripts/lumos:23079`:`docs/.gitignore` 骨架的內容,是固定的本機帳清單。
- file: `scripts/lumos:27097`:`_BOOKKEEPING_FILES` 要放逐字路徑。
- file: `scripts/lumos:27116`:`_BOOKKEEPING_DIRS` 要放目錄前綴。
- file: `scripts/lumos:23101`:`governance/.gitignore` 只忽略 `code-loop/` 與 `runtime/`。
- 判準:路徑未定,簿記名單與 S5 的測試都寫不出來。

### F6
severity: major
blocking: 是
- 段落:緣起(任務書三樣內容)、做法 F、分階段第 4 到 6 階段、驗收條款 S12 與 S13。
- 問題:緣起只收進任務書的三樣東西(提問九類、七道關卡、示範情境)。任務書要求的「其他開發者依文件可重現示範」沒有承接點,而任務書原文沒有進 repo。
  - S12、S13 都是 `[manual:]`,完成判準是「有 PASS 證據列」。
  - 沒有任何一條要求示範 repo 附重現文件。
  - 沒有「新環境照文件跑出同樣證據列」的驗收。
  - 也沒寫示範 repo 的位置怎麼從本 repo 的 README 或 ONBOARDING 連過去。
- file: `README.md:44`:現有的「demo」只是示意圖,與此需求無關。
- file: `ONBOARDING.md`:搜 demo 與示範字樣無相關內容。
- 判準:需求在 repo 內無落點,三個月後無人能判斷是否達成。

### F7
severity: minor
blocking: 否
- 段落:frontmatter `lands_in` 與 `related`、摘要第二行的翻案決策。
- 問題:`lands_in` 列了 `Systems/lumos-guard`,但那篇的 `about_code` 全是 TypeScript 外掛檔。本案不改 PreToolUse 或外掛,B 塊只印建議條目,所以它不是任何被改程式的家。真正被改的函式,家是 `scripts/lumos` 之下的幾篇:規格閘、`lumos-cli-write`、`pitfalls-code-loop`、效能檢核目錄。
  - 被翻案的舊決策住在 `開發工作流總覽`,它不在 `lands_in` 或回退節的作廢步驟裡。
  - `skills/lumos-project-notes/reference.md:854` 的工作樹改動(未提交,不是我改的)已寫「2026-10-12 已作廢」,但被取代的功能還沒做。
- file: `docs/lumos-toolchain-knowledge/Systems/lumos-guard.md:8`:`about_code` 起始處。
- file: `skills/lumos-project-notes/reference.md:854`。
- 判準:`lands_in` 對錯是文件正確性問題,沒有執行失敗場景。

### F8
severity: minor
blocking: 否
- 段落:做法 B(`claude mcp list`、`permissions.ask`)、待決問題 Q1。
- 問題:本 repo 明確支援 Codex(`~/.codex/hooks.json`),README 也寫「三項外掛目前沒有對應的 Codex 外掛」。B 塊從頭到尾只有 Claude Code 的做法,`lumos capabilities` 的探測和建議條目都綁死 Claude。Codex 會談跑它時,探測命令不存在,會把所有 MCP 判成不可用。Codex 的核准設定在 `config.toml`,spec 沒提,AGENTS.md 也沒有對應敘述。
- file: `scripts/lumos:23519`:`_HARNESS_HOME` 同時登記 claude 與 codex。
- file: `README.md:22`:Codex 無對應外掛的說明。
- 判準:Codex 路徑是遺漏,影響範圍限於能力探測與權限建議。

### F9
severity: major
blocking: 是 ⚠(Claude Code 對 Bash 權限規則怎麼比對包裝命令,我沒有在本 repo 內找到可驗證的出處;理由如下)
- 段落:實務隱患「不可逆」(「破壞性指令照 Claude Code 既有權限確認」)。
- 問題:`evidence run -- <指令>` 的外層命令字串是 `lumos evidence run …`。使用者若已允許 `lumos` 開頭的 Bash,被包在後面的指令不會再被確認。spec 把 MCP 工具的 `permissions.ask` 當成唯一防線,沒涵蓋這條包裝路徑。
  - 全域設定沒有 `Bash(lumos…)` 允許規則。
  - 本 repo 也沒有任何 allow 清單可驗證。
  - 缺的是 `evidence run` 對內層指令的預檢,例如正式環境連線字串檢查,或破壞性關鍵字詢問。
- file: `~/.claude/settings.json`:搜 lumos 只有 hooks 與外掛啟用。
- 判準:包裝層繞過權限確認屬 prod-irreversible 類;證據不足,所以標 ⚠。

### F10
severity: minor
blocking: 否
- 段落:做法 A「題目從哪來」(`_PITFALL_QUESTIONS` 新增「後端資料與交易」類)。
- 問題:spec 只提 `_PITFALL_QUESTIONS` 要改形狀,但新類還牽動別處。
  - 命中類由 `PITFALL_CLASSES` 的關鍵字表決定,`_PITFALL_COMPILED` 和 `_PITFALL_QUESTIONS` 要同鍵,新類要同時補關鍵字。
  - 命中新類後,`pitfalls --check` 會要求計劃有〈實務隱患〉小節。
  - 效能檢核目錄現在只是 `_STACK_QUESTION_SPECS` 的內容源,不是 `_PITFALL_QUESTIONS` 的,「目錄改動須同步此表」的漂移守衛是針對棧別題庫。
  - 程式註解寫三處同步,其中一處是 `skills/lumos-design-loop/templates.md`,新類是否也要寫進去,spec 沒寫。
  - 四個中文類名(`_DOOR_CLASS_ZH`、`_RISK_ENUM`)是風險門的正式集合。新類不屬於「風險類」時,不能被誤解成可標 `risk/` 的值。
- file: `scripts/lumos:26465`:`_PITFALL_COMPILED` 由 `PITFALL_CLASSES` 派生。
- file: `scripts/lumos:26471`:「三處同步:此處+templates.md:31+design-loop skill」。
- file: `scripts/lumos:42877`:命中類後 `--check` 要求〈實務隱患〉小節。
- file: `scripts/lumos:7059`:`_DOOR_CLASS_ZH` 正式集合只有四類。
- 判準:新增類別的連動範圍不明,尚無單一失敗場景。

### 實務隱患鏡頭(pitfalls 命中類)
- payment:無。spec 寫「已排除:金流」,訂單只到建立與扣庫存,與 F9 無關。
- external-send:無。k6 目標限定 localhost,只寫在示範 repo 的設定,本 repo 沒有機械擋。
- prod-irreversible:有,見 F9。

最嚴重 severity:major,blocking 共 6 條(F1、F2、F3、F5、F6、F9)。

## 補引句(編排者續談請同席補,只補不改判)

- F1 引句:「綁定測試全綠、推送關卡過、CI 綠」
- F2 引句:「新寫:擴 `spec-trace` 認 `[evidence:]` 綁定」
- F3 引句:「lint 對 2026-10-19 之後新建、狀態 pass、證據帳沒有有效列的驗證筆記報錯」
- F4 引句:「`_STATUS_ENUM` 的 verification 加 `fail` 與 `blocked`」
- F5 引句:「證據帳與原始檔目錄要加進這兩份名單」
- F6 引句:「原文沒有進 repo),要 Lumos 延伸成能驅動後端開發全流程的工具」
- F7 引句:「唯一的工具限制在審查子代理身上,見 [[Systems/lumos-guard]]」
- F8 引句:「MCP 看 `claude mcp list`、CLI 看指令在不在」
- F9 引句:「破壞性指令照 Claude Code 既有權限確認」
- F10 引句:「風險面放進既有的計劃稿題庫(`_PITFALL_QUESTIONS` 那一族)新增一個」
