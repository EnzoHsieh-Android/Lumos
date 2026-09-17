severity: blocker

# 規格落成可驗收條件_計劃 r4 審查報告(對照 r3→r4 折的 C1–C22,聚焦本輪立場:補丁是否仍能被繞)

## 逐節讀後總覽
「為什麼」「兩層要分開」「進度」「要動什麼」「誠實界線」「審計修正紀錄」四節已讀,交叉引用(`_CLAUSE_LEAD_RE`、`cmd_contracts`、`IRREVERSIBLE_RE`、`CHECKPOINT_RE`、`_visible_lines`、`_plans_in_range`、`_door_for_loop`、`_round_valid_m2`、`_vault_write_lock`、`PITFALL_CLASSES`、`INV_TAG_RE`、`_CI_RED`、`_jsonl_append_verified`、`_clause_bindings_for`、`_ran_evidence_check`)在 `scripts/lumos` 逐一存在,無懸空引用,無新 finding。

## F1(角度①:實務隱患節邊界能否被降級標題繞過)—— 已讀,查無 finding
引句:「節的範圍到下一個 `##` 或 `#` 標題(三級標題屬於節內)」
判定機制是「`_excluded_line` 逐行比對 `已排除:<四類中文名>:<理由>` 這個嚴格格式,再檢查該行是否落在節範圍內」——節邊界只影響「哪些"已排除:"格式行算合格」,不影響「一般文字是否被跳過」。把其餘各節降成 `###` 塞進實務隱患節,只會讓更多"已排除:"格式行落入節內被跳過,不會讓不符合該格式的一般关键字命中句被豁免;硬單向門規則 1 掃描範圍仍是「計劃全文」。未找到能讓「全文關鍵字也全被跳過」的具體路徑。
severity: minor
blocking: 否——找不到可利用的失敗場景,只是節邊界在「實務隱患是最後一個 `##`(無後續標題)時如何收尾」未明寫,屬於文件遺漏而非繞過口。

## F2(角度②:keeps 既存性檢查依賴 `created` 欄位,但該欄位可由作者自由回填)
severity: blocker
引句:「取測試檔在 `created` 日期之前的最後一次提交(`git log -1 --before=<created> --format=%H -- <測試檔>`)」
`created` 是計劃筆記 frontmatter 裡的純量欄位,`lumos set` 可自由覆寫(`scripts/lumos:28164` `p = sub.add_parser("set", ...)`,`scripts/lumos:28179` 只擋「不帶 value 整個拿掉」,不擋改值),且全庫沒有任何地方把 `created` 拿去跟該計劃檔案自己的 git 首次提交時間核對(`grep -n "created.*git log\|first commit" scripts/lumos` 零命中)。作者可以:先在別的、不相干的提交裡塞進一支樁測試 `def test_x(): pass`,隔天再寫計劃並用 `lumos set <計劃> created <未來日期>`,`git log -1 --before=<created>` 就會抓到那支「早於 created」的提交,樁測試被判定為既存,`[keeps]` 直接放行——這正是本輪 C2 想堵的「舊名繞過」的姊妹漏洞,只是攻擊面從「測試名字」換成「created 這個自報欄位」。
severity: blocker
blocking: 是——直接讓三層防線裡最關鍵的一層(既存性)失效,而且不需要動測試名,只需要一次 `lumos set`,成本比 C2 原本擋的 pickaxe 繞法更低。

## F3(角度③:紅的判準只定義了「失敗」,skip/xfail/error 未定義)
severity: major
引句:「N==1 且失敗才算紅;N==0**(匯入錯、檔名錯、環境缺)是弱證據,擋下並印原因,不當紅也不當綠」
spec 只講「N==1 且失敗才算紅」,但沒有定義「失敗」本身怎麼從輸出裡判出來(rc、還是輸出裡出現 `FAILED`/`N failed` 字樣),也完全沒提 `skip`/`xfail`/`error` 這三類非 fail 非 pass 的結果怎麼歸類。以字面演算法推:pytest 只加總「N failed / N passed」,一支被 skip/xfail/error 的測試不落在這兩個桶,算出 N=0,會落進「弱證據擋下」(尚算安全,但診斷訊息會誤導成「匯入錯/檔名錯/環境缺」);unittest 的 `Ran N test(s)` 卻會把 skip 算進 N(`Ran 1 test ... OK (skipped=1)`,rc=0),N==1 但不是「失敗」,依現有文字不會被判紅——這種情況下 S6/S7 會怎麼收尾(印「格式看不懂」?當綠擋下?)完全沒寫,是留給實作者自由發揮的未定義行為,而不是機械判準。
severity: major
blocking: 否——目前兩條路徑的自然推論都不會「誤放行」(pytest 側落入弱證據擋下、unittest 側至少不會被算成紅),但這是未定義行為,落地時如果實作者選了不同的加總方式(例如用「N=collected 而非 failed+passed」),就可能反過來把 skip 誤算成通過測試而放行,建議在落地前把「失敗」偵測與 skip/xfail/error 的歸類寫死,不要留給實作者猜。

