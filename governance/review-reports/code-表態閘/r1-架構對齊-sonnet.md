severity: major

## Findings

### f1 留痕座標有效性判定有兩套,新的那套沒接進舊呼叫點
severity: major
blocking: 是
file: `scripts/lumos:21268`
引句:「留痕座標有效性(pass/skip 與表態共用同一套):同 sha;或 rec_sha 是 marker_sha 的祖先且中間只動簿記檔」
`_codeloop_record_valid` 的 docstring 宣稱跟 pass/skip 共用同一套判定,但 `grep -n "_codeloop_record_valid" scripts/lumos` 只出現兩行:21268(定義)與 21383(表態閘 `_dispositions_verdict` 裡唯一的呼叫點)。`_codeloop_guard_verdict` 裡 tier=high 審查留痕的祖先+簿記豁免判定(scripts/lumos:21598-21609)完全沒被改寫成呼叫這支新函式,兩段邏輯(`git merge-base --is-ancestor` + `git diff --name-only` + 簿記白名單比對)逐字相同卻各自維護,以後改一邊很容易忘改另一邊。

### f2 棧別觸發要看哪些檔案的過濾條件也重複了一份,同樣沒收斂舊呼叫點
severity: major
blocking: 是
file: `scripts/lumos:16873`
引句:「棧別觸發要不要看這支檔的改動行:非代碼副檔名、審計證物、簿記檔、測試檔一律不看(同 claims 的過濾)」
`_stack_changed_ok` 的 5 個條件(副檔名黑名單、審計證物目錄、簿記檔、簿記目錄、測試檔 pattern)跟 `_pitfall_diff_collect` 裡原本給 `claims` 用的內聯條件(scripts/lumos:16927-16935)逐字相同,但後者沒有被改寫成呼叫前者——同一個判斷現在有兩份原始碼並存。這跟 f1 是同一種模式(先寫一支「跟既有做法一樣」的新函式,卻沒把舊呼叫點收斂過去),在同一份 diff 裡出現第二次。

### f3 表態家族的函式命名混用三套前綴
severity: minor
blocking: 否
file: `scripts/lumos:21171`
引句:「def _disp_validate(d, platforms=None, default_platform=None):」
同一個表態功能底下,校驗類函式用 `_disp_*`(本行、`_disp_check_test`、`_disp_check_issue` 等共 7 支)、判定/樣板用 `_dispositions_*`(`_dispositions_verdict`:21367、`_dispositions_template`:21444)、讀寫用 `_codeloop_*dispositions*`(`_codeloop_write_dispositions`:21225、`_codeloop_read_dispositions`:21236、`_codeloop_dispositions_gov_log`:21209),三種前綴並存。鄰居家族(`_lens_*`、`_ci_*`)都是單一前綴到底,之後要找「表態相關的函式」得記住三種開頭——f1 已經示範了這種分散命名容易讓人漏改其中一處。

### f4 表態寫治理帳失敗當硬擋,pass/skip 寫治理帳失敗是靜默放行
severity: minor
blocking: 否
file: `scripts/lumos:21214`
引句:「這個專案沒有 docs/,表態進不了治理帳、CI 端讀不到(跟 pass 留痕同一個限制)」
`_codeloop_dispositions_gov_log` 寫不進治理帳時,`dispositions` 子指令回 rc2、連 marker 檔都不寫(scripts/lumos 內 `_cmd_codeloop_dispositions` 的 `if not ok: return 2`);而 `pass`/`skip`(scripts/lumos:21775 `return 0`)不論 `_codeloop_gov_log` 有沒有寫成功都固定印 ✅ 並回 0(`_codeloop_gov_log` 自己的 docstring 寫的是「vault 找不到...→靜默跳過」)。註解說兩者「同一個限制」,但遇到這個限制時的實際處置(拒寫 vs 照樣放行)並不一樣。

## 圖譜鏡頭逐條判定

