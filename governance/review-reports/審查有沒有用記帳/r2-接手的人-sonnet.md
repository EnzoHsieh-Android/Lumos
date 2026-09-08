severity: major

# r2 接手的人(sonnet)——審查有沒有用記帳_計劃(驗收 r1 十六條折入)

立場不變:三個月後拿這本帳回答 Enzo「審查有沒有用」的人。被審(凍結):`governance/review-reports/審查有沒有用記帳/r2-snapshot.md`(sha256 7057acae6ec612d12554f53a33178fbfcf1ff9f89d281f14dd473c44a40375ea,已核對與磁碟一致)。

LUMOS-SPEC: docs/lumos-toolchain-knowledge/Projects/審查有沒有用記帳_計劃.md

方法:讀完 r2-snapshot 全文、r1-intake.md 與 r1 五份席報告(通才/接手的人/簡化守護者/架構對齊/外家否決-codex);對照 `git show HEAD:scripts/lumos` 落地的 `_report_severities`(4815-4825)、`cmd_canary`(4924 起,含 5063-5169 既有六選配欄寫側)、`_render_gov_stats`(4345 起)、`_loop_status_disposal`(13528 起)現況代碼;對 `docs/.canary-log.jsonl`(1221 筆,`reported` 欄位 0 筆)機械核對「五格」全新欄位確實還沒有任何一筆;讀 `skills/lumos-design-loop/SKILL.md` 步驟 10、`skills/lumos-code-loop/SKILL.md` 第 8 步後段落核對 [S4] 現況描述;讀 `_MANUAL_MIN_CHARS` 既有「≥4字且至少一個實字」機械檢查(scripts/lumos:4147)核對 [S2]「理由含實字」有沒有可重用的既有實作。

---

## (a) `--reported` 必填,但下限守衛對標題內嵌/列表格式形同虛設——三個月後 reported 的可信度是什麼

### F1
severity: major
blocking: 是
spec 段落:[S1]、實務隱患
判準:不改;帳面沒有任何欄位記錄「這筆 `reported` 有沒有被下限守衛咬到」,三個月後任何人讀 `gov --stats` 的 Σ報,都無法區分「有機械佐證的數字」跟「編排者自己打的、守衛形同虛設沒驗到的數字」,而後者 spec 自己已經承認存在且不會誤擋。

`--report`/`--snapshot` 兩個路徑與 sha256 現在就已經逐筆存進帳(`scripts/lumos:5269` `rec[_k + "_path"], rec[_k + "_sha256"] = _stored, _h`),原料都在,理論上可以事後重算 `_report_severities` 對每一筆 `reported` 判「守衛有咬中/守衛形同虛設」再彙總;但 [S1]/[S3] 都沒有提議存這個判準或在 `gov --stats` 新段裡多印一句「其中幾筆是獨立行格式、守衛真的驗過」。三個月後想回答「reported 有多可信」,唯一辦法是重新寫一支腳本掃全部報告檔——這正是本案自己批評過的「REVISIT 沒有指令=沒人會做」那個模式,只是這次連 REVISIT 都沒寫。

