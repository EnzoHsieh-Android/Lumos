severity: minor

# 治理帳例行紀錄分流 r3 整合審(外部投稿,第 3 版修訂稿)

立場:三個月後接手的人。驗〈做法〉7 的同步範圍與 spec 內所有 [[連結]]。

結論先講:沒有 blocking。所有 [[連結]] 指的節點都存在(Systems/reversibility-governance-ledger、retrieval-ranking、lumos-cli-read、Verification/2026-08-21_工具鏈體檢修復批、Projects/交接2026-10-03_計劃、Issues/code-loop-pass自失效追尾、Projects/消費專案接入靜默失效_計劃、Projects/全repo審視_計劃,以及〈做法〉外提到的 Systems/bound-tests-gate、pitfalls-code-loop 都在 docs/lumos-toolchain-knowledge/ 底下)。r2 的 major 修正(白名單、新檔不停止追蹤、舊 vault 補建 docs/.gitignore、兩本依時間排序)我對照程式逐項核過,方向正確:四支直寫入口(`scripts/lumos:1358`、`:1426`、`:42423`、`:43253`)、`.usage-log.jsonl` 唯一寫入點(`scripts/lumos:16186`)、判定類讀者(`:1250`、`:10198`、`:11146`、`:12367`、`:43295`、`governance/autonomous_loop/replay_weekly.py:38`)與統計類讀者(`:2238`、`:2869`、`:3867`、`:8161`)都對得上;`kind` 值(ran、fast、green、ok、hinted、reminded 之類)程式裡都有人寫(`:3489`、`:2289`、`:42952`、`:37050`、`:28520`、`:31575-31597`)。`lumos update` 會呼叫 `_init_additive_setup`(`scripts/lumos:20693`),〈做法〉5 的補丁路徑成立。

剩下的都是〈做法〉7 同步清單「寫得比實際少、或指到不存在的東西」的問題,全是 minor。

1. 程式註解同步只列兩處,漏了會變成說錯話的註解
severity: minor
blocking: 否(不影響判定正確;只是留下過期說明,實作者照單打勾會漏改)
引句:「程式註解:scaffold 與 `_init_additive_setup` 的忽略清單註解。」
佐證:
- `scripts/lumos:20553-20556`(`_pull_source_or_abort` 註解):「唯讀的 `lumos show`/`context` 就會 append docs/.usage-log.jsonl,而那本帳是版控的」。這句正是本案要消除的症狀,上線後對新寫入不再成立,卻不在清單裡。
- `scripts/lumos:2226-2227`(帳本成長段):「這本帳有四個整檔讀者(rewrite 血緣查詢、gov 彙整、code-loop 的 CI fallback、週回放)」,本案後 gov 與 S18、spec-gate 段多讀一本,且 `:2869`、`:3867` 的讀法也變了,這句要跟著改。
- `scripts/test_lumos.py:38658-38661`(update 聯集合併測試的 docstring)同樣寫「那本帳是版控的」「只要有人在來源 clone 裡查過一次圖譜」。
修法方向:〈做法〉7 的程式註解項補上這三處(或寫成「grep `usage-log`、`整檔讀者` 後逐處判斷」)。

