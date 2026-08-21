---
type: project
status: doing
created: 2026-08-21
updated: 2026-08-21
tags:
  - type/project
  - status/doing
related:
  - "[[Issues/只退場不痛的機制]]"
  - "[[Issues/寫下風險當成處理風險]]"
  - "[[Issues/自足性審計提醒空轉四十六天]]"
  - "[[Issues/外家席長期缺席仍照跑loop]]"
  - "[[Issues/流程自產工作量未量測]]"
---
# 檢核收緊五件_計劃

> 白話:2026-08-20 開了七張自我批判單([[Issues/只退場不痛的機制]] 等),Enzo 2026-08-21 裁「不只補齊,要自動化檢核」並點破「功能越改越多、檢核越來越寬鬆」。本案把五張能自動化的單子包成一包:**三件硬擋、兩件只給數字**。不再預設「軟提醒、不擋」——那個預設就是寬鬆的來源。

## 緣起與裁定鏈

- 2026-08-20 七張 Issue 立案(全部未處置,只確立事實)。
- 2026-08-21 兩張 P1 收線(外家管道恢復、30 節點 L4 清帳)——清帳 70 條不一致大宗=計數漂移,且抓到多處「紀律寫了、code 零檢查」。
- 2026-08-21 [[Issues/寫下風險當成處理風險]] 立三型判準(A 天花板/B 可機械未做/C 已接受)。
- 2026-08-21 Enzo:「不想只是補齊,我想要優化成自動化檢核」「你打我臉的那些,我要有足夠好的優化方法」「確實功能越改越多,但檢核卻越來越寬鬆」→ 本案。

## 新機制準入三問(Growth test)

1. **真事故?** 有,且本週密集:①check-s 軟提醒響 18,283 次/46 天零人處理,靠做別的事順手 grep 才發現([[Issues/自足性審計提醒空轉四十六天]])②外家席連續數週缺席,三輪九席同門,處置只是文件加一句——而 skill 明寫 tier=high fail-closed、**code 未實作**③probe 三參數/pass --note 效能答案:skill 寫「須」、code 零檢查([[Issues/probe輪三參數只在散文]])④Check N 建成 9 天存量零使用。共同形態=**宣稱有守衛、實際沒有**,這是正確性問題。
2. **風格偏好?** 否——每件都是「文件承諾了工具不做的事」或「提醒存在但無人可能看到」。
3. **既有小修蓋得住?** 五件全是既有指令讀側加段或留痕加欄,**零新子命令**:Check A 抄 Check N 掃描結構;棘輪讀既有治理帳;外家 streak 讀既有 rN-dispatch manifest+既有 `_roster_family`;findings-doc 是 record 既有旗標旁加一個;stale-gates 是 gov --stats 加一欄一旗標。新增資料結構=承認句詞表常數一個、標記語法一種(與 Check N 同款 HTML 註解)。

## PRIOR-ART

① 最小解層級——全部掛在 doctor/lint/loop status/gov 既有骨架上。② 世界解過沒——有:**SRE 告警升級(escalation policy)**=未確認的告警在 N 分鐘後升級到下一層,對應本案棘輪;**告警必須可操作(actionability)**對應承認句必須標型;**SonarQube quality gate 的 new-code 門檻**(只對新碼硬擋、存量寬限)對應 cutoff 制,本 repo lint 已用此慣例(aliases 2026-08-05)。③ 裁定=**borrow-design**(借升級政策/new-code 門檻概念,零依賴自寫)。

## 設計

### S1 Check A:承認句必須標型(**硬**)

- **詞表** `_RISK_ADMIT_LEXICON`(常數,封閉集):`靠自律`/`honor-system`/`無機械守衛`/`零檢查`/`零實作`/`純靠`/`不驗`(後兩者需與「工具」「code」同行才算,避免誤傷「純靠 hashlib」類句)。★詞表是 Check A 自己的 B 型弱點:漏詞=漏抓;記在退場條件★。
- **標記**(同 Check N 的 HTML 註解慣例,同一行):
  - `<!--lumos:risk=A-->` 天花板型,無其他欄。
  - `<!--lumos:risk=B issue=Issues/<stem>-->` 或 `<!--lumos:risk=B downgraded=YYYY-MM-DD-->`;issue 必須 resolve 到存在節點且 `type: issue`;downgraded 必須是合法 `YYYY-MM-DD` 且不晚於今天(pre-flight:原稿未定義 downgraded 的失敗條件)。
  - `<!--lumos:risk=C why=<非空> revisit=<非空>-->`。
