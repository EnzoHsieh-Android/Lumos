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

> 白話:2026-08-20 開了七張自我批判單([[Issues/只退場不痛的機制]] 等),Enzo 2026-08-21 裁「不只補齊,要自動化檢核」並點破「功能越改越多、檢核越來越寬鬆」。本案 v1 包五件(三硬兩數),★r1 六席 10 blocker/24 major,核心裁定=兩件軟的沒有自己的事故、搭便車,且與「收緊」背道而馳 → **v2 砍成三件,全部硬擋**★。不再預設「軟提醒、不擋」——那個預設就是寬鬆的來源。(節點名沿用「五件」不改,免斷連結;實際範圍三件。)

## 緣起與裁定鏈

- 2026-08-20 七張 Issue 立案(全部未處置,只確立事實)。
- 2026-08-21 兩張 P1 收線(外家管道恢復、30 節點 L4 清帳)——清帳 70 條不一致大宗=計數漂移,且抓到多處「紀律寫了、code 零檢查」。
- 2026-08-21 [[Issues/寫下風險當成處理風險]] 立三型判準(A 天花板/B 可機械未做/C 已接受)。
- 2026-08-21 Enzo:「不想只是補齊,我想要優化成自動化檢核」「你打我臉的那些,我要有足夠好的優化方法」「確實功能越改越多,但檢核卻越來越寬鬆」→ 本案。

## 新機制準入三問(Growth test)——★逐件答,不搭便車★

| 件 | 1 真事故 | 2 風格? | 3 既有小修? |
|---|---|---|---|
| S1 承認句檢核 | 2026-08-21 L4 清帳抓到「pass --note 須含效能答案」「probe 三參數」兩處 skill 寫「須」而 code 零檢查,編排者照 skill 排程會在 cap 撞牆才發現([[Issues/probe輪三參數只在散文]]);全庫 28~51 句承認句零分類。★這是「宣稱有守衛、實際沒有」的正確性問題★ | 否 | 抄 Check J 雙入口結構;新增=一個詞表常數+一種標記 |
| S2 軟提醒棘輪 | check-s 響 18,283 次/46 天零人處理,靠做別的事順手 grep 才發現;check-e1 現仍有 5 組 (gate,node) 超 20 次在被念([[Issues/自足性審計提醒空轉四十六天]]) | 否 | 讀既有治理帳;新增=doctor 一段+ack 一個 list 鍵 |
| S3 外家 fail-closed | skill 明寫 code/high fail-closed、`_TIER_ROSTER` 標 required-fail-closed、★code 只「轉述,不阻斷」★;外家缺席數週三輪九席同門照收斂([[Issues/外家席長期缺席仍照跑loop]]) | 否 | `code-loop pass` 加一個前置判定;新增=一個旗標 |

**砍掉的 S4(findings-doc 欄)/S5(stale-gates)**:無獨立事故、且「不擋」——退回 [[Issues/流程自產工作量未量測]]/[[Issues/只退場不痛的機制]] 當選項,不在本案。

## PRIOR-ART

① 最小解層級——三件全掛既有骨架(doctor/lint 雙入口、run_doctor 頂端、code-loop pass 前置)。② 世界解——SRE escalation policy(未確認告警升級)對應 S2;actionability 對應 S1;**branch protection required status check**(合併前必須有某個檢查綠燈,不是信任申報)對應 S3 把閘綁在真正的放行點。③ 裁定=borrow-design。

## 設計

### S1 Check A:承認句必須標型(**硬**)

**詞表** `_RISK_ADMIT_LEXICON`(封閉常數):`靠自律`/`honor-system`/`無機械守衛`/`零檢查`/`零實作`;`純靠`/`不驗` 僅在同行出現 `工具|code|程式|機制` 時算。
**否定前綴豁免**(r1 s3-F1):命中詞前 6 字內含 `非|不是|而非|不再|不靠|取代|≠|~~` 任一 → 不算承認(「靠 schema 而非靠自律」不擋)。
**區段豁免**(r1 s3-F3):標題為 `審計修正紀錄|審計紀錄|歷史|變更紀錄` 的 section 內不掃(敘述過去式承認);圍欄內不掃(沿用 Check N)。
**掃描範圍**(r1 s1-F3):整檔文字=frontmatter `summary` 區塊 + body(★兩者都掃,不是「body 為主 summary 也掃」的含糊講法★),扣掉上述豁免。
**標記**(同一行):
- `<!--lumos:risk=A-->` 天花板型;★帶任何其他欄=違規★(r1 s1-F5)。
- `<!--lumos:risk=B issue=Issues/<stem>-->`(resolve 到存在且 `type: issue`)或 `<!--lumos:risk=B downgraded=YYYY-MM-DD-->`(合法日期、不晚於今日)。
- `<!--lumos:risk=C why=<非空> revisit=<非空>-->`。
**判定**:命中行無標/型別外/A 帶欄/B 兩欄皆無或皆有/B issue 不存在或非 issue/B 日期非法/C 缺欄 → finding。
**硬度**:`lumos lint` rc1;`doctor --ci` 計 issues;純 doctor 列不計。雙入口抄 `check_regen_provenance()`。
**治理帳**:`--ci` 命中寫 `gate: check-a, kind: blocked, hard: true, nodes:[rel]`。
**存量**:實作時以詞表實掃,逐條分型補標(數量以實掃為準);★分型表進 Verification 供抽查★。[[Issues/寫下風險當成處理風險]] 內列舉句式的那段改放圍欄(r1 s3-F2)。