佐證:引句「**下限守衛的邊界**:`_report_severities` 只認獨立行,標題內嵌/列表格式的報告數到 0 → 守衛形同虛設(不擋),但不會誤擋;獨立行格式的報告若宣告行比填的多才擋。」
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:71`
file: `scripts/lumos:5247,5269`(寫側 `for _flag, _p in (("--report", report), …): rec[_k + "_path"], rec[_k + "_sha256"] = _stored, _h`——`report_path`/`report_sha256` 已逐筆存帳)
file: `scripts/lumos:4833,4844`(讀側 `_severity_check_row` 已在用這兩個既有欄位重讀報告檔——原料存在,但 spec 未提議用它回算「守衛有沒有咬中」)

---

## (b) 五格 ?:2026-09-09 前全 ?,K<5 提醒消失後誰保證樣本夠

### F2
severity: major
blocking: 否
spec 段落:[S3]
判準:不擋;K<5 印一句提醒是對我在 r1 F7 提的「沒講全庫彙總數字要多少筆才有意義」的合理回應,但 5 這個數字本身沒有任何理由,一旦越過就完全沉默,不再區分「K=6 這種剛過門檻」跟「K=600 這種真的夠」,也不分 design-loop / code-loop / 不同 tier 混算的問題。

機械核對 `docs/.canary-log.jsonl`(1221 筆)目前 `reported` 欄位 0 筆——K 從 0 起跳;但這個 repo 光是今天一天就已經在 `governance/review-reports/` 底下開了 `code-batch13`、`code-clause-bindings`、`code-clause-bindings-b`、`code-enforcement-obs`、`agentflow-absorption` 等多條迴圈,以現在的審查密度,K 很可能幾天內就衝過 5、遠早於「三個月」——那之後這句提醒就永久消失,而 spec 自己在同一行已經引用「全庫 227 個迴圈 45% 兩週內沒新帳」這個異質性事實,卻沒有回頭讓 K 的計算或警示反映這個異質性。

佐證:引句「(接手席:全庫 227 個迴圈 45% 兩週內沒新帳,舊帳永遠是 ?)」
引句:「K < 5 時多印一句」
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:54`
file: `docs/.canary-log.jsonl`(機械核對:1221 筆,`reported` 欄位 0 筆,K=0 起跳)

---

## (c) 「編排者重現不到」、self-found、算術不通——沒讀過計劃的人怎麼讀,有沒有一句話講 N 是人填的

### F3
severity: major
blocking: 是
spec 段落:[S2]、[S3]
判準:不改;[S2] 與 [S3] 對「R 這個值該怎麼標」給了三種不同的字面文字,實作者依字面挑到哪一種、讀者最終看到什麼,spec 沒講清楚,是會改變可見輸出的歧義,不是措辭潔癖。

三處分別是:[S2] 第三句講「讀側把 R 標成」後面接的是一個完整片語(含「人填」與「已對 intake」兩個限定詞);[S3] 第一句定義的一行式 funnel 樣板裡,R 前面只掛裸詞、沒有任何動作者或限定詞;[S3] 最後一句又講「所有輸出裡一律寫」後面接的是介於前兩者之間、缺限定詞的版本。三段互相打架,而唯一「逐字定義輸出格式」的是 [S3] 第一句那個裸版本,跟另外兩段承諾的內容對不上。

佐證:引句「閘仍不驗駁回的對錯(那是人工判斷,intake 留重現指令)」
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:48`(讀側把 R 標成「編排者重現不到(人填,已對 intake)」)
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:53`(一行式樣板本身只寫「重現不到 R」,無動作者、無限定詞)
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:56`(「駁回」在所有輸出裡一律寫「編排者重現不到」——比 :48 少了「人填,已對 intake」)

### F4
severity: major
blocking: 是
spec 段落:[S3]
判準:不改;「這是人記的帳、Σ報是人填的」這兩句揭露只掛在 `gov --stats` 新段的段首,`loop status --disposal` 尾端那一行式 funnel(工作流程裡每次收尾都會看到、比特地跑一次 `gov --stats` 頻繁得多的輸出)完全沒有對應揭露,單獨讀那一行的人不會知道 N 不是機器算出來的。

一個沒讀過計劃的人在收尾時看到「席位報 8(+編排者自找 1)→ 存活 9 / 重現不到 2 → 折 7 / 放行 0」這種行,字面上跟 `gov --stats` 表裡那些去重計數、commit 數這類機械數字並排長得一樣;要等到他另外去跑 `gov --stats` 才會讀到「Σ報是人填的、各席口徑不一」這句話,而正常工作流程不會逼他跑那個指令。

佐證:引句「N=該輪席位列 `reported` 加總;任何欄位缺(2026-09-09 前的帳)就★該格印」
引句:「這段內部也不印比率、也別自己算 Σ折/Σ報 當『審查有用率』——Σ報是人填的、各席口徑不一」
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:53`(一行式 funnel 樣板,無揭露句)
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:55`(★段首固定兩句★只掛在 `gov --stats` 新段,原文「這段」/「這段內部」指涉的是同一句上文的 `gov --stats` 段)

---

## (d) 兩條 REVISIT 量得到嗎——列出量的指令

### F5
severity: minor
blocking: 否
spec 段落:實務隱患
判準:不擋;2026-10-08 那條本來就要求「人工對」,完全自動化不合理,但連「找出 20 份候選席報告與各自 `reported` 值配對」這種純機械的準備工作都沒有給指令,人抽查前得先自己手動翻帳跟翻檔案配對,門檻比必要的高。

佐證:引句「REVISIT:2026-10-08 抽 20 份席報告人工對一次」
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:72`

