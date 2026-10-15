severity: major

審查席:整合/知識同步(r1)。對照材料是 `web-react` 分支的 `Projects/前端框架從vue分出_計劃.md`(下稱 React 計劃),以及本工作樹的 `scripts/lumos`、`skills/lumos-design-loop/templates.md`、`scripts/test_lumos.py`。前掃 r1-intake 已修的條目沒有重報。

## 整合

### F1 前端判準太鬆,卻拿來整套換掉設計審鏡頭
- 位置:做法 1(`_FE_PLAN_WHEN`)對上做法 4(§7.7〈前端計劃改述〉)。
- 問題:做法 1 說判錯「只是多列幾題」,但做法 4 用同一個判準決定要不要把五個設計審鏡頭「換成」前端措辭。判準是計劃全文出現 `.tsx`、React、Vue、Vite、「前端」或「瀏覽器」任一個,所以只要提到就算。
- 具體例:審「前端知識與風險詞」這份計劃本身(Python 工具改動,正文滿是 `.tsx`、React、前端)。
  - `pitfalls --check` 會印前端提醒。
  - 編排者照 §7.7 把資源併發席換成「計時器、輪詢、訂閱的生命週期」。
  - 設計審的資源席因此不再問子程序、大輸入、記憶體,而這些正是 lumos 自己計劃最該問的。
  - React 計劃也會中同一招。
- 佐證:
  - 引句:「判錯的代價是多列幾題,不擋任何東西。」
  - 引句:「五個設計審鏡頭的立場照下表換成前端版措辭」
  - file: `skills/lumos-design-loop/templates.md:404`,A 表的資源併發列。
severity: major
- blocking: 是(照字面做,工具鏈自己的計劃會被審錯方向)

### F2 infra 題的觸發字被字串剝除吃掉
- 位置:做法 6 六題表,以及 S12。
- 問題:表只寫「每題 when 只收那一題的寫法」,沒分 `when`(字串字面先挖空)與 `when_raw`。shell 裡的路徑、位址幾乎都在引號裡。
- 實測 `_stack_norm_line`:
  - `PIDFILE="/tmp/e2e.pid"` 變成 `PIDFILE=""`。
  - `curl -s "http://localhost:8080/health"` 變成 `curl -s ""`。
  - `rm -rf "$DIR"` 變成 `rm -rf ""`。
- 後果:`/tmp/`、`localhost:數字` 這類 infra-shared 觸發字在常見寫法下不會亮。S12 若測試行寫成引號內的 `/tmp/`,字面實作會紅;只測未加引號寫法則會綠,實際漏題。
- 佐證:
  - 引句:「每題 when 只收那一題的寫法」
  - file: `scripts/lumos:30503`(`_stack_norm_line`)
  - file: `scripts/lumos:30531`(只有 `when_raw` 保留字串內容)
severity: major
- blocking: 是(題組上線後在最常見的 shell 寫法下不亮)

### F3 資安席的〈網頁前端類〉沒有人會去貼
- 位置:做法 5。
- 問題:
  - 計劃只在新小節裡寫「把這段接在六類後面一起貼」。
  - 編排者實際照著走的是圍欄裡的填空行和圍欄後的「兩個填空怎麼填」說明段,兩處都只寫貼〈消費專案六類〉。
  - 填空行被測試逐字釘住,計劃沒說改哪裡。
- 後果:
  - 照現有指引派工的編排者不會看到新類,F27 等於沒做。
  - 那段說明沒被逐字釘,可以補,但計劃沒寫要補。
- 佐證:
  - 引句:「把這段接在六類後面一起貼進逐類清單填空」
  - file: `skills/lumos-design-loop/templates.md:440`
  - file: `skills/lumos-design-loop/templates.md:459`
  - file: `scripts/test_lumos.py:97053`(`_SEC_FILL_CLASSES` 逐字釘)
  - file: `scripts/test_lumos.py:97252`(⑤ 也釘六類逐字相同)
severity: major
- blocking: 是

### F4 `_stack_key_for_file` 與題庫的先後合併沒有雙邊約定,S11 在合併後無力
- 位置:做法 7 交界。
- 問題:
  - 本計劃把順序(infra 在前)交給「後合進主線的那份」,但 React 計劃全文沒有 infra、本計劃或 `_TEST_INFRA_PATH_RE` 的任何字樣,只在「不做」寫「各在別的組」。
  - 本計劃的 related 與 lands_in 有指向對方,對方沒有回指。
  - 兩份都要改的地方有:`_stack_key_for_file` 本體與 docstring、`_review_role_for` 的 `key == "vue"`、`_arch_alignment_hints`、`t_stack_question_triggers` 的全表 id 集合。
  - 另外 templates.md §7.8 的 idioms 清單行(第 436 行)與本計劃新增的選配行緊鄰,git 會當衝突。
