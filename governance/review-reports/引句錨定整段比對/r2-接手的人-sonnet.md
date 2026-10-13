severity: major

我手上沒有 git 寫入權限,也沒建任何實驗檔,沒有東西要清。以下是 7 條 finding 和實務隱患逐類答。

## 1. 量測節的數字無法重算,算術也自相矛盾
severity: major
blocking: 是
引句:「得 2631 組;不分載體與非載體席。實作後用 `lumos quote-check --compare-rules` 重算同一口徑」
file: `docs/.canary-log.jsonl:1` 我用 spec 寫的口徑重算。

1. 口徑是「每列取 `report_path` 與 `snapshot_path`(沒有就取 `spec_path`),同一組只算一次,讀得到的才算」。在 repo 根實跑,不重複的組有 3279,讀得到的有 3259。我試過「只取 `snapshot_path`」,結果一樣是 3279 和 3259。
2. spec 寫的是 2631。口徑裡沒有任何條件能解釋 3259 變成 2631。可能是量測時的帳比較舊,可能是還有未寫出的篩選(例如排除抽不到引句的組),也可能是在別的工作樹量的。三個月後的人用這個口徑只會得到另一個數字。
3. 算術也對不上。「都判全數錨定 2587」加「舊過新不過 44」加「舊不過新過 45」已經是 2676,大於 2631。「舊判不過、新判也不過」那一格和「零引句(`_quote_rows` 回 None)」那一格都沒寫。
4. 這一節宣稱「數字以 `--compare-rules` 輸出為準」,但沒寫實作後兩邊對不上時以誰為準,也沒寫 `_quote_rows` 回 None 的組在交叉表放哪一格。
5. 「2026-09-20 之後 1718 組」「這 21 條那幾類共 5 條」也沒說依哪個欄位切(`ts` 或其他),無法重算。
6. 修法:把口徑補成可執行的篩選條件,四格交叉表加上「零引句」列,2631 改成重算後的實數,或註明量測日與當時的帳 commit。

## 2. `quote-check --compare-rules` 現有程式的參數表跑不起來,〈同步改的地方〉沒列這一項
severity: major
blocking: 是
引句:「`lumos quote-check --compare-rules [--since YYYY-MM-DD] [--repo 根]`:照〈量測〉的口徑掃帳」
file: `scripts/lumos:53141` 現有 `quote-check` 的 `qc_report` 是必填位置參數,`--spec` 是 `required=True`。
file: `scripts/lumos:53479` 現行分派只傳 `args.qc_report`、`args.qc_spec`、`as_json`。

1. 照 spec 與測試 `t_quote_full_span_compare_and_event` 下 `quote-check --compare-rules --repo X`,argparse 會直接報缺少位置參數和 `--spec`。要改成可選,還得在 `cmd_quote_check` 之外另開分支。
2. 〈同步改的地方〉只列範本、`_CODEX_AGENT_INSTRUCTIONS`、錯誤訊息等,沒列 parser 改動。`--rule`、`--compare-rules`、`--since`、`--repo` 四個旗標都沒寫互斥關係。例如 `--compare-rules` 搭配報告參數時怎麼處理,沒定義。
3. `--repo` 的語意不明。spec 寫「根」。測試用 `mkvault()` 造出的假 vault 沒有 `.git`,所以 `_vault_repo_root` 退回 `vault.parent`,帳就在 `--repo` 指的目錄底下。
4. 真實 repo 的帳在 `<根>/docs/.canary-log.jsonl`(`env.vault.parent`)。spec 沒寫 `--repo` 之後帳路徑怎麼解:是 `<repo>/.canary-log.jsonl` 還是 `<repo>/docs/.canary-log.jsonl`。
5. 此外 `quote-check` 目前註解寫明是 vault-free(`scripts/lumos:10168`),不碰圖譜。compare-rules 要讀帳,是否要建 `env`,spec 沒寫。
6. 報告路徑解析的相對根也沒寫。帳裡存的是相對 repo 根的路徑,工作目錄不同就讀不到。

## 3. RETIRE-IF 的「誤傷多於抓到」無法機械執行,分母還跟真正被擋的對象不同
severity: major
blocking: 是
引句:「就把記帳蓋的章改回舊判準並重新設計;或之後改成結構化引句」