### F6
severity: major
blocking: 是
spec 段落:實務隱患
判準:不改;2026-11-08 那條要量的兩件事,一件是「比例」而 [S3] 提案的 `gov --stats` 只有「總和」(Σ重現不到 是加總不是「有 findings-set 的輪裡 refuted-set 非 none 的比例」,兩個是不同數字),另一件「算術不通出現的輪數」在整份 [S3] 提案裡完全沒有任何欄位或段落去累積它——這正是本案自己要根治的「回頭條件沒有指令=沒人會回頭」,只是這次發生在自己身上。

`⚠ 算術不通` 只是 `loop status --disposal` 當下那一輪的即時提示,不落帳、不進 `gov --stats` 任何欄位;而 `_loop_status_disposal` 現有邏輯只讀「同一 loop 最新一輪」(`rid, latest = next(reversed(groups.items()))`,`scripts/lumos:13574`),同一迴圈較早輪次的 `⚠ 算術不通` 狀態在下一輪記帳後就讀不到、也沒有任何地方保存過——三個月後想回答「算術不通出現過幾輪」,唯一辦法是逐迴圈重放全部歷史帳列自己重算,同樣是「沒有指令」。

佐證:引句「REVISIT:2026-11-08 量兩件事——有 findings-set 的輪裡 refuted-set 非 none 的比例(0% 也是答案:代表沒人駁回或沒人記),以及」
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:75`
file: `governance/review-reports/審查有沒有用記帳/r2-snapshot.md:54`(`gov --stats` 新段只列 K、Σ報、Σ自找、Σ存活、Σ重現不到、Σ折、Σ放行、逃逸筆數,無「算術不通輪數」欄)
file: `scripts/lumos:13574`(HEAD 版本;`_loop_status_disposal` 只取 `next(reversed(groups.items()))`,同迴圈舊輪的即時提示不可回頭重讀)

---

## (e) r1 五席 blocking 各拿一條回頭看——修法有沒有真的解

已讀,對五條逐一核對如下(通才 F1/F5、接手 F2、簡化 finding 1、Codex #1/#2):

**通才 F1(blocker)/接手 F2(blocker)/簡化 finding 1(blocker)——自動數在標題內嵌/`- [major]` 列表/現行報告格式上數到 0**:三條問題核心都是「自動算出來的數字被當成官方 N」,[S1] 折入後把 `--reported` 改必填、`_report_severities` 只當下限守衛(見上引句),自動數不再是 N 的來源,原本「算錯的數字冒充真相」這件事已經不存在——三條原始 blocker 都解了。殘留的是新問題:守衛在同樣格式上一樣打不到,見本報告 F1(a)。

**通才 F5(blocker)——報 8 → 存活 9 算術倒退**:`--self-found-set` 讓自找項有處可去,`N+S < M+R` 時印「⚠ 算術不通」而不是悄悄放過,已用今天的真帳(`-b r1`,i9 自踩)驗過邏輯能對上;唯一沒講清楚的是 N 缺值(印 `?`)時這條比較式怎麼處理(`?` 不能參與數值比較),屬於實作細節層級,不影響「原本會算術倒退」這個 blocker 解沒解——解了。

**Codex #1(major,blocking:是)——舊帳缺欄位時只印「報 ?」,其他四格卻被要求印出來、偽裝成數字**:「五格各自判」直接對應 N/M/R/F/A(不含括號裡的 S 自找、不含迴圈累計的 E)各自獨立判斷缺值,不再拿散文猜——機械核對 `docs/.canary-log.jsonl` 現況(`findings_set` 等既有欄位本來就有些舊列有、`reported`/`refuted_set` 全新欄位全部沒有)證實五格會出現「部分格是 ?、部分格是真數字」混排,這是誠實呈現、不是偽裝,解了。

**Codex #2(major,blocking:是)——refuted-set 可由任意 id 與一字理由灌大,不是可驗的駁回**:id 造假這條路被「必帶 `--intake`、每個駁回 id 要在 intake 檔文字裡出現(子字串)」關死;「理由 ≥4 字且含實字」不是新發明的模糊詞,`scripts/lumos:4147` 既有 `[manual:]` 欄位已經在用同一套機械檢查(`len(x.strip()) >= _MANUAL_MIN_CHARS and re.search(r"[^\W_]", x)`),有現成可重用的實作,不是空話——解了。殘留的是 spec 自己已經誠實承認的天花板(id 對得上 intake 不代表重現做對了),那不是這條 Codex finding 原本要關的洞。

---

## [S4]/[S5]/PRIOR-ART/審計修正紀錄

已讀,無 finding。[S4] 現況核對:`skills/lumos-code-loop/SKILL.md` 第 8 步(「過了留痕」)之後、`## 停手與護欄` 之前確有一段獨立散文講 `lumos loop escape`(第 31 行);`skills/lumos-design-loop/SKILL.md` 步驟 10(第 39-40 行)目前只講合約候選,沒有逃逸字樣——[S4] 對兩份 skill 現況的描述準確,補位置對。[S5] 範圍刀逐條核對跟現況代碼(`cmd_canary`/`_render_gov_stats` 都是在既有結構加欄位/段落)一致。審計修正紀錄的五席 severity/blocking 數字(通才 2 blocker/6 blocking、接手 1 blocker/5 blocking、簡化 1 blocker/1 blocking、Codex 2 major/2 blocking、架構 1 major/1 blocking)逐份核對與各自報告的「總結」行一致。

