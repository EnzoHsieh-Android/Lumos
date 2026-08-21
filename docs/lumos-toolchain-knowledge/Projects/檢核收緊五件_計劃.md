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

## 設計(v3,2026-08-21;r2 六席後重寫)

### S1 Check A:承認句必須標型(**硬**)

**詞表**(封閉常數,★下列定義放圍欄,否則本節點自撞★):
```
_RISK_ADMIT_LEXICON = 靠自律 | honor-system | 無機械守衛 | 零檢查 | 零實作
_RISK_ADMIT_CTX     = 純靠 | 不驗        ← 同行另含 工具|code|程式|機制 才算
_RISK_NEG_PREFIX    = 非 | 不是 | 而非 | 不再 | 不靠 | 取代 | ≠ | ~~   ← 命中詞前 6 字內出現即不算
```
**掃描範圍**:整檔文字(frontmatter 全部——含 summary/decisions[].content/why_chosen——加 body),先經 `_strip_fences_text`(★全檔唯一合法 fence 判定;r2 s4-F3:禁用 ```.*?``` 型正則★),再逐行比對。★不做區段標題豁免★(frontmatter 無標題,r2 s4-F4)——歷史敘述改用 H 型標記。
**標記**(同一行;★值一律雙引號,允許任意中文與空白,r2 s4-F5★):
- `<!--lumos:risk=A-->` 天花板型;帶任何欄=違規。
- `<!--lumos:risk=H-->` 歷史/引用型:敘述過去式承認、引用他處句子、定義詞表——非現行承認;帶欄=違規。
- `<!--lumos:risk=B issue="Issues/<stem>"-->`(以 `Issues/` 開頭、stem 經 `by_stem` 解析到存在節點且 `type: issue`;★不接受裸 stem,r2 s4-F6★)或 `<!--lumos:risk=B downgraded="YYYY-MM-DD"-->`(合法日期、不晚於**執行機器本地日期**;時區差屬天花板,H 標)。
- `<!--lumos:risk=C why="…" revisit="…"-->` 兩欄非空。
**判定**:命中行無標/型別外/A、H 帶欄/B 兩欄皆無或皆有/B issue 不合法/B 日期非法或未來/C 缺欄 → finding(訊息含 rel:line 與命中詞)。
**雙入口**:新函式 `check_risk_admissions(notes) -> list[finding]`(★不沿用 `check_regen_provenance` 簽名,r2 s4-F8★),`cmd_lint` 與 `run_doctor` 各呼叫;lint rc1、`--ci` 計 issues、純 doctor 列不計。
**治理帳**:`--ci` 命中寫 `{"gate": "check-a", "kind": "blocked", "hard": true, "nodes": [stem]}`(★nodes 存 stem,與全帳一致★)。
**存量**:實作時以上述規則實掃(r2 s4 席拋棄式腳本實測 61 行命中),逐條分型補標,分型表進 Verification;[[Issues/寫下風險當成處理風險]] 的句式列舉段與本節點詞表段**放圍欄**(r2 s4-F1/F9——r1 宣稱已做其實沒做,本次列為實作第一步)。★本節點退場條件那句「人工盤點」自己也是承認句,見下方已標★。

### S2 軟提醒棘輪(**硬**)

