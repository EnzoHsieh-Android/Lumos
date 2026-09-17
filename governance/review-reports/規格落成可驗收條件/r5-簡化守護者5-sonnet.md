severity: blocker

# 外部審稿意見——《規格落成可驗收條件_計劃》第 5 版(拆後半套)

## 固定席節點判定(機器附加:Systems/design-loop INVARIANT)

會影響。第四節明寫要把處置閘第五步改呼叫 `_clause_check(plan, door="one-way")`,直接重寫該節點列為 ★INVARIANT★ 的合約行本體(而不是外圍加一層)。判斷理由見下方 finding 1。

---

### finding 1
- 節:設計(半套)§四、處置閘第五步共用檢查器
- 問題:本案直接改寫 `Systems/design-loop` 列為 ★INVARIANT★ 的處置閘第五步合約行,不是新增旁支;作者自己在「要動什麼」與「實務隱患」都已列此風險並配了代碼審+錨點核可,屬已揭露、有配套的變更,不構成新風險。
- 引句:「處置閘第五步改成呼叫同一支 `_clause_check(plan, door="one-way")`(單一來源——這是改 [[Systems/design-loop]] 的不可變合約行,要綁測試加審計)」
- file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:29`(KEY:★INVARIANT★ 段落,現行合約行文字)
- blocking: 否(判準:已揭露 + 已配代碼審/錨點核可流程,不是遺漏)
severity: minor

### finding 2
- 節:PRIOR-ART、設計(半套)§三
- 問題:本案要新開 `cmd_spec_gate`+`_clause_check`,但同一支 `scripts/lumos` 裡已有 `cmd_bound_tests`/`_bound_tests_check`/`_run_bound_tests`/`_RAN_EVIDENCE`/`_ran_evidence_check`,已經對「真跑一次、紅/綠/弱證據(unproven)、no-cmd、逾時、{method} 缺失時的整套跑判定」做了幾乎相同的事,而且已掛在推送閘上;PRIOR-ART 只提到沿用 `_clause_bindings_for` 與泛用 `run_cmd`,沒有把這支既有的「真跑印紅綠」機器列進來比對過,是否有更小形狀(擴充 `cmd_bound_tests` 認一種新的 binding 來源,而非整支新指令+新檢查器+新 Systems 節點+五處 skill 同步)沒有被排除。
- 引句:「借用不自建:條款存在性沿用 `_clause_bindings_for`(處置閘第五步那支)、測試執行沿用 `.lumos/config.json` 的 `run_cmd`;**支數解析是新寫的**」
- file: `scripts/lumos:25810`(`_run_bound_tests`,已含 green/red/unproven 判定與整套跑處理)、`scripts/lumos:25696`(`_RAN_EVIDENCE`,已含 pytest/jest/xunit/xctest 四棧「跑過證據」正則)
- blocking: 是(判準:同一支檔案裡已有解同一問題九成的機器,PRIOR-ART 沒有把它列入排除理由就直接開新指令,不符合「先問世界」的最小解原則,而這正是 CLAUDE.md 鐵則要求先查的)
severity: major

### finding 3
- 節:設計(半套)§三 3.「不留痕、不寫審查帳」與(背景)Projects/逃逸自動記_計劃
- 問題:已落地的逃逸自動記靠 `_door_for_loop` 讀 `.canary-log.jsonl` 裡 `kind: spec-gate` 帶 `door` 欄位的帳,判斷推送閘該記 `push-gate-unreviewed` 或不記;本篇半套明文規格閘不寫帳,代表 `kind: spec-gate` 永遠不會被寫入,`_door_for_loop` 會永遠回 `unknown`——已上線的逃逸判斷有一支分支被這個決定悄悄致殘,全篇(含實務隱患、誠實界線)沒有一處承認或排代辦。
- 引句:「不留痕、不寫審查帳(半套沒有放行這件事)。」
- file: `scripts/lumos:7504-7518`(`_door_for_loop` 讀 `kind: spec-gate` + `door` 欄)、`docs/lumos-toolchain-knowledge/Projects/逃逸自動記_計劃.md:41`(推送閘規則明寫依賴「該計劃有 `kind: spec-gate` 雙向門留痕」)
- blocking: 是(判準:已上線功能的一個分支因這個決定變成永遠打不中,且未在文件任何一處揭露或排代辦,屬於遺漏而非取捨)
severity: blocker

### finding 4
- 節:設計(半套)§一、條款句式
- 問題:「機械只驗這條」的正式產生式(觸發子句定義)只列了中文四個觸發詞(當/在/若啟用/若),散文另外宣稱英文 When/While/Where/If…then/shall 同等,但那句承諾沒有反映進正式文法;若照文件所寫「機械只驗這條」實作,英文觸發的條款會落進「句首不是 當/在/若」而被誤判無條件型或直接格式看不懂——這正是 r1「S4/S12 過不了自己的句式」同一族的縫,第 5 版又長出一個新的。
- 引句:「「在」型不再要求「期間」二字(狀態可以是「在雙向門的計劃裡」「在閘上線前」);英文關鍵字 When/While/Where/If…then/shall 同等。」
- file: 對照該節上方的正式產生式(觸發子句 = ("當" | "在" | "若啟用" | "若") …),spec 第 128-133 行,不含英文詞
- blocking: 是(判準:S1 的驗收條款寫「不合那條文法…應判為格式看不懂」,若英文詞未進正式產生式,S1 自身測試 `t_spec_gate_ears_shapes` 若涵蓋英文範例就會直接證偽這句承諾)
severity: major

### finding 5
- 節:RETIRE-IF ②、實務隱患
- 問題:RETIRE-IF ②「規格閘印出來的『紅』在後續實作裡從沒變綠」需要跨時間追蹤同一條款的判定序列才量得到,但 finding 3 已證半套明文不留痕、不寫帳——沒有任何持久化資料源可以回答「這條紅有沒有變過綠」,這條退場條件在本篇設計下量不到,屬裝飾性承諾。
- 引句:「半套上線 90 天內,規格閘印出來的「紅」在後續實作裡從沒變綠(=沒人理它)→「跑」那一步收掉,只留句式與綁定」
- file: 對照 §三第 156 行「不留痕、不寫審查帳」
- blocking: 是(判準:量不到的 RETIRE-IF 等於沒有回頭條件,違反 CLAUDE.md 鐵則四「寫不出回頭條件就是該處理不該承認」)
severity: major

### finding 6
- 節:誠實界線、為什麼(數字表)
- 問題:「為什麼」那張表原本論證的是「該不該少審」,半套已明文不減少任何審查,作者自己在誠實界線已承認這張表現在只剩 RETIRE-IF ①② 能用它,但正文標題與段落順序仍維持原樣、沒有把表挪到雙向門放行_計劃或加一句「本篇不再靠此表論證少審」,讀者容易誤以為這張表仍在支撐本篇主張。
- 引句:「半套不減少任何審查——它只是把「條款有沒有接到測試」變成可見的數字。「少審一點」的價值要等第二階段;在那之前本案的價值只有 RETIRE-IF ①② 能量。」
- blocking: 否(判準:已在誠實界線段落口頭承認,只是表格位置未隨之搬動,屬文件組織問題不影響機械判定)
severity: minor

---

## Panel 立場逐項回答

① **11 條裡守原題/守機制/守機制的機制各幾條**(逐條列,⚠ 判準見下):
- 守原題(直接驗「條款能不能真的跑出紅綠」):S1、S6、S8 → 3 條
- 守機制(防止上述機制被誤用/繞過/誤判):S2、S3、S4、S5、S7、S9、S10 → 7 條
- 守機制的機制(對機制本身的度量層):S11 → 1 條
⚠ S9(處置閘與規格閘同源判定)介於「守原題」與「守機制」之間,因為它保證的是「同一份計劃兩處問到答案一致」而非「條款本身可驗」,判為守機制。

② 半套跟既有 `lumos spec-trace` 的差,如果只差「真的跑一次印紅綠」——finding 2 已證,repo 裡已經有一支更完整的「真跑印紅綠+弱證據」機器(`cmd_bound_tests`/`_run_bound_tests`/`_RAN_EVIDENCE`),只是綁定來源是 pin(檔案級合約)不是 [SN](計劃條款級)。更小的形狀存在:給 `cmd_bound_tests` 加一種 items 來源(從 `_clause_bindings_for` 取 [SN] 綁定),或給 `spec-trace` 加 `--run` 旗標直接呼叫既有 `_run_bound_tests`,不必新開 `cmd_spec_gate`+`_clause_check`+新 Systems 節點+五處 skill 同步。這條在 finding 2 判 major/blocking。

③ RETIRE-IF 三條各自量得到嗎:①(有條款計劃比例)量得到,靠 S11 doctor 段;②(紅有沒有變綠)量不到,見 finding 5——是裝飾;③(跑過 30 份計劃且逃逸自動記對回率過關)本身量得到,但「對回率」這個分母依賴 finding 3 指出的 `_door_for_loop`/`push-gate-unreviewed` 分支,那條分支已被本案的「不留痕」決定打殘,所以③的「過關」判準本身立在一段永遠讀不到真值的資料上。

④ 停用詞表、支數解析收進逐棧表、`_SPEC_GATE_SINCE`——半套還需要嗎:三者都需要,而且都經核對是真新增(finding 2 已排除的是「支數解析」本身的必要性被誇大,但「停用詞表」與 `_SPEC_GATE_SINCE` 目前 repo 裡確實不存在,不是重複造輪)。`_ran_evidence_check` 只有布林「有沒有跑過」,沒有計數,S6/S7/S8 需要的 N==0/1/≥2 三分類要新寫,這點作者的 r3 訂正是對的。

⑤ 「為什麼」那張表原本替「少審」立論,半套不少審,這張表跟本篇還有沒有關係:見 finding 6,關係已弱化到只剩 RETIRE-IF ①②,作者自己承認了,但表格沒有隨之搬到雙向門放行_計劃或改標題,是文件組織遺留,非機械缺陷。

⑥ 本篇自己是散文收斂樣本,第 5 版有沒有再長出新的「守機制的機制」:有,S11(doctor 印條款比例與紅綠弱證據數)本質是對 S1–S10 的觀測層,不驗任何使用者行為,屬於典型「守機制的機制」;但它跟前四輪被折掉的那些不同——它是餵 RETIRE-IF ①②③ 的必要基礎設施而非新增擋門檻,而且作者自己已在誠實界線第三點承認「11 條全部在驗機制自己、零條驗使用者行為」,已經把這件事講清楚,不算隱藏。

## 其餘各節

- 「兩層要分開」節:已讀,無 finding。
- 「要動什麼」表格:已讀,無 finding(與正文一致)。
- 「回退」節:已讀,回退 sha 待填屬已知未完成項,REVISIT:2026-10-17 已盯,無新 finding。
- 「審計修正紀錄」:已讀,無 finding(與卷證目錄結構一致,未逐篇核對 r1–r4 報告內容,超出本輪範圍)。
- decisions 區塊(d1–d13):已讀,superseded 鏈完整、valid 欄一致,無 finding。

---

最嚴重 severity:blocker;blocking 幾條:4(finding 2、3、4、5)。