### S2 軟提醒棘輪(**硬**)

**輸入**:`docs/.governance-log.jsonl` 中 `hard=false ∧ kind=warned` 的事件。★只涵蓋會寫帳的 gate(現 7 道);不寫帳的軟提醒不在棘輪內,明講(r1 s2-F3)★。
**執行單位=「一次 --ci run」**:同 commit 的所有事件視為一次 run;run 依首筆 ts 排序。
**判準**(r1 s3-F6/F7,s6-2):鍵=(gate, **節點相對路徑**,非 stem;r1 s2-F2)。取最近 **N=20 次 run**;該鍵在**這 20 次每一次都出現**(連續,無間斷)→ 升級。★「20 次 run」是執行次數不是日曆,高低頻團隊語意一致★;★今天剛清零的鍵在最新 run 不出現 → 不升,v1「末見 7 天內」判準已撤(r1 編排者自核:會把剛清的 30 節點全升)★。
**輸出**:doctor **最頂端**印「★長期未處理 N 項★」逐項 `gate/路徑/連續 run 數/首見日`;`--ci` 每項計 1 issue。
**升級落帳**(r1 s4-F2):`--ci` 時每項寫 `gate: ratchet, kind: promoted, hard: true, nodes:[rel], detail: <source gate>`。
**逃生門**:frontmatter list 鍵 `ratchet_acks`(走 `lumos append`,LIST_KEYS 加鍵;r1 s1-F2/s2-F1/s4-F1),元素 `<gate>@<YYYY-MM-DD>`;自該日 30 天內該鍵不升級,過期恢復;append 時寫 `gate: ratchet-ack, kind: acked`。★自簽是天花板(本機 CLI 無身份),處置=ack 必落帳、`gov --stats` 可見 ack 數,人查;標 risk=A★(r1 s3-F8)。
**上線基線**(r1 s3-F5):實作當下實算最新 20 run——目前 check-e1 有 5 組會立刻升級(guard-kill + 4 個 slim 節點的死背書)。★這不是誤擋,是棘輪第一批該處理的東西★;上線 PR 必須先把這 5 組解掉或 ack,不得帶著紅上線。

### S3 外家 fail-closed 綁在放行點(**硬,限 code/high**)

**放行點**(r1 s4-F3 blocker):真正擋 push 的是 `code-loop pass/skip` 留痕,不是 `loop status`。故判定掛在 **`code-loop pass`**:
- `pass` 新增 `--loop <id>`;tier=high 時(pass 內自跑 `pitfalls --diff <range>` 判 tier,range 取 merge-base..HEAD,同 pre-push)**必帶** `--loop` 或 `--no-loop "<理由>"`;兩者皆無 → rc2 不寫留痕。
- 帶 `--loop`:讀該 loop 的 `rN-dispatch*.json`(★無 ts 欄,r1 s2-F5——輪序取 `canary-log` 同 loop 各 round 首筆 ts 排序★),取最後 **min(K=2, 輪數)** 輪(r1 s6-1 冷啟動);其中至少一輪的 external 席數 ≥ `_TIER_ROSTER[("code","high")]` 中 `required-fail-closed` 席數(=2:finder+否決;r1 s1-F1)→ 過;否則 rc1 印「外家 fail-closed 未滿足」不寫留痕。
- `--no-loop "<理由>"`/`--waive-external "<理由>"`:明確旗標(★不是 note 子字串,r1 s3-F9★),寫留痕 `status: passed, waiver: {...}` 並寫 `gate: external-waived, kind: waived, detail: 理由`。★這與 skip 一樣是逃生門,差別是留痕語意(passed-with-waiver vs skipped)★。
- kind 不需推斷(code-loop pass 定義上就是 code loop;r1 s2-F7 的前綴推斷風險消失)。
- 無 dispatch 檔 → rc1(★不 vacuous:code/high 沒派工快照=沒證據,fail-closed 的本意★;與 seat-check 觀測語意不同,明講)。
**standard 檔**:`loop next` 印「外家連續 N 輪缺席」(跨 loop,依 canary-log ts),N≥3 印★並寫 `gate: external-absent, nodes:[<loop-id>]`(★nodes 語意=loop id,登記進 `_STATS_NODE_SEMANTICS`,r1 s4-F4★)。不擋。
**pre-push 不改**:仍只讀 passed/skipped。

