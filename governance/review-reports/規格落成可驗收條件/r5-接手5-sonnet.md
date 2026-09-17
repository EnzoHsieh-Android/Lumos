severity: blocker

## 逐節審查

### 摘要/PRIOR-ART/RETIRE-IF
已讀,無 finding。

### 兩層要分開
已讀,無 finding。

### 一、條款句式
已讀,無 finding(停用詞硬排除規則與 r1/r2/r3 折入脈絡自洽,S1/S2 對應得上)。

### 二、綁定與回退節
已讀,無 finding(`_clause_bindings_for` 存在性複用屬實;`_MANUAL_MIN_CHARS` 早已存在,S4 與現制一致)。

### 三、新閘 `lumos spec-gate`(含①支數解析)

**finding 1**
severity: blocker
S6–S8 依賴的「解析支數」設計,把 N 定義成「跑到的測試支數」,但本 repo 自己的 `.lumos/config.json`(`test_profile: python`、`run_cmd: python3 scripts/test_lumos.py -k {method}`)輸出摘要行 `N passed, M failed` 統計的是 `check()` 斷言次數(`scripts/test_lumos.py:79-85` 的全域 `PASS`/`FAIL`,由 `:29439` 印出),不是 `-k` 匹配到的測試函式數(函式數另外印在 `:29353` 的「N 案例」)。實測 `t_escape_auto_dedup`(唯一匹配 1 支函式)印出 `2 passed, 0 failed`——同一支函式因為內部有 2 個 `check()` 就會被規格閘誤判成「N≥2,篩選匹配到 N 支」。
引句:「解析支數:unittest `Ran N test(s)`(含 skipped)、pytest 的 failed+passed+skipped+error+xfail 相加」
blocking: 是——判準:本 repo 是這份設計唯一已知的真實落地場域(python profile),若不修正,S7/S8 對本 repo 幾乎所有測試都會系統性誤報「弱證據/篩選不唯一」,規格閘的紅綠匯總從一開始就不可信。

**finding 2**
severity: minor
S5「run_cmd 不能鎖單支測試就略過並印怎麼改」與既有 `{method}` 佔位符慣例(`scripts/lumos:9475-9478`、`:14743`)一致,無新增風險。
引句:「若 run_cmd 不能鎖單支測試,則規格閘應略過跑的步驟並印出怎麼改」
blocking: 否——判準:純複用既有機制,沒有新行為需要驗證。

### 四、處置閘第五步共用檢查器(③共用檢查器一致性)

**finding 3**
severity: major
「新合約文字草稿」是準備直接替換 ★INVARIANT★ 的文字,但草稿裡完全沒提 `_SPEC_GATE_SINCE` 的不回溯例外,而同一節緊接著又寫「新的 `_SPEC_GATE_SINCE` 只決定句式那一段跳不跳」、S10 也要求「規格閘與處置閘第五步應跳過句式檢查」。現行姊妹合約(`_CLAUSE_GATE_SINCE`/`_LANDING_GATE_SINCE`)的 ★INVARIANT★ 文字都把跳過條件寫進正文(`docs/lumos-toolchain-knowledge/Systems/design-loop.md` 該行:「code- 迴圈、無 [SN]、舊迴圈、凍結/回放模式跳過」),本案草稿若照抄落地,會是三支不回溯常數裡唯一一支跳過條件不在合約正文、只活在計劃筆記裡的。
引句:「每條 `[SN]` 定義行要合一條文法、綁 `[test:]` 或 `[manual:≥4 字]`;沒標的擋、懸空只提醒不擋;不合文法印『格式看不懂』;回退節不足 20 字擋;判定與 `lumos spec-trace` 同源」
blocking: 是——判準:落地時若照這份「草稿」字面搬進 ★INVARIANT★,S10 的行為就沒有合約文字背書,下一個接手者讀合約行會判斷不出舊迴圈為何被跳過句式檢查,重演本節點自己「S21 落點」那次「規則只寫一句流程規則、沒人照做」的舊教訓。

**finding 4**
severity: minor
S9「處置閘第五步應呼叫與規格閘同一支條款檢查器且對同一份計劃給出相同判定」,在半套只有 `door="one-way"` 一種取值的前提下,兩端呼叫必然給出相同判定,測試是重言式,驗不出「門不同時判定不同」這件事(那是雙向門放行_計劃的範圍)。
引句:「處置閘第五步應呼叫與規格閘同一支條款檢查器且對同一份計劃給出相同判定」
blocking: 否——判準:不影響半套本身的正確性,只是提前埋的測試對第二階段沒有實質保障力,風險留在雙向門放行_計劃自己的設計審裡處理即可。

### 為什麼(⑤半套下這張表還撐得住嗎)