- 具體例:S11 的斷言是「適用題應不含 vue-reactive」。React 計劃合進去後,React 專案的 `.ts` 本來就不會出 vue 題,S11 即使順序被接錯(`e2e/` 走成 react 題組)也照綠。
- 修法方向:S11 要改成斷言 `_stack_key_for_file` 的回傳值就是 `infra`,fixture 用 React 依賴的 package.json;兩份計劃互相寫明合併順序。
- 佐證:
  - 引句:「誰後合進主線,誰負責把這個順序接好,並保留兩邊的測試」
  - 引句:「適用題應不含 vue-reactive、應改列 infra 題組」
  - file: `web-react/docs/lumos-toolchain-knowledge/Projects/前端框架從vue分出_計劃.md:77`(該計劃改 `_stack_key_for_file` 與 docstring)
  - file: `web-react/docs/lumos-toolchain-knowledge/Projects/前端框架從vue分出_計劃.md:83`(該計劃改 `_review_role_for`)
  - file: `web-react/docs/lumos-toolchain-knowledge/Projects/前端框架從vue分出_計劃.md:91`(該計劃改 templates.md 兩處 idioms 清單)
severity: major
- blocking: 是(順序接錯沒有任何測試會紅)

### F5 PAYMENT 例外比 WHY 宣稱的寬,S25 驗不到邊界
- 位置:做法 9 金流半。
- 問題:
  - WHY 說「`STRIPE_SECRET_KEY` 這類大寫識別字多半真的在接金流」所以不能一起豁免,S25 用它當「照舊命中」的例子。
  - 但 `STRIPE_SECRET_KEY` 是靠詞表裡獨立的 `stripe` 一條命中,跟 payment 的例外無關,S25 在例外開多寬都會綠。
  - 實測給定正規式(re.I)結果:`PAYMENT_API_KEY`、`PAYMENT_GATEWAY_URL`、`MOCK_PAYMENT_ENABLED` 全不算金流;`PAYMENT-timeout` 與 `PAYMENT.timeout` 仍算。
  - 沒有任何驗收條款釘住「真在接金流的 PAYMENT_* 識別字」該算還是不算。
- 具體例:計劃只在一行寫 `PAYMENT_GATEWAY_URL`、全文沒有付款、金流、扣款等其他金流詞,金流類不亮,門可判低。S28 量到的 0 份只代表現有 356 份沒有這種寫法。
- 佐證:
  - 引句:「前面或後面緊貼底線時不算」
  - file: `scripts/lumos:29908`(`stripe` 是獨立詞)
severity: major
- blocking: 是(守衛面放寬的邊界沒被任何驗收釘住)

## 次要

### F6 infra 路徑規則對任何副檔名都生效,留下雜訊
- 位置:做法 7。
- 問題:`_stack_key_for_file` 的 infra 規則對任何副檔名成立,而 `pitfalls --diff` 組 `stack_questions` 時的 `added` 迴圈不過 `_stack_changed_ok` 的副檔名過濾。
- 後果:
  - `e2e/README.md`、`fixtures/orders.json`、`seeds/data.csv` 這類檔會讓人讀輸出多一段 `[infra 效能檢核]` 全表。
  - `.sql` 放在 `seeds/` 底下會從 sql 題組改走 infra。
- 另一處不一致:計劃寫 `.bash`,但 `.bash` 不在五份「什麼算程式檔」清單裡(`t_code_exts_lists_agree` 釘),改檔前推播、提交前掛鉤都不會碰它。
- 佐證:
  - 引句:「不再拿 vue-reactive、sql-transaction 這類產品題」
  - file: `scripts/lumos:47272`(`for f in added` 迴圈)
severity: minor
- blocking: 否(多印一段題目,不影響擋與放)

### F7 知識同步的幾個漏點
- `Systems/情境出題` 第 48 行寫死「14 項」和「依任務書提問九類與六個階段挑出」,加完是 25 列。計劃只說「記內容源」,沒說要改這句。
- `Systems/規格閘`:
  - 計劃只補了「四類關鍵字表粗」那句(第 40 行)。
  - 第 134 行「條款含「送出」就變風險高」和第 62 行金流詞表也沒跟上例外。
  - `Projects/雙向門放行_計劃` 第 135 行的範例「送出查詢」仍命中,不用改。
- lands_in 沒列 `Systems/arch-alignment-lens`。做法 6、7 改的 `_review_role_for` 與 `_arch_alignment_hints` 寫在那一篇(它是角色鏡頭 review_roles 的說明處),React 計劃有列它。
  - `Projects/代碼審前後端角色鏡頭_計劃` 第 85 行「題組鍵對應角色」那句,兩份計劃都要改。