1. 「人工逐條看後誤傷」是人判。可以接受,但該寫成 `[retire:人裁]` 並附 `[until:]`。CLAUDE.md 規定 RETIRE-IF 要寫成看到什麼就撤,這裡沒有機械式的觸發量。
2. `--compare-rules --since 2026-10-14` 掃的是全帳每一份報告,包含非載體席。非載體席的報告寫側不驗引句,本來就允許錨不到,新判準判不過也不會擋下任何東西。
3. 真正有後果的是載體席被擋的事件。分母混了不會被擋的席,誤傷和抓到的比例會失真。應該以寫側 blocked 事件(`quote-rule=full-span-v1`)為準再去對帳。
4. 另一個問題:上線後寫側會擋住新判準判不過的載體,所以「新判不過、舊判過」在上線後的新帳裡不會出現在載體席上,因為它們根本寫不進去。`--since 2026-10-14` 能數到的只剩非載體席。
5. REVISIT 寫「用 `lumos gov` 數 quote-rule 擋下事件」。`gov` 能不能按 note 內容篩 `quote-rule=`,spec 沒查證。我只確認 `gov` 子指令存在(`scripts/lumos:9688`、`52455`)。

## 4. 推翻 Issue 前提的紀錄方式不夠具體
severity: minor
blocking: 否
引句:「用 `lumos decision-add` 在本計劃記成決策,Issue 結案時註明前提失效的理由。」
file: `docs/lumos-toolchain-knowledge/Issues/引句錨定只驗前綴_後半可編造.md:1` Issue 現況是 `status: open`,`decisions` 欄位沒有任何一條。

1. 計劃檔 frontmatter 目前沒有 `decisions:` 欄位。`decision-add` 本身可以建,所以不算缺口。
2. 但「決策四欄」(決定、不選、因、代價)的內容 spec 沒寫。Issue 裡原話是「改判準必須同時推進回放引擎版本」。決策應寫明為什麼 `_REPLAY_ENGINE_REV` 不推,要不要在 Issue 本體也記 `decision-supersede` 或結案摘要,三個月後的人才查得到。
3. 立案清單第 18 項的「怎麼算做完」寫的是「所有講收貨三道的地方都有那句明文承認」。我查到 `skills/lumos-design-loop/reference.md`、`templates.md`、`SKILL.md`、`skills/lumos-code-loop/reference.md`、`docs/.../Systems/design-loop.md` 等都出現「收貨三道」。spec 的〈同步改的地方〉只覆蓋其中一部分,結案條件對不上。

## 5. 〈同步改的地方〉對現況的說法有三處對不上
severity: major
blocking: 是
引句:「`skills/lumos-project-notes/commands/05-設計審查迴圈.md` 講收貨三道那一行,補「格式不合也不採信;判準版本跟著帳上的章」。」
file: `skills/lumos-project-notes/commands/05-設計審查迴圈.md:14` 這一行是 quote-check 的指令表列,檔內沒有「收貨三道」這個詞。
file: `skills/lumos-design-loop/templates.md:63` 範本現行文字用全形括號(`（巢狀會被機械收貨截斷）`),spec 引的是半形。
file: `scripts/test_lumos.py:45493` `t_no_adhoc_normalizer_in_review_reports` 釘的是 `templates.md` 加「卷證規則」,以及 `巢狀` 二字。

1. 05 檔裡沒有「收貨三道」這行。最接近的是第 14 行(quote-check)和第 15 行(severity-check,寫的是「第四道收貨」)。改哪一行不明確,spec 要寫成「第 14 行」。
2. 範本改寫用的是「改成」整句取代。原句是全形括號,spec 引的原句是半形,照 spec 做逐字取代會找不到。
3. 範本漂移守衛:`t_no_adhoc_normalizer_in_review_reports` 只釘 SKILL.md 含「巢狀」。spec 說「保留『巢狀』二字」是對的。但新範本句「示範引句格式時不要寫『引句』這個標籤」會讓範本自己在文字裡出現「引句」二字。目前標籤正則要求後面緊接冒號和開引號,所以不會被誤抓。
4. spec 沒列哪些既有測試要先跑。新規則 4(落單收尾引號)可能讓既有 fixture 變紅,而既有 `t_quote_check_*`、`t_disposal_*`、`t_canary_record_*` 都用真報告造 fixture。要列出 `python3.14 scripts/test_lumos.py -k quote`、`-k disposal`、`-k canary` 這幾個子集,並先在實作前跑一次當基線。
5. `_quote_rows(..., rule=)` 的預設值沒寫。若預設是新判準,既有直接呼叫(包括 `seat-check` 的 `_quote_rows(rtext, "")`)行為會跟著變。spec 只說 `seat-check` 用 `_QUOTE_RULE_WRITE`,其他 3 個直接呼叫點的預設沒寫。