## F4(角度④:退場門檻分子公式排除了 CI/推送閘來源的逃逸)
severity: blocker
引句:「分子只數 `precision: finding` 與手動記的列」
`precision` 欄位目前只有代碼審來源會寫(`scripts/lumos:6211-6214`,`extra={"precision": _precision}`);CI 來源(`scripts/lumos:22399` `_ci_red_escape` 呼叫 `_auto_escape` 未帶 `extra`)與推送閘兩路(`scripts/hooks/pre-push:240,246` `loop escape --auto --stage push-gate[-unreviewed]`,經 `scripts/lumos:7635` 呼叫 `_auto_escape(..., source=stage.strip())` 同樣未帶 `extra`)寫出來的紀錄天生沒有 `precision` 欄;而手動記的紀錄(`scripts/lumos:7714` 的 `rec = {...}`,不含 `precision`、也不含 `auto`/`source`)才是唯一「無 precision 但要被計入」的類別。按字面公式「precision=finding 與手動記的列」實作,CI 紅與推送閘擋下這兩種本案自己認定「機械證據最硬」的來源(第五節逃逸定義的三個來源之二)會被排除在撤除條件的分子之外,而它們才是第六節撤除條件①②(blocker/major 逃逸計數)最該接住的東西。
severity: blocker
blocking: 是——直接讓 RETIRE-IF ①/② 這面「誠實界線」自稱的承重牆失真,雙向門即使持續在 CI/推送閘炸出 blocker 級缺陷,只要沒人手動補記、代碼審也沒給 `--finding-severity`,分子可以恆為零,退場機制形同虛設。

## F5(角度⑤:CI 步驟名判準只看「/」後段,是否被步驟名本身的「/」切錯邊界)—— 已讀,查無 finding
引句:「只看每段「/」後面的步驟名(r3 回滾席:本 repo 唯一的工作叫 `test`」
`file: scripts/lumos:22365-22366` `step = seg.split("/", 1)[1] if "/" in seg else seg` 用的是 `maxsplit=1`,只在第一個「/」切一刀;由於 `failed_step` 是程式自己組的 `f"{job}/{step}"`(job id 不含「/」),不論步驟名本身含幾個「/」(如「Deploy to prod/eu」),第一刀永遠落在 job 與 step 的邊界上,`step` 部分會完整保留後續所有「/」,不會被切錯。找不到能讓邊界切錯的具體輸入。
severity: minor
blocking: 否——找不到可利用的失敗場景,`maxsplit=1` 加上 job id 天生不含「/」使這條攻擊面不成立。

## 固定席節點逐條判(這份設計會不會破壞該節點宣稱的行為/合約)
- Systems/design-loop(★INVARIANT★處置閘第五步):**會動,但屬計劃內已知、已綁測試的改動**——spec 明寫要改寫這條不可變合約行(新文字草稿見設計第四節),且 C11 已把「懸空只提醒不擋」這條既有語意保留、綁 `t_disposal_step5_shares_checker`(S8)。不算破壞,是有留痕的合約變更。
- Systems/bound-tests-gate(★INVARIANT★):**不影響**——r3 已訂正 PRIOR-ART,spec-gate 的支數解析是新寫的判準,不再誤稱借用 `_ran_evidence_check`,兩者互不干涉。
- Issues/code-loop守衛main-direct盲區:**不影響**——spec 明寫 range 必須沿用 pre-push 既有的 push-range 計算、不得自算 merge-base,正是為了不重開這個事故。
- Systems/anchor-integrity(★RISK★):**不影響合約本身**——pre-push、test_lumos.py 是錨點檔,spec 的「進度」節已按既定流程執行 `lumos anchor approve`,是走正常審批路徑而非繞過。
- Systems/每支檔有家:**不影響**——`lands_in` 已列 `Systems/design-loop` 與新開的 `Systems/規格閘`,改到的檔都有家可歸。
- Systems/canary-audit(★INVARIANT★ record/second 落盤可讀回、second 不影響 rc):**不影響**——spec-gate 留痕明寫走既有 `cmd_canary` 寫入口(只擴充 `kind` 列舉),沿用同一支 `_jsonl_append_verified` 等落盤/讀回機制,沒有另開寫路徑。
- Systems/guard-kill(★INVARIANT★):**不影響**——本案完全不碰 guard-kill 的 rc 判定與 JSON 純淨輸出邏輯。
- Systems/lumos-cli-lifecycle(★INVARIANT★ re-inject sentinel 保護):**不影響**——「要動什麼」節提到消費端要跑 `lumos update` 同步模板句子,用的是既有 re-inject 機制走正常路徑,沒有改動 sentinel 邊界規則。

## 實務隱患鏡頭逐類
- **併發**:碰到——寫側共用 `_vault_write_lock`(CI/推送閘/代碼審三來源共用同一把鎖去重),已處理,無新 finding。
- **效能**:碰到——文件自己「已排除:效能」一行,理由是閘只跑綁定的幾支測試、全套留給推送閘,合理,無新 finding。
- **資源**(磁碟滿/唯讀):碰到——fail-open 失敗寫治理帳,雙重失敗承認「量不到」並已把對應 REVISIT 改綁事件而非日期,誠實但仍是已知缺口,已在 r3 折入,不重複開。
- **回滾**:碰到——回退節的基準 sha 待填,已有 REVISIT 綁 S8 落地時必填,無新 finding。
- **遷移**:碰到——「生效範圍」明寫比照 `_CLAUSE_GATE_SINCE` 不回溯舊計劃,`_DOOR_RULE_VERSION` 改版要求「從零重數 30 份、舊帳不重分類」,已處理,無新 finding。

## 最終彙總
最嚴重 severity:blocker
blocking 計數:2 條(F2、F4);F1/F3/F5 blocking 皆為否,F3 為 major 但非阻塞——共 2 條 blocking(與正文逐條 blocking 欄一致)。