- 做法 8 改的 `commands/test-quality-standard.md` 沒有任何 Systems 節點引用它。`Systems/test-quality-cli` 管的是 `test_quality.py` 與 `test_test_quality_cli.py`,不管這份標準,lands_in 指它對不上。
- `commands/02-動手前算波及.md` 的 `--stage` 說明、`skills/lumos-project-notes/SKILL.md` 第 42 行、`lumos pitfalls` 的 help 字串都沒列入要改,新增的「前端面」段和 `--check` 提醒在使用說明裡找不到。
- `Systems/效能檢核目錄` 的「題目 id 對照」表,本計劃(infra 六題)和 React 計劃(react 七題)都要加列,是同一張表的衝突點。
- 門規則版本升 13 會讓其他在途分支(web-react、web-notes、web-ledger 等)已記的規格閘留痕全部重數。計劃的〈相容〉只談題庫形狀,沒提這個;web-notes 的小修計劃第 165 行還依賴「門判定規則版本與現在一樣」。
severity: minor
- blocking: 否(都是文件與說明不同步,不改變程式行為)

### F8 §7.7 小節位置與涵蓋範圍沒講清楚
- A 表後面緊接「三條硬性配套」(問句每輪改述、單席通才不套立場),再才是 `### C`。計劃只說「A 表之後加一個 ### 小節」,字面做會把配套切到新小節底下。
- 前端措辭表只涵蓋五個鏡頭,A 表的簡化/反過度設計沒有對應列。
- 固定措辭表與「立場句每輪改述、不逐字貼」的配套互相拉扯,計劃沒說這張表也是語意規格。
- 佐證:
  - 引句:「A 表之後加一個 ### 小節〈前端計劃改述〉」
  - file: `skills/lumos-design-loop/templates.md:416`(三條硬性配套)
severity: minor
- blocking: 否

### F9 S28 與 REVISIT 要重跑的比對腳本沒有存放處
- 「2026-10-15 那支唯讀比對腳本」沒有名字,也沒說存在哪裡。三個消費專案 repo(order-demo、order-web、order-web-impl)也沒給路徑。
- 三個月後接手的人無法照做,重寫一支的口徑(「(行, 類)命中」怎麼算)就會跟 0 份的基準不可比。
- 佐證:引句:「重跑 2026-10-15 那支唯讀比對腳本」
severity: minor
- blocking: 否(實作者不會做錯,但 2027-01-15 那兩條 REVISIT 無法執行)

### F10 `_stack_changed_ok` 是共用函式,跳過 infra 路徑要放對位置
- 計劃要的是「掃代碼型樣時跳過」,不是「棧別觸發也跳過」。
- 但 `_stack_changed_ok` 被兩邊共用,`_tension_candidates_into` 還依賴「候選的題必在 `stack_questions_applicable`」這個不變量。把跳過寫進這個共用函式,infra 題就拿不到 `changed_lines`,S12 會紅。
- 計劃應明說「只在 claims 迴圈跳過,不改共用函式」。
- 佐證:
  - 引句:「分級不因造資料的 SQL 變 high」
  - file: `scripts/lumos:46644`
  - file: `scripts/lumos:47252`(claims 迴圈)
severity: minor
- blocking: 否(S12 紅時會被當場發現)

## 風險類
- **守衛面**:F5 是放寬缺口。infra 進表態閘(d2)會讓工具鏈自己的 `get.sh`、`governance/*.sh` 多一道手續,計劃已自述,我不報。
- **舊資料與舊帳相容**:門規則版本升 13 會讓在途分支的留痕重數,見 F7。題庫形狀的相容(多一個 `role` 鍵、多一個 `infra` 值)我實查了呼叫端,`_STACK_TRIGGERS` 與 `_ROLE_BACK_KEYS` 的查詢都不會崩。
- **與其他計劃的交界**:F4(React 計劃)、F7(web-notes 的規格閘小修依賴門規則版本)。

已讀,無 finding:現況段其餘宣稱我逐條對過程式,都屬實。
- `.sh` 在 `_stack_key_for_file` 回 None。
- `e2e/` 底下的 `.ts` 現在判 vue。
- `_PITFALL_DIFF_TEST_PAT` 不認 e2e。
- 架構對齊對照檔沒排除工具自帶檔。
- `_vendored_skip` 已在 `_pitfall_diff_collect` 算好。
- 風險詞的送出例外正規式,在 Python 3.14 下六個例句行為都與 S18 到 S22 相符。
- 做法 9 的其餘部分。

最嚴重 severity:major;blocking 共 5 條(F1、F2、F3、F4、F5)。