- **Issues/code-loop守衛main-direct盲區.md**(事故,status: done):不影響。病灶是「main-direct commit 時 `code-loop check` 用 merge-base..HEAD 算出空 diff、tier 恆判 standard」;這份 diff 裡 pre-push 呼叫 `code-loop check` 仍帶 `--diff "$_range" --at-sha "$_lsha"`(推送範圍,不是 merge-base..HEAD),表態閘自己算適用範圍時也明講「推主線本身...用推送範圍」——延續既有修法,沒有讓盲區復發。
- **Systems/canary-audit.md**(★INVARIANT★,間接相依):不影響,這份 diff 沒有碰任何 canary record/second 相關程式碼。
- **Systems/design-loop.md**(★INVARIANT★,間接相依):不影響,處置閘第五步的判定邏輯(loop id 前綴、審材須是 .md)不在改動範圍內。
- **Systems/guard-kill.md**(★INVARIANT★,間接相依):不影響,`_bound_tests_check` 仍呼叫既有 `_kill_run`,guard kill 的 rc 判定與 JSON 輸出邏輯未被觸及。
- **Systems/lumos-cli-lifecycle.md**(★INVARIANT★,間接相依):不影響,re-inject sentinel 相關程式碼未出現在 diff 裡。
- **Systems/lumos-cli-read.md**(★INVARIANT★,間接相依):不影響,search 排除 superseded/stale 的邏輯未被觸及。
- **Systems/slim-get-一行安裝.md**(★INVARIANT★,間接相依):不影響,這份 diff 沒有任何 .ps1 檔案異動。
- **Systems/bound-tests-gate.md**(★INVARIANT★,篇幅超限只列名,因與本次改動直接相關額外核對):INVARIANT 本身(紅/懸空/不合法→blocked=True rc1;其餘不擋但記帳)沒被改寫,`_bound_tests_check` 核心邏輯本次未動,只多了 `bound_advisory` 參數延續既有 red-advisory/red-blocked 分類,判「不影響核心 INVARIANT」。但這份筆記「## 怎麼跑」段落寫的是「低風險推送:pre-push 直接呼叫 `lumos bound-tests --advisory`」,這份 diff 把分支低風險路徑改成走 `code-loop check --bound-tests-advisory`(獨立呼叫只留給 tag);筆記本身不在 r1-snapshot.patch 審材範圍內,判不準,標 ⚠ 交編排者核對筆記是否已同步。
- 其餘篇幅超限只列名的節點(slim-install/slim-uninstall/授權與歸屬/測試假綠形態/anchor-integrity/pitfalls-code-loop/loop-convergence-recording/check-r-guard/cochange-guard/lumos-deinit/reversibility-governance-ledger/core-invariant-baseline/judge-severity-gate/check-t-sentinel/lumos-refcheck/doctor-irreversible-hint):內容未附,無法逐條核對,判不準,標 ⚠ 交編排者;其中 pitfalls-code-loop.md 極可能直接描述這份 diff 改的 `_STACK_PERF_QUESTIONS`/`cmd_code_loop` 機制,建議優先補查。

最嚴重 severity: major,blocking 條數 2

## 三問

**1. 分層與依賴方向**:對齊。表態核心確實插在 `_codeloop_guard_verdict`(scripts/lumos:21476 起)之前,樣板邏輯在 `cmd_pitfalls` 的 `--dispositions-template` 分支,適用性計算在 `_pitfall_diff_collect`/`cmd_impact` 裡呼叫——跟派工單描述一致。沒有出現 hook 自己算適用性:`scripts/hooks/claude/impact-hook.py` 只多送 `delta_text` 原始內容,判定仍在 lumos 那端的 `_stack_applicability` 做;pre-push 對分支 ref 擋不擋完全交給 `code-loop check` 的 rc,自己不下判斷只轉印訊息,對非 heads(tag)沿用改動前就有的「pre-push 自己 grep pf_json 判斷要不要印 advisory」慣例,不是新引入的跨層直呼。dispatch-lens(`cmd_dispatch_lens`)新增呼叫 `_codeloop_read_dispositions` 是第一次跨進 code-loop 家族讀資料,但呼叫的是既有讀取入口而非重讀檔案,且是派工單第(6)項明確要的功能,判對齊。

**2. 命名與錯誤處理**:部分不對齊(f3、f4)。rc 慣例(2=參數錯、1=擋)在 `_cmd_codeloop_dispositions`/`_cmd_codeloop_recall_miss`/`cmd_code_loop` 裡遵守,三段式訊息在 dispositions blocked 分支確實照做——這兩點對齊。但函式命名混用 `_disp_*`/`_dispositions_*`/`_codeloop_*dispositions*` 三種前綴(scripts/lumos:21171/21367/21225),而且 `dispositions` 子指令寫治理帳失敗的處置(rc2、拒寫,scripts/lumos:21214)跟 pass/skip 寫同一份治理帳失敗的處置(靜默放行、rc0,scripts/lumos:21775)不一致——結構都對,但跟鄰居的慣例有落差。

**3. 第二種做法**:多數對齊,但抓到兩個貨真價實的「第二套」。CJK 判定明確沿用 `_RANK_CJK_RE`(diff 自己註明「單一真相」)、設定檔讀法沿用 `_ci_config`/`load_test_profile` 同款直讀 `.lumos/config.json`、payload 也只是在既有的單一 JSON dict 裡加欄位——這三處都對齊,沒有另立入口。但留痕座標有效性判定(`_codeloop_record_valid` vs scripts/lumos:21598-21609 未改寫的舊內聯判定,f1)與棧別觸發要看哪些檔案的過濾條件(`_stack_changed_ok` vs scripts/lumos:16927-16935 未改寫的舊內聯條件,f2)各自形成了兩份要維護的原始碼,兩支新函式的 docstring 都聲稱跟舊邏輯「共用」但實際沒有接上。另外,`extract_delta_text`(scripts/hooks/claude/impact-hook.py:415)與既有 `extract_delta_query`(同檔:437)對 Edit/MultiEdit/Write 的 parts 抽取邏輯逐字重複,但兩者下游用途明顯不同(保留換行的原文 vs 詞彙融合用的截斷字串),diff 自己的註解也解釋了原因——算不算「第二種做法」見仁見智,判不準,標 ⚠,不計入正式 finding。

不對齊共 4 條,其中 major 2 條