### 範圍刀(明確不做)

- 不掃 skills/ 散文;不自動分型;不做 design/high 與 standard 的外家硬擋;不改 `_TIER_ROSTER` 內容;不改 pre-push;不改 loop status 判定式(S3 完全在 code-loop pass 內)。
- S4/S5 不做(退回各自 Issue)。
- 棘輪不涵蓋不寫帳的軟提醒(另案若要,先讓它們寫帳)。

## 退場條件(★每條指名「哪個指令印哪個數」★,r1 s5 全席)

| 件 | 量測來源(指令) | 條件 |
|---|---|---|
| S1 | `gov --stats --since 90` 的 `check-a` 筆數 | 連續 90 天零筆 → 退場候選。★漏抓無法自動量測(負事件)★:改為**每 90 天人工盤點一次**寫 Verification(`plan_refs` 回指本節點);盤點發現漏抓 ≥3 → 補詞表或改只列 |
| S2 | `gov --stats --since 90` 的 `ratchet`(升級)與 `ratchet-ack` 筆數 | 90 天零升級 → 退場候選;ack/升級 ≥50% → 門檻 20 重議 |
| S3 | `gov --stats --since 90` 的 `external-waived` 筆數 vs `code-loop`(passed)筆數 | waived/passed ≥50% → 管道不穩,問題在管道,攤人;連續 90 天零 waived 且有 passed → 維持 |

三件的分子分母**全部是已寫帳或本案新寫帳的 gate**,`gov --stats` 現有欄位即可印(★v1「寫入 gov --stats 可量」對五件不成立,v2 對三件逐條成立★)。

## 測試策略(TDD,先紅後綠)

1. `t_checka_unmarked_fails` / 2. `t_checka_valid_ABC_pass` / 3. `t_checka_B_rules`(issue 不存在/非 issue/兩欄皆有/皆無/日期非法/未來日) / 4. `t_checka_C_fields` / 5. `t_checka_A_extra_field_fails` / 6. `t_checka_negation_prefix_exempt`(「而非靠自律」不報;「靠自律」報) / 7. `t_checka_section_exempt`(審計修正紀錄段內不報,段外報) / 8. `t_checka_fence_skipped` / 9. `t_checka_summary_scanned`(KEY 行命中報) / 10. `t_checka_lint_and_ci_dual_entry`(lint rc1、doctor --ci 計 issue、純 doctor rc0 但列出) / 11. `t_checka_gov_event`(--ci 寫 check-a)。
12. `t_ratchet_20_consecutive_runs`(19 連續不升;20 升;20 次中斷一次不升;最新 run 不出現不升) / 13. `t_ratchet_key_is_relpath`(同 stem 不同資料夾不互撞) / 14. `t_ratchet_top_and_ci`(印在首個 `[` 段前;--ci 計 issue;寫 `ratchet` 事件) / 15. `t_ratchet_acks_list`(append 可寫;30 天內不升;第 31 天升;寫 `ratchet-ack`;同節點兩閘各自 ack 互不覆蓋)。
16. `t_codeloop_pass_high_requires_loop`(tier=high 無 --loop 無 --no-loop → rc2 無留痕) / 17. `t_codeloop_pass_external_window`(min(K,輪數):1 輪有 2 external 過;2 輪末輪 1 external 前輪 2 過;兩輪皆 <2 → rc1 無留痕) / 18. `t_codeloop_pass_no_dispatch_fails`(無 dispatch → rc1) / 19. `t_codeloop_pass_waiver`(`--waive-external` 寫 passed+waiver+`external-waived` 事件;note 含 `external-waived:` 字樣**不**豁免) / 20. `t_codeloop_pass_standard_untouched`(tier=standard 不帶 --loop 照舊 pass) / 21. `t_loop_next_external_streak`(跨 loop 3 輪無外家印★寫 `external-absent`,nodes=loop id) / 22. `t_known_gates_and_semantics`(`check-a`/`ratchet`/`ratchet-ack`/`external-waived`/`external-absent` 在 `_KNOWN_GATES`;`external-absent` 在 `_STATS_NODE_SEMANTICS`) / 23. `t_list_keys_ratchet_acks`。