2. 〈做法〉7 的測試項指到一類不存在的測試,且沒說明簿記檔名單與 update 合併測試要保留
severity: minor
blocking: 否(實作者查不到會自行判斷;風險是反方向——順手把 update 合併測試的帳檔名改成新檔,測試就不再測到舊來源 clone)
引句:「斷言例行事件寫進 `docs/.governance-log.jsonl`、斷言 `.usage-log.jsonl` 被寫的」
佐證:
- `scripts/test_lumos.py` 裡所有提到 `.usage-log.jsonl` 的位置:`:411`(斷言 scaffold 的 docs/.gitignore 含它)、`:756-761`(`_porcelain_z_paths` 的字串 fixture)、`:15253`(docstring)、`:25140`、`:25160`(註解,明寫「不斷言其無」)、`:38684-38728`(update 聯集合併 fixture,自己直接寫檔)、`:42493`(忽略清單斷言)。沒有任何一支斷言「`show`/`context` 之後它被寫了」。所以「斷言 `.usage-log.jsonl` 被寫的」這一類既有測試並不存在,S1 的 `t_gov_split_routine_goes_local` 才是第一支斷言 usage 寫入位置的測試。
- 反過來,`:38684-38728`、`:411`、`:42493` 這幾處**必須保留舊檔名**:舊 `.usage-log.jsonl` 仍在 `_BOOKKEEPING_FILES`(`scripts/lumos:24193`)、cochange 排除清單(`scripts/lumos:36525`)、scaffold 忽略清單(`scripts/lumos:20881`)裡,舊版來源 clone 與尚未升級的消費專案還會把它弄髒,`_pull_source_or_abort` 的合併分支(`scripts/lumos:20585-20586`)靠 `_BOOKKEEPING_FILES` 判斷。r2 整合席 finding 9(`r2-整合-sonnet.md` 末段)已提過「spec 沒說保留還是移除」,r3 仍未明說。
- 新本機帳被 `.gitignore` 忽略,不會出現在 `git status --porcelain`,所以不需要加進 `_BOOKKEEPING_FILES`;spec 應把這個結論寫出來,免得實作者因為「新帳檔都是簿記檔」順手加進去。
修法方向:〈做法〉4 或 7 加一句「`_BOOKKEEPING_FILES`、cochange 排除清單、scaffold 的 `.usage-log.jsonl` 忽略行、update 合併測試都保留舊檔名;新本機帳因被忽略不加進這些清單」;測試項把「斷言 `.usage-log.jsonl` 被寫的」刪掉。

3. 「兩條近期到期的 REVISIT」數量不對,而且其中一條指到的那行其實不受影響
severity: minor
blocking: 否(統計類提醒,偏吵不偏漏;spec 的判準句「若讀的是本機名單上的種類」本身是對的,錯的是點名的數量與位置)
引句:「兩條近期到期的 REVISIT(合約測試閘、守檔筆記對照改動)」
佐證:
- 合約測試閘那篇有兩條 2026-10-07 的 REVISIT:`docs/lumos-toolchain-knowledge/Projects/合約測試閘什麼時候跑_計劃.md:282` 查 `red-advisory`——這個種類在 spec 的不在名單清單裡(自動放行與降級),照舊進版控,**不受影響**;`:285` 查 bound-tests 的耗時欄位——耗時掛在 `green` 事件上(`scripts/lumos:42952` 寫 green,`:42447-42455` 說明 secs 是獨立欄位),`green` 在本機名單,**受影響**。spec 沒分這兩條。
- 漏列:`docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:37`(REVISIT:2026-10-14,離今天 10 天)寫的是 `grep '"check": "old-sentence"' docs/.governance-log.jsonl`;這類事件由 `_drift_m1_ledger` 寫成 gate=drift-check(`scripts/lumos:35704-35727`),kind 為 `passed` 時 hard=False,依〈做法〉1 進本機帳。分流後這條 grep 在版控帳上只剩 warned、blocked、range-unavailable,兩週量到的「通過」會憑空消失;而且它還要請 rtb 會談跑同一個 grep,rtb 那份也一樣。
修法方向:〈做法〉7 的 REVISIT 項改成「`grep -rn REVISIT` 後凡查治理帳且種類在本機名單的都改」,並點名舊句檢查:37 與合約測試閘:285(:282 不用改)。