- **判定**:命中詞表的行無標記/型別非 A|B|C/B 的 issue 不存在或非 issue/B 的 downgraded 非法或未來日/C 缺欄 → 一條 finding。
- **硬度**:`lumos lint <node>` 對**任何**含命中行的節點硬擋(rc1),不分新舊——因為本案實作時存量全部補標(★數量以詞表實掃為準:pre-flight 實測依詞表 28~51 行不等,「38」是 08-21 手數的近似,不再引用★),之後不存在「存量寬限」問題;**雙入口實作抄 Check J `check_regen_provenance()` 模式**(單一函式,cmd_lint 與 run_doctor 各呼叫一次;★Check N 是 doctor 單入口,不是這部分的範本★);`doctor --ci` 同樣計 issues(硬);純 `doctor` 列出不計 rc(與其他硬檢查一致)。
- **掃描範圍**:`docs/<slug>-knowledge/**/*.md` 的 body(frontmatter 的 summary 行也掃——承認句多在 KEY 行);★圍欄內不掃★(沿用 Check N 2026-08-21 修法)。**不掃 skills/**(另案,見範圍刀)。
- **治理帳**:`--ci` 時寫 `gate: check-a`;`_KNOWN_GATES` 同步加入(漂移測試會逼)。

### S2 軟提醒棘輪:被無視 N 次升級硬擋(**硬**)

- **輸入**:既有 `docs/.governance-log.jsonl`,只看 `hard=false ∧ kind=warned` 的事件。
- **判準**:同一 (gate, node) 在 **≥20 個不同 commit** 出現、且末次出現在最近 7 天內(=仍在被念,非已停止)→ 該 (gate,node) 升級。
- **輸出**:①doctor **最頂端**(vault 行之後、任何 Check 之前)印「★長期未處理 N 項★」逐項列 `gate/node/被念 commit 數/首見日`;②`--ci` 時每項計 1 issue(**硬**);純 doctor 列出不計。
- **為什麼是 20**:check-s 本輪清帳前最高 1,003 次原始/420 commit;20 個 commit 在本 repo 節奏約 2-3 天連續推送,夠確定「不是剛發生」。★拍的,寫進未決★。
- **逃生門**:節點 frontmatter `ratchet_ack: <gate>@<date>`(走 `lumos set`,白名單加一鍵)= 人明示「知道了,暫不處理」,該 (gate,node) 自 date 起 30 天不升級;過期自動恢復。ack 寫治理帳 `gate: ratchet-ack`。
- **基線**:2026-08-21 check-s 已清零,棘輪上線時理論零命中;若非零=立刻有東西該處理,不寬限。

### S3 外家席缺席 fail-closed(**硬,限 code/high**)

- **輸入**:既有 `governance/review-reports/<loop>/rN-dispatch*.json` + 既有 `_roster_family()`。
- **判準(code/high)**:`loop status --panel --gate` 對 **kind=code ∧ tier=high** 的 loop(kind 依 loop id 前綴三值規則,同派工編制案),**最後 K 輪(K=2)內至少一輪有 ≥1 席 family=external**,否則合取 FAIL,訊息引 skill fail-closed 條款。★pre-flight 抓到:`_TIER_ROSTER` 只有 `(code,high)` 標 `required-fail-closed`,`(design,high)` 外家席是 `note-if-absent`——原稿寫「tier=high」會把 design/high 也硬擋,違反自家編制合約,已改限 code/high★。design/high 與 standard 同走下一條(streak 觀測)。這是把 `_TIER_ROSTER` 裡 `required-fail-closed` 從「轉述」變「執行」——★與派工編制資料化 v1「觀測恆 rc0」明確相反,本案即該案預告的「進閘另立案」★。
- **判準(design/high、standard、indeterminate kind)**:不擋;`loop next` 印「外家席連續 N 輪缺席」(跨 loop 累計,讀全部 dispatch 依 ts 排序),N≥3 印★並寫治理帳 `gate: external-absent`。
- **豁免**:人明示 `canary record ... --note` 含 `external-waived:<理由>` 的輪不計入 FAIL(留痕式豁免,非靜默)。
- **無 dispatch 檔的舊 loop**:vacuous 不擋(同 seat-check 慣例)。

### S4 findings 加「文件自身缺陷」欄(**資料,不擋**)

- `canary record` 加 `--findings-doc <N>`(選填,預設不寫欄):該輪存活 findings 中屬「規格文件自身缺陷」(未定義詞/章節矛盾/測試枚舉不齊)的條數。**驗證**:須同時帶 `--findings`,且 0 ≤ doc ≤ findings,否則 rc2(pre-flight:既有 `--findings` 本身無非負驗證,本案順帶補 `--findings < 0` rc2,與同組 `--tokens` 等一致)。
- `loop status` 各模式輸出末尾加一行:「本 loop 累計 findings X,其中文件自身 Y(Z%)」;無欄的舊輪不計入分母、另印「舊輪 N 無此欄」。
- 分類仍是人判;本案只讓比例**可算**。累積 ≥10 案後回看 [[Issues/流程自產工作量未量測]]。

### S5 `gov --stats` 零筆閘天數(**數字,不擋**)

- 表加一欄「距末見天數」(零筆 gate 印 `—`)。
- 加旗標 `--stale-gates N`:只列「距末見 ≥N 天或從未出現」的 gate,段落標題固定為「退場候選(需人判;未出現≠無用,見限制聲明)」。
- 不改既有 `--stats` 其他輸出。

### 範圍刀(明確不做)

- **不掃 skills/ 散文**的承認句(150K 字元,另案;[[Issues/嚴謹度分配偏向機械層]] 維持 Issue)。
- **不自動分型**——A/B/C 由人標,機器只驗完整性。
- **不做 standard 檔外家 fail-closed**(只 high)。
- **不自動退場任何閘**——S5 只列候選。
- **不改 `_TIER_ROSTER` 表內容**,只讓 `required-fail-closed` 語意在 high 檔被執行。
- **單一作者與嚴謹度兩張單子不在本案**(前者改措辭、後者無好自動化,各自留痕)。

## 退場條件(★本案五件自己也是機制,先寫好什麼時候拆★)

| 件 | 退場條件(寫入 gov --stats 可量) |
|---|---|
| S1 Check A | 上線 90 天內 `check-a` 在 `--ci` 零新命中(存量 38 處補標後算起)→ 退場候選;詞表漏抓實例 ≥3 筆且無人補詞表 → 改為只列不擋 |
| S2 棘輪 | 90 天內零升級事件 → 表示軟提醒都有人處理,棘輪退場候選;反之若升級後仍被 ack 掉 ≥50% → 門檻 20 調整或承認某道軟提醒該整個退場 |
| S3 外家 fail-closed | 連續 10 個 high loop 皆有外家 → 維持(它有用);若連續 5 個 high loop 靠 waived 過 → 外家管道根本不穩,問題在管道不在閘,攤人 |
| S4 | 累積 10 案後比例 <10% → 欄位退場(流程自產量不值得追) |
| S5 | 純數字,無退場問題;隨 --stats 走 |

## 測試策略(TDD,先紅後綠;每件至少一紅一綠一邊界)

1. `t_checka_unmarked_fails`:含「靠自律」無標記 → lint rc1、doctor --ci 計 issue。
2. `t_checka_valid_ABC_pass`:三型合法標記各一 → 不報。
3. `t_checka_B_issue_must_exist`:B 指向不存在/非 issue 節點 → 報;`downgraded=日期` → 過。
4. `t_checka_C_fields_required`:缺 why 或 revisit → 報。
5. `t_checka_fence_skipped`:圍欄內的詞不掃。
6. `t_checka_lexicon_context`:「純靠 hashlib」不報;「純靠 code 不驗」報。
7. `t_ratchet_promotes_at_20`:fixture 帳 19 commit 不升、20 升、且末見 8 天前不升(已停止)。
8. `t_ratchet_top_of_output`:升級項印在任何 `[X]` 段之前;`--ci` 計 issue。
9. `t_ratchet_ack_window`:`ratchet_ack` 30 天內不升、第 31 天恢復;ack 寫治理帳。
10. `t_external_failclosed_code_high`:`code-` 前綴 high loop 最後 2 輪皆無 external → gate FAIL 並引條款;有一輪有 → 過;★design/high 同狀況不擋(只印 streak)★;standard 不擋。
11. `t_external_waived_note`:note 含 `external-waived:` 的輪不計 FAIL;無 dispatch 檔 → vacuous 過。
12. `t_external_streak_print`:跨 loop 連續 3 輪無外家 → loop next 印★且寫 `external-absent`。
13. `t_findings_doc_field`:`--findings-doc` > `--findings` 或無 `--findings` 或負值 rc2;★loop status 五模式(legacy/--panel/--light/--settle/--disposal)各一案皆印比例行★;舊輪無欄不入分母。
14. `t_gov_stats_stale_gates`:距末見欄正確;`--stale-gates 30` 只列超過者與從未出現者;標題含「需人判」。
15. `t_known_gates_updated`:`check-a`/`ratchet-ack`/`external-absent` 皆在 `_KNOWN_GATES`(既有漂移測試自動逼);★`doctor --ci` 有 Check A 命中時治理帳確實 append `gate: check-a`(pre-flight:原無此斷言)★。
16. `t_set_whitelist_ratchet_ack`:`lumos set <node> ratchet_ack` 可寫(白名單加鍵)。

## 實務隱患

**通用三問**:併發——S1/S2/S5 純讀;S3 讀 dispatch 檔純讀;S4 record 走既有 append 路徑,與既有 record 同鎖語意;`ratchet_ack` 走 `lumos set` 既有 atomic_write_verify。效能——S2 每次 doctor 多掃一遍治理帳(2 萬行,線性,<1s);S3 每次 loop status 多讀該 loop 的 dispatch 檔(個位數)。資源——全 with-open。

**風險類**:
- **self-governance(命中)**:★本案三件硬擋,誤擋的逃生口各自明列★——S1 標 `risk=A` 即過(最低成本逃生,但留痕);S2 `ratchet_ack` 30 天窗;S3 `external-waived:` note。三個逃生口**全部寫治理帳**,繞過有痕。★反向風險:逃生口太便宜會被濫用(人人標 A)——退場條件裡「詞表漏抓 ≥3」與「ack ≥50%」就是在量這個★。
- **已排除:金流/對外送出/不可逆/PII**——全為本地讀檔與 frontmatter 寫入,`lumos set` 既有可逆。
- **遷移**:`_KNOWN_GATES` 加三值、`SCALAR_KEYS` 加 `ratchet_ack`——兩處皆有漂移測試釘;無帳檔格式變更(S4 是可選新鍵,舊讀者 `.get` 不炸)。

## 審計修正紀錄

- **r1 pre-flight(2026-08-21,機械掃)**:①S3 把 design/high 與 code/high 混為「tier=high」——編制表只有 code/high 是 fail-closed,已限縮 ②「存量 38 處」無法重現(依詞表 28~51),改以實掃為準 ③`downgraded=` 無失敗條件,補日期格式+不得未來 ④`--findings-doc` 在無 `--findings` 時未定義,補驗證並順帶補既有 `--findings` 非負 ⑤雙入口範本引錯(Check N 是 doctor 單入口,應抄 Check J)⑥`check-a` 落帳無測試、S4 各模式無逐模式測試,已補。

## 未決

- S2 門檻 20 與 ack 窗 30 天是拍的;上線後以 gov --stats 的 ratchet 事件數回看。
- S1 詞表初版 7 詞,一定漏;漏抓不是失敗,是退場條件裡的量測項。
- 存量 38 處補標由實作者(本 session)分型——這是判準的第一次大規模套用,**分型結果本身要進 Verification 供人抽查**。