**finding 5**
severity: minor
⚠
「逃逸帳」那一列的論證(「這套流程從來沒量過自己的漏網率」)原本服務於「雙向門不派審敢不敢做」的決策,現在逃逸自動記已拆成獨立計劃、雙向門本身也拆走待命,這一列留在半套的「為什麼」裡對讀者的實際說服力變弱(半套沒有「少審」這件事可被逃逸帳驗證)。誠實界線一節已部分自認這個張力,沒有新增隱患,只是論證強度打折。
引句:「這套流程從來沒量過自己的漏網率;帳空不代表沒漏,只代表沒人記」
blocking: 否——判準:不影響半套的機制正確性,只是文檔說服力問題,且作者已在「誠實界線」自陳結構性自指,不算隱藏遺漏。

### 落地順序 六步(⑥每步可獨驗、哪步會讓現行處置閘變壞)

**finding 6**
severity: major
第二步「`_clause_check(plan, door)` 接處置閘(S9)」是六步裡唯一會改動現行處置閘輸出的一步:一旦落地,凡首筆帳晚於 `_SPEC_GATE_SINCE` 的新迴圈,即使計劃早就掛了 [SN] 條款,只要沒補「## 回退」節或條款句式不合新文法,就會從「原本能過」變成「處置閘 FAIL」。這個行為變化本身在設計裡是刻意的(單向門、要綁測試+審計),但正是因為 finding 3 指出的合約文字缺口,實作者若只照搬草稿去接線,回溯例外容易被漏掉,行為就會波及到不該波及的舊迴圈。
引句:「`_clause_check(plan, door)` 接處置閘(S9,先填回退 sha、`anchor approve`)」
blocking: 是——判準:此步是唯一直接改變現行處置閘 PASS/FAIL 結果的步驟,若 `_SPEC_GATE_SINCE` 回溯例外沒有連同 S9 一起機械驗證(而不是只在筆記裡提一句),落地當下會讓一批既有計劃在未被告知的情況下從能過閘變成過不了閘。

### 實務隱患
已讀,無 finding(七類逐一排除都附了理由,「守衛面」一類正確點出改動不可變合約行本身的風險並要求代碼審+錨點核可)。

### 驗收條款(S1–S11)逐條對設計節

已核對:11 條全部能在設計節(一/二/三/四)裡找到對應描述,11 個測試名(`t_spec_gate_ears_shapes` … `t_doctor_spec_gate_stats`)互不相同,且與 `scripts/test_lumos.py` 現有 968 支 `t_` 開頭測試逐一比對零撞名。設計節裡「印匯總」「不留痕不寫帳」「`_SPEC_GATE_SINCE`」「模板/CLAUDE.md/skill 同步」都各自有對應的 [S] 或「要動什麼」表項,沒有條款漏掉設計、也沒有設計漏掉條款(唯一弱連結是 S9 因 finding 3 而在「相同判定」定義上不完整,已列為 major)。

### 回退節
已讀,無 finding(sha 待填有 REVISIT:2026-10-17 盯,非閘擋條件)。

### 誠實界線
已讀,無 finding(自陳「這條文法很鬆」「零條驗使用者行為」都是坦白揭露,不是隱藏)。

### 交叉引用核對(④)

`逃逸自動記_計劃` 的「九支測試綠」核對為真(`t_escape_auto_from_prepush/from_ci/scope_rules/ci_only_test_step/unreviewed_twoway/code_finding_severity/lock/dedup/from_code_loop` 共 9 支,`scripts/test_lumos.py:31273-31498`),S1–S9 條款編號與該計劃九條一一對應。`雙向門放行_計劃` status 確認為 `todo`、内容確為「原封搬入待命」,與本篇摘要「待命」的描述一致。已讀,無 finding。

### 固定席節點判斷:`Systems/design-loop` ★INVARIANT★(處置閘第五步)

**finding 7**
severity: minor
這份設計會改寫該節點的 ★INVARIANT★ 正文(新增句式檢查與回退節門檻),屬於「宣稱行為被直接推翻」而非破壞——但推翻方式合乎該節點自己的慣例(改合約行要綁測試+審計,S9 已標明),與節點過去多次修改 ★INVARIANT★ 的先例(如「每支檔有家_計劃」S21 加落點步)同形狀,不是繞過。
引句:「處置閘第五步(2026-09-08,[[Projects/條款綁測試算進度_計劃]] d3/d4):設計審迴圈」
blocking: 否——判準:節點自身容許並要求合約行隨新計劃修訂,只要新文字完整(finding 3 已點出目前不完整)、綁對測試,就不算破壞既有治理紀律。

## 總結

最嚴重 severity:blocker(finding 1);blocking 條數:4 條(finding 1、3、4→非,6;重數一次:finding 1 是、finding 3 是、finding 6 是,finding 4 否、finding 2 否、finding 5 否、finding 7 否)——共 3 條 blocking:是。