4. 手冊項指到的「段落」在 reference.md 裡不存在,實際要改的是一格表格列
severity: minor
blocking: 否
引句:「`skills/lumos-project-notes/reference.md` 講治理帳寫在哪裡的段落。」
佐證:
- `skills/lumos-project-notes/reference.md` 全檔提到 `governance-log` 的只有 `:61`(指令對照表的一列:「唯讀彙整 bypass/rot/governance-log;本機可見性」)與 `:88`(cochange 預設排除治理帳,不受本案影響),沒有任何一段在講「治理帳寫在哪裡」。`:61` 還提到已拆除的 rot 來源(`docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:31` 已記 2026-08-22 拆除)。
- 其餘 skills 提到治理帳的位置(`skills/lumos-project-notes/commands/INDEX.md:22` 的 `ci-wait`、`commands/06-代碼審與推送.md:10,14`、`skills/lumos-code-loop/reference.md:200` 等)講的都是 ci、lint-waive、bound-tests 跳過、表態這些種類,依〈做法〉1 照舊進版控,不用動。
修法方向:改成「`reference.md:61` 那一列:補上本機帳、拿掉 rot」,免得實作者找不到那個段落而空手打勾。

5. 圖譜節點「要改的說法」引的不是原文,接手的人要自己猜
severity: minor
blocking: 否(r2 整合席 finding 8 已提過,r3 只修了一半:補上 `lumos:count` 正則,沒補原文位置)
引句:「「帳檔都進版控」的說法」
佐證:
- `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:103` 實際措辭是「帳檔已入 git 追蹤,非 gitignore」;`:54` 是「doctor 是唯一新寫者且只在 --ci append」;`:31` 是 `lumos:count=6` 加正則 `(?m)^\s+load\((?:\"\.|CI_LOG_NAME)`。spec 引的「帳檔都進版控」在該篇不是原文,grep 找不到。
- 正則只認 `load(".…` 與 `load(CI_LOG_NAME`。〈做法〉3 要用常數 `GOV_LOCAL_LOG_NAME`,若 `cmd_gov` 寫成 `load(GOV_LOCAL_LOG_NAME, …)` 就不會被數到(標記仍 6,Check N 不報),寫成字面值 `load(".governance-local.jsonl"` 才會被數到變 7。spec 說「含它的正則」要同步,但沒說該選哪一種寫法,兩種寫法的後果不同。
修法方向:同步項直接列行號(`:31`、`:54`、`:103`),並指定 `load` 的寫法與數字標記要一起對。

6. 「r2 整合席報告列出的既有測試」把清單外包給卷證檔,行號會漂
severity: minor
blocking: 否
引句:「r2 整合席報告列出的既有測試」
佐證:
- 該清單在 `governance/review-reports/gov-ledger-split/r2-整合-sonnet.md`(finding 8 的最後一條),含 `scripts/test_lumos.py:5954-5955,6038-6058,8907-8991,10509,15394,23716,25031` 與 `scripts/test_autonomous_loop.py:1736`。我驗了其中 `test_autonomous_loop.py:1736`(確實把 converged 事件寫進 `docs/.governance-log.jsonl`,但 converged 是 design-loop 種類,依〈做法〉1 照舊進版控,**不用改**)與 `test_lumos.py:8907-8912`(bound-tests `--advisory` 後讀版控帳找 `red-advisory`,同樣屬不在名單的種類,**不用改**)。也就是說 r2 這份清單裡至少有兩處在 r3 的白名單下反而不用改,照單全改會把測試改錯。⚠ 其餘行號我沒逐條驗。
修法方向:同步項不要引卷證檔當清單;改成「實作時 `grep -n 'governance-log' scripts/test_lumos.py scripts/test_autonomous_loop.py`,逐條依〈做法〉1 判斷該事件種類是否在本機名單」。

總結:沒有 blocking;連結全部存在、r2 的重大修正改對了,剩 6 條 minor 都是〈做法〉7 同步清單的精確度(漏列 3 處註解與 1 條 REVISIT、一條測試項指到不存在的測試、手冊與圖譜的「要改的句子」不是原文、簿記檔名單該保留沒寫明)。