引句:「design-loop skill 步驟 10 之後補一段獨立散文(跟 code-loop skill 第 8 步後那段同款)」
引句:「不新開帳本(全部加在既有 canary 列與 gov --stats 上)、不回填舊卷證」
引句:「PRIOR-ART: 世界=code review analytics 的」

## 圖譜鏡頭

已讀:`Systems/loop-convergence-recording.md`、`Issues/流程自產工作量未量測.md`——r2 折入的 [S1]/[S2]/[S3] 改動不動 `severity`/`findings`/`finding_kinds` 既有語意與收斂判準,兩節點宣稱的合約與量測欄位未受影響,無新 finding。

---

## 總結

最嚴重 severity:major(F1、F3、F4、F6 四條;無 blocker)。finding 條數:6(F1-F6)。blocking 條數:4(F1、F3、F4、F6 為 blocking:是;F2、F5 為 blocking:否)。核心結論:r1 五席指名的五個 blocking 洞(通才F1/F5、接手F2、簡化finding1、Codex#1/#2)折入後確實都關上了原本描述的那個具體漏洞;但折入的做法(必填+下限守衛、五格各自判、intake子字串驗)本身又開出兩類新的、更細的殘留問題——**帳上分不出「reported 有機械佐證」跟「reported 純自報」**(F1),以及**R 的標示文字與「N是人填的」揭露只寫在 spec 散文裡、沒有一致落到實際會被讀到的那一行輸出**(F3/F4);兩條 REVISIT 裡有一條(2026-11-08)想量的東西,現有提案完全沒有機制能算出來(F6),是本案自己要根治的毛病重演在自己身上。