## 實務隱患

**通用三問**:併發——S1/S2 純讀;S2 ack 與 S3 留痕走既有 atomic/append 路徑。效能——S2 每次 doctor 多掃治理帳一遍(2 萬行線性);S3 pass 多跑一次 pitfalls --diff(pre-push 本就跑)。資源——全 with-open。
**self-governance(命中)**:三件硬擋,逃生口=S1 標 A、S2 ack、S3 `--no-loop/--waive-external`,★三個全部落治理帳、`gov --stats` 可數、退場條件直接拿這些數當分子★——逃生口濫用不是沒對策,是對策就是「被數」(r1 s3-F10 的回應:合規成本 vs 逃生成本結構確實存在,本案不假裝消滅它,而是讓逃生可見可量)。自簽=天花板(risk=A)。
**已排除**:金流/對外送出/PII——本地讀檔與 frontmatter/JSON 留痕。**不可逆**:無(留痕 append、frontmatter 走可逆寫入)。**遷移**:`_KNOWN_GATES` +5、`LIST_KEYS` +1、`_STATS_NODE_SEMANTICS` +1,皆有漂移測試釘;code-loop 留痕 JSON 新增選填 `waiver` 鍵,舊讀者 `.get` 不炸。

## 未決

- S2 N=20 run 仍是拍的;上線後以 `ratchet`/`ratchet-ack` 筆數回看。
- S3 要求 2 席 external(照編制表);若外家管道只剩一家(現況 gemini 一家),★兩席同家族算不算兩席★——編制表目前只分 claude/external 兩族,本案照表算(同族兩席=2);是否該區分外家之間的家族,另案。

## 審計修正紀錄

- **r1 panel(2026-08-21,五席同門+★外家否決席 gemini-3-flash 首次到位★)**:blocker 10 / major 24 / minor 5。★裁定=不補丁,重寫 v2:砍 S4/S5(無獨立事故、不擋、搭便車——s5-F7/F8)、三件全硬★。blocker 逐條:s2-F1/s1-F2/s4-F1 ack 純量撞閘→改 list 鍵;s2-F4 tier 不在 loop status→S3 改掛 code-loop pass(自跑 pitfalls 判 tier);s3-F1 否定句誤判→前綴豁免;s3-F2 Issue 節點自撞→例句入圍欄;s3-F5 棘輪基線→判準改「最近 20 run 連續」且上線先清 check-e1 5 組;s3-F8 自簽→標天花板+落帳可數;s3-F9 waived 子字串→明確旗標;s4-F3 閘可繞→綁放行點;s5-F1 漏抓不可量→改人工盤點 Verification;s6-1 冷啟動→min(K,輪數)。major 全數折入(路徑鍵/連續 run/升級落帳/dispatch 無 ts/席數照編制/nodes 語意登記/範圍句自相矛盾/A 帶欄違規/退場條件逐條指名指令/Growth test 逐件)。**收貨**:六席引句全數錨定(外家席報告做了一次純格式正規化:粗體標籤→裸標籤,內容未動);refcheck 全 ok。**辯方路由**:blocker 皆經編排者以 file:line/實跑資料自核(含實算治理帳證實 s3-F5),路由 i。

- **r1 pre-flight(2026-08-21,機械掃)**:①S3 把 design/high 與 code/high 混為「tier=high」——編制表只有 code/high 是 fail-closed,已限縮 ②「存量 38 處」無法重現(依詞表 28~51),改以實掃為準 ③`downgraded=` 無失敗條件,補日期格式+不得未來 ④`--findings-doc` 在無 `--findings` 時未定義,補驗證並順帶補既有 `--findings` 非負 ⑤雙入口範本引錯(Check N 是 doctor 單入口,應抄 Check J)⑥`check-a` 落帳無測試、S4 各模式無逐模式測試,已補。

## 未決

- S2 門檻 20 與 ack 窗 30 天是拍的;上線後以 gov --stats 的 ratchet 事件數回看。
- S1 詞表初版 7 詞,一定漏;漏抓不是失敗,是退場條件裡的量測項。
- 存量 38 處補標由實作者(本 session)分型——這是判準的第一次大規模套用,**分型結果本身要進 Verification 供人抽查**。