## 6. 自我治理的驗證步驟有兩處無法照做
severity: major
blocking: 是
引句:「確認舊判準那欄跟現行程式的結果逐組相同(證明舊分支沒被改壞)」
引句:「並對 `governance/replay/` 下抽 20 個已凍結迴圈實跑回放,零漂移才推。」
file: `scripts/lumos:1060` `cmd_loop_replay` 實際用法是 `lumos loop replay <編號> --golden governance/replay/<編號>/verdict.json`。

1. 「跟現行程式的結果逐組相同」是自己比自己。新程式裡的 legacy 分支和 `--compare-rules` 的 legacy 欄用的是同一份程式碼,必然相同,證明不了舊分支沒被改壞。
2. 要有意義,必須在改程式之前先用未改的 commit 跑一遍,把全帳每組的判定存成基線檔,上線前再拿新程式的 legacy 欄逐組比對。spec 沒寫要先存基線。
3. 回放指令確實存在,我實跑了一個:`lumos loop replay 爆炸半徑供糧 --golden governance/replay/爆炸半徑供糧/verdict.json`,約 0.8 秒,輸出「回放一致」。305 個凍結檔的 `engine_rev` 全是 `d5-2026-08-25`,等於現行 `_REPLAY_ENGINE_REV`,所以回放會真的重算,不會被跳過。
4. 既然單個只要不到 1 秒,抽 20 個沒有理由。305 個全跑約 4 分鐘左右,可以全跑。spec 沒寫抽樣方式(隨機、固定種子、還是涵蓋含巢狀引號的迴圈),三個月後的人無法複現。
5. 全帳 compare-rules 要跑多久,spec 沒寫。我用 Python 載入整份腳本的方式想重算,超過 120 秒被停掉,所以沒有得到跑時資料,⚠ 不確定是載入本身慢還是迴圈慢。spec 該註明預期時間。

## 7. 事件與比較表需要的「類別」沒有資料欄位承載
severity: minor
blocking: 否
引句:「note 帶 `quote-rule=full-span-v1` 與不合的類別,REVISIT 到期有資料可數。」
file: `scripts/lumos:25773` 現行 `_quote_rows` 格式不合只有 `{"malformed": True}` 一個旗標,沒有分類欄位。

1. spec 要求列出「哪一類」(引號沒閉合、落單收尾引號、整段比對後錨不到),但回傳的 row 形狀沒有類別欄位。
2. 測試只檢查 note 含 `quote-rule=full-span-v1` 這個子字串,類別格式沒有被任何測試釘住。
3. 事件 note 要有隨機 `id=` 才不會被 `gov` 去重折掉。現有同類事件都這樣寫(`scripts/lumos:10564` 起);spec 沒提,實作者可能漏掉。

## 已讀,無 finding 的部分
- 〈抽取規則〉六點與〈判準版本蓋在帳上〉的機制本身,我核對了 `_loop_status_disposal` 的取帳方式:有載體取載體(`scripts/lumos:26316`),所以蓋章只蓋在載體那一筆是對的。
- 回放機制確認屬實:凍結閉包存整行原樣,305 個凍結檔都沒有 `quote_rule` 欄。

## 實務隱患逐類
- 判定漂移或回放:spec 的機制成立,但驗證步驟的缺口見第 6 條。
- 欄位向前相容:`scripts/lumos:6572` 的註解寫明工具對未知欄位前向容忍,多寫 `quote_rule` 不會被讀側拒收。我沒找到會拒收未知欄位的白名單。
- 多機別版本:spec 自己已寫(舊版程式不認章)。無新增。
- 金流、對外送出:無,本機讀報告和帳本,與 spec 一致。

總結:最高等級 major,blocking 共 5 條(第 1、2、3、5、6 條)。