**輸入**:治理帳 `hard=false ∧ kind=warned` 事件;★只涵蓋寫帳的 7 道 gate,明講★。
**run 定義**(r2 s3-F2):一個 commit 內**至少含一筆 `gate` 以 `check-` 開頭的事件**才算一次 doctor run;anchor-approve/code-loop 單獨的 commit 不算 run。run 依**帳本 append 序**(★不 ts 排序,r2 s1-F3/s2-F3:既有慣例且 ts 只到秒★)。
**鍵**:(gate, stem)——★帳本 `nodes` 本就存 stem,路徑鍵不可實作(r2 s1-F2/s3-F1)★;同名 basename 碰撞由既有 doctor Check G 守,棘輪不重做。
**判準**:該鍵在最近 20 次 run **每一次**都出現 → 升級;最新 run 不出現 → 不升(剛清的不升)。
**輸出**:doctor 最頂端(vault 行後、首個 `[` 段前)印「★長期未處理 N 項★」;`--ci` 每項 1 issue;寫 `{"gate": "ratchet", "kind": "promoted", "hard": true, "nodes": [stem], "detail": "<source gate>"}`。
**逃生門**:LIST 鍵 `ratchet_acks`(`lumos append`),元素 `"<gate>@<YYYY-MM-DD>"`(本地日期);30 天內不升;append 時寫 `{"gate": "ratchet-ack", "kind": "acked", "hard": false, "nodes": [stem]}`。自簽=天花板 `<!--lumos:risk=A-->`。★ack 過期不自動清,`doctor` 在該鍵再升級時印「曾 ack 於 <date>,已過期」(r2 外家 #6 的雜訊顧慮:不清但可見)★。
**上線基線**:實作時以本定義重算最近 20 run;命中者在同一 PR 內解掉或 ack,不得帶紅上線(r2 s3-F2:v2 的「5 組」是舊定義,以重算為準)。

### S3 外家 fail-closed 綁在 push 檢查點(**硬,限 code/high**)

**原則**(r2 s2-F1/F2、s5-F1、外家 #1):閘必須在 **pre-push 實際執行的 `code-loop check`** 裁決,`pass` 只負責把證據寫進留痕;`check` 重算並比對,比不上就擋。loop id 不能重用:留痕綁 range 與 HEAD。
- **`code-loop pass --loop <id>`**:①算 range=`_codeloop_range()`(新共用函式:有 upstream → `@{u}..HEAD`;無 → `merge-base(預設分支)..HEAD`)②跑 `pitfalls --diff <range>` 得 tier ③tier=high 時 `--loop` 必帶,否則 rc2 不寫留痕 ④讀該 loop:輪=canary-log 內同 loop 的 round 依 append 序(★dispatch 有檔但尚無 record 的進行中輪不算,r2 s2-F4★);取最後 min(2,輪數) 輪;各輪 external 席數=該輪 `rN-dispatch*.json`(三形狀:dict.auditor/dict.seats[]/list)以 `_roster_family()` 分類為 external 的席數;至少一輪 ≥ `_TIER_ROSTER[("code","high")]` 的 `required-fail-closed` 席數(2)→ 通過 ⑤留痕 `{status: passed, head_sha, loop, range, tier, external_ok: true}`。
- **`code-loop check`**(pre-push 呼叫,range 由 hook 傳入,不改 hook):tier=high 時,有效留痕=`status=passed ∧ head_sha 符 ∧ marker.range == check 的 range ∧ external_ok`;★range 不同源=視同無留痕,印「留痕範圍 X ≠ 推送範圍 Y,重跑 pass」★(r2 s2-F2/s5-F1 的 fail-closed 化)。
- **`--waive-external "<理由>"`**(pass 的明確旗標):跳過④,留痕 `external_ok: false, waiver: 理由`,寫 `{"gate": "external-waived", "kind": "waived", "hard": false, "nodes": [loop-id], "detail": 理由}`;check 接受之。
- **`skip` 在 tier=high 改破窗制**(r2 s2-F1/F6):必帶 `--class false-positive|emergency`,否則 rc2;留痕 `class` 欄;`_codeloop_gov_log` 的 detail 帶 `class=…`。★skip 仍是合法逃生門——但從「免費」變「必須自報類別、被計數」;這就是本案對「更便宜的門」的回應,不是消滅它★。
- **無 dispatch 檔** → pass rc1(fail-closed,不 vacuous)。
- **standard 檔**:`loop next` **只印**「外家連續 N 輪缺席」(依 canary-log append 序跨 loop 算),★不寫帳——`loop next` 是唯讀指針契約(r2 s1-F4)★;v2 的 `external-absent` gate 撤銷。
- **`--no-loop` 撤銷**(r2 s2-F5):tier=high 要嘛 pass --loop,要嘛 skip --class。

### 範圍刀(明確不做)

不掃 skills/;不自動分型;不擋 design/high 與 standard 的外家;不改 `_TIER_ROSTER`;**不改 pre-push hook**(只改它呼叫的 `code-loop check`);不改 `loop status` 判定式;不做 S4/S5;棘輪不涵蓋不寫帳的軟提醒;不區分外家之間的家族(同族兩席=2,見未決)。

## 退場條件(★每條指名指令與欄位★)

| 件 | 量測(指令) | 條件 |
|---|---|---|
| S1 | `gov --stats --since 90`:`check-a` 列 | 連續 90 天零筆 → 退場候選。漏抓為負事件不可自動量 → 每 90 天人工盤點寫 Verification(`plan_refs` 回指本節點) <!--lumos:risk=C why="負事件無法由命中型檢查自記,結構限制" revisit="若 Verification 盤點出漏抓 ≥3 則補詞表或改只列"-->;★這條人工盤點本身靠自律★ <!--lumos:risk=A--> |
| S2 | `gov --stats --since 90`:`ratchet` 與 `ratchet-ack` 列的去重筆數 | 90 天 `ratchet`=0 → 退場候選;`ratchet-ack`/`ratchet` ≥0.5(★兩者同為 (gate,stem) 事件粒度,r2 s5-F3 尺度問題以「每鍵每 run 最多一筆」解★)→ 門檻 20 重議 |
| S3 | `gov --since 90 --full` 逐行計 `[code-loop/passed]`、`[code-loop/skipped]`(detail 含 `class=emergency`)、`[external-waived/waived]`(★`gov --full` 輸出格式本就逐筆印 gate/kind/detail,r2 s5-F2:不靠 --stats 表★) | (emergency skip + waived)/passed ≥0.5 → 外家管道不穩,攤人;90 天零 waived 零 emergency 且 passed>0 → 維持 |

## 本 PR 怎麼過自己的規則(r2 s5-F4)

上線 PR 本身是 code/high(動 doctor/lint/code-loop):①先補標存量承認句+兩處圍欄,使 Check A 上線即綠;②實算棘輪基線,解/ack 命中者;③本 PR 的 code-loop 走 `pass --loop 檢核收緊五件`——本 loop r1/r2 已各有 1 席 gemini 外家(family=external);照 S3 需「最後兩輪內至少一輪 ≥2 席 external」,★r3 派兩席外家(gemini 兩次獨立呼叫,不同 prompt 鏡頭)★以滿足自家規則;若外家 503 不可用 → `--waive-external` 留痕,這會成為 S3 退場條件的第一筆分子,如實。

## 測試策略(TDD,先紅後綠)

S1:1 unmarked→lint rc1/ci issue/純 doctor rc0 列出;2 A/H/B/C 合法各一過;3 A/H 帶欄違規;4 B issue 裸 stem/不存在/非 issue/未來日/兩欄皆有皆無 各報;5 C 缺欄報;6 否定前綴豁免(「而非靠自律」不報,「靠自律」報);7 圍欄內不報(含未閉合圍欄不吞下文——沿 `_strip_fences_text` 既有測試語意);8 frontmatter decisions[].content 命中報;9 why 含空白/中文/等號/引號內 `-->` 以外字元皆解析;10 `--ci` 寫 `check-a` 事件。
S2:11 run=含 check-* 事件的 commit(anchor-approve 單獨 commit 不算);12 20 連續升/19 不升/中斷不升/最新 run 缺不升;13 append 序非 ts 序(造 ts 亂序 fixture);14 頂端位置+`--ci` issue+`ratchet` 事件;15 `ratchet_acks` 多閘互不覆蓋、30 天窗、過期印「曾 ack」、寫 `ratchet-ack`;16 LIST_KEYS 含 `ratchet_acks`。
S3:17 `_codeloop_range()` 有/無 upstream 兩路;18 pass high 無 --loop rc2 無留痕;19 窗口 min(2,輪數) 三案;20 進行中輪(有 dispatch 無 record)不計;21 三種 dispatch 形狀各一;22 無 dispatch rc1;23 waiver 留痕+事件;24 check:range 不同源視同無留痕並印提示;25 skip high 無 --class rc2、帶 class 留痕+detail;26 standard 不受影響;27 `loop next` streak 只印不寫帳;28 `_KNOWN_GATES` 含 check-a/ratchet/ratchet-ack/external-waived,且四者皆以 `"gate": "…"` 字面值寫入(漂移測試自動釘)。

## 實務隱患

**通用三問**:併發——純讀為主;留痕/ack/append 走既有 atomic 路徑。效能——S2 多掃治理帳一遍(線性);S3 pass 多跑一次 pitfalls。資源——全 with-open。
**self-governance(命中)**:三件硬擋;逃生門=A/H 標記、ack、waive、skip --class——★四個全部落帳可數,退場條件直接以它們為分子★。自簽與時區=天花板。**range 不同源改為 fail-closed**是本案把「靜默失效」翻成「明擋+提示」的核心。
**已排除**:金流/對外送出/PII。**不可逆**:無。**遷移**:`_KNOWN_GATES` +4、`LIST_KEYS` +1;code-loop 留痕 JSON 新增選填鍵(loop/range/tier/external_ok/waiver/class),舊讀者 `.get` 不炸;`check` 對舊留痕(無 range 欄)在 tier=high 下視同無效——★這是刻意的:舊 passed 留痕不該放行新規則下的 high 推送★。

## 未決

- 棘輪 N=20、ack 30 天:拍的,上線後以 `ratchet`/`ratchet-ack` 筆數回看。
- 外家同族兩席算兩席(編制表只分 claude/external):現況只有 gemini 一家可用,本案照表;是否該要求異族,另案。
- `_codeloop_range()` 無 upstream 時「預設分支」取 `origin/HEAD` → 無 origin 時退 `main`;與 pre-push 的 stdin 範圍仍可能不同(例如 force-push 歷史改寫)——不同即擋、印提示,不猜。

## 審計修正紀錄

- **r1 panel(2026-08-21,五席同門+★外家否決席 gemini-3-flash 首次到位★)**:blocker 10 / major 24 / minor 5。★裁定=不補丁,重寫 v2:砍 S4/S5(無獨立事故、不擋、搭便車——s5-F7/F8)、三件全硬★。blocker 逐條:s2-F1/s1-F2/s4-F1 ack 純量撞閘→改 list 鍵;s2-F4 tier 不在 loop status→S3 改掛 code-loop pass(自跑 pitfalls 判 tier);s3-F1 否定句誤判→前綴豁免;s3-F2 Issue 節點自撞→例句入圍欄;s3-F5 棘輪基線→判準改「最近 20 run 連續」且上線先清 check-e1 5 組;s3-F8 自簽→標天花板+落帳可數;s3-F9 waived 子字串→明確旗標;s4-F3 閘可繞→綁放行點;s5-F1 漏抓不可量→改人工盤點 Verification;s6-1 冷啟動→min(K,輪數)。major 全數折入(路徑鍵/連續 run/升級落帳/dispatch 無 ts/席數照編制/nodes 語意登記/範圍句自相矛盾/A 帶欄違規/退場條件逐條指名指令/Growth test 逐件)。**收貨**:六席引句全數錨定(外家席報告做了一次純格式正規化:粗體標籤→裸標籤,內容未動);refcheck 全 ok。**辯方路由**:blocker 皆經編排者以 file:line/實跑資料自核(含實算治理帳證實 s3-F5),路由 i。

- **r2 panel(2026-08-21,五席同門+外家 gemini-3-flash)**:blocker 9 / major 15 / minor 4(外家 6 條中 2 條引句含省略號不採信;其 #1「loop id 可重用」論點編排者自核成立,以自查名義折入)。★裁定=v3 重寫★:S3 閘從 pass 移到 push 檢查點 `code-loop check`(留痕綁 range+HEAD,不同源即擋)、skip 在 high 改破窗制、撤 `--no-loop`、撤 `external-absent`(loop next 唯讀契約)、輪序改 append 序、進行中輪不計;S2 run 改「含 check-* 事件的 commit」、鍵改 stem(路徑不可實作)、append 序;S1 加 H 型、欄位加引號、issue 須 `Issues/` 前綴、撤區段豁免、圍欄改 `_strip_fences_text`(★同日早上我給 Check N 加的正則正是檔頭明禁的 FENCE_RE,本輪抓到已另 commit 修正★)、r1 宣稱的圍欄修法確認未落地列為實作第一步;退場條件 S3 改用 `gov --full` 逐筆計;加「本 PR 怎麼過自己規則」段。**收貨**:五席同門引句全錨定、refcheck 2 條 missing(皆為引用他檔的大括號展開寫法,判格式)。
- **r1 pre-flight(2026-08-21,機械掃)**:①S3 把 design/high 與 code/high 混為「tier=high」——編制表只有 code/high 是 fail-closed,已限縮 ②「存量 38 處」無法重現(依詞表 28~51),改以實掃為準 ③`downgraded=` 無失敗條件,補日期格式+不得未來 ④`--findings-doc` 在無 `--findings` 時未定義,補驗證並順帶補既有 `--findings` 非負 ⑤雙入口範本引錯(Check N 是 doctor 單入口,應抄 Check J)⑥`check-a` 落帳無測試、S4 各模式無逐模式測試,已補。

